#!/bin/bash
# Install Lynx Crypto Converter Desktop Integration

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
DESKTOP_FILE="lynx-crypto-converter.desktop"
LAUNCHER_SCRIPT="lynx-launcher.sh"

echo "🖥️  Installing Lynx Crypto Converter Desktop Integration..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "$DESKTOP_FILE" ]; then
    echo "❌ Desktop file not found. Please run from project directory."
    exit 1
fi

# Make launcher script executable
chmod +x "$LAUNCHER_SCRIPT"
echo "✅ Made launcher script executable"

# Create assets directory and icon if it doesn't exist
mkdir -p assets
if [ ! -f "assets/lynx-icon.png" ]; then
    # Create a simple text-based icon (you can replace with actual icon)
    echo "Creating default icon..."
    # For now, we'll use a system icon or create a placeholder
    if [ -f "/usr/share/pixmaps/applications-office.png" ]; then
        cp "/usr/share/pixmaps/applications-office.png" "assets/lynx-icon.png"
    else
        # Create a simple placeholder icon using ImageMagick if available
        if command -v convert > /dev/null; then
            convert -size 64x64 xc:lightblue -pointsize 20 -fill darkblue -gravity center -annotate +0+0 "LCC" "assets/lynx-icon.png"
        else
            # Use a system icon as fallback
            touch "assets/lynx-icon.png"
        fi
    fi
    echo "✅ Created application icon"
fi

# Install desktop file to user applications
DESKTOP_DIR="$HOME/.local/share/applications"
mkdir -p "$DESKTOP_DIR"

# Create desktop file with correct paths
echo "📝 Creating desktop file with correct paths..."
sed "s|%PROJECT_DIR%|$PROJECT_DIR|g" "$DESKTOP_FILE" > "$DESKTOP_DIR/$DESKTOP_FILE"
echo "✅ Installed desktop file to $DESKTOP_DIR"

# Update desktop database
if command -v update-desktop-database > /dev/null; then
    update-desktop-database "$DESKTOP_DIR"
    echo "✅ Updated desktop database"
fi

# Make desktop file executable
chmod +x "$DESKTOP_DIR/$DESKTOP_FILE"

# Create menu shortcut (optional)
MENU_DIR="$HOME/.local/share/applications"
if [ -d "$MENU_DIR" ]; then
    echo "✅ Desktop launcher will appear in applications menu"
fi

echo ""
echo "🎉 Desktop integration installed successfully!"
echo ""
echo "You can now:"
echo "  • Find 'Lynx Crypto Converter' in your applications menu"
echo "  • Launch from Activities/Menu search"
echo "  • Pin to taskbar/favorites"
echo ""
echo "To uninstall:"
echo "  rm $DESKTOP_DIR/$DESKTOP_FILE"
echo ""

# Test if desktop file is valid
if command -v desktop-file-validate > /dev/null; then
    if desktop-file-validate "$DESKTOP_DIR/$DESKTOP_FILE"; then
        echo "✅ Desktop file validation passed"
    else
        echo "⚠️  Desktop file validation warnings (but should still work)"
    fi
fi

echo "Installation complete! 🚀"