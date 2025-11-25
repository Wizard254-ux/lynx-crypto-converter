# Lynx Crypto Converter - Complete Client Manual

## Overview

Lynx Crypto Converter is a complete cryptocurrency conversion system that parses balance files, converts USD amounts to cryptocurrencies, and sends transactions to blockchain wallets. The system supports both CLI and desktop interfaces with full API integration.

## System Architecture

### Core Components

1. **Parser Module** (`parser.py`) - Extracts balance data from .docx/.dox files
2. **Converter Module** (`converter.py`) - Handles cryptocurrency conversion logic
3. **Rate Service** (`rate_service.py`) - Fetches live exchange rates from CoinGecko
4. **Wallet Service** (`wallet_service.py`) - Manages wallet addresses and validation
5. **Transaction Service** (`transaction_service.py`) - Handles blockchain transactions
6. **API Server** (`app.py`) - Flask REST API endpoints
7. **CLI Tool** (`cli.py`) - Command line interface
8. **Desktop Launcher** (`lynx-launcher.sh`) - Interactive desktop application

## Detailed Service Architecture

### Parser Service (`parser.py`)

**Purpose:** Extracts monetary values from document files

**Key Features:**
- **Document Processing:** Uses `python-docx` library to read .docx files
- **Pattern Recognition:** Regex patterns to identify currency values
- **Context Extraction:** Captures surrounding text for balance identification
- **Data Validation:** Ensures extracted values are valid numbers

**Processing Flow:**
```python
# Example extraction patterns
patterns = [
    r'\$([0-9,]+\.?[0-9]*)',           # $1,234.56
    r'([0-9,]+\.?[0-9]*)\s*USD',       # 1234.56 USD
    r'Balance:?\s*\$?([0-9,]+\.?[0-9]*)', # Balance: $1234
]
```

**Output Format:**
```json
{
  "value": 1234.56,
  "currency_symbol": "$",
  "context": "Checking Account Balance",
  "position": 15
}
```

**Error Handling:**
- Invalid file formats → ValueError with descriptive message
- Corrupted documents → Graceful fallback with partial results
- No values found → Empty list with warning log

### Rate Service (`rate_service.py`)

**Purpose:** Fetches and manages live cryptocurrency exchange rates

**Data Source:** CoinGecko API (free tier)

**Supported Rate Pairs:**
- USD → BTC (Bitcoin)
- USD → ETH (Ethereum)
- USD → USDT (Tether)
- USD → SOL (Solana)
- USD → USDC (USD Coin)

**Caching Strategy:**
```python
class RateService:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        self.last_update = None
    
    def get_rates(self):
        if self._is_cache_valid():
            return self.cache
        return self._fetch_fresh_rates()
```

**Rate Calculation:**
- Fetches current USD price per 1 crypto unit
- Calculates conversion: `crypto_amount = usd_amount / usd_per_crypto`
- Example: $1000 USD ÷ $50,000 USD/BTC = 0.02 BTC

**Fallback Mechanisms:**
- Network failure → Use cached rates with warning
- API rate limit → Exponential backoff retry
- Invalid response → Default to last known good rates

### Converter Service (`converter.py`)

**Purpose:** Orchestrates the complete conversion workflow

**Main Conversion Flow:**
```python
def convert_balances(file_path, target_currency='USD'):
    # 1. Parse document
    balances = parser.parse(file_path)
    
    # 2. Calculate total USD
    total_usd = sum(balance['value'] for balance in balances)
    
    # 3. Get exchange rates
    rates = rate_service.get_rates()
    
    # 4. Convert to each cryptocurrency
    conversions = {}
    for currency, rate in rates.items():
        crypto_amount = total_usd / float(rate)
        conversions[currency] = crypto_amount
    
    # 5. Associate with wallets
    wallet_info = wallet_service.associate_amounts_with_wallets(conversions)
    
    return {
        'success': True,
        'total_usd_amount': total_usd,
        'conversions': conversions,
        'wallet_info': wallet_info
    }
```

**Conversion Methods:**

1. **File-based Conversion:**
   - Input: Document file path
   - Process: Parse → Sum → Convert → Associate
   - Output: Complete conversion report

2. **Single Amount Conversion:**
   - Input: Amount, from_currency, to_currency
   - Process: Direct rate lookup and calculation
   - Output: Converted amount with rate information

