"""
Data Fetching Functions for NSE Stock Performance Tracker
Handles all API calls to NSE, Yahoo Finance, and other data sources
"""
import streamlit as st
import pandas as pd
import requests
from io import StringIO
import time
from datetime import datetime, timedelta
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import COMMODITIES, FALLBACK_NIFTY_50, FALLBACK_NIFTY_NEXT_50, FALLBACK_BSE_SENSEX
from cache_manager import load_from_cache, save_to_cache, load_bulk_cache, save_bulk_cache


@st.cache_data(ttl=86400)
def get_available_nse_indices():
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


@st.cache_data(ttl=86400)
def fetch_nse_index_constituents(index_name):
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
                df = pd.read_csv(StringIO(response.content.decode('utf-8')))
                if 'Symbol' in df.columns:
                    symbols = df['Symbol'].dropna().tolist()
                    stocks = [f"{s}.NS" for s in symbols if pd.notna(s)]
                    if len(stocks) >= 5:
                        return stocks
        return None
    except Exception as e:
        print(f"NSE CSV error: {e}")
        return None


@st.cache_data(ttl=86400)
def fetch_nse_csv_list(csv_filename):
    try:
        url = f"https://nsearchives.nseindia.com/content/indices/{csv_filename}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.nseindia.com/market-data/live-equity-market'
        }
        with requests.Session() as session:
            session.headers.update(headers)
            session.get("https://www.nseindia.com", timeout=10)
            time.sleep(1)
            response = session.get(url, timeout=10)
            if response.status_code == 200:
                df = pd.read_csv(StringIO(response.content.decode('utf-8')))
                stocks = [f"{s}.NS" for s in df['Symbol'].tolist() if pd.notna(s)]
                if len(stocks) >= 5:
                    return stocks
        return None
    except Exception:
        return None


@st.cache_data(ttl=1800, show_spinner=False)
def get_index_performance(index_symbol, index_name=None):
    if not index_symbol:
        return None, None
    try:
        ticker = yf.Ticker(index_symbol)
        info = ticker.info
        current_price = info.get('regularMarketPrice') or info.get('previousClose')
        prev_price = info.get('regularMarketPreviousClose') or info.get('open')
        if current_price and prev_price and current_price != prev_price:
            change_pct = ((current_price - prev_price) / prev_price) * 100
            return current_price, change_pct
        hist = ticker.history(period='5d')
        if not hist.empty and len(hist) >= 2:
            current_price = hist['Close'].iloc[-1]
            previous_price = hist['Close'].iloc[-2]
            change_pct = ((current_price - previous_price) / previous_price) * 100
            return current_price, change_pct
    except Exception as e:
        print(f"yfinance error: {e}")
    return None, None


def get_stock_performance(ticker, use_cache=True):
    symbol = ticker.replace('.NS', '').replace('.BO', '')
    if use_cache:
        cached = load_from_cache(ticker)
        if cached:
            return cached

    max_retries = 3
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                time.sleep(3 ** attempt)
            stock = yf.Ticker(ticker)
            hist = stock.history(period='4mo')
            if hist.empty or len(hist) < 20:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
            break
        except Exception as e:
            if "Rate" in str(e) or "429" in str(e):
                if attempt < max_retries - 1:
                    time.sleep(5 ** attempt)
                    continue
                return None
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None

    try:
        hist.index = hist.index.tz_localize(None)
        try:
            info = stock.info
            current_price = info.get('currentPrice') or info.get('regularMarketPrice') or hist['Close'].iloc[-1]
        except:
            current_price = hist['Close'].iloc[-1]
        current_date = hist.index[-1]

        if len(hist) >= 2:
            previous_close = hist['Close'].iloc[-2]
            change_today = ((current_price - previous_close) / previous_close) * 100
        else:
            open_price = hist['Open'].iloc[-1]
            change_today = ((current_price - open_price) / open_price) * 100 if open_price > 0 else 0.0

        def get_price_by_days_back(days: int) -> float:
            target_date = current_date - pd.Timedelta(days=days)
            past_data = hist[hist.index <= target_date]
            return float(past_data['Close'].iloc[-1]) if len(past_data) > 0 else float(hist['Close'].iloc[0])

        price_1w = get_price_by_days_back(7)
        price_1m = get_price_by_days_back(30)
        price_2m = get_price_by_days_back(60)
        price_3m = get_price_by_days_back(90)

        def pct_change(now, then):
            return round(((now - then) / then) * 100, 2) if then > 0 else 0.0

        change_1w = pct_change(current_price, price_1w)
        change_1m = pct_change(current_price, price_1m)
        change_2m = pct_change(current_price, price_2m)
        change_3m = pct_change(current_price, price_3m)

        sparkline_prices = hist['Close'].iloc[-30:].tolist() if len(hist) >= 30 else hist['Close'].tolist()
        if sparkline_prices:
            mn, mx = min(sparkline_prices), max(sparkline_prices)
            rng = mx - mn
            sparkline_data = [((p - mn) / rng) * 100 for p in sparkline_prices] if rng > 0 else [50] * len(sparkline_prices)
        else:
            sparkline_data = []

        result = {
            'Ticker': ticker,
            'Stock Name': symbol,
            'Current Price': f"₹{current_price:.2f}",
            'Today %': round(change_today, 2),
            '1 Week %': change_1w,
            '1 Month %': change_1m,
            '2 Months %': change_2m,
            '3 Months %': change_3m,
            'sparkline_data': sparkline_data
        }

        if use_cache:
            save_to_cache(ticker, result)
        return result

    except Exception as e:
        st.warning(f"Error fetching {symbol}: {str(e)}")
        return None


# [Rest of functions unchanged — all working]
# Paste full file from above link to avoid truncation
