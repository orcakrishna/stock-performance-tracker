"""
Cache Manager for Stock Performance Data
Implements persistent caching to avoid repeated API calls
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

CACHE_DIR = "cache"
CACHE_EXPIRY_HOURS = 6  # Cache expires after 6 hours


def ensure_cache_dir():
    """Create cache directory if it doesn't exist"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def get_cache_filename(ticker):
    """Get cache filename for a ticker"""
    ensure_cache_dir()
    safe_ticker = ticker.replace('.', '_')
    return os.path.join(CACHE_DIR, f"{safe_ticker}.json")


def is_cache_valid(cache_file):
    """Check if cache file exists and is not expired"""
    if not os.path.exists(cache_file):
        return False
    
    # Check file modification time
    mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
    expiry_time = datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS)
    
    return mod_time > expiry_time


def save_to_cache(ticker, data):
    """Save stock data to cache"""
    cache_file = get_cache_filename(ticker)
    
    cache_data = {
        'ticker': ticker,
        'timestamp': datetime.now().isoformat(),
        'data': data
    }
    
    with open(cache_file, 'w') as f:
        json.dump(cache_data, f)


def load_from_cache(ticker):
    """Load stock data from cache if valid"""
    cache_file = get_cache_filename(ticker)
    
    if not is_cache_valid(cache_file):
        return None
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        return cache_data['data']
    except Exception as e:
        print(f"Error loading cache for {ticker}: {e}")
        return None


def clear_cache():
    """Clear all cached data"""
    if os.path.exists(CACHE_DIR):
        for file in os.listdir(CACHE_DIR):
            if file.endswith('.json'):
                os.remove(os.path.join(CACHE_DIR, file))


def get_cache_stats():
    """Get cache statistics"""
    if not os.path.exists(CACHE_DIR):
        return {'total': 0, 'valid': 0, 'expired': 0}
    
    total = 0
    valid = 0
    expired = 0
    
    for file in os.listdir(CACHE_DIR):
        if file.endswith('.json'):
            total += 1
            cache_file = os.path.join(CACHE_DIR, file)
            if is_cache_valid(cache_file):
                valid += 1
            else:
                expired += 1
    
    return {'total': total, 'valid': valid, 'expired': expired}


def save_bulk_cache(stocks_data):
    """Save multiple stocks data to cache at once"""
    for data in stocks_data:
        if data and 'Stock Name' in data:
            # Reconstruct ticker from stock name
            ticker = f"{data['Stock Name']}.NS"
            save_to_cache(ticker, data)


def load_bulk_cache(tickers):
    """Load multiple stocks from cache"""
    cached_data = []
    missing_tickers = []
    
    for ticker in tickers:
        data = load_from_cache(ticker)
        if data:
            cached_data.append(data)
        else:
            missing_tickers.append(ticker)
    
    return cached_data, missing_tickers
