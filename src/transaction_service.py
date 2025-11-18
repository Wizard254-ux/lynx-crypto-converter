"""
Transaction Service for Lynx Crypto Converter
Handles sending cryptocurrency transactions to specified wallet addresses
"""

import os
import asyncio
from typing import Dict, Optional
from web3 import Web3, HTTPProvider
from eth_account import Account
from eth_utils import to_checksum_address
from dotenv import load_dotenv
from logger import converter_logger


class TransactionService:
    """Handles cryptocurrency transactions and wallet operations"""
    
    def __init__(self):
        load_dotenv()
        
        # Ethereum node configuration
        self.eth_node_url = os.getenv('ETH_NODE_URL', 'http://eth-mainnet.g.alchemy.com/v2/KettzPrWNtxGAbLpVrFNT')
        self.wallet_private_key = self._load_private_key()
        self.destination_wallet = os.getenv('DESTINATION_WALLET')
        
        # Gas configuration
        self.max_gas_price_gwei = float(os.getenv('MAX_GAS_PRICE_GWEI', '100'))
        self.gas_limit = int(os.getenv('GAS_LIMIT', '21000'))
        
        # Token contract addresses
        self.token_addresses = {
            'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
            'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
        }
        
        # Initialize web3
        self.web3 = Web3(HTTPProvider(self.eth_node_url))
        
        # Set up account
        if self.wallet_private_key:
            self.account = self.web3.eth.account.from_key(self.wallet_private_key)
        else:
            self.account = None
            converter_logger.warning("No wallet private key found. Transaction sending disabled.")
    
    def _load_private_key(self) -> Optional[str]:
        """Load private key from Documents/key/wallet.txt"""
        try:
            # Try environment variable first
            # env_key = os.getenv('WALLET_PRIVATE_KEY')
            # if env_key and env_key != 'YOUR_PRIVATE_KEY_HERE':
            #     return env_key
            
            # Load from Documents/key/wallet.txt
            home_dir = os.path.expanduser('~')
            key_file = os.path.join(home_dir, 'Documents', 'key', 'wallet.txt')
            
            if os.path.exists(key_file):
                with open(key_file, 'r') as f:
                    private_key = f.read().strip()
                    if private_key:
                        converter_logger.info(f"Private key loaded from {key_file}")
                        return private_key
            
            converter_logger.warning(f"Private key file not found: {key_file}")
            return None
            
        except Exception as e:
            converter_logger.error(f"Failed to load private key: {e}")
            return None

    async def send_eth(self, to_address: str, amount_eth: float, currency: str = 'ETH') -> Dict:
        """Send ETH or tokens to an address"""
        if not self.account:
            return {'error': 'No account configured for sending transactions'}
            
        try:
            # For tokens, use token transfer
            if currency.upper() in self.token_addresses:
                return await self._send_token(to_address, amount_eth, currency.upper())
            
            # For ETH
            if currency.upper() != 'ETH':
                return {'error': f'Unsupported currency: {currency}'}
            
            # Convert amount to wei
            amount_wei = self.web3.to_wei(amount_eth, 'ether')
            
            # Get nonce
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            
            # Get gas price
            gas_price = min(
                self.web3.eth.gas_price,
                self.web3.to_wei(self.max_gas_price_gwei, 'gwei')
            )
            
            # Build transaction
            tx = {
                'nonce': nonce,
                'to': to_address,
                'value': amount_wei,
                'gas': self.gas_limit,
                'gasPrice': gas_price,
                'chainId': 1
            }
            
            # Estimate gas
            estimated_gas = self.web3.eth.estimate_gas(tx)
            tx['gas'] = estimated_gas
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.wallet_private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return {
                'status': 'pending',
                'tx_hash': self.web3.to_hex(tx_hash),
                'message': 'Transaction submitted to network',
                'amount': amount_eth,
                'to_address': to_address,
                'currency': currency.upper()
            }
            
        except Exception as e:
            converter_logger.error(f"Error sending {currency}: {e}")
            return {'error': str(e)}

    async def _send_token(self, to_address: str, amount: float, token_symbol: str) -> Dict:
        """Send ERC20 token to specified address"""
        try:
            token_address = self.token_addresses.get(token_symbol)
            if not token_address:
                return {'error': f'Token {token_symbol} not supported'}
            
            # Token ABI for transfer function
            token_abi = [{
                "constant": False,
                "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }]
            
            # Create contract instance
            contract = self.web3.eth.contract(
                address=to_checksum_address(token_address),
                abi=token_abi
            )
            
            # Convert amount (assuming 6 decimals for USDT/USDC)
            decimals = 6 if token_symbol in ['USDT', 'USDC'] else 18
            amount_wei = int(amount * (10 ** decimals))
            
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            
            tx = contract.functions.transfer(
                to_checksum_address(to_address),
                amount_wei
            ).build_transaction({
                'chainId': 1,
                'from': self.account.address,
                'nonce': nonce,
                'gasPrice': self.web3.to_wei(self.max_gas_price_gwei, 'gwei'),
                'gas': 200000
            })
            
            # Sign and send
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.wallet_private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            return {
                'status': 'pending',
                'tx_hash': self.web3.to_hex(tx_hash),
                'message': 'Token transfer submitted to network',
                'amount': amount,
                'to_address': to_address,
                'token_address': token_address,
                'currency': token_symbol
            }
            
        except Exception as e:
            converter_logger.error(f"Failed to send {token_symbol}: {e}")
            return {'error': str(e)}


# Global instance
transaction_service = TransactionService()