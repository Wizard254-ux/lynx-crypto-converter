#!/usr/bin/env python3
"""
Check Wallet Configuration
Diagnose private key and wallet setup issues
"""

import os
import sys
sys.path.append('src')

def check_private_key_file():
    """Check if private key file exists and is valid"""
    home_dir = os.path.expanduser('~')
    key_file = os.path.join(home_dir, 'Documents', 'key', 'wallet.txt')
    
    print("🔍 Checking private key file...")
    print(f"   Expected location: {key_file}")
    
    if not os.path.exists(key_file):
        print("❌ Private key file not found")
        return False
    
    print("✅ Private key file exists")
    
    try:
        with open(key_file, 'r') as f:
            content = f.read().strip()
            
        if not content:
            print("❌ Private key file is empty")
            return False
            
        if content == 'YOUR_PRIVATE_KEY_HERE':
            print("❌ Private key file contains placeholder text")
            return False
            
        # Remove 0x prefix if present
        if content.startswith('0x'):
            content = content[2:]
            
        if len(content) != 64:
            print(f"❌ Invalid private key length: {len(content)} (expected 64)")
            return False
            
        # Check if it's valid hex
        try:
            int(content, 16)
        except ValueError:
            print("❌ Private key contains invalid characters (not hex)")
            return False
            
        print("✅ Private key format is valid")
        
        # Try to create account
        try:
            from eth_account import Account
            account = Account.from_key(content)
            print(f"✅ Private key successfully loaded")
            print(f"   Wallet address: {account.address}")
            return True
        except Exception as e:
            print(f"❌ Failed to create account from private key: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error reading private key file: {e}")
        return False

def check_transaction_service():
    """Check transaction service status"""
    print("\n🔧 Checking transaction service...")
    
    try:
        from transaction_service import transaction_service
        
        print(f"   Private key loaded: {bool(transaction_service.wallet_private_key)}")
        print(f"   Account created: {bool(transaction_service.account)}")
        print(f"   Web3 connected: {transaction_service.web3.is_connected() if transaction_service.web3 else False}")
        
        if transaction_service.account:
            print(f"   Account address: {transaction_service.account.address}")
            
        return bool(transaction_service.wallet_private_key and transaction_service.account)
        
    except Exception as e:
        print(f"❌ Error checking transaction service: {e}")
        return False

def main():
    """Run all checks"""
    print("🔐 Lynx Crypto Converter - Wallet Diagnostic")
    print("=" * 50)
    
    key_valid = check_private_key_file()
    service_ready = check_transaction_service()
    
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY:")
    print(f"   Private key file: {'✅ Valid' if key_valid else '❌ Invalid'}")
    print(f"   Transaction service: {'✅ Ready' if service_ready else '❌ Not ready'}")
    
    if key_valid and service_ready:
        print("\n🎉 Wallet is properly configured for real transactions!")
    else:
        print("\n🔧 Setup required:")
        if not key_valid:
            print("   1. Run: ./setup-wallet.sh")
            print("   2. Enter your valid Ethereum private key")
        print("   3. Restart the application")

if __name__ == "__main__":
    main()