#!/usr/bin/env python3
"""
Test Real Transaction Flow
Shows what you should expect to see when real transactions are attempted
"""

import sys
import os
sys.path.append('src')

from wallet_service import wallet_service

def test_transaction_with_key():
    """Test what happens when we try to send USDT"""
    print("🧪 Testing Real Transaction Flow")
    print("=" * 50)
    
    # Test USDT transaction
    print("\n💰 Attempting USDT transaction...")
    result = wallet_service.send_to_wallet('USDT', 0.01)
    
    print(f"\n📊 Result:")
    print(f"   Success: {result.get('success')}")
    print(f"   Error: {result.get('error', 'None')}")
    print(f"   TX Hash: {result.get('tx_hash', 'None')}")
    print(f"   Type: {result.get('transaction_type', 'None')}")
    
    print(f"\n📝 What you should see with a real private key:")
    print(f"   === TRANSACTION ATTEMPT START ===")
    print(f"   Currency: USDT, Amount: 0.01, Address: 0x...")
    print(f"   Private key available: True")
    print(f"   Web3 connected: True")
    print(f"   Account loaded: True")
    print(f"   All checks passed - attempting real blockchain transaction")
    print(f"   Attempting to send 0.01 USDT to 0x...")
    print(f"   Using token transfer for USDT")
    print(f"   Starting token transfer: 0.01 USDT to 0x...")
    print(f"   Token contract address: 0xdAC17F958D2ee523a2206206994597C13D831ec7")
    print(f"   Token decimals from contract: 6")
    print(f"   Amount in wei: 10000")
    print(f"   Current balance: 50000000 wei (50.0 USDT)")
    print(f"   Chain ID: 1")
    print(f"   Nonce: 42")
    print(f"   Built transaction: {{'chainId': 1, 'from': '0x...', 'nonce': 42, ...}}")
    print(f"   Estimated gas: 65000")
    print(f"   🚀 REAL TRANSACTION SENT: 0.01 USDT to 0x...")
    print(f"   🔗 TX Hash: 0x1234567890abcdef...")
    print(f"   📡 Transaction type: Token transfer")
    print(f"   === TRANSACTION ATTEMPT END ===")

if __name__ == "__main__":
    test_transaction_with_key()