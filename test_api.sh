#!/bin/bash
# Test API endpoints

API_URL="http://localhost:5000"

echo "Testing Lynx Crypto Converter API..."
echo ""

# Health check
echo "▶ Health Check:"
curl -s $API_URL/health | python3 -m json.tool
echo ""

# Check if demo file exists
if [ ! -f "src/demo_balances.docx" ]; then
    echo "Creating demo file..."
    cd src
    python3 cli.py demo > /dev/null 2>&1
    cd ..
fi

# Test parse
echo "▶ Parse Test:"
curl -s -X POST -F "file=@src/demo_balances.docx" $API_URL/api/parse | python3 -m json.tool
echo ""

echo "✓ All tests completed"
