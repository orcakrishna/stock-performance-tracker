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

from config import COMMODITIES, FALLBACK_NIFTY_50, FALLBACK_NIFTY_NEXT_50, FALLBACK_BSE_SENSEX
from cache_manager import load_from_cache, save_to_cache, load_bulk_cache, save_bulk_cache

DEFAULT_EXCHANGE_SUFFIX = '.NS'


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


def get_stock_performance(ticker, use_cache=True):
    """Fetch stock performance with low-latency Yahoo Finance access."""
    normalized_ticker = normalize_symbol(ticker)
    display_symbol = normalized_ticker.replace('.NS', '').replace('.BO', '')

    cache_key = normalized_ticker if ticker != normalized_ticker else ticker

    if use_cache:
        cached_data = load_from_cache(cache_key)
        if cached_data:
            return cached_data

    ticker_obj = yf.Ticker(normalized_ticker)
    fast_info = getattr(ticker_obj, 'fast_info', None)

    hist = get_cached_history(normalized_ticker, period='6mo', interval='1d')
    if hist is None or hist.empty:
        return None

    try:
        if hasattr(hist.index, 'tz') and hist.index.tz is not None:
            hist.index = hist.index.tz_localize(None)
    except Exception:
        pass

    current_price = fast_get(fast_info, 'last_price')
    previous_close = fast_get(fast_info, 'previous_close')

    hist_close_latest = float(hist['Close'].iloc[-1])
    if current_price is None:
        current_price = hist_close_latest
    current_price = float(current_price)

    if previous_close is None and len(hist) >= 2:
        previous_close = float(hist['Close'].iloc[-2])
    elif previous_close is not None:
        previous_close = float(previous_close)

    if previous_close:
        change_today = ((current_price - previous_close) / previous_close) * 100
    else:
        open_price = float(hist['Open'].iloc[-1]) if 'Open' in hist.columns else hist_close_latest
        change_today = ((current_price - open_price) / open_price) * 100 if open_price else 0.0

    current_date = hist.index[-1]

    def get_price_by_date(target_date):
        valid_hist = hist.loc[hist.index <= target_date]
        if not valid_hist.empty:
            return float(valid_hist['Close'].iloc[-1])
        return hist_close_latest

    price_1w = get_price_by_date(current_date - pd.Timedelta(days=7))
    change_1w = ((current_price - price_1w) / price_1w) * 100 if price_1w else 0.0

    price_1m = get_price_by_date(current_date - pd.DateOffset(months=1))
    change_1m = ((current_price - price_1m) / price_1m) * 100 if price_1m else 0.0

    price_2m = get_price_by_date(current_date - pd.DateOffset(months=2))
    change_2m = ((current_price - price_2m) / price_2m) * 100 if price_2m else 0.0

    price_3m = get_price_by_date(current_date - pd.DateOffset(months=3))
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


