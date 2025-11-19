#!/bin/bash

# Universal Setup Script for Lynx Crypto Converter
# Works on: Linux Mint, Ubuntu, WSL
# Handles: File permissions, venv creation, dependency installation

set -e

echo "╔══════════════════════════════════════════════════════╗"
echo "║   LYNX CRYPTO CONVERTER - UNIVERSAL SETUP            ║"
echo "║   Milestone 1: Setup & Validation                    ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; exit 1; }
print_info() { echo -e "${YELLOW}ℹ $1${NC}"; }
print_step() { echo -e "${BLUE}▶ $1${NC}"; }

# Detect environment
print_step "Detecting environment..."
if grep -qi microsoft /proc/version 2>/dev/null; then
    ENV_TYPE="WSL"
elif [ -f /etc/linuxmint/info ]; then
    ENV_TYPE="Linux Mint"
elif [ -f /etc/lsb-release ] && grep -qi ubuntu /etc/lsb-release; then
    ENV_TYPE="Ubuntu"
else
    ENV_TYPE="Linux"
fi
print_success "Environment: $ENV_TYPE"

# Check if running in /mnt/c (Windows mount) - WSL issue
CURRENT_DIR=$(pwd)
if [[ "$CURRENT_DIR" == /mnt/c/* ]] || [[ "$CURRENT_DIR" == /mnt/* ]]; then
    print_error "Cannot run in Windows filesystem (/mnt/c/). Move to Linux filesystem:
    
    Run these commands:
    cd ~
    mkdir lynx-crypto-converter
    cd lynx-crypto-converter
    # Copy this script here and run again
    "
fi

print_success "Running in Linux filesystem"

# Check Python
print_step "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_info "Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv python3-dev
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
print_success "Python $PYTHON_VERSION installed"

# Check pip
print_step "Checking pip..."
if ! command -v pip3 &> /dev/null; then
    print_info "Installing pip..."
    sudo apt install -y python3-pip
fi
print_success "pip installed"

# Check venv availability
print_step "Checking venv support..."
if ! python3 -m venv --help &> /dev/null; then
    print_info "Installing venv..."
    sudo apt install -y python3-venv
fi
print_success "venv available"

# Create project structure
print_step "Creating project directories..."
mkdir -p src tests data/sample docs logs uploads
touch logs/.gitkeep uploads/.gitkeep data/sample/.gitkeep
print_success "Directory structure created"

# Remove old venv if exists
if [ -d "venv" ]; then
    print_info "Removing old virtual environment..."
    rm -rf venv
fi

# Create virtual environment
print_step "Creating virtual environment..."
python3 -m venv venv

if [ ! -f "venv/bin/activate" ]; then
    print_error "Failed to create virtual environment"
fi
print_success "Virtual environment created"

# Activate virtual environment
print_step "Activating virtual environment..."
source venv/bin/activate

if [ -z "$VIRTUAL_ENV" ]; then
    print_error "Failed to activate virtual environment"
fi
print_success "Virtual environment activated"

# Upgrade pip
print_step "Upgrading pip..."
pip install --upgrade pip --quiet
print_success "pip upgraded"

# Create requirements.txt
print_step "Creating requirements.txt..."
cat > requirements.txt << 'EOF'
python-docx==1.1.0
flask==3.0.0
flask-cors==4.0.0
pytest==7.4.3
tabulate==0.9.0
python-dotenv
requests
web3==6.11.0
eth-account==0.9.0
setuptools
EOF
print_success "requirements.txt created"

# Install dependencies
print_step "Installing dependencies (this may take a minute)..."
pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    print_error "Failed to install dependencies. Try manually: pip install -r requirements.txt"
fi
print_success "All dependencies installed"

# Create .gitignore
print_step "Creating .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
venv/
env/

# Flask
instance/
.webassets-cache

# Logs
logs/*.log
*.log

# Uploads
uploads/*
!uploads/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
*.env

# Test
.pytest_cache/
.coverage
htmlcov/

# Data
data/sample/*
!data/sample/.gitkeep

# Demo files
demo_balances.docx
test_balances.docx
EOF
print_success ".gitignore created"

# Create environment template
print_step "Creating .env.example..."
cat > .env.example << 'EOF'
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=change-this-in-production

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_FOLDER=uploads

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
EOF
print_success "Environment template created"

# Create start script
print_step "Creating start.sh..."
cat > start.sh << 'EOF'
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
EOF

chmod +x start.sh
print_success "start.sh created"

# Create test script
print_step "Creating test_api.sh..."
cat > test_api.sh << 'EOF'
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
EOF

chmod +x test_api.sh
print_success "test_api.sh created"

# Create quick command script
print_step "Creating quick commands script..."
cat > commands.sh << 'EOF'
#!/bin/bash
# Quick commands for Lynx Crypto Converter

case "$1" in
    start)
        source venv/bin/activate
        cd src && python app.py
        ;;
    cli)
        source venv/bin/activate
        cd src && python cli.py "${@:2}"
        ;;
    test)
        source venv/bin/activate
        ./test_api.sh
        ;;
    demo)
        source venv/bin/activate
        cd src && python cli.py demo
        ;;
    *)
        echo "Usage: ./commands.sh {start|cli|test|demo}"
        echo ""
        echo "Examples:"
        echo "  ./commands.sh start              - Start Flask API"
        echo "  ./commands.sh demo               - Run CLI demo"
        echo "  ./commands.sh cli parse file.docx - Parse a file"
        echo "  ./commands.sh test               - Test API endpoints"
        ;;
esac
EOF

chmod +x commands.sh
print_success "commands.sh created"

# Check if source files exist
print_step "Checking source files..."
MISSING_FILES=0

if [ ! -f "src/parser.py" ]; then
    print_info "src/parser.py missing - needs to be created"
    MISSING_FILES=1
fi

if [ ! -f "src/app.py" ]; then
    print_info "src/app.py missing - needs to be created"
    MISSING_FILES=1
fi

if [ ! -f "src/cli.py" ]; then
    print_info "src/cli.py missing - needs to be created"
    MISSING_FILES=1
fi

if [ $MISSING_FILES -eq 1 ]; then
    print_info "Create the Python files in src/ directory before running"
else
    print_success "All source files present"
fi

# Create comprehensive README
print_step "Creating README.md..."
cat > README.md << 'EOF'
# Lynx Crypto Converter

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
EOF
print_success "README.md created"

# Verify installation
print_step "Verifying installation..."
source venv/bin/activate

python3 << 'PYEOF'
try:
    import docx
    import flask
    import flask_cors
    import pytest
    import tabulate
    print("✓ All modules imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
PYEOF

if [ $? -ne 0 ]; then
    print_error "Module verification failed"
fi
print_success "All modules verified"

# Final summary
echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║   SETUP COMPLETE! ✅                                 ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""
print_success "Environment: $ENV_TYPE"
print_success "Python: $PYTHON_VERSION"
print_success "Virtual environment: $(pwd)/venv"
print_success "All dependencies installed"
echo ""
echo "Next Steps:"
echo ""
echo "1. Ensure Python files are in src/ directory:"
echo "   - src/parser.py"
echo "   - src/app.py"
echo "   - src/cli.py"
echo ""
echo "2. Run demo:"
echo "   ./commands.sh demo"
echo ""
echo "3. Start API:"
echo "   ./commands.sh start"
echo ""
echo "4. Quick commands:"
echo "   ./commands.sh {start|cli|test|demo}"
echo ""
print_info "Virtual environment is activated!"
print_info "To deactivate: deactivate"
print_info "To reactivate: source venv/bin/activate"
echo ""
