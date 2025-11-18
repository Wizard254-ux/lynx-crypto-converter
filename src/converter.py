"""
Lynx Crypto Converter - Main Conversion Engine
Handles cryptocurrency conversion with wallet integration
"""

from typing import Dict, List, Optional
from datetime import datetime
from parser import BalanceParser
from rate_service import rate_service
from wallet_service import wallet_service
from conversion_storage import conversion_storage
from logger import converter_logger


class CryptoConverter:
    """Main cryptocurrency converter class"""

    def __init__(self):
        pass

    def convert_balances(self, file_path: str, target_currency: str = 'USD', send_to_wallet: bool = False) -> Dict:
        """
        Convert USD balances from file to cryptocurrencies

        Args:
            file_path: Path to balance file
            target_currency: Target currency (default: USD, used as source)
            send_to_wallet: Whether to send converted amounts to wallet

        Returns:
            Dict with conversion results and wallet info
        """
        try:
            # Parse balances from file
            parser = BalanceParser(file_path)
            balance_list = parser.parse()

            if not balance_list:
                return {'error': 'No valid balances found in file'}

            converter_logger.info(f"Parsed {len(balance_list)} balances from {file_path}")

            # Calculate total USD amount from parsed balances
            total_usd = sum(item['value'] for item in balance_list)
            converter_logger.info(f"Total USD amount: ${total_usd:,.2f}")

            # Get current crypto rates (USD to crypto)
            rates = rate_service.get_rates()

            if not rates:
                return {'error': 'Failed to fetch exchange rates'}

            # Convert USD to each cryptocurrency
            conversions = {}

            for currency, usd_rate in rates.items():
                # Calculate how much crypto we can buy with total USD
                # Rate is in USD per 1 crypto, so we divide
                crypto_amount = total_usd / float(usd_rate)
                conversions[currency] = crypto_amount
                converter_logger.info(f"Converted ${total_usd:,.2f} USD to {crypto_amount:.8f} {currency}")

            # Associate with wallets
            wallet_info = wallet_service.associate_amounts_with_wallets(conversions)

            # Send to wallet if requested
            wallet_transactions = []
            if send_to_wallet:
                for currency, amount in conversions.items():
                    transaction = wallet_service.send_to_wallet(currency, amount)
                    wallet_transactions.append(transaction)

            # Prepare rates for output (convert Decimal to float)
            rates_output = {k: float(v) for k, v in rates.items()}

            result = {
                'success': True,
                'source_file': file_path,
                'parsed_balances': balance_list,
                'total_usd_amount': total_usd,
                'rates': rates_output,
                'conversions': conversions,
                'wallet_info': wallet_info,
                'timestamp': datetime.now().isoformat()
            }

            if send_to_wallet:
                result['wallet_transactions'] = wallet_transactions

            # Save conversion for later use
            conversion_id = conversion_storage.save_conversion(result)
            result['conversion_id'] = conversion_id

            return result

        except Exception as e:
            converter_logger.error(f"Conversion failed: {e}")
            return {'error': f'Conversion failed: {str(e)}'}
    
    def convert_single_amount(self, amount: float, from_currency: str, to_currency: str = 'BTC') -> Dict:
        """
        Convert a single USD amount to cryptocurrency

        Args:
            amount: Amount in USD to convert
            from_currency: Source currency (should be USD)
            to_currency: Target cryptocurrency (BTC, ETH, USDT, SOL)

        Returns:
            Dict with conversion result
        """
        try:
            # Get all crypto rates
            rates = rate_service.get_rates()

            if not rates:
                return {'error': 'Failed to fetch exchange rates'}

            # Handle USD to crypto conversion
            if from_currency.upper() == 'USD':
                if to_currency.upper() not in rates:
                    return {'error': f'Rate not available for {to_currency}'}

                usd_rate = float(rates[to_currency.upper()])
                converted_amount = amount / usd_rate

                return {
                    'success': True,
                    'original_amount': amount,
                    'original_currency': from_currency.upper(),
                    'converted_amount': converted_amount,
                    'target_currency': to_currency.upper(),
                    'rate': usd_rate,
                    'calculation': f'{amount} USD / {usd_rate} USD per {to_currency} = {converted_amount:.8f} {to_currency}',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'error': 'Only USD to crypto conversion supported. Use from_currency="USD"'}

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
    
    def send_converted_amounts_to_wallet(self, file_path: str, wallet_id: str = None) -> Dict:
        """
        Convert balances and send to client's wallet
        
        Args:
            file_path: Path to balance file
            wallet_id: Wallet ID (defaults to client address)
            
        Returns:
            Dict with conversion and transaction results
        """
        # First convert the balances
        result = self.convert_balances(file_path)
        
        if not result.get('success'):
            return result
        
        # Send each converted amount to wallet
        wallet_transactions = []
        for currency, amount in result['conversions'].items():
            transaction = wallet_service.send_to_wallet(currency, amount, wallet_id)
            wallet_transactions.append(transaction)
        
        result['wallet_transactions'] = wallet_transactions
        result['sent_to_wallet'] = True
        
        converter_logger.info(f"Sent {len(wallet_transactions)} converted amounts to wallet")
        return result
    
    def send_saved_conversion(self, conversion_id: str, wallet_id: str = None) -> Dict:
        """
        Send a previously saved conversion to wallet
        
        Args:
            conversion_id: ID of saved conversion
            wallet_id: Wallet ID (defaults to client address)
            
        Returns:
            Dict with transaction results
        """
        try:
            # Get saved conversion
            conversion = conversion_storage.get_conversion(conversion_id)
            
            if not conversion:
                return {'error': f'Conversion {conversion_id} not found'}
            
            if conversion.get('sent', False):
                return {'error': f'Conversion {conversion_id} already sent'}
            
            # Send each converted amount to wallet
            wallet_transactions = []
            for currency, amount in conversion['conversions'].items():
                transaction = wallet_service.send_to_wallet(currency, amount, wallet_id)
                wallet_transactions.append(transaction)
            
            # Mark as sent
            conversion_storage.mark_as_sent(conversion_id)
            
            result = {
                'success': True,
                'conversion_id': conversion_id,
                'conversions': conversion['conversions'],
                'wallet_transactions': wallet_transactions,
                'sent_to_wallet': True,
                'original_file': conversion.get('source_file', 'unknown'),
                'total_usd_amount': conversion.get('total_usd_amount', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            converter_logger.info(f"Sent saved conversion {conversion_id} to wallet")
            return result
            
        except Exception as e:
            converter_logger.error(f"Failed to send saved conversion: {e}")
            return {'error': f'Send failed: {str(e)}'}
    
    def list_saved_conversions(self, include_sent: bool = True) -> Dict:
        """
        List all saved conversions
        
        Args:
            include_sent: Whether to include already sent conversions
            
        Returns:
            Dict with conversion list
        """
        try:
            conversions = conversion_storage.list_conversions(include_sent)
            
            return {
                'success': True,
                'conversions': conversions,
                'total_count': len(conversions),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            converter_logger.error(f"Failed to list conversions: {e}")
            return {'error': f'List failed: {str(e)}'}


# Global converter instance
crypto_converter = CryptoConverter()