3. **Portfolio Summary:**
   - Input: Document file
   - Process: Full conversion + wallet validation
   - Output: Portfolio analysis with wallet status

**Error Recovery:**
- Parser failure → Return error with file validation tips
- Rate service failure → Use cached rates or return error
- Wallet service failure → Continue with conversion, mark wallets invalid

### Wallet Service (`wallet_service.py`)

**Purpose:** Manages wallet addresses, validation, and transaction coordination

**Wallet Address Management:**
```python
class WalletService:
    def __init__(self):
        self.wallets = {
            'BTC': os.getenv('BTC_WALLET'),
            'ETH': os.getenv('ETH_WALLET'),
            'USDT': os.getenv('USDT_WALLET'),
            'SOL': os.getenv('SOL_WALLET')
        }
```

**Address Validation Rules:**

1. **Bitcoin (BTC):**
   - Legacy: `^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$`
   - SegWit: `^bc1[a-z0-9]{39,59}$`

2. **Ethereum (ETH/USDT):**
   - Format: `^0x[a-fA-F0-9]{40}$`
   - Checksum validation using Web3

3. **Solana (SOL):**
   - Format: `^[1-9A-HJ-NP-Za-km-z]{32,44}$`
   - Base58 encoding validation

**Transaction Coordination:**
```python
def send_to_wallet(currency, amount, wallet_id=None):
    # 1. Determine destination address
    address = wallet_id or self.get_wallet_address(currency)
    
    # 2. Validate address format
    if not self.validate_address(currency, address):
        return {'error': 'Invalid wallet address'}
    
    # 3. Check private key availability
    if not transaction_service.wallet_private_key:
        return self._simulate_transaction(currency, amount, address)
    
    # 4. Execute blockchain transaction
    return asyncio.run(transaction_service.send_eth(address, amount, currency))
```

**Simulation Mode:**
- Activated when no private key is available
- Generates mock transaction IDs
- Logs all transaction details for testing
- Returns success response with simulation markers

### Transaction Service (`transaction_service.py`)

**Purpose:** Handles actual blockchain transactions

**Blockchain Integration:**

1. **Web3 Connection:**
```python
self.web3 = Web3(HTTPProvider(eth_node_url))
self.account = self.web3.eth.account.from_key(private_key)
```

2. **Contract Addresses (Smart Contracts):**
```python
self.token_addresses = {
    'USDT': '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # Tether contract
    'USDC': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'   # USDC contract
}
```

3. **Wallet Addresses (Destinations):**
```python
self.wallet_addresses = {
    'ETH': os.getenv('ETH_WALLET'),    # Where to send ETH
    'USDT': os.getenv('USDT_WALLET'), # Where to send USDT tokens
    'BTC': os.getenv('BTC_WALLET')    # Where to send BTC
}
```

**Transaction Types:**

1. **Native ETH Transfer:**
```python
tx = {
    'nonce': nonce,
    'to': destination_address,
    'value': amount_in_wei,
    'gas': estimated_gas,
    'gasPrice': current_gas_price,
    'chainId': network_chain_id
}
```

2. **ERC-20 Token Transfer:**
```python
# Build contract transaction
tx = contract.functions.transfer(
    destination_address,
    amount_in_token_units
).build_transaction({
    'chainId': chain_id,
    'from': sender_address,
    'nonce': nonce,
    'gasPrice': gas_price
})
```

**Gas Management:**
- **Dynamic Estimation:** `web3.eth.estimate_gas(tx)`
- **Price Limits:** `min(current_price, max_allowed_price)`
- **Fallback Limits:** 21000 for ETH, 100000 for tokens

**Security Features:**
- Private key loaded from secure file only
- Transaction signing happens locally
- Gas price limits prevent excessive fees
- Address validation before sending

## Storage & Data Management

### File Storage Structure

```
lynx-crypto-converter/
├── uploads/                    # Temporary file storage
│   ├── 20241201_143022_balances.docx
│   └── 20241201_143155_portfolio.docx
├── logs/                      # Application logs
│   ├── app.log               # Main application log
│   ├── server.log            # API server log
│   └── converter.log         # Conversion operations log
├── data/
│   ├── sample/               # Sample files for testing
│   └── cache/                # Rate cache storage (optional)
└── ~/Documents/key/          # Private key storage
    └── wallet.txt            # Ethereum private key
```

### Upload Management

