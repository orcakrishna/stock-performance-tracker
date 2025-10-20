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
from config import FALLBACK_NIFTY_50, FALLBACK_NIFTY_NEXT_50, FALLBACK_BSE_SENSEX, COMMODITIES
from cache_manager import load_from_cache, save_to_cache, load_bulk_cache, save_bulk_cache


@st.cache_data(ttl=86400)  # Cache for 24 hours
def fetch_nse_csv_list(csv_filename):
    """Fetch stock list from NSE CSV endpoint (stable, avoids API 421 errors)"""
    try:
        url = f"https://nsearchives.nseindia.com/content/indices/{csv_filename}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/market-data/live-equity-market'
        }
        
        with requests.Session() as session:
            session.headers.update(headers)
            # Warm-up: Visit homepage to set cookies (prevents blocks)
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)  # Brief pause for stability
            
            response = session.get(url, timeout=10)
            
            if response.status_code == 200:
                csv_content = response.content.decode('utf-8')
                df = pd.read_csv(StringIO(csv_content))
                stocks = [f"{symbol}.NS" for symbol in df['Symbol'].tolist() if pd.notna(symbol)]
                if len(stocks) >= 40:  # Validate
                    return stocks
                else:
                    return None
            else:
                return None
    except Exception as e:
        return None
    
    return None


@st.cache_data(ttl=86400)
def fetch_nifty_50_from_nse():
    return fetch_nse_csv_list('ind_nifty50list.csv')


@st.cache_data(ttl=86400)
def fetch_nifty_next_50_from_nse():
    return fetch_nse_csv_list('ind_niftynext50list.csv')


@st.cache_data(ttl=86400)
def fetch_nifty_total_market_from_nse():
    return fetch_nse_csv_list('ind_niftytotalmarket_list.csv')


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
        
        # Calculate prices for different periods
        # For 1 week: go back 5 trading days (1 week of trading)
        if len(hist) >= 5:
            price_1w = hist['Close'].iloc[-6]  # 5 trading days ago
        else:
            price_1w = hist['Close'].iloc[0]
        
        # For longer periods: use date-based lookup
        def get_price_by_days_back(days):
            target_date = current_date - pd.Timedelta(days=days)
            # Find the closest date in history
            idx = hist.index.get_indexer([target_date], method='nearest')[0]
            return hist['Close'].iloc[max(0, min(idx, len(hist)-1))]
        
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
    """Fetch current prices for oil, gold, silver, and BTC"""
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
    """Get stock list with dynamic fetching and fallback"""
    
    if category_name == 'Nifty 50':
        stocks = fetch_nifty_50_from_nse()
        if stocks:
            return stocks, f"✅ Fetched {len(stocks)} stocks from {category_name}"
        return FALLBACK_NIFTY_50, f"⚠️ Using cached {category_name} list"
    
    elif category_name == 'Nifty Next 50':
        stocks = fetch_nifty_next_50_from_nse()
        if stocks:
            return stocks, f"✅ Fetched {len(stocks)} stocks from {category_name}"
        return FALLBACK_NIFTY_NEXT_50, f"⚠️ Using cached {category_name} list"
    
    elif category_name == 'Nifty Total Market':
        stocks = fetch_nifty_total_market_from_nse()
        if stocks:
            return stocks, f"✅ Fetched {len(stocks)} stocks from {category_name}"
        fallback = list(set(FALLBACK_NIFTY_50 + FALLBACK_NIFTY_NEXT_50))[:100]  # Sample fallback
        return fallback, f"⚠️ Using cached {category_name} sample"
    
    return [], "❌ No data available"
