"""
Data Fetching Functions for NSE Stock Performance Tracker
Handles all API calls to NSE, Yahoo Finance, and other data sources
"""

import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import COMMODITIES, FALLBACK_NIFTY_50, FALLBACK_NIFTY_NEXT_50, FALLBACK_BSE_SENSEX
from cache_manager import load_from_cache, save_to_cache, load_bulk_cache, save_bulk_cache


@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_available_nse_indices():
    """Available indices with live data from Yahoo Finance"""
    # Only indices that Yahoo Finance has live data for
    indices = {
        'Nifty 50': 'NIFTY 50',
        'Nifty Bank': 'NIFTY BANK',
        'Nifty IT': 'NIFTY IT',
        'Nifty Pharma': 'NIFTY PHARMA',
        'Nifty Realty': 'NIFTY REALTY',
        'Nifty Metal': 'NIFTY METAL',
    }
    return indices


@st.cache_data(ttl=86400)  # Cache for 24 hours (refreshes daily)
def fetch_nse_index_constituents(index_name):
    """Fetch index constituents from NSE CSV (auto-updated when composition changes)"""
    try:
        # Map to NSE CSV filenames
        csv_map = {
            'NIFTY 50': 'ind_nifty50list.csv',
            'NIFTY BANK': 'ind_niftybanklist.csv',
            'NIFTY IT': 'ind_niftyitlist.csv',
            'NIFTY PHARMA': 'ind_niftypharmalist.csv',
            'NIFTY REALTY': 'ind_niftyrealtylist.csv',
            'NIFTY METAL': 'ind_niftymetallist.csv',
        }
        
        if index_name not in csv_map:
            return None
        
        csv_filename = csv_map[index_name]
        
        # Fetch from NSE archives (updated when index composition changes)
        url = f"https://nsearchives.nseindia.com/content/indices/{csv_filename}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/csv',
            'Referer': 'https://www.nseindia.com/'
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            # Visit homepage first to set cookies
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)
            
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                csv_content = response.content.decode('utf-8')
                df = pd.read_csv(StringIO(csv_content))
                
                if 'Symbol' in df.columns:
                    symbols = df['Symbol'].dropna().tolist()
                    stocks = [f"{symbol}.NS" for symbol in symbols if pd.notna(symbol)]
                    
                    if len(stocks) >= 5:
                        return stocks
        
        return None
    except Exception as e:
        print(f"NSE CSV error for {index_name}: {str(e)}")
        return None


@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_nse_csv_list(csv_filename):
    """Fetch stock list from NSE CSV endpoint (fallback method)"""
    try:
        url = f"https://nsearchives.nseindia.com/content/indices/{csv_filename}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/market-data/live-equity-market'
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)
            
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                csv_content = response.content.decode('utf-8')
                df = pd.read_csv(StringIO(csv_content))
                stocks = [f"{symbol}.NS" for symbol in df['Symbol'].tolist() if pd.notna(symbol)]
                if len(stocks) >= 5:
                    return stocks
        return None
    except Exception as e:
        return None


# Removed hardcoded functions - now using dynamic get_stock_list()


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_index_performance(index_symbol, index_name=None):
    """Fetch index performance - prioritize info dict to avoid hist bugs"""
    if index_symbol:
        try:
            ticker = yf.Ticker(index_symbol)
            
            # Try info first (faster, no hist download)
            info = ticker.info
            current_price = info.get('regularMarketPrice') or info.get('previousClose')
            prev_price = info.get('regularMarketPreviousClose') or info.get('open')
            
            if current_price and prev_price and current_price != prev_price:
                change_pct = ((current_price - prev_price) / prev_price) * 100
                return current_price, change_pct
            
            # Fallback to hist if info incomplete
            hist = ticker.history(period='5d')
            if not hist.empty and len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - previous_price) / previous_price) * 100
                return current_price, change_pct
                
        except Exception as e:
            print(f"yfinance debug for {index_symbol}: {e}")  # Silent log, no st.error
            return None, None
    return None, None