**File Processing Pipeline:**
```python
# 1. File Upload
filename = secure_filename(file.filename)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
unique_filename = f"{timestamp}_{filename}"
filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

# 2. Validation
if not allowed_file(filename):
    return {'error': 'Invalid file type'}
if file.content_length > MAX_FILE_SIZE:
    return {'error': 'File too large'}

# 3. Processing
file.save(filepath)
result = process_file(filepath)

# 4. Cleanup (optional)
os.remove(filepath)  # Remove after processing
```

**Storage Policies:**
- **Retention:** Files deleted after processing (configurable)
- **Security:** Uploaded files stored in restricted directory
- **Naming:** Timestamped filenames prevent conflicts
- **Size Limits:** 10MB maximum file size

### Logging System

**Log Configuration:**
```python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()  # Console output
    ]
)
```

**Log Categories:**

1. **Application Logs (`app.log`):**
   - API requests and responses
   - File processing events
   - Error conditions and recovery

2. **Conversion Logs:**
   - Rate fetching operations
   - Conversion calculations
   - Wallet associations

3. **Transaction Logs:**
   - Blockchain transaction attempts
   - Gas estimation and pricing
   - Transaction confirmations

4. **Security Logs:**
   - Private key loading events
   - Address validation results
   - Authentication attempts

### Cache Management

**Rate Caching:**
```python
class RateCache:
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
        self.max_cache_size = 100
    
    def get(self, key):
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.cache_duration:
                return entry['data']
        return None
    
    def set(self, key, data):
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        self._cleanup_old_entries()
```

**Cache Strategies:**
- **Exchange Rates:** 5-minute cache to reduce API calls
- **Wallet Validation:** Cache valid addresses for session
- **Gas Prices:** 1-minute cache for transaction optimization

### Configuration Management

**Environment Variables (.env):**
```bash
# Application Settings
FLASK_ENV=production
SECRET_KEY=your_secret_key
MAX_FILE_SIZE=10485760

# Wallet Configuration
BTC_WALLET=your_btc_address
ETH_WALLET=your_eth_address
USDT_WALLET=your_usdt_address

# Blockchain Settings
ETH_NODE_URL=your_ethereum_rpc_url
MAX_GAS_PRICE_GWEI=100
GAS_LIMIT=21000

# API Keys (optional)
COINGECKO_API_KEY=your_api_key
```

**Configuration Loading:**
```python
from dotenv import load_dotenv

load_dotenv()  # Load .env file

# Access configuration
max_file_size = int(os.getenv('MAX_FILE_SIZE', '10485760'))
eth_wallet = os.getenv('ETH_WALLET')
api_key = os.getenv('COINGECKO_API_KEY')
```

### Data Flow Architecture

**Complete Processing Pipeline:**

1. **Input Stage:**
   - File upload via API/CLI
   - Validation and temporary storage
   - Security checks and format verification

2. **Processing Stage:**
   - Document parsing and value extraction
   - Rate fetching with caching
   - Conversion calculations
   - Wallet address association

3. **Transaction Stage:**
   - Private key loading and validation
   - Blockchain transaction preparation
   - Gas estimation and optimization
   - Transaction signing and broadcasting

4. **Output Stage:**
   - Result formatting and logging
   - Response generation
   - Cleanup and resource management

**Error Handling at Each Stage:**
- Input validation errors → 400 Bad Request
- Processing errors → Partial results with warnings
- Transaction errors → Simulation mode fallback
- System errors → 500 Internal Server Error with logging

### Supported Cryptocurrencies

- **Bitcoin (BTC)** - Native blockchain
- **Ethereum (ETH)** - Native blockchain  
- **Tether USD (USDT)** - ERC-20 token on Ethereum
- **USD Coin (USDC)** - ERC-20 token on Ethereum
- **Solana (SOL)** - Native blockchain
- **Euro Coin (EURC)** - ERC-20 token on Ethereum

## Installation & Setup

### 1. Initial Setup
```bash
# Clone and setup
git clone <repository>
cd lynx-crypto-converter
./setup.sh
```

### 2. Desktop Integration
```bash
# Install desktop app
./install-desktop.sh

# Launch desktop app
./lynx-launcher.sh
```

### 3. Private Key Configuration
```bash
# Create key directory
mkdir -p ~/Documents/key

# Add your Ethereum private key (without 0x prefix)
echo "your_private_key_here" > ~/Documents/key/wallet.txt
chmod 600 ~/Documents/key/wallet.txt
```

