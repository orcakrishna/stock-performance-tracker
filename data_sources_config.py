"""
Configurable Data Sources for NSE Stock Tracker
Define all data sources and their fallback order here
"""

# Data source configurations
DATA_SOURCES = {
    'stock_prices': {
        'enabled': True,
        'sources': [
            {
                'name': 'yfinance',
                'priority': 1,
                'timeout': 10,
                'retry_count': 2
            },
            {
                'name': 'nse_api',
                'priority': 2,
                'timeout': 15,
                'retry_count': 1
            },
            {
                'name': 'bse_api',
                'priority': 3,
                'timeout': 15,
                'retry_count': 1
            }
        ]
    },
    
    'market_indices': {
        'enabled': True,
        'sources': [
            {
                'name': 'yfinance',
                'priority': 1,
                'timeout': 10,
                'retry_count': 2
            },
            {
                'name': 'nse_api',
                'priority': 2,
                'timeout': 15,
                'retry_count': 1
            }
        ]
    },
    
    'fii_dii_data': {
        'enabled': True,
        'sources': [
            {
                'name': 'nse_api',
                'priority': 1,
                'timeout': 15,
                'retry_count': 2
            },
            {
                'name': 'nse_website',
                'priority': 2,
                'timeout': 15,
                'retry_count': 1
            },
            {
                'name': 'moneycontrol',
                'priority': 3,
                'timeout': 10,
                'retry_count': 1
            }
        ]
    },
    
    'stock_lists': {
        'enabled': True,
        'sources': [
            {
                'name': 'nse_csv',
                'priority': 1,
                'timeout': 15,
                'retry_count': 2
            },
            {
                'name': 'nse_api',
                'priority': 2,
                'timeout': 15,
                'retry_count': 1
            }
        ]
    },
    
    'commodities': {
        'enabled': True,
        'sources': [
            {
                'name': 'yfinance',
                'priority': 1,
                'timeout': 10,
                'retry_count': 2
            },
            {
                'name': 'investing_com',
                'priority': 2,
                'timeout': 15,
                'retry_count': 1
            }
        ]
    }
}

# Source-specific configurations
SOURCE_CONFIGS = {
    'yfinance': {
        'base_url': None,  # Library-based, no URL
        'requires_session': False,
        'requires_cookies': False
    },
    
    'nse_api': {
        'base_url': 'https://www.nseindia.com/api',
        'requires_session': True,
        'requires_cookies': True,
        'cookie_url': 'https://www.nseindia.com',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br'
        }
    },
    
    'nse_csv': {
        'base_url': 'https://nsearchives.nseindia.com/content/indices',
        'requires_session': True,
        'requires_cookies': True,
        'cookie_url': 'https://www.nseindia.com',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/csv',
            'Referer': 'https://www.nseindia.com/'
        }
    },
    
    'nse_website': {
        'base_url': 'https://www.nseindia.com',
        'requires_session': True,
        'requires_cookies': True,
        'cookie_url': 'https://www.nseindia.com',
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        }
    },
    
    'bse_api': {
        'base_url': 'https://api.bseindia.com',
        'requires_session': False,
        'requires_cookies': False,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    },
    
    'moneycontrol': {
        'base_url': 'https://www.moneycontrol.com',
        'requires_session': False,
        'requires_cookies': False,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    },
    
    'investing_com': {
        'base_url': 'https://www.investing.com',
        'requires_session': False,
        'requires_cookies': False,
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    }
}

# Cache settings per data type
CACHE_SETTINGS = {
    'stock_prices': {
        'ttl': 21600,  # 6 hours
        'enabled': True
    },
    'market_indices': {
        'ttl': 300,  # 5 minutes
        'enabled': True
    },
    'fii_dii_data': {
        'ttl': 3600,  # 1 hour
        'enabled': True
    },
    'stock_lists': {
        'ttl': 86400,  # 24 hours
        'enabled': True
    },
    'commodities': {
        'ttl': 300,  # 5 minutes
        'enabled': True
    }
}

# Logging settings
LOGGING_CONFIG = {
    'log_source_attempts': True,
    'log_fallback_usage': True,
    'log_failures': True,
    'verbose': False  # Set to True for detailed debugging
}
