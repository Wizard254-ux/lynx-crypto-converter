#!/usr/bin/env python3
"""
Test Transaction Service
Verify that the transaction service is working correctly
"""

import os
import sys
sys.path.append('src')

from transaction_service import transaction_service
from wallet_service import wallet_service
import asyncio

def test_private_key_loading():
    """Test private key loading"""
    print("🔑 Testing private key loading...")
    
    if transaction_service.wallet_private_key:
        print(f"✅ Private key loaded successfully")
        print(f"   Account address: {transaction_service.account.address}")
        return True
    else:
        print("❌ No private key found")
        print("   Expected location: ~/Documents/key/wallet.txt")
        return False

def test_web3_connection():
    """Test Web3 connection"""
    print("\n🌐 Testing Web3 connection...")
    
    if transaction_service.web3 and transaction_service.web3.is_connected():
        print(f"✅ Connected to Ethereum network")
        print(f"   Chain ID: {transaction_service.web3.eth.chain_id}")
        print(f"   Latest block: {transaction_service.web3.eth.block_number}")
        return True
    else:
        print("❌ Not connected to Ethereum network")
        return False

def test_wallet_service():
    """Test wallet service functionality"""
    print("\n💼 Testing wallet service...")
    
    # Test sending USDT
    result = wallet_service.send_to_wallet('USDT', 0.01)
    
    if result['success']:
        print(f"✅ Wallet service working")
        print(f"   Transaction type: {result.get('transaction_type', 'unknown')}")
        print(f"   Status: {result.get('status', 'unknown')}")
        if result.get('tx_hash'):
            print(f"   TX Hash: {result['tx_hash']}")
        return True
    else:
        print(f"❌ Wallet service failed: {result.get('error', 'unknown error')}")
        return False

async def test_direct_transaction():
    """Test direct transaction service"""
    print("\n🚀 Testing direct transaction service...")
    
    if not transaction_service.wallet_private_key:
        print("⚠️  Skipping direct transaction test - no private key")
        return False
    
    try:
        # Test USDT transfer
        result = await transaction_service.send_eth(
            to_address="0xa67e2dab68568ccede61769d3627bd3b0911f3a8",
            amount_eth=0.01,
            currency="USDT"
        )
        
        if 'error' in result:
            print(f"❌ Direct transaction failed: {result['error']}")
            return False
        else:
            print(f"✅ Direct transaction successful")
            print(f"   TX Hash: {result.get('tx_hash')}")
            return True
            
    except Exception as e:
        print(f"❌ Direct transaction error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Lynx Crypto Converter - Transaction Service Test")
    print("=" * 60)
    
    tests = [
        test_private_key_loading(),
        test_web3_connection(),
        test_wallet_service()
    ]
    
    # Run async test
    try:
        async_result = asyncio.run(test_direct_transaction())
        tests.append(async_result)
    except Exception as e:
        print(f"❌ Async test failed: {e}")
        tests.append(False)
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {sum(tests)}/{len(tests)} passed")
    
    if not any(tests):
        print("\n🔧 Setup Instructions:")
        print("1. Create private key file: mkdir -p ~/Documents/key")
        print("2. Add your private key: echo 'YOUR_PRIVATE_KEY' > ~/Documents/key/wallet.txt")
        print("3. Set permissions: chmod 600 ~/Documents/key/wallet.txt")
        print("4. Configure .env file with wallet addresses")

if __name__ == "__main__":
    main()