### 4. Environment Configuration
Edit `.env` file with your wallet addresses:
```bash
# Wallet Addresses
BTC_WALLET=3CFXYcS8CLDWpvhQta8U63rCCydJJK7Dfe
ETH_WALLET=0x09a28669bD58a9242Ff4c759d052293E823e3dDb
USDT_WALLET=0x09a28669bD58a9242Ff4c759d052293E823e3dDb
EURC_WALLET=0xa67e2dab68568ccede61769d3627bd3b0911f3a8
SOL_WALLET=Am9hEzWcaYEp1TEmJyGfnaauM4VwHamtsipy3aMfKutC

# Blockchain Settings
ETH_NODE_URL=http://eth-mainnet.g.alchemy.com/v2/KettzPrWNtxGAbLpVrFNT
MAX_GAS_PRICE_GWEI=100
GAS_LIMIT=21000
```

## Usage Methods

### Method 1: Desktop Application (Recommended)

Launch the desktop app:
```bash
./lynx-launcher.sh
```

Available commands in desktop mode:
- `demo` - Run demonstration with sample data
- `parse` - Parse balance file and show results
- `convert` - Convert balances to cryptocurrency
- `send` - Convert and send to wallet addresses
- `api` - Open API documentation in browser
- `stop` - Stop background server
- `help` - Show detailed help

### Method 2: Command Line Interface

```bash
# Activate environment
source venv/bin/activate
cd src

# Basic operations
python cli.py demo                           # Run demo
python cli.py parse balances.docx            # Parse file
python cli.py validate balances.docx         # Validate file

# Cryptocurrency operations
python cli.py convert balances.docx          # Convert & save
python cli.py send balances.docx             # Convert & send to wallet
python cli.py api                            # Open API docs
```

### Method 3: REST API

Start API server:
```bash
cd src && python app.py
# Server runs on http://localhost:5001
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/health` | Health check | None |
| GET | `/` | API documentation (HTML) | None |
| GET | `/api/docs` | API documentation (JSON) | None |
| POST | `/api/parse` | Parse balance file | `file` (multipart) |
| POST | `/api/validate` | Validate file format | `file` (multipart) |
| POST | `/api/convert` | Convert to crypto & save | `file` (multipart), `target_currency` (optional) |
| POST | `/api/send-to-wallet` | Convert & send to wallet | `file` (multipart), `wallet_id` (optional) |
| POST | `/api/convert-single` | Convert single amount | JSON: `amount`, `from_currency`, `to_currency` |
| POST | `/api/portfolio` | Get portfolio summary | `file` (multipart) |

### API Examples

**Health Check:**
```bash
curl http://localhost:5001/health
```

**Parse File:**
```bash
curl -X POST -F "file=@balances.docx" http://localhost:5001/api/parse
```

**Convert File:**
```bash
curl -X POST -F "file=@balances.docx" http://localhost:5001/api/convert
```

**Send to Wallet:**
```bash
curl -X POST -F "file=@balances.docx" http://localhost:5001/api/send-to-wallet
```

**Single Conversion:**
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"amount": 1000, "from_currency": "USD", "to_currency": "BTC"}' \
     http://localhost:5001/api/convert-single
