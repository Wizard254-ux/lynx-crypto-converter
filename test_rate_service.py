#!/usr/bin/env python3
"""Test script for rate service"""

import sys
sys.path.insert(0, 'src')

from src.rate_service import rate_service

print('Testing Rate Service...')
print('=' * 60)

# Test fetching rates
rates = rate_service.get_rates()

if rates:
    print('✓ Successfully fetched rates from CoinGecko API')
    print(f'\nCurrent Crypto Rates (USD):')
    for currency, rate in rates.items():
        print(f'  {currency}: ${float(rate):,.2f}')

    # Check fallback file
    import os
    fallback_path = 'data/fallback_rates.json'
    if os.path.exists(fallback_path):
        print(f'\n✓ Fallback rates saved to: {fallback_path}')
    else:
        print(f'\n⚠ Fallback file not created')
else:
    print('✗ Failed to fetch rates')
    sys.exit(1)

print('\n' + '=' * 60)
print('Rate Service Test: PASSED')
