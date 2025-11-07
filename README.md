# Lynx Crypto Converter

![Lynx Crypto Converter](assets/img.png)

## Status: Milestone 3 Complete ✅

Production-ready cryptocurrency converter with comprehensive API documentation and desktop integration.

## Quick Start

### 1. Activate Environment
```bash
source venv/bin/activate
```

### 2. Run Demo
```bash
./commands.sh demo
```

### 3. Start System (Desktop Launcher)
```bash
./lynx-launcher.sh
```
Or start API server manually:
```bash
./commands.sh start
```
API available at: http://localhost:5001

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

# Convert to cryptocurrency (NEW)
python cli.py convert balances.docx

# Convert to specific currency (NEW)
python cli.py convert balances.docx --currency BTC

# Open API documentation (NEW)
python cli.py api
```

### API Usage

**Health Check:**
```bash
curl http://localhost:5001/health
```

**API Documentation:**
```bash
# HTML Documentation
open http://localhost:5001/

# JSON API Specification
curl http://localhost:5001/api/docs
```

**Convert Balances:**
```bash
curl -X POST -F "file=@balances.docx" http://localhost:5001/api/convert
```

**Portfolio Summary:**
```bash
curl -X POST -F "file=@balances.docx" http://localhost:5001/api/portfolio
```

**Single Conversion:**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"amount": 1.5, "from_currency": "BTC", "to_currency": "USD"}' \
  http://localhost:5001/api/convert-single
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

| Method | Endpoint           | Description                    |
|--------|--------------------|--------------------------------|
| GET    | /                  | HTML API Documentation        |
| GET    | /health            | Health check                   |
| GET    | /api/docs          | JSON API Specification         |
| POST   | /api/convert       | Convert balances to crypto     |
| POST   | /api/portfolio     | Portfolio summary & validation |
| POST   | /api/convert-single| Single amount conversion       |

## What It Does

**Complete Features:**
- ✅ Balance file parsing (.docx, .dox)
- ✅ Cryptocurrency conversion (BTC, ETH, USDT, SOL, etc.)
- ✅ Live exchange rates with fallback
- ✅ Wallet address validation
- ✅ Portfolio analysis and summaries
- ✅ Comprehensive API documentation
- ✅ Desktop integration (Linux Mint)
- ✅ CLI and web interfaces
- ✅ Production-ready deployment

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

## Desktop Integration

**Install Desktop Launcher:**
```bash
./install-desktop.sh
```

**Manual Desktop Entry:**
```bash
cp lynx-crypto-converter.desktop ~/.local/share/applications/
update-desktop-database ~/.local/share/applications/
```

**Interactive Launcher Commands:**
- `demo` - Run demonstration
- `parse` - Parse balance file
- `convert` - Convert to cryptocurrency
- `api` - Open API documentation
- `stop` - Stop background server
- `help` - Show detailed help

## Support

For issues, check logs:
```bash
tail -f logs/app.log
```
