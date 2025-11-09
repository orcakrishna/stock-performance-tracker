"""
Smart caching utilities for stock data based on market status
Implements intelligent cache TTL based on weekends, holidays, and market hours
"""

import pytz
from datetime import datetime, timedelta


def _is_market_open():
    """Check if market is currently open (weekday + trading hours)"""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(pytz.utc).astimezone(ist)
    
    # Check if weekend
    weekday = current_time.weekday()
    if weekday >= 5:  # Saturday or Sunday
        return False
    
    current_hour = current_time.hour
    current_minute = current_time.minute
    current_time_mins = current_hour * 60 + current_minute
    
    # Market timings (IST): 9:15 AM to 3:30 PM
    market_open = 9 * 60 + 15
    market_close = 15 * 60 + 30
    
    return market_open <= current_time_mins < market_close


def _is_nse_holiday():
    """
    Check if today is an NSE holiday
    Returns True if it's a known holiday
    """
    ist = pytz.timezone('Asia/Kolkata')
    current_date = datetime.now(pytz.utc).astimezone(ist).date()
    
    # NSE 2025 holidays - update annually
    nse_holidays_2025 = [
        datetime(2025, 1, 26).date(),  # Republic Day
        datetime(2025, 3, 14).date(),  # Mahashivratri
        datetime(2025, 3, 31).date(),  # Holi
        datetime(2025, 4, 10).date(),  # Mahavir Jayanti
        datetime(2025, 4, 14).date(),  # Dr. Ambedkar Jayanti
        datetime(2025, 4, 18).date(),  # Good Friday
        datetime(2025, 5, 1).date(),   # Maharashtra Day
        datetime(2025, 8, 15).date(),  # Independence Day
        datetime(2025, 8, 27).date(),  # Ganesh Chaturthi
        datetime(2025, 10, 2).date(),  # Gandhi Jayanti
        datetime(2025, 10, 21).date(), # Dussehra
        datetime(2025, 11, 5).date(),  # Diwali
        datetime(2025, 11, 6).date(),  # Diwali (Balipratipada)
        datetime(2025, 11, 24).date(), # Guru Nanak Jayanti
        datetime(2025, 12, 25).date(), # Christmas
    ]
    
    return current_date in nse_holidays_2025


def get_smart_cache_ttl():
    """
    Returns intelligent cache TTL (in seconds) based on market status:
    - Market open (weekday, trading hours): 5 minutes (300 sec) - for fresh data
    - Market closed (weekday, after hours): 1 hour (3600 sec) - data won't change
    - Weekend: 24 hours (86400 sec) - data frozen until Monday
    - Holiday: 24 hours (86400 sec) - data frozen until next trading day
    """
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(pytz.utc).astimezone(ist)
    weekday = current_time.weekday()
    
    # Weekend - cache for 24 hours
    if weekday >= 5:
        return 86400
    
    # Holiday - cache for 24 hours
    if _is_nse_holiday():
        return 86400
    
    # Weekday - check if market is open
    if _is_market_open():
        # Market open - cache for 5 minutes
        return 300
    else:
        # Market closed (before/after hours) - cache for 1 hour
        return 3600


def should_refresh_cache(cache_timestamp):
    """
    Determines if cached data should be refreshed based on smart TTL
    
    Args:
        cache_timestamp: datetime when data was cached
        
    Returns:
        bool: True if cache should be refreshed, False if cache is still valid
    """
    if cache_timestamp is None:
        return True
    
    current_time = datetime.now(pytz.utc)
    ttl_seconds = get_smart_cache_ttl()
    
    # Cache is valid if it's within the TTL window
    cache_age = (current_time - cache_timestamp).total_seconds()
    return cache_age > ttl_seconds


def get_cache_info_message():
    """
    Returns a user-friendly message about current cache strategy
    """
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(pytz.utc).astimezone(ist)
    weekday = current_time.weekday()
    
    if weekday >= 5:
        return "📅 Weekend detected - Using 24-hour cache (market closed)"
    elif _is_nse_holiday():
        return "🏖️ Holiday detected - Using 24-hour cache (market closed)"
    elif _is_market_open():
        return "📈 Market open - Data refreshes every 5 minutes"
    else:
        return "🌙 After hours - Data refreshes every hour"