def get_stock_performance(ticker, use_cache=True):
    """Fetch stock performance with semi-live current price"""
    symbol = ticker.replace('.NS', '').replace('.BO', '')
    
    # Try loading from cache first
    if use_cache:
        cached_data = load_from_cache(ticker)
        if cached_data:
            return cached_data
    
    # Retry logic for rate limiting with longer delays
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Add small delay before each request to avoid rate limits
            if attempt > 0:
                time.sleep(3 ** attempt)  # 3s, 9s, 27s
            
            stock = yf.Ticker(ticker)
            hist = stock.history(period='4mo')
            
            if hist.empty or len(hist) < 20:
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                return None
            break  # Success, exit retry loop
        except Exception as e:
            error_msg = str(e)
            if "Rate" in error_msg or "429" in error_msg or "curl_cffi" in error_msg:
                if attempt < max_retries - 1:
                    time.sleep(5 ** attempt)  # 5s, 25s, 125s exponential backoff
                    continue
                else:
                    # Don't show warning, just skip silently
                    return None
            else:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                # Don't show warning for common errors
                return None
    
    try:
        # Remove timezone
        hist.index = hist.index.tz_localize(None)
        
        # Get semi-live current price via info
        try:
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or hist['Close'].iloc[-1]
        except:
            current_price = hist['Close'].iloc[-1]
        current_date = hist.index[-1]
        
        # Get previous close for today's change
        if len(hist) >= 2:
            previous_close = hist['Close'].iloc[-2]
            change_today = ((current_price - previous_close) / previous_close) * 100
        else:
            # If only 1 day of data, use open price
            open_price = hist['Open'].iloc[-1]
            if open_price > 0:
                change_today = ((current_price - open_price) / open_price) * 100
            else:
                change_today = 0.0
        
        # Calculate prices for different periods
        # For 1 week: go back 5 trading days (1 week of trading)
        if len(hist) >= 5:
            price_1w = hist['Close'].iloc[-6]  # 5 trading days ago
        else:
            price_1w = hist['Close'].iloc[0]
        
        # For longer periods: use date-based lookup with better accuracy
        def get_price_by_days_back(days):
            target_date = current_date - pd.Timedelta(days=days)
            # Filter data before or on target date
            past_data = hist[hist.index <= target_date]
            if len(past_data) > 0:
                # Get the closest date that's on or before target
                return past_data['Close'].iloc[-1]
            else:
                # If no data before target, use earliest available
                return hist['Close'].iloc[0]
        
        price_1m = get_price_by_days_back(30)
        price_2m = get_price_by_days_back(60)
        price_3m = get_price_by_days_back(90)
        
        # Changes
        change_1w = ((current_price - price_1w) / price_1w) * 100
        change_1m = ((current_price - price_1m) / price_1m) * 100
        change_2m = ((current_price - price_2m) / price_2m) * 100
        change_3m = ((current_price - price_3m) / price_3m) * 100
        
        # Get sparkline data (last 30 trading days for mini chart)
        sparkline_data = []
        if len(hist) >= 30:
            sparkline_prices = hist['Close'].iloc[-30:].tolist()
        else:
            sparkline_prices = hist['Close'].tolist()
        
        # Normalize sparkline data to 0-100 range for consistent display
        if sparkline_prices:
            min_price = min(sparkline_prices)
            max_price = max(sparkline_prices)
            price_range = max_price - min_price
            if price_range > 0:
                sparkline_data = [((p - min_price) / price_range) * 100 for p in sparkline_prices]
            else:
                sparkline_data = [50] * len(sparkline_prices)  # Flat line if no change
        
        result = {
            'Stock Name': symbol,
            'Current Price': f"₹{current_price:.2f}",
            'Today %': round(change_today, 2),
            '1 Week %': round(change_1w, 2),
            '1 Month %': round(change_1m, 2),
            '2 Months %': round(change_2m, 2),
            '3 Months %': round(change_3m, 2),
            'sparkline_data': sparkline_data  # Add sparkline data
        }
        
        # Save to cache
        if use_cache:
            save_to_cache(ticker, result)
        
        return result
        
    except Exception as e:
        st.warning(f"⚠️ Error fetching {symbol}: {str(e)}")  # Show error to user
        return None


