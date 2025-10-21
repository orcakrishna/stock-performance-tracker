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
from config import COMMODITIES
from cache_manager import load_from_cache, save_to_cache, load_bulk_cache, save_bulk_cache


@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_available_nse_indices():
    """Dynamically fetch available NSE indices"""
    # NSE API index names (for equity-stockIndices endpoint)
    indices = {
        'Nifty 50': 'NIFTY 50',
        'Nifty Bank': 'NIFTY BANK',
        'Nifty PSU Bank': 'NIFTY PSU BANK',
        'Nifty Private Bank': 'NIFTY PRIVATE BANK',
        'Nifty IT': 'NIFTY IT',
        'Nifty Pharma': 'NIFTY PHARMA',
        'Nifty Auto': 'NIFTY AUTO',
        'Nifty FMCG': 'NIFTY FMCG',
        'Nifty Metal': 'NIFTY METAL',
        'Nifty Realty': 'NIFTY REALTY',
        'Nifty Energy': 'NIFTY ENERGY',
        'Nifty Midcap 50': 'NIFTY MIDCAP 50',
        'Nifty Smallcap 50': 'NIFTY SMALLCAP 50',
        'Nifty Total Market': 'NIFTY TOTAL MARKET',
    }
    return indices


@st.cache_data(ttl=3600)  # Cache for 1 hour (more frequent updates)
def fetch_nse_api_stocks(index_name):
    """Fetch stock list from NSE API (real-time data)"""
    try:
        url = f"https://www.nseindia.com/api/equity-stockIndices?index={index_name.replace(' ', '%20')}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nseindia.com/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin'
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            
            # Critical: Visit homepage first to get cookies
            homepage_response = session.get("https://www.nseindia.com", timeout=10)
            time.sleep(2)  # Important delay for cookie setting
            
            # Now fetch the actual data
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and isinstance(data['data'], list):
                    stocks = []
                    for item in data['data']:
                        if isinstance(item, dict) and 'symbol' in item:
                            symbol = item['symbol']
                            # Skip index itself and empty symbols
                            if symbol and symbol not in ['', index_name, index_name.replace(' ', '')]:
                                stocks.append(f"{symbol}.NS")
                    
                    if len(stocks) >= 1:  # At least 1 stock
                        return stocks
                    
            return None
    except Exception as e:
        print(f"NSE API error for {index_name}: {str(e)}")
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
        
        result = {
            'Stock Name': symbol,
            'Current Price': f"₹{current_price:.2f}",
            'Today %': round(change_today, 2),
            '1 Week %': round(change_1w, 2),
            '1 Month %': round(change_1m, 2),
            '2 Months %': round(change_2m, 2),
            '3 Months %': round(change_3m, 2)
        }
        
        # Save to cache
        if use_cache:
            save_to_cache(ticker, result)
        
        return result
        
    except Exception as e:
        st.warning(f"⚠️ Error fetching {symbol}: {str(e)}")  # Show error to user
        return None


def get_commodities_prices():
    """Fetch current prices for oil, gold, silver, BTC, and USD/INR"""
    prices = {}
    
    try:
        oil = yf.Ticker(COMMODITIES['oil'])
        oil_price = oil.history(period='1d')['Close'].iloc[-1]
        prices['oil'] = f"${oil_price:.2f}"
    except:
        prices['oil'] = "--"
    
    try:
        gold = yf.Ticker(COMMODITIES['gold'])
        gold_price = gold.history(period='1d')['Close'].iloc[-1]
        prices['gold'] = f"${gold_price:.2f}"
    except:
        prices['gold'] = "--"
    
    try:
        silver = yf.Ticker(COMMODITIES['silver'])
        silver_price = silver.history(period='1d')['Close'].iloc[-1]
        prices['silver'] = f"${silver_price:.2f}"
    except:
        prices['silver'] = "--"
    
    try:
        btc = yf.Ticker(COMMODITIES['btc'])
        btc_price = btc.history(period='1d')['Close'].iloc[-1]
        prices['btc'] = f"${btc_price:,.0f}"
    except:
        prices['btc'] = "--"
    
    try:
        # Fetch USD to INR exchange rate with 2-day history for change calculation
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
    """Get stock list using NSE API ONLY (dynamic real-time data)"""
    
    # Get available indices
    available_indices = get_available_nse_indices()
    
    # Check if category exists in available indices
    if category_name in available_indices:
        api_index_name = available_indices[category_name]
        
        # Fetch from NSE API (dynamic data only)
        stocks = fetch_nse_api_stocks(api_index_name)
        
        if stocks:
            return stocks, f"✅ Fetched {len(stocks)} stocks from {category_name} (Live NSE API)"
        else:
            return [], f"❌ Failed to fetch {category_name} from NSE API. Please try again."
    
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
    
    # Return None if API fails - will display as N/A
    return None
