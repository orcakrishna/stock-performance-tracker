"""
Data Fetching Functions for NSE Stock Performance Tracker
Handles all API calls to NSE, Yahoo Finance, and other data sources
"""
import streamlit as st
import pandas as pd
import requests
import json
import os
from io import StringIO
import time
from datetime import datetime, timedelta
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps

from config import COMMODITIES, FALLBACK_NIFTY_50, FALLBACK_NIFTY_NEXT_50, FALLBACK_BSE_SENSEX
from cache_manager import load_from_cache, save_to_cache, load_bulk_cache, save_bulk_cache

DEFAULT_EXCHANGE_SUFFIX = '.NS'


def retry_with_backoff(max_retries=3, initial_delay=1.0, backoff_factor=2.0):
    """Decorator to retry function calls with exponential backoff on failure"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay)
                        delay *= backoff_factor
                    # Log the retry attempt
                    if hasattr(st, 'logger'):
                        st.logger.warning(f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {str(e)}")
            
            # All retries failed, raise the last exception
            raise last_exception
        return wrapper
    return decorator


def normalize_symbol(symbol: str, default_suffix: str = DEFAULT_EXCHANGE_SUFFIX) -> str:
    """Ensure ticker symbols include the correct exchange suffix."""
    if not symbol:
        return symbol
    clean = symbol.strip().upper()
    if clean.endswith('.NS') or clean.endswith('.BO'):
        return clean
    return f"{clean}{default_suffix}"


def fast_get(source, key, default=None):
    """Safely retrieve a key from yfinance fast_info objects or dicts."""
    if source is None:
        return default
    if isinstance(source, dict):
        return source.get(key, default)
    return getattr(source, key, default)


@st.cache_data(ttl=120, show_spinner=False)
def get_cached_history(symbol: str, period: str = '6mo', interval: str = '1d'):
    """Fetch and cache yahoo finance history with sensible defaults."""
    ticker = yf.Ticker(symbol)
    return ticker.history(period=period, interval=interval, auto_adjust=True, actions=False, prepost=False)


@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_available_nse_indices():
    """Available indices with live data from Yahoo Finance"""
    indices = {
        'Nifty 50': 'NIFTY 50',
        'Nifty 500': 'NIFTY 500',
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
        csv_map = {
            'NIFTY 50': 'ind_nifty50list.csv',
            'NIFTY 500': 'ind_nifty500list.csv',
            'NIFTY BANK': 'ind_niftybanklist.csv',
            'NIFTY IT': 'ind_niftyitlist.csv',
            'NIFTY PHARMA': 'ind_niftypharmalist.csv',
            'NIFTY REALTY': 'ind_niftyrealtylist.csv',
            'NIFTY METAL': 'ind_niftymetallist.csv',
        }
       
        if index_name not in csv_map:
            return None
       
        csv_filename = csv_map[index_name]
        url = f"https://nsearchives.nseindia.com/content/indices/{csv_filename}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/csv',
            'Referer': 'https://www.nseindia.com/'
        }
       
        with requests.Session() as session:
            session.headers.update(headers)
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


@st.cache_data(ttl=120, show_spinner=False)  # Cache for 2 minutes for intraday updates
def get_index_performance(index_symbol, index_name=None):
    """Fetch index performance using fast_info for speed"""
    if index_symbol:
        try:
            ticker = yf.Ticker(index_symbol)
            fast_info = getattr(ticker, 'fast_info', None)
           
            current_price = fast_get(fast_info, 'last_price')
            prev_price = fast_get(fast_info, 'previous_close')
           
            if current_price and prev_price and current_price != prev_price:
                change_pct = ((current_price - prev_price) / prev_price) * 100
                return float(current_price), change_pct
           
            hist = get_cached_history(index_symbol, period='5d', interval='1d')
            if not hist.empty and len(hist) >= 2:
                current_price = hist['Close'].iloc[-1]
                previous_price = hist['Close'].iloc[-2]
                change_pct = ((current_price - previous_price) / previous_price) * 100
                return float(current_price), change_pct
               
        except Exception as e:
            print(f"yfinance debug for {index_symbol}: {e}")
            return None, None
    return None, None


@retry_with_backoff(max_retries=3, initial_delay=0.5, backoff_factor=2.0)
def _fetch_stock_data_with_retry(normalized_ticker):
    """Internal function to fetch stock data with retry logic"""
    ticker_obj = yf.Ticker(normalized_ticker)
    fast_info = getattr(ticker_obj, 'fast_info', None)
    hist = get_cached_history(normalized_ticker, period='6mo', interval='1d')
    return fast_info, hist


def get_stock_performance(ticker, use_cache=True):
    """Fetch stock performance with low-latency Yahoo Finance access and retry on failure."""
    normalized_ticker = normalize_symbol(ticker)
    display_symbol = normalized_ticker.replace('.NS', '').replace('.BO', '')

    cache_key = normalized_ticker if ticker != normalized_ticker else ticker

    if use_cache:
        cached_data = load_from_cache(cache_key)
        if cached_data:
            return cached_data

    try:
        fast_info, hist = _fetch_stock_data_with_retry(normalized_ticker)
    except Exception as e:
        # All retries failed, return None
        if hasattr(st, 'logger'):
            st.logger.error(f"Failed to fetch data for {normalized_ticker} after retries: {str(e)}")
        return None
    
    if hist is None or hist.empty:
        return None

    try:
        if hasattr(hist.index, 'tz') and hist.index.tz is not None:
            hist.index = hist.index.tz_localize(None)
    except Exception:
        pass

    # Get current price - use fast_info or fallback to latest hist close
    current_price = fast_get(fast_info, 'last_price')
    hist_close_latest = float(hist['Close'].iloc[-1])
    if current_price is None:
        current_price = hist_close_latest
    current_price = float(current_price)

    # CRITICAL FIX: Use hist data for previous_close (more reliable than fast_info)
    # fast_info.previous_close is unreliable during market hours
    previous_close = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else current_price
    change_today = ((current_price - previous_close) / previous_close) * 100 if previous_close else 0.0

    # CRITICAL FIX: Use TRADING DAYS instead of calendar months for accurate lookback
    # Professional platforms use trading days, not calendar dates
    def get_price_n_days_ago(close_series, trading_days):
        """Get price N trading days ago (not calendar days)"""
        if len(close_series) < trading_days + 1:
            # Not enough data, return earliest available price
            return float(close_series.iloc[0])
        # Go back N trading days from latest close
        idx = max(-len(close_series), -1 - trading_days)
        return float(close_series.iloc[idx])
    
    # Use industry-standard trading day periods:
    # 1 Week = ~5 trading days
    # 1 Month = ~21 trading days (4.2 weeks)
    # 2 Months = ~42 trading days
    # 3 Months = ~63 trading days (quarter)
    price_1w = get_price_n_days_ago(hist['Close'], 5)
    change_1w = ((current_price - price_1w) / price_1w) * 100 if price_1w else 0.0

    price_1m = get_price_n_days_ago(hist['Close'], 21)
    change_1m = ((current_price - price_1m) / price_1m) * 100 if price_1m else 0.0

    price_2m = get_price_n_days_ago(hist['Close'], 42)
    change_2m = ((current_price - price_2m) / price_2m) * 100 if price_2m else 0.0

    price_3m = get_price_n_days_ago(hist['Close'], 63)
    change_3m = ((current_price - price_3m) / price_3m) * 100 if price_3m else 0.0

    spark_period = min(len(hist), 60)
    sparkline_prices = hist['Close'].iloc[-spark_period:].tolist() if spark_period else []
    sparkline_data = []
    if sparkline_prices:
        min_price = min(sparkline_prices)
        max_price = max(sparkline_prices)
        price_range = max_price - min_price
        if price_range > 0:
            sparkline_data = [((p - min_price) / price_range) * 100 for p in sparkline_prices]
        else:
            sparkline_data = [50] * len(sparkline_prices)

    result = {
        'Ticker': normalized_ticker,
        'Stock Name': display_symbol,
        'Current Price': f"₹{current_price:.2f}",
        'Today %': round(change_today, 2),
        '1 Week %': round(change_1w, 2),
        '1 Month %': round(change_1m, 2),
        '2 Months %': round(change_2m, 2),
        '3 Months %': round(change_3m, 2),
        'sparkline_data': sparkline_data,
    }

    if use_cache:
        save_to_cache(cache_key, result)

    return result


@retry_with_backoff(max_retries=2, initial_delay=0.5, backoff_factor=2.0)
def _fetch_52week_data_with_retry(normalized):
    """Internal function to fetch 52-week data with retry logic"""
    stock = yf.Ticker(normalized)
    fast_info = getattr(stock, 'fast_info', None)
    hist = stock.history(period='1y', interval='1d', auto_adjust=True, actions=False)
    return fast_info, hist


@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_52_week_range(ticker):
    """Return current price and 52-week high/low details using fast_info and cached history with retry logic"""
    try:
        normalized = normalize_symbol(ticker)
        fast_info, hist = _fetch_52week_data_with_retry(normalized)
        
        # Try to get 52W data from fast_info first (much faster)
        week_52_high = fast_get(fast_info, 'year_high')
        week_52_low = fast_get(fast_info, 'year_low')
        current_price = fast_get(fast_info, 'last_price')
        
        # If fast_info has the data, use it
        if week_52_high and week_52_low and current_price:
            return {
                'current_price': float(current_price),
                'high': float(week_52_high),
                'low': float(week_52_low),
                'high_date': None,  # fast_info doesn't provide dates
                'low_date': None,
            }
        
        # Fallback to history if fast_info incomplete (already fetched with retry)
        if hist is None or hist.empty:
            return None
        
        try:
            if hasattr(hist.index, 'tz') and hist.index.tz is not None:
                hist.index = hist.index.tz_localize(None)
        except Exception:
            pass
        
        current_price = current_price or float(hist['Close'].iloc[-1])
        week_52_high = float(hist['High'].max())
        week_52_low = float(hist['Low'].min())
        high_date = hist['High'].idxmax()
        low_date = hist['Low'].idxmin()
        
        def _format_date(date_value):
            if isinstance(date_value, pd.Timestamp):
                return date_value.strftime('%d %b %Y')
            return None
        
        return {
            'current_price': current_price,
            'high': week_52_high,
            'low': week_52_low,
            'high_date': _format_date(high_date),
            'low_date': _format_date(low_date),
        }
    except Exception as e:
        print(f"52-week data fetch failed for {ticker}: {e}")
        return None


@st.cache_data(ttl=3600, show_spinner=False)
def get_commodities_prices():
    """OPTIMIZED: Fetch all commodity prices with SINGLE bulk download - 5-10x faster"""
    prices = {}
    
    # CRITICAL FIX: Use SINGLE bulk download instead of 6+ separate API calls
    # This dramatically reduces ban risk and is much faster
    tickers_list = [
        COMMODITIES['oil'],      # CL=F
        COMMODITIES['gold'],     # GC=F  
        COMMODITIES['silver'],   # SI=F
        COMMODITIES['btc'],      # BTC-USD
        COMMODITIES['ethereum'], # ETH-USD
        'INR=X'                  # USD/INR rate
    ]
    
    try:
        # Download all at once - much more efficient
        data = yf.download(tickers_list, period='1mo', interval='1d', progress=False, 
                          group_by='ticker', threads=False)
        
        # Helper function to extract commodity data
        def extract_commodity_data(ticker_symbol, name_key):
            """Extract price and change data for a commodity"""
            try:
                ticker_data = data[ticker_symbol] if len(tickers_list) > 1 else data
                if ticker_data.empty or len(ticker_data) < 2:
                    return {f'{name_key}': '--', f'{name_key}_change': 0, 
                            f'{name_key}_arrow': '', f'{name_key}_color': '#ffffff', 
                            f'{name_key}_week_change': 0}
                
                current = float(ticker_data['Close'].iloc[-1])
                previous = float(ticker_data['Close'].iloc[-2])
                change_pct = ((current - previous) / previous) * 100
                arrow = 'Up' if change_pct >= 0 else 'Down'
                color = '#00FFA3' if change_pct >= 0 else '#FF6B6B'
                
                week_change = 0
                if len(ticker_data) >= 7:
                    week_ago = float(ticker_data['Close'].iloc[-6])
                    week_change = ((current - week_ago) / week_ago) * 100
                
                return {
                    'current': current,
                    f'{name_key}_change': change_pct,
                    f'{name_key}_arrow': arrow,
                    f'{name_key}_color': color,
                    f'{name_key}_week_change': week_change
                }
            except Exception as e:
                print(f"Error extracting {name_key}: {e}")
                return {f'{name_key}': '--', f'{name_key}_change': 0, 
                        f'{name_key}_arrow': '', f'{name_key}_color': '#ffffff', 
                        f'{name_key}_week_change': 0}
        
        # Get USD/INR rate (needed for gold/silver INR conversion)
        inr_data = extract_commodity_data('INR=X', 'usd_inr')
        usd_inr_rate = inr_data.get('current', 84.0)  # Updated default for 2025
        prices['usd_inr'] = f"₹{usd_inr_rate:.2f}"
        prices['usd_inr_change'] = inr_data['usd_inr_change'] if 'current' in inr_data else 0
        prices['usd_inr_week_change'] = inr_data.get('usd_inr_week_change', 0)
        
        # Oil
        oil_data = extract_commodity_data(COMMODITIES['oil'], 'oil')
        if 'current' in oil_data:
            prices['oil'] = f"${oil_data['current']:.2f}"
            prices.update({k: v for k, v in oil_data.items() if k != 'current'})
        else:
            prices.update(oil_data)
        
        # Gold
        gold_data = extract_commodity_data(COMMODITIES['gold'], 'gold')
        if 'current' in gold_data:
            gold_per_gram_usd = gold_data['current'] / 31.1035
            gold_per_10g_inr = gold_per_gram_usd * 10 * usd_inr_rate
            prices['gold'] = f"${gold_data['current']:.2f}"
            prices['gold_inr'] = f"₹{gold_per_10g_inr:,.0f}/10g"
            prices.update({k: v for k, v in gold_data.items() if k != 'current'})
        else:
            prices.update(gold_data)
            prices['gold_inr'] = "--"
        
        # Silver
        silver_data = extract_commodity_data(COMMODITIES['silver'], 'silver')
        if 'current' in silver_data:
            silver_per_gram_usd = silver_data['current'] / 31.1035
            silver_per_kg_inr = silver_per_gram_usd * 1000 * usd_inr_rate
            prices['silver'] = f"${silver_data['current']:.2f}"
            prices['silver_inr'] = f"₹{silver_per_kg_inr:,.0f}/kg"
            prices.update({k: v for k, v in silver_data.items() if k != 'current'})
        else:
            prices.update(silver_data)
            prices['silver_inr'] = "--"
        
        # Bitcoin
        btc_data = extract_commodity_data(COMMODITIES['btc'], 'btc')
        if 'current' in btc_data:
            prices['btc'] = f"${btc_data['current']:,.0f}"
            prices.update({k: v for k, v in btc_data.items() if k != 'current'})
        else:
            prices.update(btc_data)
        
        # Ethereum
        eth_data = extract_commodity_data(COMMODITIES['ethereum'], 'ethereum')
        if 'current' in eth_data:
            prices['ethereum'] = f"${eth_data['current']:,.2f}"
            prices.update({k: v for k, v in eth_data.items() if k != 'current'})
        else:
            prices.update(eth_data)
        
    except Exception as e:
        print(f"Bulk commodity fetch failed: {e}")
        # Return empty defaults for all commodities
        for key in ['oil', 'gold', 'silver', 'btc', 'ethereum']:
            prices[key] = "--"
            prices[f'{key}_change'] = 0
            prices[f'{key}_arrow'] = ''
            prices[f'{key}_color'] = '#ffffff'
            prices[f'{key}_week_change'] = 0
        prices['gold_inr'] = "--"
        prices['silver_inr'] = "--"
        prices['usd_inr'] = "--"
        prices['usd_inr_change'] = 0
        prices['usd_inr_week_change'] = 0
    
    return prices


def fetch_stocks_bulk(tickers, max_workers=4, use_cache=True, status_placeholder=None):
    """Fetch stocks in bulk with optimized caching and thread management"""
    if use_cache:
        cached_data, missing_tickers = load_bulk_cache(tickers)
        if cached_data and status_placeholder:
            status_placeholder.info(f"Loaded {len(cached_data)} stocks from cache, fetching {len(missing_tickers)} fresh...")
    else:
        cached_data = []
        missing_tickers = tickers
   
    if missing_tickers:
        fresh_data = []
        progress_bar = st.progress(0)
       
        # CRITICAL FIX: Limit workers to 3 max to avoid Yahoo Finance rate limiting/bans
        # Yahoo aggressively blocks Indian IPs making >50 requests/minute
        safe_workers = min(max_workers, 3, len(missing_tickers))
       
        with ThreadPoolExecutor(max_workers=safe_workers) as executor:
            # CRITICAL FIX: Use use_cache=True to leverage file-based caching
            # Previous use_cache=False defeated the whole caching mechanism
            future_to_ticker = {
                executor.submit(get_stock_performance, ticker, use_cache=True): ticker
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
       
        if use_cache and fresh_data:
            save_bulk_cache(fresh_data)
       
        return cached_data + fresh_data
   
    return cached_data


@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_list(category_name):
    available_indices = get_available_nse_indices()
   
    if category_name in available_indices:
        api_index_name = available_indices[category_name]
        try:
            yahoo_stocks = fetch_nse_index_constituents(api_index_name)
            if yahoo_stocks and len(yahoo_stocks) >= 5:
                return yahoo_stocks, f"Fetched {len(yahoo_stocks)} stocks from {category_name}"
        except Exception as e:
            print(f"Error fetching {category_name} dynamically: {str(e)}")
       
        fallback_map = {
            'Nifty 50': FALLBACK_NIFTY_50,
            'Nifty Next 50': FALLBACK_NIFTY_NEXT_50,
            'BSE Sensex': FALLBACK_BSE_SENSEX,
            'Nifty IT': [
                'TCS.NS', 'INFY.NS', 'WIPRO.NS', 'HCLTECH.NS', 'TECHM.NS',
                'LTIM.NS', 'MPHASIS.NS', 'PERSISTENT.NS', 'COFORGE.NS', 'LTI.NS'
            ],
            'Nifty Pharma': [
                'SUNPHARMA.NS', 'DRREDDY.NS', 'CIPLA.NS', 'DIVISLAB.NS', 'TORNTPHARMA.NS',
                'LUPIN.NS', 'AUROPHARMA.NS', 'ALKEM.NS', 'GLAND.NS', 'BIOCON.NS'
            ],
            'Nifty Metal': [
                'TATASTEEL.NS', 'JSWSTEEL.NS', 'HINDALCO.NS', 'VEDL.NS', 'JINDALSTEL.NS',
                'NMDC.NS', 'HINDZINC.NS', 'COALINDIA.NS', 'NATCOPHARM.NS', 'RATNAMANI.NS'
            ],
            'Nifty Realty': [
                'DLF.NS', 'PRESTIGE.NS', 'SOBHA.NS', 'GODREJPROP.NS', 'OBEROIRLTY.NS',
                'BRIGADE.NS', 'MAHLIFE.NS', 'PHOENIXLTD.NS', 'SUNTECK.NS', 'MAHINDALIFE.NS'
            ]
        }
       
        if category_name in fallback_map:
            fallback_stocks = fallback_map[category_name]
            print(f"Warning: Using fallback data for {category_name}")
            return fallback_stocks, f"Using fallback data for {category_name} (NSE may be down)"
       
        return [], f"No data available for {category_name}"
   
    return [], "Invalid category"


def validate_stock_symbol(symbol):
    """Validate stock symbol using fast_info for speed"""
    try:
        ticker = yf.Ticker(symbol)
        fast_info = getattr(ticker, 'fast_info', None)
        if fast_info:
            # If fast_info exists and has basic attributes, symbol is valid
            return hasattr(fast_info, 'last_price') or hasattr(fast_info, 'currency')
        # Fallback to quick history check
        hist = ticker.history(period='1d')
        return not hist.empty
    except:
        return False


@st.cache_data(ttl=86400, show_spinner=False)
def get_next_nse_holiday():
    fallback_holidays = [
        "05-Nov-2025",
        "25-Dec-2025",
    ]
   
    try:
        url = "https://www.nseindia.com/api/holiday-master?type=trading"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/regulations/holiday-master'
        }
       
        with requests.Session() as session:
            session.headers.update(headers)
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)
           
            response = session.get(url, timeout=10)
           
            if response.status_code == 200:
                data = response.json()
                today = datetime.now().date()
               
                if 'CM' in data:
                    for holiday in data['CM']:
                        holiday_date_str = holiday.get('tradingDate', '')
                        if holiday_date_str:
                            try:
                                holiday_date = datetime.strptime(holiday_date_str, "%d-%b-%Y").date()
                                if holiday_date > today:
                                    return holiday_date.strftime("%d-%b-%Y")
                            except:
                                continue
    except Exception as e:
        print(f"Error fetching NSE holidays from API: {e}")
   
    try:
        today = datetime.now().date()
        for holiday_str in fallback_holidays:
            holiday_date = datetime.strptime(holiday_str, "%d-%b-%Y").date()
            if holiday_date > today:
                return holiday_str
    except Exception as e:
        print(f"Error parsing fallback holidays: {e}")
   
@st.cache_data(ttl=60, show_spinner=False)
def get_fii_dii_data():
    json_file = os.path.join(os.path.dirname(__file__), "fii_dii_data.json")

    # 1. Try cached JSON (valid for today/yesterday and has real data)
    try:
        if os.path.exists(json_file):
            with open(json_file, "r") as f:
                data = json.load(f)

            file_date = data.get("date", "")
            today = datetime.utcnow().strftime("%d-%b-%Y")
            yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%d-%b-%Y")

            # Check if cache has meaningful data (not all zeros)
            fii_net = data.get("fii", {}).get("net", 0)
            dii_net = data.get("dii", {}).get("net", 0)
            has_real_data = (fii_net != 0 or dii_net != 0)

            if (
                data.get("status") == "success"
                and (data.get("fii") or data.get("dii"))
                and file_date in [today, yesterday]
                and has_real_data
            ):
                data.setdefault("source", "JSON Cache")
                print(f"FII/DII: Using cached data from {file_date}")
                return data
            elif not has_real_data:
                print(f"FII/DII: Cached data has all zeros, fetching fresh data...")
    except Exception as e:
        print(f"FII/DII JSON read error: {e}")

    # 2. Live NSE API fetch
    try:
        url = "https://www.nseindia.com/api/fiidiiTradeReact"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.nseindia.com",
        }

        with requests.Session() as session:
            session.headers.update(headers)
            # First request to set cookies
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(2)

            response = session.get(url, timeout=10)
            response.raise_for_status()
            live_data = response.json()

        # fiidiiTradeReact returns array of objects with category, buyValue, sellValue, netValue
        print(f"FII/DII API Response type: {type(live_data)}")
        
        data_array = live_data if isinstance(live_data, list) else []
        if not data_array:
            print(f"FII/DII: Empty or invalid API response")
            raise ValueError("Empty API response")
            
        print(f"FII/DII: Found {len(data_array)} records")

        def _clean_value(val):
            try:
                return float(str(val).replace(",", ""))
            except:
                return 0.0

        fii_data = None
        dii_data = None
        report_date = None
        
        for item in data_array:
            if not isinstance(item, dict):
                continue
                
            category = str(item.get("category", "")).upper()
            if item.get("date"):
                report_date = item["date"]
            
            if "FII" in category or "FPI" in category:
                fii_data = {
                    "buy": _clean_value(item.get("buyValue", 0)),
                    "sell": _clean_value(item.get("sellValue", 0)),
                    "net": _clean_value(item.get("netValue", 0)),
                }
            elif "DII" in category:
                dii_data = {
                    "buy": _clean_value(item.get("buyValue", 0)),
                    "sell": _clean_value(item.get("sellValue", 0)),
                    "net": _clean_value(item.get("netValue", 0)),
                }
        
        if not fii_data and not dii_data:
            print(f"FII/DII: No FII or DII data found in response")
            raise ValueError("No FII/DII data in response")

        print(f"FII/DII parsed: FII net={fii_data['net'] if fii_data else 0}, DII net={dii_data['net'] if dii_data else 0}")

        final_output = {
            "status": "success",
            "date": report_date or datetime.utcnow().strftime("%d-%b-%Y"),
            "fii": fii_data or {"buy": 0, "sell": 0, "net": 0},
            "dii": dii_data or {"buy": 0, "sell": 0, "net": 0},
            "source": "NSE Live API",
        }

        # Save to JSON cache
        try:
            with open(json_file, "w") as f:
                json.dump(final_output, f, indent=4)
            print(f"FII/DII: Saved fresh data to cache")
        except Exception as e:
            print(f"FII/DII JSON write error: {e}")

        return final_output

    except Exception as e:
        print(f"FII/DII Live API fetch failed: {e}")
        import traceback
        traceback.print_exc()

    # 3. If everything fails → return safe fallback
    return {
        "status": "error",
        "date": datetime.utcnow().strftime("%d-%b-%Y"),
        "fii": {"buy": 0, "sell": 0, "net": 0},
        "dii": {"buy": 0, "sell": 0, "net": 0},
        "source": "Fallback",
    }



@st.cache_data(ttl=120, show_spinner=False)  # 2-min cache for intraday volume updates
def get_highest_volume_stocks(stock_list, top_n=5):
    """Fetch highest volume stocks using bulk download for speed"""
    if not stock_list:
        return []
   
    try:
        normalized = [normalize_symbol(s) for s in stock_list]
        unique_symbols = list(dict.fromkeys(normalized))
       
        # Batch download in chunks
        chunk_size = 20
        all_results = []
       
        for i in range(0, len(unique_symbols), chunk_size):
            chunk = unique_symbols[i:i + chunk_size]
           
            data = yf.download(
                tickers=chunk,
                period='2d',
                interval='1d',
                group_by='ticker',
                progress=False,
                auto_adjust=True,
                actions=False,
                threads=True
            )
           
            if data.empty:
                continue
           
            is_multi = isinstance(data.columns, pd.MultiIndex)
           
            for ticker in chunk:
                try:
                    if is_multi and len(chunk) > 1:
                        vol_series = data[(ticker, 'Volume')].dropna()
                        close_series = data[(ticker, 'Close')].dropna()
                    else:
                        vol_series = data['Volume'].dropna() if 'Volume' in data.columns else pd.Series()
                        close_series = data['Close'].dropna() if 'Close' in data.columns else pd.Series()
                   
                    if vol_series.empty or close_series.empty:
                        continue
                   
                    volume = float(vol_series.iloc[-1])
                    if volume <= 0:
                        continue
                   
                    current_price = float(close_series.iloc[-1])
                    prev_price = float(close_series.iloc[-2]) if len(close_series) > 1 else current_price
                    change_pct = ((current_price - prev_price) / prev_price) * 100 if prev_price else 0.0
                   
                    all_results.append({
                        'symbol': ticker.replace('.NS', '').replace('.BO', ''),
                        'price': current_price,
                        'change_pct': change_pct,
                        'volume': volume
                    })
                except Exception as e:
                    print(f"Volume parse failed for {ticker}: {e}")
                    continue
       
        if not all_results:
            return []
       
        all_results.sort(key=lambda x: x['volume'], reverse=True)
        return all_results[:top_n]
       
    except Exception as e:
        print(f"Error fetching highest volume stocks: {e}")
        return []