@st.cache_data(ttl=3600, show_spinner=False)
def get_stock_52_week_range(ticker):
    """Return current price and 52-week high/low details using fast_info and cached history"""
    try:
        normalized = normalize_symbol(ticker)
        stock = yf.Ticker(normalized)
        fast_info = getattr(stock, 'fast_info', None)
        
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
        
        # Fallback to history if fast_info incomplete
        hist = stock.history(period='1y', interval='1d', auto_adjust=True, actions=False)
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
    """Fetch current prices for oil, gold, silver, BTC, and USD/INR with change indicators"""
    prices = {}
    yahoo_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    def fetch_with_retry(ticker_symbol, max_retries=2):
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(ticker_symbol)
                hist = ticker.history(period='1mo')
                if hist is not None and not hist.empty:
                    return hist
                time.sleep(0.5)
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Failed to fetch {ticker_symbol} after {max_retries} attempts: {str(e)}")
                time.sleep(0.5)
        return None
    def fetch_quote_summary(symbol):
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?modules=price"
        try:
            response = requests.get(url, headers=yahoo_headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            result = data.get('quoteSummary', {}).get('result')
            if not result:
                return None, None
            price_data = result[0].get('price', {})
            current = price_data.get('regularMarketPrice', {}).get('raw')
            previous = price_data.get('regularMarketPreviousClose', {}).get('raw')
            return current, previous
        except Exception as e:
            print(f"Warning: Quote summary fallback failed for {symbol}: {e}")
            return None, None
    def fetch_chart_series(symbol, range_period="10d", interval="1d"):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_period}&interval={interval}"
        try:
            response = requests.get(url, headers=yahoo_headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            result = data.get('chart', {}).get('result')
            if not result:
                return None
            closes = result[0].get('indicators', {}).get('quote', [{}])[0].get('close', [])
            return [close for close in closes if close is not None]
        except Exception as e:
            print(f"Warning: Chart fallback failed for {symbol}: {e}")
            return None

    # Oil
    try:
        hist = fetch_with_retry(COMMODITIES['oil'])
        if hist is not None and len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            previous = hist['Close'].iloc[-2]
            change_pct = ((current - previous) / previous) * 100
            arrow = 'Up' if change_pct >= 0 else 'Down'
            color = '#00ff00' if change_pct >= 0 else '#ff4444'
            prices['oil'] = f"${current:.2f}"
            prices['oil_change'] = change_pct
            prices['oil_arrow'] = arrow
            prices['oil_color'] = color
            if len(hist) >= 7:
                week_ago = hist['Close'].iloc[-6]
                week_change_pct = ((current - week_ago) / week_ago) * 100
                prices['oil_week_change'] = week_change_pct
            else:
                prices['oil_week_change'] = 0
        elif hist is not None and not hist.empty:
            prices['oil'] = f"${hist['Close'].iloc[-1]:.2f}"
            prices['oil_change'] = 0
            prices['oil_arrow'] = ''
            prices['oil_color'] = '#ffffff'
            prices['oil_week_change'] = 0
        else:
            prices['oil'] = "--"
            prices['oil_change'] = 0
            prices['oil_arrow'] = ''
            prices['oil_color'] = '#ffffff'
            prices['oil_week_change'] = 0
    except Exception as e:
        print(f"Warning: Oil fetch error: {str(e)}")
        prices['oil'] = "--"
        prices['oil_change'] = 0
        prices['oil_arrow'] = ''
        prices['oil_color'] = '#ffffff'
        prices['oil_week_change'] = 0

    # Ethereum
    try:
        eth = yf.Ticker(COMMODITIES['ethereum'])
        hist = eth.history(period='1mo')
        if hist is not None and len(hist) >= 2:
            current = float(hist['Close'].iloc[-1])
            previous = float(hist['Close'].iloc[-2])
            change_pct = ((current - previous) / previous) * 100 if previous else 0
            arrow = 'Up' if change_pct >= 0 else 'Down'
            color = '#00ff00' if change_pct >= 0 else '#ff4444'
            week_change_pct = 0
            if len(hist) >= 7:
                week_baseline = float(hist['Close'].iloc[-6])
                if week_baseline:
                    week_change_pct = ((current - week_baseline) / week_baseline) * 100
            prices['ethereum'] = f"${current:,.2f}"
            prices['ethereum_change'] = change_pct
            prices['ethereum_arrow'] = arrow
            prices['ethereum_color'] = color
            prices['ethereum_week_change'] = week_change_pct
        elif hist is not None and not hist.empty:
            current = float(hist['Close'].iloc[-1])
            prices['ethereum'] = f"${current:,.2f}"
            prices['ethereum_change'] = 0
            prices['ethereum_arrow'] = ''
            prices['ethereum_color'] = '#ffffff'
            prices['ethereum_week_change'] = 0
        else:
            prices['ethereum'] = "--"
            prices['ethereum_change'] = 0
            prices['ethereum_arrow'] = ''
            prices['ethereum_color'] = '#ffffff'
            prices['ethereum_week_change'] = 0
    except Exception as e:
        print(f"Warning: Ethereum fetch error: {str(e)}")
        prices['ethereum'] = "--"
        prices['ethereum_change'] = 0
        prices['ethereum_arrow'] = ''
        prices['ethereum_color'] = '#ffffff'
        prices['ethereum_week_change'] = 0

    # Gold
    try:
        gold = yf.Ticker(COMMODITIES['gold'])
        hist = gold.history(period='1mo')
        usd_inr_rate = 83.5
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
            arrow = 'Up' if change_pct >= 0 else 'Down'
            color = '#00ff00' if change_pct >= 0 else '#ff4444'
            gold_per_gram_usd = current / 31.1035
            gold_per_10g_inr = gold_per_gram_usd * 10 * usd_inr_rate
            prices['gold'] = f"${current:.2f}"
            prices['gold_inr'] = f"₹{gold_per_10g_inr:,.0f}/10g"
            prices['gold_change'] = change_pct
            prices['gold_arrow'] = arrow
            prices['gold_color'] = color
            if len(hist) >= 7:
                week_ago = hist['Close'].iloc[-6]
                week_change_pct = ((current - week_ago) / week_ago) * 100
                prices['gold_week_change'] = week_change_pct
            else:
                prices['gold_week_change'] = 0
        else:
            current = hist['Close'].iloc[-1]
            gold_per_gram_usd = current / 31.1035
            gold_per_10g_inr = gold_per_gram_usd * 10 * usd_inr_rate
            prices['gold'] = f"${current:.2f}"
            prices['gold_inr'] = f"₹{gold_per_10g_inr:,.0f}/10g"
            prices['gold_change'] = 0
            prices['gold_arrow'] = ''
            prices['gold_color'] = '#ffffff'
            prices['gold_week_change'] = 0
    except:
        prices['gold'] = "--"
        prices['gold_inr'] = "--"
        prices['gold_change'] = 0
        prices['gold_arrow'] = ''
        prices['gold_color'] = '#ffffff'
        prices['gold_week_change'] = 0

    # Silver
    try:
        silver = yf.Ticker(COMMODITIES['silver'])
        hist = silver.history(period='1mo')
        usd_inr_rate = 83.5
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
            arrow = 'Up' if change_pct >= 0 else 'Down'
            color = '#00ff00' if change_pct >= 0 else '#ff4444'
            silver_per_gram_usd = current / 31.1035
            silver_per_kg_inr = silver_per_gram_usd * 1000 * usd_inr_rate
            prices['silver'] = f"${current:.2f}"
            prices['silver_inr'] = f"₹{silver_per_kg_inr:,.0f}/kg"
            prices['silver_change'] = change_pct
            prices['silver_arrow'] = arrow
            prices['silver_color'] = color
            if len(hist) >= 7:
                week_ago = hist['Close'].iloc[-6]
                week_change_pct = ((current - week_ago) / week_ago) * 100
                prices['silver_week_change'] = week_change_pct
            else:
                prices['silver_week_change'] = 0
        else:
            current = hist['Close'].iloc[-1]
            silver_per_gram_usd = current / 31.1035
            silver_per_kg_inr = silver_per_gram_usd * 1000 * usd_inr_rate
            prices['silver'] = f"${current:.2f}"
            prices['silver_inr'] = f"₹{silver_per_kg_inr:,.0f}/kg"
            prices['silver_change'] = 0
            prices['silver_arrow'] = ''
            prices['silver_color'] = '#ffffff'
            prices['silver_week_change'] = 0
    except:
        prices['silver'] = "--"
        prices['silver_inr'] = "--"
        prices['silver_change'] = 0
        prices['silver_arrow'] = ''
        prices['silver_color'] = '#ffffff'
        prices['silver_week_change'] = 0

    # Bitcoin
    try:
        btc = yf.Ticker(COMMODITIES['btc'])
        hist = btc.history(period='1mo')
        if len(hist) >= 2:
            current = hist['Close'].iloc[-1]
            previous = hist['Close'].iloc[-2]
            change_pct = ((current - previous) / previous) * 100
            arrow = 'Up' if change_pct >= 0 else 'Down'
            color = '#00ff00' if change_pct >= 0 else '#ff4444'
            prices['btc'] = f"${current:,.0f}"
            prices['btc_change'] = change_pct
            prices['btc_arrow'] = arrow
            prices['btc_color'] = color
            if len(hist) >= 7:
                week_ago = hist['Close'].iloc[-6]
                week_change_pct = ((current - week_ago) / week_ago) * 100
                prices['btc_week_change'] = week_change_pct
            else:
                prices['btc_week_change'] = 0
        else:
            prices['btc'] = f"${hist['Close'].iloc[-1]:,.0f}"
            prices['btc_change'] = 0
            prices['btc_arrow'] = ''
            prices['btc_color'] = '#ffffff'
            prices['btc_week_change'] = 0
    except:
        prices['btc'] = "--"
        prices['btc_change'] = 0
        prices['btc_arrow'] = ''
        prices['btc_color'] = '#ffffff'
        prices['btc_week_change'] = 0

    # USD/INR
    try:
        usd_inr = yf.Ticker('INR=X')
        hist = usd_inr.history(period='1mo')
        if len(hist) >= 2:
            current_rate = hist['Close'].iloc[-1]
            previous_rate = hist['Close'].iloc[-2]
            change = current_rate - previous_rate
            prices['usd_inr'] = f"₹{current_rate:.2f}"
            prices['usd_inr_change'] = change
            if len(hist) >= 7:
                week_ago = hist['Close'].iloc[-6]
                week_change_pct = ((current_rate - week_ago) / week_ago) * 100
                prices['usd_inr_week_change'] = week_change_pct
            else:
                prices['usd_inr_week_change'] = 0
        else:
            prices['usd_inr'] = f"₹{hist['Close'].iloc[-1]:.2f}"
            prices['usd_inr_change'] = 0
            prices['usd_inr_week_change'] = 0
    except:
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
       
        # Limit workers to avoid rate limiting
        safe_workers = min(max_workers, 4, len(missing_tickers))
       
        with ThreadPoolExecutor(max_workers=safe_workers) as executor:
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
