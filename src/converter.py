"""
Lynx Crypto Converter - Main Conversion Engine
Handles cryptocurrency conversion with wallet integration
"""

from typing import Dict, List, Optional
from parser import BalanceParser
from rate_service import rate_service
from wallet_service import wallet_service
from logger import converter_logger


class CryptoConverter:
    """Main cryptocurrency converter class"""
    
    def __init__(self):
        self.parser = BalanceParser()
        
    def convert_balances(self, file_path: str, target_currency: str = 'USD') -> Dict:
        """
        Convert cryptocurrency balances from file
        
        Args:
            file_path: Path to balance file
            target_currency: Currency to convert to (default: USD)
            
        Returns:
            Dict with conversion results and wallet info
        """
        try:
            # Parse balances from file
            balances = self.parser.parse_file(file_path)
            if not balances:
                return {'error': 'No valid balances found in file'}
            
            converter_logger.info(f"Parsed {len(balances)} balances from {file_path}")
            
            # Get current rates
            currencies = list(balances.keys())
            rates = rate_service.get_rates(currencies, target_currency)
            
            if not rates:
                return {'error': 'Failed to fetch exchange rates'}
            
            # Perform conversions
            conversions = {}
            total_value = 0
            
            for currency, amount in balances.items():
                if currency in rates:
                    converted_amount = amount * rates[currency]
                    conversions[currency] = converted_amount
                    total_value += converted_amount
                    converter_logger.info(f"Converted {amount} {currency} to {converted_amount:.2f} {target_currency}")
                else:
                    converter_logger.warning(f"No rate available for {currency}")
            
            # Associate with wallets
            wallet_info = wallet_service.associate_amounts_with_wallets(conversions)
            
            return {
                'success': True,
                'original_balances': balances,
                'rates': rates,
                'conversions': conversions,
                'wallet_info': wallet_info,
                'total_value': total_value,
                'target_currency': target_currency,
                'timestamp': rate_service.last_update
            }
            
        except Exception as e:
            converter_logger.error(f"Conversion failed: {e}")
            return {'error': f'Conversion failed: {str(e)}'}
    
    def convert_single_amount(self, amount: float, from_currency: str, to_currency: str = 'USD') -> Dict:
        """
        Convert a single amount between currencies
        
        Args:
            amount: Amount to convert
            from_currency: Source currency
            to_currency: Target currency
            
        Returns:
            Dict with conversion result
        """
        try:
            rates = rate_service.get_rates([from_currency], to_currency)
            
            if from_currency not in rates:
                return {'error': f'Rate not available for {from_currency}'}
            
            converted_amount = amount * rates[from_currency]
            
            return {
                'success': True,
                'original_amount': amount,
                'original_currency': from_currency,
                'converted_amount': converted_amount,
                'target_currency': to_currency,
                'rate': rates[from_currency],
                'timestamp': rate_service.last_update
            }
            
        except Exception as e:
            converter_logger.error(f"Single conversion failed: {e}")
            return {'error': f'Conversion failed: {str(e)}'}
    
    def get_portfolio_summary(self, file_path: str) -> Dict:
        """
        Get portfolio summary with wallet validation
        
        Args:
            file_path: Path to balance file
            
        Returns:
            Dict with portfolio summary
        """
        result = self.convert_balances(file_path)
        
        if not result.get('success'):
            return result
        
        # Add wallet validation summary
        wallet_summary = {
            'total_wallets': len(result['wallet_info']),
            'valid_wallets': sum(1 for w in result['wallet_info'].values() if w['valid']),
            'invalid_wallets': sum(1 for w in result['wallet_info'].values() if not w['valid']),
            'missing_wallets': sum(1 for w in result['wallet_info'].values() if w['address'] is None)
        }
        
        result['wallet_summary'] = wallet_summary
        return result


# Global converter instance
crypto_converter = CryptoConverter()