# Lynx Crypto Converter - Portable Installation Guide

## 🚀 Universal Installation (Any Linux System)

This installation works on **any Linux system** and **any directory**. No hardcoded paths!

### Quick Install

```bash
# 1. Clone or download to ANY directory
git clone <repository-url> lynx-crypto-converter
# OR extract downloaded zip to any folder

# 2. Navigate to the directory
cd lynx-crypto-converter

# 3. Run setup (works from any location)
chmod +x setup.sh
./setup.sh

# 4. Install desktop integration (optional)
chmod +x install-desktop.sh
./install-desktop.sh
```

### What Makes It Portable

✅ **No hardcoded paths** - All scripts detect their location automatically  
✅ **Works in any directory** - Install anywhere: `/home/user/apps/`, `/opt/`, `~/Downloads/`  
✅ **User-specific installation** - No system-wide changes required  
✅ **Self-contained** - Everything in one folder  

### Installation Examples

**Home directory:**
```bash
cd ~
git clone <repo> lynx-crypto-converter
cd lynx-crypto-converter
./setup.sh
```

**Applications folder:**
```bash
mkdir -p ~/Applications
cd ~/Applications
git clone <repo> lynx-crypto-converter
cd lynx-crypto-converter
./setup.sh
```

**System-wide (requires sudo):**
```bash
sudo mkdir -p /opt/lynx-crypto-converter
sudo chown $USER:$USER /opt/lynx-crypto-converter
cd /opt/lynx-crypto-converter
git clone <repo> .
./setup.sh
```

### How Path Detection Works

**Launcher Script (`lynx-launcher.sh`):**
```bash
# Automatically finds script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
```

**Desktop Integration (`install-desktop.sh`):**
```bash
# Detects installation directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Replaces %PROJECT_DIR% with actual path
sed "s|%PROJECT_DIR%|$PROJECT_DIR|g" lynx-crypto-converter.desktop
```

### Moving the Installation

If you need to move the installation:

```bash
# 1. Move entire folder
mv lynx-crypto-converter /new/location/

# 2. Reinstall desktop integration
cd /new/location/lynx-crypto-converter
./install-desktop.sh
```

The scripts will automatically detect the new location!

### Verification

After installation, verify it works:

```bash
# Test CLI
./commands.sh demo

# Test API
./commands.sh start
# In another terminal:
./commands.sh test

# Test desktop launcher (if installed)
# Look for "Lynx Crypto Converter" in applications menu
```

### Troubleshooting

**Permission errors:**
```bash
chmod +x *.sh
```

**Virtual environment issues:**
```bash
rm -rf venv
./setup.sh
```

**Desktop launcher not appearing:**
```bash
# Reinstall desktop integration
./install-desktop.sh
# Update desktop database
update-desktop-database ~/.local/share/applications/
```

### System Requirements

- Linux (any distribution)
- Python 3.8+
- Internet connection (for initial setup)
- 100MB disk space

### Supported Systems

✅ Ubuntu/Debian  
✅ Linux Mint  
✅ CentOS/RHEL/Fedora  
✅ Arch Linux  
✅ WSL (Windows Subsystem for Linux)  
✅ Any Linux distribution with Python 3.8+  

---

## 🔧 Developer Notes

### Making Scripts Portable

When creating new scripts, use this pattern:

```bash
#!/bin/bash
# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Use relative paths from PROJECT_DIR
cd "$PROJECT_DIR"
source venv/bin/activate
```

### Desktop File Template

Use placeholders in `.desktop` files:
```ini
Exec=%PROJECT_DIR%/script.sh
Icon=%PROJECT_DIR%/assets/icon.png
Path=%PROJECT_DIR%
```

Replace during installation:
```bash
sed "s|%PROJECT_DIR%|$ACTUAL_PATH|g" template.desktop > final.desktop
```

This ensures the application works regardless of installation location!