"""
Rate Service for Lynx Crypto Converter
Fetches live rates from CoinGecko API with fallback mechanism
"""

import requests
import json
import os
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Dict, Optional
from logger import converter_logger


class RateService:
    """Manages cryptocurrency exchange rates with API and fallback"""
    
    def __init__(self, fallback_file="data/fallback_rates.json", cache_ttl_minutes=15):
        self.api_url = "https://api.coingecko.com/api/v3/simple/price"
        self.fallback_file = fallback_file
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.last_fetch = None
        self.cached_rates = None
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.fallback_file), exist_ok=True)
    
    def get_rates(self) -> Dict[str, Decimal]:
        """
        Get current exchange rates for supported cryptocurrencies
        
        Returns:
            Dict mapping currency codes to USD rates
        """
        # Check if cached rates are still valid
        if self._is_cache_valid():
            converter_logger.debug("Using cached rates")
            return self.cached_rates
        
        # Try to fetch from API
        try:
            rates = self._fetch_from_api()
            if rates:
                self.cached_rates = rates
                self.last_fetch = datetime.now()
                self._save_fallback_rates(rates)
                converter_logger.info("Successfully fetched rates from CoinGecko API")
                return rates
        except Exception as e:
            converter_logger.api_failure(str(e))
        
        # Fallback to cached rates
        fallback_rates = self._load_fallback_rates()
        if fallback_rates:
            converter_logger.fallback_rates_used()
            return fallback_rates
        
        # Last resort - hardcoded rates (should rarely happen)
        converter_logger.error("No rates available - using emergency fallback")
        return self._get_emergency_rates()
    
    def _fetch_from_api(self) -> Optional[Dict[str, Decimal]]:
        """Fetch rates from CoinGecko API"""
        params = {
            'ids': 'bitcoin,ethereum,tether,solana',
            'vs_currencies': 'usd'
        }
        
        response = requests.get(self.api_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Map API response to our format
        rate_mapping = {
            'bitcoin': 'BTC',
            'ethereum': 'ETH', 
            'tether': 'USDT',
            'solana': 'SOL'
        }
        
        rates = {}
        for api_name, currency_code in rate_mapping.items():
            if api_name in data and 'usd' in data[api_name]:
                rates[currency_code] = Decimal(str(data[api_name]['usd']))
        
        return rates if len(rates) == 4 else None
    
    def _is_cache_valid(self) -> bool:
        """Check if cached rates are still valid"""
        if not self.cached_rates or not self.last_fetch:
            return False
        
        return datetime.now() - self.last_fetch < self.cache_ttl
    
    def _save_fallback_rates(self, rates: Dict[str, Decimal]) -> None:
        """Save rates to fallback file"""
        try:
            fallback_data = {
                'timestamp': datetime.now().isoformat(),
                'rates': {k: str(v) for k, v in rates.items()}
            }
            
            with open(self.fallback_file, 'w') as f:
                json.dump(fallback_data, f, indent=2)
            
            converter_logger.debug(f"Saved fallback rates to {self.fallback_file}")
        except Exception as e:
            converter_logger.error(f"Failed to save fallback rates: {e}")
    
    def _load_fallback_rates(self) -> Optional[Dict[str, Decimal]]:
        """Load rates from fallback file"""
        try:
            if not os.path.exists(self.fallback_file):
                return None
            
            with open(self.fallback_file, 'r') as f:
                data = json.load(f)
            
            rates = {}
            for currency, rate_str in data['rates'].items():
                rates[currency] = Decimal(rate_str)
            
            converter_logger.debug(f"Loaded fallback rates from {self.fallback_file}")
            return rates
        
        except Exception as e:
            converter_logger.error(f"Failed to load fallback rates: {e}")
            return None
    
    def _get_emergency_rates(self) -> Dict[str, Decimal]:
        """Emergency hardcoded rates (last resort)"""
        return {
            'BTC': Decimal('45000.00'),
            'ETH': Decimal('2800.00'),
            'USDT': Decimal('1.00'),
            'SOL': Decimal('180.00')
        }
    
    def get_rate_for_currency(self, currency: str) -> Optional[Decimal]:
        """Get rate for specific currency"""
        rates = self.get_rates()
        return rates.get(currency.upper())
    
    def force_refresh(self) -> Dict[str, Decimal]:
        """Force refresh rates from API"""
        self.cached_rates = None
        self.last_fetch = None
        return self.get_rates()


# Global rate service instance
rate_service = RateService()