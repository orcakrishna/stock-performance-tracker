"""
Enhanced Data Fetchers with Configurable Fallback Support
Example implementation showing how to use the fallback system
"""

import yfinance as yf
import requests
import time
from typing import Optional, Dict, Any
from fallback_fetcher import FallbackFetcher, MultiSourceDataManager
from bs4 import BeautifulSoup


# ============================================
# STOCK PRICE FETCHERS (Multiple Sources)
# ============================================

def fetch_stock_price_yfinance(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch stock price from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='4mo')
        
        if hist.empty:
            return None
        
        current_price = hist['Close'].iloc[-1]
        
        # Calculate performance metrics
        price_1m = hist['Close'].iloc[-30] if len(hist) >= 30 else hist['Close'].iloc[0]
        change_1m = ((current_price - price_1m) / price_1m) * 100
        
        return {
            'symbol': symbol,
            'price': current_price,
            'change_1m': round(change_1m, 2),
            'source': 'yfinance'
        }
    except Exception as e:
        print(f"yfinance error for {symbol}: {e}")
        return None


def fetch_stock_price_nse_api(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch stock price from NSE API"""
    try:
        # Remove .NS suffix for NSE API
        nse_symbol = symbol.replace('.NS', '')
        
        fetcher = FallbackFetcher('stock_prices')
        session = fetcher.get_session('nse_api')
        
        if not session:
            return None
        
        url = f"https://www.nseindia.com/api/quote-equity?symbol={nse_symbol}"
        response = session.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            price_info = data.get('priceInfo', {})
            
            current_price = price_info.get('lastPrice')
            change_pct = price_info.get('pChange')
            
            if current_price:
                return {
                    'symbol': symbol,
                    'price': current_price,
                    'change_1m': change_pct or 0,
                    'source': 'nse_api'
                }
        
        return None
    except Exception as e:
        print(f"NSE API error for {symbol}: {e}")
        return None


def fetch_stock_price_bse_api(symbol: str) -> Optional[Dict[str, Any]]:
    """Fetch stock price from BSE API (placeholder - implement as needed)"""
    # This is a placeholder - BSE API implementation would go here
    return None


def get_stock_price_with_fallback(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get stock price using configured fallback sources
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS')
        
    Returns:
        Stock price data from first successful source
    """
    fetcher_functions = {
        'yfinance': fetch_stock_price_yfinance,
        'nse_api': fetch_stock_price_nse_api,
        'bse_api': fetch_stock_price_bse_api
    }
    
    return MultiSourceDataManager.fetch_with_fallback(
        'stock_prices',
        fetcher_functions,
        symbol
    )


# ============================================
# MARKET INDICES FETCHERS (Multiple Sources)
# ============================================

def fetch_index_yfinance(symbol: str) -> Optional[Dict[str, float]]:
    """Fetch index from Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='2d')
        
        if len(hist) < 2:
            return None
        
        current_price = hist['Close'].iloc[-1]
        prev_price = hist['Close'].iloc[-2]
        change = ((current_price - prev_price) / prev_price) * 100
        
        return {
            'price': current_price,
            'change': change,
            'source': 'yfinance'
        }
    except:
        return None


def fetch_index_nse_api(symbol: str) -> Optional[Dict[str, float]]:
    """Fetch index from NSE API"""
    try:
        fetcher = FallbackFetcher('market_indices')
        session = fetcher.get_session('nse_api')
        
        if not session:
            return None
        
        # Map Yahoo symbols to NSE index names
        nse_map = {
            '^NSEI': 'NIFTY 50',
            '^NSEBANK': 'NIFTY BANK'
        }
        
        nse_index = nse_map.get(symbol)
        if not nse_index:
            return None
        
        url = f"https://www.nseindia.com/api/allIndices"
        response = session.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            for index in data.get('data', []):
                if index.get('index') == nse_index:
                    return {
                        'price': index.get('last'),
                        'change': index.get('percentChange'),
                        'source': 'nse_api'
                    }
        
        return None
    except Exception as e:
        print(f"NSE API index error: {e}")
        return None


def get_index_with_fallback(symbol: str) -> Optional[Dict[str, float]]:
    """
    Get market index using configured fallback sources
    
    Args:
        symbol: Index symbol (e.g., '^NSEI')
        
    Returns:
        Index data from first successful source
    """
    fetcher_functions = {
        'yfinance': fetch_index_yfinance,
        'nse_api': fetch_index_nse_api
    }
    
    return MultiSourceDataManager.fetch_with_fallback(
        'market_indices',
        fetcher_functions,
        symbol
    )


# ============================================
# USAGE EXAMPLES
# ============================================

def example_usage():
    """Example of how to use the fallback system"""
    
    print("=" * 60)
    print("FALLBACK FETCHER EXAMPLES")
    print("=" * 60)
    
    # Example 1: Fetch stock price with fallback
    print("\n1. Fetching RELIANCE.NS with fallback:")
    stock_data = get_stock_price_with_fallback('RELIANCE.NS')
    if stock_data:
        print(f"   ✅ Success from {stock_data['source']}")
        print(f"   Price: ₹{stock_data['price']:.2f}")
        print(f"   1M Change: {stock_data['change_1m']:.2f}%")
    else:
        print("   ❌ All sources failed")
    
    # Example 2: Fetch index with fallback
    print("\n2. Fetching Nifty 50 with fallback:")
    index_data = get_index_with_fallback('^NSEI')
    if index_data:
        print(f"   ✅ Success from {index_data['source']}")
        print(f"   Price: {index_data['price']:.2f}")
        print(f"   Change: {index_data['change']:.2f}%")
    else:
        print("   ❌ All sources failed")
    
    # Example 3: Check enabled sources
    print("\n3. Enabled sources for stock_prices:")
    sources = MultiSourceDataManager.get_enabled_sources('stock_prices')
    for i, source in enumerate(sources, 1):
        print(f"   {i}. {source}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    example_usage()
