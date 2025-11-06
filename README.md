# Lynx Crypto Converter

![Lynx Crypto Converter](assets/img.png)

## Status: Milestone 1 Complete ✅

Balance file parser with CLI and API interface.

## Quick Start

### 1. Activate Environment
```bash
source venv/bin/activate
```

### 2. Run Demo
```bash
./commands.sh demo
```

### 3. Start API Server
```bash
./commands.sh start
```
API available at: http://localhost:5000

### 4. Test API
```bash
# In new terminal
./commands.sh test
```

## Manual Commands

### CLI Usage
```bash
source venv/bin/activate
cd src

# Run demo
python cli.py demo

# Parse a file
python cli.py parse balances.docx

# Parse with details
python cli.py parse balances.docx --detailed

# Export to JSON
python cli.py parse balances.docx --output results.json

# Validate file
python cli.py validate balances.docx
```

### API Usage

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Parse File:**
```bash
curl -X POST -F "file=@balances.docx" http://localhost:5000/api/parse
```

**Validate File:**
```bash
curl -X POST -F "file=@balances.docx" http://localhost:5000/api/validate
```

## Project Structure
```
lynx-crypto-converter/
├── src/
│   ├── parser.py      # Balance extraction logic
│   ├── app.py         # Flask API server
│   └── cli.py         # Command line interface
├── uploads/           # Uploaded files storage
├── logs/              # Application logs
├── data/sample/       # Sample data files
├── venv/              # Virtual environment
├── requirements.txt   # Python dependencies
├── setup.sh           # Setup script
├── start.sh           # Start API server
├── commands.sh        # Quick commands
└── test_api.sh        # API testing script
```

## API Endpoints

| Method | Endpoint       | Description              |
|--------|----------------|--------------------------|
| GET    | /health        | Health check             |
| POST   | /api/parse     | Parse balance file       |
| POST   | /api/validate  | Validate file format     |

## What It Does

**Milestone 1:**
- Reads .docx balance files
- Extracts all numeric values
- Returns via CLI or API
- Calculates totals and statistics

**Coming in Milestone 2:**
- Crypto conversion (BTC, ETH, USDT, SOL)
- Live exchange rates
- Wallet integration

## Troubleshooting

**Virtual environment issues:**
```bash
rm -rf venv
./setup.sh
```

**Permission errors:**
Make sure you're in Linux filesystem, not /mnt/c/

**Module not found:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## System Requirements

- Python 3.8+
- Linux/WSL/Linux Mint/Ubuntu
- 100MB disk space
- Internet connection (for pip install)

## Next Steps for Milestone 2

Provide:
1. Real balance .docx files (3-5 samples)
2. Wallet addresses (BTC, ETH, USDT, SOL)
3. CoinGecko API key or exchange keys

## Support

For issues, check logs:
```bash
tail -f logs/app.log
```
