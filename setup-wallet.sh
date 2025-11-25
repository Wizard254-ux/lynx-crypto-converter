#!/bin/bash
# Setup Wallet for Lynx Crypto Converter
# Configures private key and wallet addresses for real transactions

echo "🔐 Lynx Crypto Converter - Wallet Setup"
echo "========================================"
echo ""

# Create key directory
KEY_DIR="$HOME/Documents/key"
KEY_FILE="$KEY_DIR/wallet.txt"

echo "📁 Creating key directory..."
mkdir -p "$KEY_DIR"

if [ -f "$KEY_FILE" ]; then
    echo "⚠️  Private key file already exists: $KEY_FILE"
    read -p "Do you want to replace it? (y/N): " replace
    if [[ ! $replace =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled"
        exit 1
    fi
fi

echo ""
echo "🔑 Private Key Setup"
echo "==================="
echo "You need to provide your Ethereum private key for real transactions."
echo "This key will be stored securely in: $KEY_FILE"
echo ""
echo "⚠️  SECURITY WARNING:"
echo "   • Never share your private key with anyone"
echo "   • Make sure this is a dedicated wallet for crypto conversion"
echo "   • Keep backups of your private key in a secure location"
echo ""

read -p "Enter your Ethereum private key (without 0x prefix): " private_key

if [ -z "$private_key" ]; then
    echo "❌ No private key provided"
    exit 1
fi

# Validate key length
if [ ${#private_key} -ne 64 ]; then
    echo "❌ Invalid private key length. Expected 64 characters, got ${#private_key}"
    exit 1
fi

# Save private key
echo "$private_key" > "$KEY_FILE"
chmod 600 "$KEY_FILE"

echo "✅ Private key saved successfully"
echo "   Location: $KEY_FILE"
echo "   Permissions: 600 (owner read/write only)"

echo ""
echo "💼 Wallet Address Configuration"
echo "=============================="
echo "Configure wallet addresses in your .env file:"
echo ""

# Try to derive address from private key
if command -v python3 > /dev/null; then
    echo "🔍 Deriving wallet address from private key..."
    
    cat > /tmp/derive_address.py << 'EOF'
import sys
sys.path.append('src')
try:
    from eth_account import Account
    private_key = sys.argv[1]
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    account = Account.from_key(private_key)
    print(f"Your wallet address: {account.address}")
except Exception as e:
    print(f"Could not derive address: {e}")
EOF
    
    cd "$(dirname "$0")"
    if [ -f "venv/bin/python" ]; then
        venv/bin/python /tmp/derive_address.py "$private_key"
    else
        python3 /tmp/derive_address.py "$private_key" 2>/dev/null || echo "Could not derive address (missing dependencies)"
    fi
    rm -f /tmp/derive_address.py
fi

echo ""
echo "📝 Add these to your .env file:"
echo "BTC_WALLET=your_btc_address"
echo "ETH_WALLET=your_eth_address"  
echo "USDT_WALLET=your_usdt_address"
echo "SOL_WALLET=your_sol_address"
echo "EURC_WALLET=your_eurc_address"

echo ""
echo "🧪 Testing Setup"
echo "==============="
echo "Run this command to test your setup:"
echo "  venv/bin/python test_transaction.py"

echo ""
echo "✅ Wallet setup complete!"
echo ""
echo "🚨 IMPORTANT REMINDERS:"
echo "   • Your private key is stored in: $KEY_FILE"
echo "   • Make sure you have sufficient ETH for gas fees"
echo "   • Test with small amounts first"
echo "   • Keep your private key secure and backed up"