#!/usr/bin/env python3
"""Test API endpoints - Run this after starting the Flask server"""

import requests
import json
import sys
import os

API_URL = "http://localhost:5000"

print('=' * 60)
print('API ENDPOINTS TEST')
print('=' * 60)
print('\nMake sure Flask server is running:')
print('  cd src && python app.py')
print('\n' + '=' * 60)

def test_endpoint(name, method, url, **kwargs):
    """Test an API endpoint"""
    print(f'\nTEST: {name}')
    print('-' * 60)

    try:
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, timeout=10, **kwargs)

        print(f'Status Code: {response.status_code}')

        if response.status_code in [200, 201]:
            data = response.json()
            print(f'Response:')
            print(json.dumps(data, indent=2))
            print('✓ Test PASSED')
            return True
        else:
            print(f'Response: {response.text}')
            print('✗ Test FAILED')
            return False

    except requests.exceptions.ConnectionError:
        print('✗ ERROR: Cannot connect to Flask server')
        print('  Make sure server is running: cd src && python app.py')
        return False
    except Exception as e:
        print(f'✗ ERROR: {e}')
        return False

# Check if demo file exists
demo_file = 'src/demo_balances.docx'
if not os.path.exists(demo_file):
    print(f'\n✗ Demo file not found: {demo_file}')
    print('  Run: python test_end_to_end.py first')
    sys.exit(1)

# Test 1: Health Check
test_endpoint(
    'Health Check',
    'GET',
    f'{API_URL}/health'
)

# Test 2: Convert Balances
test_endpoint(
    'Convert Balances',
    'POST',
    f'{API_URL}/api/convert',
    files={'file': open(demo_file, 'rb')}
)

# Test 3: Portfolio Summary
test_endpoint(
    'Portfolio Summary',
    'POST',
    f'{API_URL}/api/portfolio',
    files={'file': open(demo_file, 'rb')}
)

# Test 4: Single Conversion
test_endpoint(
    'Single Conversion (USD to BTC)',
    'POST',
    f'{API_URL}/api/convert-single',
    json={
        'amount': 5000,
        'from_currency': 'USD',
        'to_currency': 'BTC'
    },
    headers={'Content-Type': 'application/json'}
)

print('\n' + '=' * 60)
print('API Tests Complete!')
print('=' * 60)
