# Updated Conversion Workflow

## Problem Solved

The client wanted to separate the conversion process from the sending process:
- Parse multiple .docx files and save conversions
- Later select which conversion to send without needing the original .docx file
- The SEND command should work independently of .docx files

## New Workflow

### 1. Parse & Convert (Saves Automatically)
```bash
# Parse and convert - automatically saves conversion
python cli.py convert balances.docx
```
**Output:** Conversion ID (e.g., `balance_file_20241201_143022`)

### 2. List Saved Conversions
```bash
# List all saved conversions
python cli.py list-conversions

# List only pending (unsent) conversions
python cli.py list-conversions --pending-only
```

### 3. Send Saved Conversion (No .docx needed)
```bash
# Send a specific saved conversion
python cli.py send-saved balance_file_20241201_143022

# Send to specific wallet
python cli.py send-saved balance_file_20241201_143022 --wallet-id custom_wallet
```

## API Endpoints

### New Endpoints Added:
- `GET /api/list-conversions` - List saved conversions
- `POST /api/send-saved` - Send saved conversion by ID

### Updated Endpoints:
- `POST /api/convert` - Now returns `conversion_id` in response

## Storage System

### Location
- Conversions stored in: `src/data/conversions/conversions.json`

### Data Structure
```json
{
  "id": "balance_file_20241201_143022",
  "timestamp": "2024-11-18T14:30:22.123456",
  "source_file": "balances.docx",
  "total_usd_amount": 75825.75,
  "conversions": {
    "BTC": 0.00123456,
    "ETH": 0.02345678,
    "USDT": 75825.75,
    "SOL": 345.67890123
  },
  "wallet_info": {...},
  "rates": {...},
  "sent": false
}
```

## Client Workflow Example

### CLI Workflow
1. **Bank sends balance.docx file**
2. **Parse & Convert:**
   ```bash
   python cli.py convert balance_nov_18.docx
   # Returns: balance_nov_18_20241201_143022
   ```

3. **Later, list available conversions:**
   ```bash
   python cli.py list-conversions
   ```

4. **Select and send conversion:**
   ```bash
   python cli.py send-saved balance_nov_18_20241201_143022
   ```

### Desktop App Workflow
1. **Launch desktop app:** `./lynx-launcher.sh`
2. **Convert file:** Type `convert` → Enter file path
3. **List conversions:** Type `list`
4. **Send conversion:** Type `send` → Choose option 2 → Enter conversion ID

## Benefits

✅ **Separation of Concerns:** Parse/convert vs send are now separate operations  
✅ **No File Dependency:** SEND command doesn't need original .docx  
✅ **Multiple Conversions:** Can save multiple conversions and choose which to send  
✅ **Audit Trail:** All conversions are saved with timestamps and status  
✅ **Flexibility:** Can send same conversion multiple times or to different wallets  

## Implementation Files

- `src/conversion_storage.py` - Storage management
- `src/converter.py` - Updated to auto-save conversions
- `src/cli.py` - New commands: `list-conversions`, `send-saved`
- `src/app.py` - New API endpoints
- `lynx-launcher.sh` - Desktop app launcher with interactive menu
- `install-desktop.sh` - Desktop integration installer

## Available Interfaces

### 1. Command Line Interface (CLI)
```bash
# All CLI commands
python cli.py demo                    # Run demo
python cli.py parse file.docx         # Parse file
python cli.py validate file.docx      # Validate file
python cli.py convert file.docx       # Convert & save
python cli.py send file.docx          # Convert & send immediately
python cli.py list-conversions        # List saved conversions
python cli.py send-saved <id>         # Send saved conversion
python cli.py api                     # Open API docs
```

### 2. Desktop Application
```bash
# Install desktop integration
./install-desktop.sh

# Launch desktop app
./lynx-launcher.sh
```
**Desktop Features:**
- Interactive menu with all CLI commands
- File path prompts and validation
- Two-option send command (file or conversion ID)
- API server auto-start and management

### 3. Web API
```bash
# Start API server
python src/app.py

# Available at http://localhost:5001
```

## Backward Compatibility

All existing commands still work:
- `python cli.py convert file.docx` - Still works, now also saves
- `python cli.py send file.docx` - Still works for immediate send