```

## File Processing

### Supported File Formats
- `.docx` - Microsoft Word documents
- `.dox` - Legacy Word documents
- Maximum file size: 10MB

### Balance File Requirements
Files should contain balance information in formats like:
- "Checking Account: $5,250.00"
- "Savings: $12,800.50"  
- "Investment Portfolio: $45,000.00"
- "Balance: 8,500.00 USD"

### Processing Flow
1. **Parse** - Extract numeric values and context from document
2. **Validate** - Verify file format and content
3. **Convert** - Calculate cryptocurrency amounts using live rates
4. **Associate** - Link amounts with configured wallet addresses
5. **Send** - Execute blockchain transactions (optional)

### Data Persistence

**Conversion Records:**
```json
{
  "conversion_id": "conv_20241201_143022",
  "timestamp": "2024-12-01T14:30:22Z",
  "source_file": "balances.docx",
  "total_usd": 75550.00,
  "conversions": {
    "BTC": 1.51100000,
    "ETH": 18.66400000,
    "USDT": 75550.00000000
  },
  "wallet_assignments": {
    "BTC": "3CFXYcS8CLDWpvhQta8U63rCCydJJK7Dfe",
    "ETH": "0x09a28669bD58a9242Ff4c759d052293E823e3dDb",
    "USDT": "0x09a28669bD58a9242Ff4c759d052293E823e3dDb"
  },
  "status": "ready_to_send"
}
```

**Transaction Records:**
```json
{
  "transaction_id": "tx_20241201_143155",
  "conversion_id": "conv_20241201_143022",
  "currency": "USDT",
  "amount": 75550.00000000,
  "to_address": "0x09a28669bD58a9242Ff4c759d052293E823e3dDb",
  "tx_hash": "0xabc123...",
  "status": "pending",
  "gas_used": 65000,
  "gas_price_gwei": 25,
  "timestamp": "2024-12-01T14:31:55Z"
}
```

## Blockchain Integration

### Transaction Service Architecture

**Contract Addresses (Token Contracts):**
- USDT: `0xdAC17F958D2ee523a2206206994597C13D831ec7`
- USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`

**Wallet Addresses (Destinations):**
- Configured in `.env` file
- Used as transaction recipients
- Support multiple cryptocurrencies

### Transaction Features
- **Dynamic Gas Estimation** - Calculates optimal gas fees
- **Chain Detection** - Automatically detects network parameters
- **ERC-20 Support** - Full token contract integration
- **Decimal Handling** - Queries contracts for precise decimals
- **Error Handling** - Graceful fallbacks and simulation mode

### Security Features
- Private key loaded from secure file (`~/Documents/key/wallet.txt`)
- File permissions set to 600 (owner read/write only)
- Gas price limits to prevent excessive fees
- Transaction validation before sending

## Configuration Files

### `.env` Configuration
```bash
# Flask Settings
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your_secret_key

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_FOLDER=uploads

# Wallet Addresses (Configure these)
BTC_WALLET=your_btc_address
ETH_WALLET=your_eth_address
USDT_WALLET=your_usdt_address
EURC_WALLET=your_eurc_address
SOL_WALLET=your_sol_address

# Blockchain Settings
ETH_NODE_URL=your_ethereum_node_url
MAX_GAS_PRICE_GWEI=100
GAS_LIMIT=21000
```

### Private Key File
Location: `~/Documents/key/wallet.txt`
```
# Add your Ethereum private key here (without 0x prefix)
abcd1234567890abcd1234567890abcd1234567890abcd1234567890abcd1234
```

## Project Structure

```
lynx-crypto-converter/
├── src/                     # Source code
│   ├── parser.py           # Balance extraction logic
│   ├── converter.py        # Conversion engine
│   ├── rate_service.py     # Exchange rate fetching
│   ├── wallet_service.py   # Wallet management
│   ├── transaction_service.py # Blockchain transactions
│   ├── app.py              # Flask API server
│   ├── cli.py              # Command line interface
│   └── logger.py           # Logging configuration
├── uploads/                # File upload storage
├── logs/                   # Application logs
├── data/sample/            # Sample data files
├── assets/                 # Desktop app assets
├── venv/                   # Python virtual environment
├── .env                    # Environment configuration
├── requirements.txt        # Python dependencies
├── setup.sh               # Initial setup script
├── install-desktop.sh     # Desktop integration
├── lynx-launcher.sh       # Desktop launcher
└── MANUAL.md              # This documentation
```

## Error Handling & Troubleshooting

### Common Issues

**1. Virtual Environment Problems:**
```bash
rm -rf venv
./setup.sh
```

**2. Permission Errors:**
- Ensure you're in Linux filesystem (not /mnt/c/ on WSL)
- Check file permissions: `chmod 600 ~/Documents/key/wallet.txt`

**3. Module Not Found:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**4. API Server Not Running:**
```bash
cd src && python app.py
# Or use desktop launcher: ./lynx-launcher.sh
```

**5. Private Key Issues:**
- Verify file exists: `~/Documents/key/wallet.txt`
- Check file format (no 0x prefix)
- Ensure secure permissions (600)

### Log Files
- Application logs: `logs/app.log`
- Server logs: `logs/server.log`

Check logs for detailed error information:
```bash
tail -f logs/app.log
```

## Security Considerations

### Private Key Security
- Store private key in secure location (`~/Documents/key/wallet.txt`)
- Set restrictive file permissions (600)
- Never commit private keys to version control
- Use separate keys for testing and production