def get_commodities_prices():
    """Fetch current prices for oil, gold, silver, BTC, and USD/INR with change indicators"""
    prices = {}
    
    # Oil
    try:
        oil = yf.Ticker(COMMODITIES['oil'])
        hist = oil.history(period='2d')
        if len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            previous = hist['Close'].iloc[-2]
            change_pct = ((current - previous) / previous) * 100
            arrow = '↑' if change_pct >= 0 else '↓'
            color = '#00ff00' if change_pct >= 0 else '#ff4444'
            prices['oil'] = f"${current:.2f}"
            prices['oil_change'] = change_pct
            prices['oil_arrow'] = arrow
            prices['oil_color'] = color
        else:
            prices['oil'] = f"${hist['Close'].iloc[-1]:.2f}"
            prices['oil_change'] = 0
            prices['oil_arrow'] = ''
            prices['oil_color'] = '#ffffff'
    except:
        prices['oil'] = "--"
        prices['oil_change'] = 0
        prices['oil_arrow'] = ''
        prices['oil_color'] = '#ffffff'
    
    # Gold (USD and INR)
    try:
        gold = yf.Ticker(COMMODITIES['gold'])
        hist = gold.history(period='2d')
        usd_inr_rate = 83.5  # Approximate rate, will be updated below
        
        # Try to get actual USD/INR rate
        try:
            usd_inr = yf.Ticker('INR=X')
            usd_inr_hist = usd_inr.history(period='1d')
            if not usd_inr_hist.empty:
                usd_inr_rate = usd_inr_hist['Close'].iloc[-1]
        except:
            pass
        
        if len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            previous = hist['Close'].iloc[-2]
            change_pct = ((current - previous) / previous) * 100
            arrow = '↑' if change_pct >= 0 else '↓'
            color = '#00ff00' if change_pct >= 0 else '#ff4444'
            
            # Gold is per troy ounce, convert to per 10 grams for INR
            # 1 troy ounce = 31.1035 grams
            gold_per_gram_usd = current / 31.1035
            gold_per_10g_inr = gold_per_gram_usd * 10 * usd_inr_rate
            
            prices['gold'] = f"${current:.2f}"
            prices['gold_inr'] = f"₹{gold_per_10g_inr:,.0f}/10g"
            prices['gold_change'] = change_pct
            prices['gold_arrow'] = arrow
            prices['gold_color'] = color
        else:
            current = hist['Close'].iloc[-1]
            gold_per_gram_usd = current / 31.1035
            gold_per_10g_inr = gold_per_gram_usd * 10 * usd_inr_rate
            
            prices['gold'] = f"${current:.2f}"
            prices['gold_inr'] = f"₹{gold_per_10g_inr:,.0f}/10g"
            prices['gold_change'] = 0
            prices['gold_arrow'] = ''
            prices['gold_color'] = '#ffffff'
    except:
        prices['gold'] = "--"
        prices['gold_inr'] = "--"
        prices['gold_change'] = 0
        prices['gold_arrow'] = ''
        prices['gold_color'] = '#ffffff'
    
    # Silver (USD and INR)
    try:
        silver = yf.Ticker(COMMODITIES['silver'])
        hist = silver.history(period='2d')
        usd_inr_rate = 83.5  # Will use the rate from gold calculation
        
        # Try to get actual USD/INR rate
        try:
            usd_inr = yf.Ticker('INR=X')
            usd_inr_hist = usd_inr.history(period='1d')
            if not usd_inr_hist.empty:
                usd_inr_rate = usd_inr_hist['Close'].iloc[-1]
        except:
            pass
        
        if len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            previous = hist['Close'].iloc[-2]
            change_pct = ((current - previous) / previous) * 100
            arrow = '↑' if change_pct >= 0 else '↓'
            color = '#00ff00' if change_pct >= 0 else '#ff4444'
            
            # Silver is per troy ounce, convert to per kg for INR
            # 1 troy ounce = 31.1035 grams, 1 kg = 1000 grams
            silver_per_gram_usd = current / 31.1035
            silver_per_kg_inr = silver_per_gram_usd * 1000 * usd_inr_rate
            
            prices['silver'] = f"${current:.2f}"
            prices['silver_inr'] = f"₹{silver_per_kg_inr:,.0f}/kg"
            prices['silver_change'] = change_pct
            prices['silver_arrow'] = arrow
            prices['silver_color'] = color
        else:
            current = hist['Close'].iloc[-1]
            silver_per_gram_usd = current / 31.1035
            silver_per_kg_inr = silver_per_gram_usd * 1000 * usd_inr_rate
            
            prices['silver'] = f"${current:.2f}"
            prices['silver_inr'] = f"₹{silver_per_kg_inr:,.0f}/kg"
            prices['silver_change'] = 0
            prices['silver_arrow'] = ''
            prices['silver_color'] = '#ffffff'
    except:
        prices['silver'] = "--"
        prices['silver_inr'] = "--"
        prices['silver_change'] = 0
        prices['silver_arrow'] = ''
        prices['silver_color'] = '#ffffff'
    
    # Bitcoin
    try:
        btc = yf.Ticker(COMMODITIES['btc'])
        hist = btc.history(period='2d')
        if len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            previous = hist['Close'].iloc[-2]
            change_pct = ((current - previous) / previous) * 100
            arrow = '↑' if change_pct >= 0 else '↓'
            color = '#00ff00' if change_pct >= 0 else '#ff4444'
            prices['btc'] = f"${current:,.0f}"
            prices['btc_change'] = change_pct
            prices['btc_arrow'] = arrow
            prices['btc_color'] = color
        else:
            prices['btc'] = f"${hist['Close'].iloc[-1]:,.0f}"
            prices['btc_change'] = 0
            prices['btc_arrow'] = ''
            prices['btc_color'] = '#ffffff'
    except:
        prices['btc'] = "--"
        prices['btc_change'] = 0
        prices['btc_arrow'] = ''
        prices['btc_color'] = '#ffffff'
    
    # USD/INR
    try:
        usd_inr = yf.Ticker('INR=X')
        hist = usd_inr.history(period='2d')
        
        if len(hist) >= 2:
            current_rate = hist['Close'].iloc[-1]
            previous_rate = hist['Close'].iloc[-2]
            change = current_rate - previous_rate
            
            prices['usd_inr'] = f"₹{current_rate:.2f}"
            prices['usd_inr_change'] = change  # Positive = INR weakened, Negative = INR strengthened
        else:
            prices['usd_inr'] = f"₹{hist['Close'].iloc[-1]:.2f}"
            prices['usd_inr_change'] = 0
    except:
        prices['usd_inr'] = "--"
        prices['usd_inr_change'] = 0
    
    return prices


