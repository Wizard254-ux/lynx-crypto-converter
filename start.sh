#!/bin/bash
# Start Lynx Crypto Converter API

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Run setup.sh first."
    exit 1
fi

source venv/bin/activate
cd src

if [ ! -f "app.py" ]; then
    echo "app.py not found in src/ directory"
    exit 1
fi

echo "Starting Lynx Crypto Converter API..."
python app.py