### Network Security
- Use secure Ethereum node endpoints
- Validate all wallet addresses before transactions
- Set reasonable gas price limits
- Monitor transaction confirmations

### File Security
- Validate uploaded file types and sizes
- Sanitize file paths and names
- Store uploads in designated directory
- Clean up temporary files

## Performance Optimization

### Rate Limiting
- Exchange rate API calls are cached
- Implement request throttling for high-volume usage
- Use connection pooling for database operations

### File Processing
- Stream large files instead of loading into memory
- Implement file size limits (10MB default)
- Use asynchronous processing for multiple files

### Blockchain Operations
- Batch multiple transactions when possible
- Use appropriate gas limits to avoid failures
- Implement retry logic for network issues

### Storage Optimization

**File Management:**
- Automatic cleanup of processed files
- Compression for long-term storage
- Efficient temporary file handling

**Memory Management:**
```python
# Stream processing for large files
def process_large_file(filepath):
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(8192)  # 8KB chunks
            if not chunk:
                break
            yield process_chunk(chunk)
```

**Cache Optimization:**
- LRU cache for frequently accessed data
- Automatic cache invalidation
- Memory-efficient storage formats

**Database Considerations (Future Enhancement):**
- SQLite for local storage
- PostgreSQL for production deployments
- Redis for high-performance caching

```sql
-- Example schema for conversion tracking
CREATE TABLE conversions (
    id SERIAL PRIMARY KEY,
    conversion_id VARCHAR(50) UNIQUE,
    timestamp TIMESTAMP DEFAULT NOW(),
    source_file VARCHAR(255),
    total_usd DECIMAL(15,2),
    conversions JSONB,
    wallet_assignments JSONB,
    status VARCHAR(20) DEFAULT 'pending'
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE,
    conversion_id VARCHAR(50) REFERENCES conversions(conversion_id),
    currency VARCHAR(10),
    amount DECIMAL(20,8),
    to_address VARCHAR(100),
    tx_hash VARCHAR(100),
    status VARCHAR(20),
    gas_used INTEGER,
    gas_price_gwei INTEGER,
    timestamp TIMESTAMP DEFAULT NOW()
);
```

## Monitoring & Maintenance

### Health Checks
- API health endpoint: `GET /health`
- Monitor server response times
- Check blockchain node connectivity
- Verify exchange rate service availability

### Regular Maintenance
- Update exchange rate cache periodically
- Clean up old uploaded files
- Rotate log files to prevent disk space issues
- Update cryptocurrency contract addresses if needed

### Backup Procedures
- Backup wallet private keys securely
- Export configuration files
- Maintain database backups if using persistent storage
- Document wallet addresses and recovery procedures

### Storage Maintenance

**Automated Cleanup:**
```python
# Daily cleanup script
def cleanup_old_files():
    upload_dir = 'uploads/'
    max_age_days = 7
    
    for filename in os.listdir(upload_dir):
        filepath = os.path.join(upload_dir, filename)
        file_age = time.time() - os.path.getctime(filepath)
        
        if file_age > (max_age_days * 24 * 3600):
            os.remove(filepath)
            logger.info(f"Cleaned up old file: {filename}")
```

**Log Rotation:**
```python
# Log rotation configuration
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
```

**Backup Strategy:**
```bash
#!/bin/bash
# backup-script.sh

# Backup configuration
cp .env backups/env_$(date +%Y%m%d).backup

# Backup private keys (encrypted)
tar -czf backups/keys_$(date +%Y%m%d).tar.gz ~/Documents/key/

# Backup logs
tar -czf backups/logs_$(date +%Y%m%d).tar.gz logs/

# Clean old backups (keep 30 days)
find backups/ -name "*.backup" -mtime +30 -delete
find backups/ -name "*.tar.gz" -mtime +30 -delete
```

## Support & Contact

For technical support:
1. Check log files for error details
2. Verify configuration settings
3. Test with sample data using demo mode
4. Ensure all dependencies are installed correctly

System Requirements:
- Python 3.8+
- Linux/WSL/Ubuntu/Linux Mint
- 100MB disk space
- Internet connection for API calls
- Ethereum node access for blockchain transactions

---

**Version:** 3.0  
**Last Updated:** December 2024  
**Status:** Production Ready ✅