def fetch_stocks_bulk(tickers, max_workers=3, use_cache=True):
    """
    Fetch multiple stocks in parallel with aggressive caching
    Optimized for large datasets (1000+ stocks)
    Uses conservative parallelism to avoid rate limits
    """
    # First, try to load from cache
    if use_cache:
        cached_data, missing_tickers = load_bulk_cache(tickers)
        if cached_data:
            st.info(f"📦 Loaded {len(cached_data)} stocks from cache, fetching {len(missing_tickers)} fresh...")
    else:
        cached_data = []
        missing_tickers = tickers
    
    # Fetch missing stocks in parallel with delays
    if missing_tickers:
        fresh_data = []
        progress_bar = st.progress(0)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ticker = {
                executor.submit(get_stock_performance, ticker, use_cache=False): ticker 
                for ticker in missing_tickers
            }
            completed = 0
            
            for future in as_completed(future_to_ticker):
                completed += 1
                try:
                    data = future.result(timeout=30)
                    if data:
                        fresh_data.append(data)
                except Exception as e:
                    ticker = future_to_ticker[future]
                    print(f"Error fetching {ticker}: {e}")
                progress_bar.progress(completed / len(missing_tickers))
        
        progress_bar.empty()
        
        # Save fresh data to cache
        if use_cache and fresh_data:
            save_bulk_cache(fresh_data)
        
        # Combine cached and fresh data
        return cached_data + fresh_data
    
    return cached_data


