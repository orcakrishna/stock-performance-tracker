# Configurable Fallback Data Fetching System

## Overview

A flexible, non-hardcoded system for fetching data from multiple sources with automatic fallback. If one source fails, it automatically tries the next configured source.

## Architecture

```
┌─────────────────────────────────────────┐
│   data_sources_config.py                │
│   (Configuration - Edit this file)      │
│   - Define sources                      │
│   - Set priorities                      │
│   - Configure timeouts                  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   fallback_fetcher.py                   │
│   (Core Logic - Don't edit)             │
│   - Tries sources in order              │
│   - Handles retries                     │
│   - Manages sessions/cookies            │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│   data_fetchers_enhanced.py             │
│   (Implementation - Add new sources)    │
│   - Implement fetcher functions         │
│   - Use MultiSourceDataManager          │
└─────────────────────────────────────────┘
```

## How to Use

### 1. Configure Data Sources

Edit `data_sources_config.py` to add/remove/reorder sources:

```python
DATA_SOURCES = {
    'stock_prices': {
        'enabled': True,
        'sources': [
            {
                'name': 'yfinance',
                'priority': 1,      # Try this first
                'timeout': 10,
                'retry_count': 2
            },
            {
                'name': 'nse_api',
                'priority': 2,      # Try this second
                'timeout': 15,
                'retry_count': 1
            }
        ]
    }
}
```

### 2. Implement Fetcher Functions

In `data_fetchers_enhanced.py` or your own file:

```python
from fallback_fetcher import MultiSourceDataManager

def fetch_from_source_a(symbol):
    # Your implementation
    return data

def fetch_from_source_b(symbol):
    # Your implementation
    return data

# Use the fallback system
def get_data_with_fallback(symbol):
    fetcher_functions = {
        'source_a': fetch_from_source_a,
        'source_b': fetch_from_source_b
    }
    
    return MultiSourceDataManager.fetch_with_fallback(
        'stock_prices',  # Data type from config
        fetcher_functions,
        symbol
    )
```

### 3. Call Your Function

```python
result = get_data_with_fallback('RELIANCE.NS')
if result:
    print(f"Got data from: {result['source']}")
```

## Adding a New Data Source

### Step 1: Add to Configuration

```python
# In data_sources_config.py

# Add to DATA_SOURCES
'my_new_data_type': {
    'enabled': True,
    'sources': [
        {'name': 'source1', 'priority': 1, 'timeout': 10, 'retry_count': 2},
        {'name': 'source2', 'priority': 2, 'timeout': 15, 'retry_count': 1}
    ]
}

# Add source configuration
SOURCE_CONFIGS['source1'] = {
    'base_url': 'https://api.example.com',
    'requires_session': True,
    'requires_cookies': False,
    'headers': {
        'User-Agent': 'Mozilla/5.0...'
    }
}
```

### Step 2: Implement Fetcher Functions

```python
# In your data fetcher file

def fetch_from_source1(param):
    try:
        # Your implementation
        return {'data': 'value', 'source': 'source1'}
    except:
        return None

def fetch_from_source2(param):
    try:
        # Your implementation
        return {'data': 'value', 'source': 'source2'}
    except:
        return None
```

### Step 3: Create Wrapper Function

```python
def get_my_data_with_fallback(param):
    fetcher_functions = {
        'source1': fetch_from_source1,
        'source2': fetch_from_source2
    }
    
    return MultiSourceDataManager.fetch_with_fallback(
        'my_new_data_type',
        fetcher_functions,
        param
    )
```

## Configuration Options

### Data Source Options

| Option | Type | Description |
|--------|------|-------------|
| `name` | string | Unique identifier for the source |
| `priority` | int | Lower = higher priority (1 is tried first) |
| `timeout` | int | Request timeout in seconds |
| `retry_count` | int | Number of retry attempts |

### Source Config Options

| Option | Type | Description |
|--------|------|-------------|
| `base_url` | string | Base URL for API calls |
| `requires_session` | bool | Whether to use requests.Session |
| `requires_cookies` | bool | Whether to set cookies first |
| `cookie_url` | string | URL to visit for setting cookies |
| `headers` | dict | HTTP headers to use |

### Cache Settings

```python
CACHE_SETTINGS = {
    'stock_prices': {
        'ttl': 21600,  # 6 hours in seconds
        'enabled': True
    }
}
```

## Examples

### Example 1: Stock Prices with 3 Fallbacks

```python
# Config
'stock_prices': {
    'sources': [
        {'name': 'yfinance', 'priority': 1},
        {'name': 'nse_api', 'priority': 2},
        {'name': 'bse_api', 'priority': 3}
    ]
}

# Usage
data = get_stock_price_with_fallback('RELIANCE.NS')
# Tries: yfinance → nse_api → bse_api
```

### Example 2: Disable a Source Temporarily

```python
# In data_sources_config.py
'stock_prices': {
    'enabled': True,
    'sources': [
        {'name': 'yfinance', 'priority': 1},
        # {'name': 'nse_api', 'priority': 2},  # Commented out
        {'name': 'bse_api', 'priority': 3}
    ]
}
```

### Example 3: Change Priority Order

```python
# Make NSE API primary, yfinance backup
'stock_prices': {
    'sources': [
        {'name': 'nse_api', 'priority': 1},    # Now first
        {'name': 'yfinance', 'priority': 2},   # Now second
    ]
}
```

## Testing

Run the example:

```bash
python data_fetchers_enhanced.py
```

Output:
```
============================================================
FALLBACK FETCHER EXAMPLES
============================================================

1. Fetching RELIANCE.NS with fallback:
   [FallbackFetcher] Trying yfinance (attempt 1/2)
   ✅ Success from yfinance
   Price: ₹2,845.50
   1M Change: 5.23%

2. Fetching Nifty 50 with fallback:
   [FallbackFetcher] Trying yfinance (attempt 1/2)
   ✅ Success from yfinance
   Price: 24,180.80
   Change: 1.45%

3. Enabled sources for stock_prices:
   1. yfinance
   2. nse_api
   3. bse_api
============================================================
```

## Logging

Control logging in `data_sources_config.py`:

```python
LOGGING_CONFIG = {
    'log_source_attempts': True,   # Log each attempt
    'log_fallback_usage': True,    # Log which source succeeded
    'log_failures': True,          # Log failures
    'verbose': False               # Detailed debugging
}
```

## Benefits

✅ **No Hardcoding**: All sources configured in one file  
✅ **Easy to Add**: Just add config + implement function  
✅ **Easy to Remove**: Comment out or delete from config  
✅ **Flexible Priority**: Change order anytime  
✅ **Automatic Retry**: Built-in retry logic  
✅ **Session Management**: Handles cookies/headers automatically  
✅ **Logging**: Track which sources work/fail  

## Integration with Existing Code

To integrate with your current `data_fetchers.py`:

```python
# In data_fetchers.py
from fallback_fetcher import MultiSourceDataManager

# Replace this:
def get_stock_performance(ticker):
    return yfinance_fetch(ticker)

# With this:
def get_stock_performance(ticker):
    fetcher_functions = {
        'yfinance': yfinance_fetch,
        'nse_api': nse_api_fetch,
        'bse_api': bse_api_fetch
    }
    return MultiSourceDataManager.fetch_with_fallback(
        'stock_prices',
        fetcher_functions,
        ticker
    )
```

## Future Enhancements

- Add more sources (Google Finance alternatives, Bloomberg, etc.)
- Implement load balancing across sources
- Add health check monitoring
- Create admin UI for configuration
- Add source performance metrics
