#!/usr/bin/env python3
"""
Test Web3 Connection
"""

from web3 import Web3

# Test different RPC endpoints
endpoints = [
    'https://ethereum-rpc.publicnode.com',
    'https://eth.llamarpc.com',
    'https://rpc.ankr.com/eth',
    'https://ethereum.blockpi.network/v1/rpc/public'
]

print("🌐 Testing Ethereum RPC Endpoints")
print("=" * 50)

for endpoint in endpoints:
    try:
        print(f"\n🔗 Testing: {endpoint}")
        web3 = Web3(Web3.HTTPProvider(endpoint))
        
        if web3.is_connected():
            chain_id = web3.eth.chain_id
            block_number = web3.eth.block_number
            print(f"✅ Connected successfully")
            print(f"   Chain ID: {chain_id}")
            print(f"   Latest block: {block_number}")
        else:
            print(f"❌ Connection failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")

print(f"\n" + "=" * 50)
print("✅ Test complete")