def get_stock_list(category_name):
    """Get stock list - Always try dynamic fetch first, fallback to hardcoded if fails"""
    
    # Fallback mapping
    fallback_map = {
        'Nifty 50': FALLBACK_NIFTY_50,
        'Nifty Next 50': FALLBACK_NIFTY_NEXT_50,
        'BSE Sensex': FALLBACK_BSE_SENSEX
    }
    
    # Get available indices
    available_indices = get_available_nse_indices()
    
    # Check if category exists in available indices
    if category_name in available_indices:
        api_index_name = available_indices[category_name]
        
        # Try 1: Fetch dynamically from NSE CSV (preferred method)
        yahoo_stocks = fetch_nse_index_constituents(api_index_name)
        
        if yahoo_stocks and len(yahoo_stocks) >= 5:
            return yahoo_stocks, f"✅ Fetched {len(yahoo_stocks)} stocks from {category_name} (🔴 NSE Dynamic)"
        
        # Try 2: Fallback to hardcoded list if dynamic fetch failed
        if category_name in fallback_map:
            fallback_stocks = fallback_map[category_name]
            print(f"⚠️ NSE dynamic fetch failed for {category_name}, using fallback list")
            return fallback_stocks, f"⚠️ Using {len(fallback_stocks)} stocks from {category_name} (📋 Fallback - NSE may be down)"
        
        # No fallback available
        return [], f"❌ Failed to fetch {category_name} and no fallback available"
    
    return [], "❌ No data available"


def validate_stock_symbol(symbol):
    """Validate if a stock symbol exists on NSE/BSE using yfinance"""
    try:
        ticker = yf.Ticker(symbol)
        # Try to get basic info - if it fails, stock doesn't exist
        info = ticker.info
        # Check if we got valid data
        if info and ('symbol' in info or 'shortName' in info or 'longName' in info):
            return True
        return False
    except:
        return False


@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_next_nse_holiday():
    """Fetch the next upcoming NSE holiday dynamically from NSE website"""
    from datetime import datetime
    
    # Fallback: Hardcoded NSE holidays for 2025 (in case API fails in cloud)
    fallback_holidays = [
        "05-Nov-2025",  # Prakash Gurpurb Sri Guru Nanak Dev
        "25-Dec-2025",  # Christmas
    ]
    
    try:
        # Fetch from NSE website
        url = "https://www.nseindia.com/api/holiday-master?type=trading"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/regulations/holiday-master'
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            # Warm-up: Visit homepage to set cookies
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)
            
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                today = datetime.now().date()
                
                # Parse holidays from API response
                if 'CM' in data:
                    for holiday in data['CM']:
                        holiday_date_str = holiday.get('tradingDate', '')
                        
                        if holiday_date_str:
                            # Parse date (format: DD-MMM-YYYY)
                            try:
                                holiday_date = datetime.strptime(holiday_date_str, "%d-%b-%Y").date()
                                if holiday_date > today:
                                    return holiday_date.strftime("%d-%b-%Y")
                            except:
                                continue
    except Exception as e:
        print(f"Error fetching NSE holidays from API: {e}")
    
    # Fallback: Use hardcoded holidays if API fails
    try:
        today = datetime.now().date()
        for holiday_str in fallback_holidays:
            holiday_date = datetime.strptime(holiday_str, "%d-%b-%Y").date()
            if holiday_date > today:
                return holiday_str
    except Exception as e:
        print(f"Error parsing fallback holidays: {e}")
    
    # Return None if everything fails
    return None


