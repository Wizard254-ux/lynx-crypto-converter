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
        self.eth_node_url = os.getenv('ETH_NODE_URL', 'https://ethereum-rpc.publicnode.com')
        converter_logger.info(f"Using Ethereum node: {self.eth_node_url}")
        self.wallet_private_key = self._load_private_key()
        self.destination_wallet = os.getenv('DESTINATION_WALLET')
        
        # Load wallet addresses from .env
        self.wallet_addresses = {
            'BTC': os.getenv('BTC_WALLET'),
            'ETH': os.getenv('ETH_WALLET'),
            'USDT': os.getenv('USDT_WALLET'),
            'EURC': os.getenv('EURC_WALLET'),
            'SOL': os.getenv('SOL_WALLET')
        }
        
        # Gas configuration
        self.max_gas_price_gwei = float(os.getenv('MAX_GAS_PRICE_GWEI', '100'))
        self.gas_limit = int(os.getenv('GAS_LIMIT', '21000'))
        
        # Token contract addresses (mainnet)
        self.token_addresses = {
            'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
            'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
        }
        
        converter_logger.info(f"Supported tokens: {list(self.token_addresses.keys())}")
        
        # Complete ERC-20 ABI
        self.erc20_abi = [
            {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
            {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
            {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "", "type": "bool"}], "type": "function"}
        ]
        
        # Initialize web3
        try:
            self.web3 = Web3(HTTPProvider(self.eth_node_url))
            if self.web3.is_connected():
                converter_logger.info(f"Web3 connected successfully")
                converter_logger.info(f"Connected to chain ID: {self.web3.eth.chain_id}")
            else:
                converter_logger.warning(f"Web3 connection failed to {self.eth_node_url}")
        except Exception as e:
            converter_logger.error(f"Failed to connect to Ethereum node: {e}")
            self.web3 = None
        
        # Set up account
        if self.wallet_private_key:
            try:
                self.account = self.web3.eth.account.from_key(self.wallet_private_key)
                converter_logger.info(f"Account loaded: {self.account.address}")
            except Exception as e:
                converter_logger.error(f"Failed to load account: {e}")
                self.account = None
        else:
            self.account = None
            converter_logger.warning("No wallet private key found. Transaction sending disabled.")
    
    def _load_private_key(self) -> Optional[str]:
        """Load private key from Documents/key/wallet.txt"""
        try:
            # Load from Documents/key/wallet.txt
            home_dir = os.path.expanduser('~')
            key_file = os.path.join(home_dir, 'Documents', 'key', 'wallet.txt')
            
            converter_logger.info(f"Looking for private key at: {key_file}")
            
            if os.path.exists(key_file):
                with open(key_file, 'r') as f:
                    private_key = f.read().strip()
                    if private_key and private_key != 'YOUR_PRIVATE_KEY_HERE':
                        converter_logger.info(f"Private key loaded from {key_file}")
                        # Validate key format
                        if private_key.startswith('0x'):
                            private_key = private_key[2:]
                        if len(private_key) == 64:
                            return private_key
                        else:
                            converter_logger.error(f"Invalid private key length: {len(private_key)}")
                            return None
                    else:
                        converter_logger.warning(f"Private key file is empty or contains placeholder")
                        return None
            else:
                converter_logger.warning(f"Private key file not found: {key_file}")
                return None
            
        except Exception as e:
            converter_logger.error(f"Failed to load private key: {e}")
            return None
    
    def get_wallet_address(self, currency: str) -> Optional[str]:
        """Get wallet address for currency from .env file"""
        return self.wallet_addresses.get(currency.upper())
    
    def reload_private_key(self) -> bool:
        """Reload private key from wallet.txt file"""
        converter_logger.info("Reloading private key from wallet.txt")
        self.wallet_private_key = self._load_private_key()
        
        if self.wallet_private_key and self.web3:
            try:
                self.account = self.web3.eth.account.from_key(self.wallet_private_key)
                converter_logger.info(f"Account reloaded: {self.account.address}")
                return True
            except Exception as e:
                converter_logger.error(f"Failed to reload account: {e}")
                self.account = None
                return False
        else:
            self.account = None
            return False

    async def send_eth(self, to_address: str = None, amount_eth: float = 0, currency: str = 'ETH') -> Dict:
        """Send ETH or tokens to an address"""
        # Use default wallet address if none provided
        if not to_address:
            to_address = self.get_wallet_address(currency)
            if not to_address:
                return {'error': f'No wallet address configured for {currency}'}
        
        # Try to reload private key if account is not available
        if not self.account:
            converter_logger.info("No account available, attempting to reload private key")
            if not self.reload_private_key():
                return {'error': 'No account configured for sending transactions - private key not found or invalid'}
        
        if not self.web3.is_connected():
            return {'error': 'Not connected to Ethereum network'}
            
        try:
            converter_logger.info(f"Attempting to send {amount_eth} {currency} to {to_address}")
            
            # For tokens (USDT, USDC), use token transfer
            if currency.upper() in self.token_addresses:
                converter_logger.info(f"Using token transfer for {currency}")
                return await self._send_token(to_address, amount_eth, currency.upper())
            
            # For ETH
            if currency.upper() != 'ETH':
                return {'error': f'Unsupported currency: {currency}'}
            
            converter_logger.info(f"Using ETH transfer for {currency}")
            
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
                'to': to_checksum_address(to_address),
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
            
            converter_logger.info(f"ETH transaction sent: {self.web3.to_hex(tx_hash)}")
            
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
            converter_logger.info(f"Starting token transfer: {amount} {token_symbol} to {to_address}")
            
            token_address = self.token_addresses.get(token_symbol)
            if not token_address:
                return {'error': f'Token {token_symbol} not supported'}
            
            converter_logger.info(f"Token contract address: {token_address}")
            
            # Create contract instance with complete ABI
            contract = self.web3.eth.contract(
                address=to_checksum_address(token_address),
                abi=self.erc20_abi
            )
            
            # Get actual decimals from contract
            try:
                decimals = contract.functions.decimals().call()
                converter_logger.info(f"Token decimals from contract: {decimals}")
            except Exception as e:
                # Fallback for USDT which may not have decimals() function
                decimals = 6 if token_symbol == 'USDT' else 18
                converter_logger.warning(f"Could not get decimals from contract, using fallback: {decimals}. Error: {e}")
            
            amount_wei = int(amount * (10 ** decimals))
            converter_logger.info(f"Amount in wei: {amount_wei}")
            
            # Check balance
            try:
                balance = contract.functions.balanceOf(self.account.address).call()
                converter_logger.info(f"Current balance: {balance} wei ({balance / (10 ** decimals)} {token_symbol})")
                
                if balance < amount_wei:
                    return {'error': f'Insufficient balance. Have: {balance / (10 ** decimals)} {token_symbol}, Need: {amount} {token_symbol}'}
            except Exception as e:
                converter_logger.warning(f"Could not check balance: {e}")
            
            # Get current network chain ID
            chain_id = self.web3.eth.chain_id
            converter_logger.info(f"Chain ID: {chain_id}")
            
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            converter_logger.info(f"Nonce: {nonce}")
            
            tx = contract.functions.transfer(
                to_checksum_address(to_address),
                amount_wei
            ).build_transaction({
                'chainId': chain_id,
                'from': self.account.address,
                'nonce': nonce,
                'gasPrice': min(self.web3.eth.gas_price, self.web3.to_wei(self.max_gas_price_gwei, 'gwei'))
            })
            
            converter_logger.info(f"Built transaction: {tx}")
            
            # Estimate gas
            try:
                estimated_gas = self.web3.eth.estimate_gas(tx)
                tx['gas'] = estimated_gas
                converter_logger.info(f"Estimated gas: {estimated_gas}")
            except Exception as e:
                # Fallback gas limit for token transfers
                tx['gas'] = 100000
                converter_logger.warning(f"Gas estimation failed, using fallback: {tx['gas']}. Error: {e}")
            
            # Sign and send
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.wallet_private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            tx_hash_hex = self.web3.to_hex(tx_hash)
            converter_logger.info(f"Token transaction sent: {tx_hash_hex}")
            
            return {
                'status': 'pending',
                'tx_hash': tx_hash_hex,
                'message': 'Token transfer submitted to network',
                'amount': amount,
                'to_address': to_address,
                'token_address': token_address,
                'currency': token_symbol
            }
            
        except Exception as e:
            converter_logger.error(f"Failed to send {token_symbol}: {e}")
            import traceback
            converter_logger.error(f"Full traceback: {traceback.format_exc()}")
            return {'error': str(e)}


# Global instance
transaction_service = TransactionService()