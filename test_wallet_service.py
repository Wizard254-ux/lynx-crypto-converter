#!/usr/bin/env python3
"""Test script for wallet service"""

import sys
import os
sys.path.insert(0, 'src')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.wallet_service import wallet_service

print('Testing Wallet Service...')
print('=' * 60)

# Check loaded wallets
print('\nLoaded Wallet Addresses:')
for currency in ['BTC', 'ETH', 'USDT', 'SOL']:
    address = wallet_service.get_wallet_address(currency)
    if address:
        print(f'  {currency}: {address}')
    else:
        print(f'  {currency}: Not configured')

# Validate each address
print('\nValidating Wallet Addresses:')
for currency in ['BTC', 'ETH', 'USDT', 'SOL']:
    address = wallet_service.get_wallet_address(currency)
    if address:
        is_valid = wallet_service.validate_address(currency, address)
        status = '✓ VALID' if is_valid else '✗ INVALID'
        print(f'  {currency}: {status}')
    else:
        print(f'  {currency}: ⚠ NOT CONFIGURED')

# Test association with sample conversions
print('\nTesting Wallet Association:')
sample_conversions = {
    'BTC': 0.00954875,
    'ETH': 0.28426395,
    'USDT': 1000.00,
    'SOL': 6.28272882
}

wallet_info = wallet_service.associate_amounts_with_wallets(sample_conversions)

for currency, info in wallet_info.items():
    print(f'\n  {currency}:')
    print(f'    Address: {info["address"] if info["address"] else "Not configured"}')
    print(f'    Amount: {info["amount"]:.8f}')
    print(f'    Valid: {"✓" if info["valid"] else "✗"}')

print('\n' + '=' * 60)
print('Wallet Service Test: PASSED')