@st.cache_data(ttl=60)  # Cache for 1 minute to fetch fresh data more often
def get_fii_dii_data():
    """
    Fetch FII/DII buy/sell data with multiple fallback sources
    Returns data in INR Crores
    Sources: 1) JSON File (GitHub Actions) 2) NSE API 3) NSE Website 4) MoneyControl
    """
    
    # Method 0: Try reading from JSON file first (updated daily by GitHub Actions)
    # But only use if it's today's data
    try:
        import json
        import os
        from datetime import datetime
        
        json_file = os.path.join(os.path.dirname(__file__), 'fii_dii_data.json')
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                data = json.load(f)
                
                # Check if data is from today
                file_date = data.get('date', '')
                today = datetime.now().strftime('%d-%b-%Y')
                
                if data.get('status') == 'success' and (data.get('fii') or data.get('dii')):
                    # Only use JSON file if it's today's data
                    if file_date == today:
                        print(f"FII/DII: Loaded from JSON file (fetched at {data.get('fetched_at', 'unknown')})")
                        return {
                            'fii': data.get('fii'),
                            'dii': data.get('dii'),
                            'status': 'success',
                            'source': f"{data.get('source', 'JSON')} (File)"
                        }
                    else:
                        print(f"FII/DII: JSON file data is old ({file_date}), trying live fetch...")
    except Exception as e:
        print(f"JSON file read failed: {e}")
    
    # Method 1: Try NSE API (may fail on cloud due to IP blocking)
    try:
        url = "https://www.nseindia.com/api/fiidiiTradeReact"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.nseindia.com/',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            # Set cookies by visiting homepage first
            homepage_response = session.get("https://www.nseindia.com", timeout=10)
            time.sleep(2)  # Increased delay
            
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                fii_data = None
                dii_data = None
                
                # Data is in flat format with category field
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict):
                            category = item.get('category', '').upper()
                            
                            # Parse FII/FPI data
                            if 'FII' in category or 'FPI' in category:
                                fii_buy = float(str(item.get('buyValue', 0) or 0).replace(',', ''))
                                fii_sell = float(str(item.get('sellValue', 0) or 0).replace(',', ''))
                                fii_net = float(str(item.get('netValue', 0) or 0).replace(',', ''))
                                fii_data = {
                                    'buy': round(fii_buy, 2),
                                    'sell': round(fii_sell, 2),
                                    'net': round(fii_net, 2)
                                }
                            
                            # Parse DII data
                            elif 'DII' in category:
                                dii_buy = float(str(item.get('buyValue', 0) or 0).replace(',', ''))
                                dii_sell = float(str(item.get('sellValue', 0) or 0).replace(',', ''))
                                dii_net = float(str(item.get('netValue', 0) or 0).replace(',', ''))
                                dii_data = {
                                    'buy': round(dii_buy, 2),
                                    'sell': round(dii_sell, 2),
                                    'net': round(dii_net, 2)
                                }
                
                if fii_data or dii_data:
                    print(f"FII/DII: Fetched from NSE API - FII Net: {fii_data['net'] if fii_data else 'N/A'} Cr, DII Net: {dii_data['net'] if dii_data else 'N/A'} Cr")
                    result = {
                        'fii': fii_data,
                        'dii': dii_data,
                        'status': 'success',
                        'source': 'NSE API'
                    }
                    # Cache successful data
                    try:
                        from datetime import datetime
                        st.session_state['last_fii_dii_data'] = {
                            'fii': fii_data,
                            'dii': dii_data,
                            'source': 'NSE API',
                            'cached_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                    except:
                        pass
                    return result
                else:
                    print(f"NSE API: No FII/DII data found in response")
    except Exception as e:
        print(f"NSE API failed: {e}")
    
    # Method 2: Try scraping NSE reports page (skip on cloud - usually blocked)
    try:
        from bs4 import BeautifulSoup
        
        url = "https://www.nseindia.com/reports/fii-dii"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.nseindia.com/'
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            session.get("https://www.nseindia.com", timeout=3)
            time.sleep(0.5)
            
            response = session.get(url, timeout=5)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for table data
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 4:
                            text = ' '.join([cell.get_text().strip() for cell in cells])
                            
                            # Try to extract FII/DII data from table
                            if 'FII' in text or 'FPI' in text:
                                try:
                                    values = [cell.get_text().strip() for cell in cells]
                                    # Parse numeric values
                                    nums = []
                                    for val in values:
                                        try:
                                            nums.append(float(val.replace(',', '')))
                                        except:
                                            pass
                                    
                                    if len(nums) >= 3:
                                        print("FII/DII: Fetched from NSE Website")
                                        return {
                                            'fii': {
                                                'buy': round(nums[0], 2),
                                                'sell': round(nums[1], 2),
                                                'net': round(nums[2], 2)
                                            },
                                            'dii': None,
                                            'status': 'success',
                                            'source': 'NSE Website'
                                        }
                                except:
                                    pass
    except Exception as e:
        print(f"NSE Website scraping failed: {e}")
    
    # Method 3: Try MoneyControl as final fallback (most reliable for cloud)
    try:
        from bs4 import BeautifulSoup
        
        url = "https://www.moneycontrol.com/stocks/marketstats/fii_dii_activity/index.php"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
        
        print("Trying MoneyControl for FII/DII data...")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for FII/DII data in tables
            tables = soup.find_all('table', class_=['tbldata14', 'mctable1'])
            
            fii_data = None
            dii_data = None
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 4:
                        row_text = cells[0].get_text().strip()
                        
                        try:
                            if 'FII' in row_text or 'FPI' in row_text:
                                buy_val = float(cells[1].get_text().strip().replace(',', ''))
                                sell_val = float(cells[2].get_text().strip().replace(',', ''))
                                net_val = float(cells[3].get_text().strip().replace(',', ''))
                                fii_data = {
                                    'buy': round(buy_val, 2),
                                    'sell': round(sell_val, 2),
                                    'net': round(net_val, 2)
                                }
                            
                            if 'DII' in row_text:
                                buy_val = float(cells[1].get_text().strip().replace(',', ''))
                                sell_val = float(cells[2].get_text().strip().replace(',', ''))
                                net_val = float(cells[3].get_text().strip().replace(',', ''))
                                dii_data = {
                                    'buy': round(buy_val, 2),
                                    'sell': round(sell_val, 2),
                                    'net': round(net_val, 2)
                                }
                        except:
                            pass
            
            if fii_data or dii_data:
                print("FII/DII: Fetched from MoneyControl")
                result = {
                    'fii': fii_data,
                    'dii': dii_data,
                    'status': 'success',
                    'source': 'MoneyControl'
                }
                # Cache successful data
                try:
                    from datetime import datetime
                    st.session_state['last_fii_dii_data'] = {
                        'fii': fii_data,
                        'dii': dii_data,
                        'source': 'MoneyControl',
                        'cached_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                except:
                    pass
                return result
    except Exception as e:
        print(f"MoneyControl fallback failed: {e}")
    
    # All methods failed - try to return last known value from session state
    print("FII/DII: All sources failed, checking for cached data...")
    
    # Try to get last successful data from session state
    try:
        if hasattr(st, 'session_state') and 'last_fii_dii_data' in st.session_state:
            cached = st.session_state['last_fii_dii_data']
            print(f"FII/DII: Using cached data from {cached.get('cached_at', 'unknown time')}")
            return {
                'fii': cached.get('fii'),
                'dii': cached.get('dii'),
                'status': 'cached',
                'source': f"{cached.get('source', 'Cache')} (Cached)"
            }
    except:
        pass
    
    # Last resort: Return placeholder data so UI doesn't show "Loading..."
    print("FII/DII: No cached data available, using placeholder")
    return {
        'fii': {
            'buy': 0.0,
            'sell': 0.0,
            'net': 0.0
        },
        'dii': {
            'buy': 0.0,
            'sell': 0.0,
            'net': 0.0
        },
        'status': 'placeholder',
        'source': 'Unavailable'
    }
