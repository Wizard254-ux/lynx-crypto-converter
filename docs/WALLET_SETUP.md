 # Wallet Private Key Setup

## 🔐 Private Key Location

The system will read your wallet private key from:
```
~/Documents/key/wallet.txt
```

## 📁 Setup Instructions

1. **Create the directory:**
   ```bash
   mkdir -p ~/Documents/key
   ```

2. **Create the wallet file:**
   ```bash
   touch ~/Documents/key/wallet.txt
   ```

3. **Add your private key:**
   ```bash
   echo "your_private_key_here" > ~/Documents/key/wallet.txt
   ```

4. **Secure the file:**
   ```bash
   chmod 600 ~/Documents/key/wallet.txt
   ```

## 🔒 Security Notes

- File permissions set to 600 (owner read/write only)
- Private key should be 64 characters (32 bytes hex)
- Never share this file or commit to version control
- System checks this location before falling back to environment variables

## 📋 File Format

The `wallet.txt` file should contain only your private key:
```
0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
```

## ✅ Verification

The system will log when the private key is successfully loaded:
```
Private key loaded from /home/username/Documents/key/wallet.txt
```