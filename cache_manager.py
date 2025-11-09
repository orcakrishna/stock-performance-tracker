"""
Cache Manager for Stock Performance Data
Implements persistent caching using Pickle for fast loading
Single-file cache for optimal performance with large datasets (25x faster than JSON)
"""

import os
import pickle
import pytz
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from smart_cache_utils import should_refresh_cache, get_smart_cache_ttl

CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "stocks_cache.pkl")


def ensure_cache_dir() -> None:
    """Create cache directory if it doesn't exist"""
    os.makedirs(CACHE_DIR, exist_ok=True)


def save_to_cache(ticker: str, data: dict) -> bool:
    """
    Save single stock data to cache.
    Loads existing cache, updates it, and saves back.
    """
    try:
        ensure_cache_dir()
        
        # Load existing cache
        all_cache = _load_cache_file()
        
        # Update with new data
        all_cache['stocks'][ticker] = {
            'data': data,
            'timestamp': datetime.now()
        }
        all_cache['last_updated'] = datetime.now()
        
        # Save back
        _save_cache_file(all_cache)
        return True
    except Exception as e:
        print(f"Error saving cache for {ticker}: {e}")
        return False


def load_from_cache(ticker: str) -> Optional[dict]:
    """
    Load single stock data from cache if valid using smart TTL.
    Returns None if not found or expired based on market status.
    """
    try:
        all_cache = _load_cache_file()
        
        if ticker not in all_cache['stocks']:
            return None
        
        stock_cache = all_cache['stocks'][ticker]
        
        # Add timezone info to cached timestamp if not present
        timestamp = stock_cache['timestamp']
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=pytz.utc)
        
        # Check if expired using smart cache logic
        if should_refresh_cache(timestamp):
            return None
        
        return stock_cache['data']
    except Exception as e:
        print(f"Error loading cache for {ticker}: {e}")
        return None


def save_bulk_cache(stocks_data: List[dict]) -> bool:
    """
    Save multiple stocks data to cache at once.
    Much faster than calling save_to_cache repeatedly.
    """
    try:
        ensure_cache_dir()
        
        # Load existing cache
        all_cache = _load_cache_file()
        
        # Update with new data
        current_time = datetime.now()
        for data in stocks_data:
            if data and 'Stock Name' in data:
                # Try to reconstruct ticker (handle both .NS and .BO)
                stock_name = data['Stock Name']
                # Check if original ticker info is preserved
                ticker = f"{stock_name}.NS"  # Default to NS
                
                all_cache['stocks'][ticker] = {
                    'data': data,
                    'timestamp': current_time
                }
        
        all_cache['last_updated'] = current_time
        
        # Save back
        _save_cache_file(all_cache)
        return True
    except Exception as e:
        print(f"Error saving bulk cache: {e}")
        return False


def load_bulk_cache(tickers: List[str]) -> Tuple[List[dict], List[str]]:
    """
    Load multiple stocks from cache using smart TTL.
    Returns (cached_data, missing_tickers).
    """
    cached_data = []
    missing_tickers = []
    
    try:
        all_cache = _load_cache_file()
        
        for ticker in tickers:
            if ticker in all_cache['stocks']:
                stock_cache = all_cache['stocks'][ticker]
                
                # Add timezone info to cached timestamp if not present
                timestamp = stock_cache['timestamp']
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=pytz.utc)
                
                # Check if expired using smart cache logic
                if not should_refresh_cache(timestamp):
                    cached_data.append(stock_cache['data'])
                else:
                    missing_tickers.append(ticker)
            else:
                missing_tickers.append(ticker)
    except Exception as e:
        print(f"Error loading bulk cache: {e}")
        missing_tickers = tickers  # Treat all as missing on error
    
    return cached_data, missing_tickers


def clear_cache() -> bool:
    """Clear all cached data by removing the cache file"""
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        return True
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return False


def get_cache_stats() -> Dict[str, int]:
    """
    Get cache statistics using smart TTL.
    Returns dict with total, valid, and expired counts.
    """
    try:
        all_cache = _load_cache_file()
        
        total = len(all_cache['stocks'])
        valid = 0
        expired = 0
        
        for ticker, stock_cache in all_cache['stocks'].items():
            timestamp = stock_cache['timestamp']
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=pytz.utc)
            
            if should_refresh_cache(timestamp):
                expired += 1
            else:
                valid += 1
        
        return {'total': total, 'valid': valid, 'expired': expired}
    except:
        return {'total': 0, 'valid': 0, 'expired': 0}


# Private helper functions

def _load_cache_file() -> dict:
    """Load the entire cache file. Returns empty structure if not found."""
    if not os.path.exists(CACHE_FILE):
        return {
            'stocks': {},
            'last_updated': datetime.now()
        }
    
    try:
        with open(CACHE_FILE, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading cache file: {e}")
        return {
            'stocks': {},
            'last_updated': datetime.now()
        }


def _save_cache_file(cache_data: dict) -> None:
    """Save the entire cache file."""
    ensure_cache_dir()
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)


def _is_expired(timestamp: datetime) -> bool:
    """Check if a timestamp is expired using smart cache TTL (DEPRECATED - use should_refresh_cache)."""
    # Keep for backward compatibility but use smart cache logic
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=pytz.utc)
    return should_refresh_cache(timestamp)
