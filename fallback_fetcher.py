"""
Generic Fallback Data Fetcher
Handles multi-source data fetching with automatic fallback
"""

import time
import requests
from typing import Any, Dict, List, Optional, Callable
from data_sources_config import DATA_SOURCES, SOURCE_CONFIGS, LOGGING_CONFIG


class FallbackFetcher:
    """
    Generic fallback fetcher that tries multiple data sources
    in priority order until one succeeds
    """
    
    def __init__(self, data_type: str):
        """
        Initialize fetcher for a specific data type
        
        Args:
            data_type: Type of data to fetch (e.g., 'stock_prices', 'fii_dii_data')
        """
        self.data_type = data_type
        self.config = DATA_SOURCES.get(data_type, {})
        self.sources = sorted(
            self.config.get('sources', []),
            key=lambda x: x['priority']
        )
        self.verbose = LOGGING_CONFIG.get('verbose', False)
    
    def fetch(self, fetcher_functions: Dict[str, Callable], *args, **kwargs) -> Optional[Any]:
        """
        Try fetching data from sources in priority order
        
        Args:
            fetcher_functions: Dict mapping source names to their fetcher functions
            *args, **kwargs: Arguments to pass to fetcher functions
            
        Returns:
            Data from first successful source, or None if all fail
        """
        if not self.config.get('enabled', True):
            self._log(f"Data type '{self.data_type}' is disabled in config")
            return None
        
        for source in self.sources:
            source_name = source['name']
            
            if source_name not in fetcher_functions:
                self._log(f"No fetcher function provided for source: {source_name}")
                continue
            
            fetcher_func = fetcher_functions[source_name]
            
            # Try fetching with retries
            for attempt in range(source.get('retry_count', 1)):
                try:
                    if LOGGING_CONFIG.get('log_source_attempts', True):
                        self._log(f"Trying {source_name} (attempt {attempt + 1}/{source['retry_count']})")
                    
                    # Call the fetcher function
                    result = fetcher_func(*args, **kwargs)
                    
                    if result is not None:
                        if LOGGING_CONFIG.get('log_fallback_usage', True):
                            self._log(f"✅ Success: {source_name} for {self.data_type}")
                        return result
                    
                except Exception as e:
                    if LOGGING_CONFIG.get('log_failures', True):
                        self._log(f"❌ {source_name} failed: {str(e)}")
                    
                    # Wait before retry
                    if attempt < source.get('retry_count', 1) - 1:
                        time.sleep(1)
        
        # All sources failed
        self._log(f"⚠️ All sources failed for {self.data_type}")
        return None
    
    def get_session(self, source_name: str) -> Optional[requests.Session]:
        """
        Create a session with proper headers and cookies for a source
        
        Args:
            source_name: Name of the data source
            
        Returns:
            Configured session or None
        """
        source_config = SOURCE_CONFIGS.get(source_name, {})
        
        if not source_config.get('requires_session', False):
            return None
        
        session = requests.Session()
        
        # Set headers
        headers = source_config.get('headers', {})
        session.headers.update(headers)
        
        # Set cookies if required
        if source_config.get('requires_cookies', False):
            cookie_url = source_config.get('cookie_url')
            if cookie_url:
                try:
                    session.get(cookie_url, timeout=10)
                    time.sleep(1)  # Wait for cookies to set
                except Exception as e:
                    self._log(f"Failed to set cookies for {source_name}: {e}")
        
        return session
    
    def _log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose or LOGGING_CONFIG.get('log_failures', True):
            print(f"[FallbackFetcher] {message}")


class MultiSourceDataManager:
    """
    Manager class to handle all data fetching with fallback support
    """
    
    @staticmethod
    def fetch_with_fallback(
        data_type: str,
        fetcher_functions: Dict[str, Callable],
        *args,
        **kwargs
    ) -> Optional[Any]:
        """
        Convenience method to fetch data with fallback
        
        Args:
            data_type: Type of data to fetch
            fetcher_functions: Dict of source_name -> fetcher_function
            *args, **kwargs: Arguments for fetcher functions
            
        Returns:
            Data from first successful source
        """
        fetcher = FallbackFetcher(data_type)
        return fetcher.fetch(fetcher_functions, *args, **kwargs)
    
    @staticmethod
    def get_enabled_sources(data_type: str) -> List[str]:
        """
        Get list of enabled sources for a data type
        
        Args:
            data_type: Type of data
            
        Returns:
            List of source names in priority order
        """
        config = DATA_SOURCES.get(data_type, {})
        if not config.get('enabled', True):
            return []
        
        sources = sorted(
            config.get('sources', []),
            key=lambda x: x['priority']
        )
        return [s['name'] for s in sources]
    
    @staticmethod
    def is_source_enabled(data_type: str, source_name: str) -> bool:
        """
        Check if a specific source is enabled for a data type
        
        Args:
            data_type: Type of data
            source_name: Name of the source
            
        Returns:
            True if source is enabled
        """
        enabled_sources = MultiSourceDataManager.get_enabled_sources(data_type)
        return source_name in enabled_sources
