# Lynx Crypto Converter

## Status: Milestone 2 Complete ✅

Full cryptocurrency conversion system with wallet integration, conversion tracking, and desktop app.

## Quick Start

### Option 1: Desktop App (Recommended)
```bash
# Install desktop integration
./install-desktop.sh

# Launch desktop app
./lynx-launcher.sh
```

### Option 2: Manual CLI
```bash
# Activate environment
source venv/bin/activate
cd src

# Run demo
python cli.py demo

# Convert balance file
python cli.py convert balances.docx

# List saved conversions
python cli.py list-conversions

# Send saved conversion
python cli.py send-saved <conversion_id>
```

## Manual Commands

### CLI Usage
```bash
source venv/bin/activate
cd src

# Basic commands
python cli.py demo                           # Run demo
python cli.py parse balances.docx            # Parse file
python cli.py validate balances.docx         # Validate file

# Crypto conversion commands
python cli.py convert balances.docx          # Convert & save
python cli.py send balances.docx             # Convert & send immediately
python cli.py list-conversions               # List saved conversions
python cli.py send-saved <conversion_id>     # Send saved conversion

# API access
python cli.py api                            # Open API documentation
```

### API Usage

**Start API Server:**
```bash
cd src && python app.py
# API available at: http://localhost:5001
```

**Basic Operations:**
```bash
# Health check
curl http://localhost:5001/health

# Parse file
curl -X POST -F "file=@balances.docx" http://localhost:5001/api/parse

# Convert file
curl -X POST -F "file=@balances.docx" http://localhost:5001/api/convert

# Send to wallet
curl -X POST -F "file=@balances.docx" http://localhost:5001/api/send-to-wallet

# List conversions
curl http://localhost:5001/api/list-conversions

# Send saved conversion
curl -X POST -H "Content-Type: application/json" \
     -d '{"conversion_id":"<id>"}' \
     http://localhost:5001/api/send-saved
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

| Method | Endpoint              | Description                    |
|--------|-----------------------|--------------------------------|
| GET    | /health               | Health check                   |
| GET    | /                     | API documentation              |
| POST   | /api/parse            | Parse balance file             |
| POST   | /api/validate         | Validate file format           |
| POST   | /api/convert          | Convert to crypto & save       |
| POST   | /api/send-to-wallet   | Convert & send to wallet       |
| GET    | /api/list-conversions | List saved conversions        |
| POST   | /api/send-saved       | Send saved conversion by ID    |

## What It Does

**Current Features (Milestone 2 Complete):**
- Parse and validate .docx/.dox balance files
- Convert to cryptocurrency (BTC, ETH, USDT, SOL)
- Live exchange rates via CoinGecko API
- Wallet integration with conversion tracking
- Save conversions for later sending
- Desktop application with interactive menu
- Web API with comprehensive endpoints
- CLI tool with full functionality

**Supported Cryptocurrencies:**
- Bitcoin (BTC)
- Ethereum (ETH) 
- Tether USD (USDT)
- Solana (SOL)

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

## Configuration

**Environment Variables (.env file):**
```bash
# Wallet addresses
BTC_WALLET=your_btc_address
ETH_WALLET=your_eth_address
USDT_WALLET=your_usdt_address
SOL_WALLET=your_sol_address
EURC_WALLET=your_eurc_address

# API keys (optional)
COINGECKO_API_KEY=your_coingecko_key
```

**Sample Files:**
Place .docx balance files in `data/sample/` directory for testing.

## Support

For issues, check logs:
```bash
tail -f logs/app.log
```
