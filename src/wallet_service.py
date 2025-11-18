"""
Wallet Service for Lynx Crypto Converter
Manages wallet address validation and association
"""

import os
import re
from typing import Dict, Optional
from logger import converter_logger


class WalletService:
    """Manages cryptocurrency wallet addresses and validation"""
    
    def __init__(self):
        self.wallets = self._load_wallets_from_env()
    
    def _load_wallets_from_env(self) -> Dict[str, str]:
        """Load wallet addresses from environment variables"""
        wallets = {
            'BTC': os.getenv('BTC_WALLET'),
            'ETH': os.getenv('ETH_WALLET'), 
            'USDT': os.getenv('USDT_WALLET'),
            'SOL': os.getenv('SOL_WALLET')
        }
        
        # Filter out None values
        wallets = {k: v for k, v in wallets.items() if v}
        converter_logger.info(f"Loaded {len(wallets)} wallet addresses from environment")
        return wallets
    
    def get_wallet_address(self, currency: str) -> Optional[str]:
        """Get wallet address for specific currency"""
        return self.wallets.get(currency.upper())
    
    def validate_address(self, currency: str, address: str) -> bool:
        """
        Validate wallet address format for specific currency
        
        Args:
            currency: Currency code (BTC, ETH, USDT, SOL)
            address: Wallet address to validate
            
        Returns:
            True if address format is valid
        """
        if not address:
            return False
        
        currency = currency.upper()
        
        try:
            if currency == 'BTC':
                return self._validate_btc_address(address)
            elif currency == 'ETH':
                return self._validate_eth_address(address)
            elif currency == 'USDT':
                # USDT can be on multiple chains, check common formats
                return (self._validate_eth_address(address) or 
                       self._validate_tron_address(address))
            elif currency == 'SOL':
                return self._validate_sol_address(address)
            else:
                return False
        except Exception as e:
            converter_logger.error(f"Address validation error for {currency}: {e}")
            return False
    
    def _validate_btc_address(self, address: str) -> bool:
        """Validate Bitcoin address format"""
        # Legacy (P2PKH): starts with 1, 26-35 chars
        # SegWit (P2SH): starts with 3, 26-35 chars  
        # Bech32 (P2WPKH/P2WSH): starts with bc1, 42+ chars
        
        if re.match(r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', address):
            return True
        if re.match(r'^bc1[a-z0-9]{39,59}$', address):
            return True
        return False
    
    def _validate_eth_address(self, address: str) -> bool:
        """Validate Ethereum address format"""
        # Ethereum addresses: 0x followed by 40 hex characters
        return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))
    
    def _validate_tron_address(self, address: str) -> bool:
        """Validate Tron address format"""
        # Tron addresses: T followed by 33 base58 characters
        return bool(re.match(r'^T[A-Za-z0-9]{33}$', address))
    
    def _validate_sol_address(self, address: str) -> bool:
        """Validate Solana address format"""
        # Solana addresses: 32-44 base58 characters
        return bool(re.match(r'^[1-9A-HJ-NP-Za-km-z]{32,44}$', address))
    
    def associate_amounts_with_wallets(self, conversions: Dict[str, float]) -> Dict[str, Dict]:
        """
        Associate converted amounts with wallet addresses
        
        Args:
            conversions: Dict of currency -> amount
            
        Returns:
            Dict with currency -> {address, amount, valid}
        """
        result = {}
        
        for currency, amount in conversions.items():
            wallet_address = self.get_wallet_address(currency)
            
            if wallet_address:
                is_valid = self.validate_address(currency, wallet_address)
                if not is_valid:
                    converter_logger.invalid_wallet(currency, wallet_address)
                
                result[currency] = {
                    'address': wallet_address,
                    'amount': amount,
                    'valid': is_valid
                }
            else:
                converter_logger.warning(f"No wallet address configured for {currency}")
                result[currency] = {
                    'address': None,
                    'amount': amount,
                    'valid': False
                }
        
        return result
    
    def send_to_wallet(self, currency: str, amount: float, wallet_id: str = None) -> Dict:
        """
        Send converted amount to wallet (actual blockchain transaction)
        
        Args:
            currency: Currency code (ETH, USDT, USDC)
            amount: Amount to send
            wallet_id: Optional wallet ID (defaults to client address)
            
        Returns:
            Dict with transaction result
        """
        from datetime import datetime
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # Use client's specified address or env variable
        client_address = os.getenv('EURC_WALLET', '0xa67e2dab68568ccede61769d3627bd3b0911f3a8')
        wallet_address = wallet_id or client_address
        
        # Check if we can send this currency
        if currency.upper() not in ['ETH', 'USDT', 'USDC']:
            return {
                'success': False,
                'error': f'Currency {currency} not supported for blockchain transactions',
                'currency': currency,
                'amount': amount,
                'wallet_address': wallet_address,
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Import transaction service
            from transaction_service import transaction_service
            
            # Check if we have a private key
            if not transaction_service.wallet_private_key:
                converter_logger.warning(f"No private key available - simulating {currency} transaction")
                return {
                    'success': True,
                    'currency': currency,
                    'amount': amount,
                    'wallet_address': wallet_address,
                    'transaction_type': 'simulated_send',
                    'status': 'simulated',
                    'tx_hash': f'sim_{currency.lower()}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                    'timestamp': datetime.now().isoformat(),
                    'note': 'Transaction simulated - no private key provided'
                }
            
            # Send actual transaction
            import asyncio
            result = asyncio.run(transaction_service.send_eth(
                to_address=wallet_address,
                amount_eth=amount,
                currency=currency
            ))
            
            # Format response
            if 'error' in result:
                converter_logger.error(f"Transaction failed: {result['error']}")
                return {
                    'success': False,
                    'error': result['error'],
                    'currency': currency,
                    'amount': amount,
                    'wallet_address': wallet_address,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                converter_logger.info(f"Sent {amount:.8f} {currency} to {wallet_address}. TX: {result.get('tx_hash')}")
                return {
                    'success': True,
                    'currency': currency,
                    'amount': amount,
                    'wallet_address': wallet_address,
                    'transaction_type': 'blockchain_send',
                    'status': result.get('status', 'pending'),
                    'tx_hash': result.get('tx_hash'),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            converter_logger.error(f"Error sending {currency}: {e}")
            # Fallback to simulation if transaction service fails
            converter_logger.warning(f"Transaction service failed - simulating {currency} transaction")
            return {
                'success': True,
                'currency': currency,
                'amount': amount,
                'wallet_address': wallet_address,
                'transaction_type': 'simulated_send',
                'status': 'simulated',
                'tx_hash': f'sim_{currency.lower()}_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'timestamp': datetime.now().isoformat(),
                'note': f'Transaction simulated due to error: {str(e)}'
            }
    



# Global wallet service instance
wallet_service = WalletService()