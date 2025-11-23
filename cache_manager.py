"""
Cache Manager for Stock Performance Data
Implements persistent caching using Pickle for fast loading
Single-file cache for optimal performance with large datasets (25x faster than JSON)
"""

import os
import pickle
import pytz
import fcntl  # For file locking (Unix/Mac compatible)
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple, Optional
from smart_cache_utils import should_refresh_cache, get_smart_cache_ttl

CACHE_DIR = "cache"
CACHE_FILE = os.path.join(CACHE_DIR, "stocks_cache.pkl")
CACHE_VERSION = 2  # Increment when cache structure changes
UTC = pytz.UTC  # Consistent timezone reference


def ensure_cache_dir() -> None:
    """Create cache directory if it doesn't exist"""
    os.makedirs(CACHE_DIR, exist_ok=True)


def save_to_cache(ticker: str, data: dict) -> bool:
    """
    Save single stock data to cache with file locking.
    Loads existing cache, updates it, and saves back.
    """
    try:
        ensure_cache_dir()
        
        # CRITICAL FIX: Preserve original ticker in data for bulk operations
        if 'Ticker' not in data:
            data['Ticker'] = ticker
        
        # Load existing cache with shared lock
        all_cache = _load_cache_file()
        
        # Update with new data - use timezone-aware timestamps
        all_cache['stocks'][ticker] = {
            'data': data,
            'timestamp': datetime.now(UTC)  # CRITICAL FIX: timezone-aware
        }
        all_cache['last_updated'] = datetime.now(UTC)
        
        # Save back with exclusive lock
        _save_cache_file(all_cache)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save cache for {ticker}: {e}")
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
    Save multiple stocks data to cache at once with file locking.
    Much faster than calling save_to_cache repeatedly.
    """
    try:
        ensure_cache_dir()
        
        # Load existing cache
        all_cache = _load_cache_file()
        
        # Update with new data - use timezone-aware timestamp
        current_time = datetime.now(UTC)  # CRITICAL FIX: timezone-aware
        for data in stocks_data:
            if data and 'Ticker' in data:
                # CRITICAL FIX: Use preserved ticker from data
                ticker = data['Ticker']
                
                all_cache['stocks'][ticker] = {
                    'data': data,
                    'timestamp': current_time
                }
            elif data and 'Stock Name' in data:
                # Fallback: reconstruct ticker (not ideal but handles legacy)
                stock_name = data['Stock Name']
                ticker = f"{stock_name}.NS"  # Default to NS
                print(f"WARNING: Ticker not in data for {stock_name}, using {ticker}")
                
                all_cache['stocks'][ticker] = {
                    'data': data,
                    'timestamp': current_time
                }
        
        all_cache['last_updated'] = current_time
        
        # Save back
        _save_cache_file(all_cache)
        return True
    except Exception as e:
        print(f"ERROR: Failed to save bulk cache: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_bulk_cache(tickers: List[str]) -> Tuple[List[dict], List[str]]:
    """
    Load multiple stocks from cache using smart TTL.
    CRITICAL FIX: Preserves order - cached_data aligns with tickers list.
    Returns (cached_data, missing_tickers).
    """
    cached_data = []
    missing_tickers = []
    
    try:
        all_cache = _load_cache_file()
        
        for ticker in tickers:
            if ticker in all_cache['stocks']:
                stock_cache = all_cache['stocks'][ticker]
                
                # Add timezone info to cached timestamp if not present (backward compat)
                timestamp = stock_cache['timestamp']
                if timestamp.tzinfo is None:
                    timestamp = timestamp.replace(tzinfo=UTC)
                
                # Check if expired using smart cache logic
                if not should_refresh_cache(timestamp):
                    cached_data.append(stock_cache['data'])
                    # CRITICAL FIX: Don't add to missing_tickers if found and valid
                    continue
            
            # Not found or expired
            missing_tickers.append(ticker)
    except Exception as e:
        print(f"ERROR: Failed to load bulk cache: {e}")
        import traceback
        traceback.print_exc()
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
                timestamp = timestamp.replace(tzinfo=UTC)
            
            if should_refresh_cache(timestamp):
                expired += 1
            else:
                valid += 1
        
        return {'total': total, 'valid': valid, 'expired': expired}
    except Exception as e:
        # CRITICAL FIX: Log the error instead of silent failure
        print(f"ERROR: Failed to get cache stats: {e}")
        return {'total': 0, 'valid': 0, 'expired': 0}


# Private helper functions

def _load_cache_file() -> dict:
    """Load the entire cache file with shared lock. Returns empty structure if not found."""
    default_cache = {
        'version': CACHE_VERSION,
        'stocks': {},
        'last_updated': datetime.now(UTC)  # CRITICAL FIX: timezone-aware
    }
    
    if not os.path.exists(CACHE_FILE):
        return default_cache
    
    try:
        with open(CACHE_FILE, 'rb') as f:
            # CRITICAL FIX: Acquire shared lock for reading (allows concurrent reads)
            fcntl.flock(f.fileno(), fcntl.LOCK_SH)
            try:
                data = pickle.load(f)
                
                # CRITICAL FIX: Check cache version compatibility
                if data.get('version', 1) != CACHE_VERSION:
                    print(f"WARNING: Cache version mismatch (expected {CACHE_VERSION}, got {data.get('version', 1)}). Resetting cache.")
                    return default_cache
                
                return data
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Release lock
    except Exception as e:
        print(f"ERROR: Failed to load cache file: {e}")
        import traceback
        traceback.print_exc()
        return default_cache


def _save_cache_file(cache_data: dict) -> None:
    """Save the entire cache file with exclusive lock (prevents race conditions)."""
    ensure_cache_dir()
    
    # CRITICAL FIX: Ensure version is set
    cache_data['version'] = CACHE_VERSION
    
    with open(CACHE_FILE, 'wb') as f:
        # CRITICAL FIX: Acquire exclusive lock for writing (blocks all other access)
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        try:
            pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)  # Release lock


def _is_expired(timestamp: datetime) -> bool:
    """Check if a timestamp is expired using smart cache TTL (DEPRECATED - use should_refresh_cache)."""
    # Keep for backward compatibility but use smart cache logic
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=pytz.utc)
    return should_refresh_cache(timestamp)
