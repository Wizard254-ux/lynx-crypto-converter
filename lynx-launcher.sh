#!/bin/bash
# Lynx Crypto Converter Desktop Launcher
# Starts API server in background and opens CLI

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
cd "$PROJECT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    read -p "Press Enter to exit..."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start API server in background
echo "🚀 Starting Lynx Crypto Converter..."
echo "📡 Starting API server in background..."
cd src
python app.py > ../logs/server.log 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server is running
if curl -s http://localhost:5001/health > /dev/null; then
    echo "✅ API server started successfully (PID: $SERVER_PID)"
    echo "🌐 API available at: http://localhost:5001"
    echo ""
    
    # Show main menu
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║           LYNX CRYPTO CONVERTER                      ║"
    echo "║           Production System v3.0                    ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
    echo "Available commands:"
    echo "  demo     - Run demonstration"
    echo "  parse    - Parse balance file"
    echo "  convert  - Convert to cryptocurrency"
    echo "  api      - Open API documentation"
    echo "  stop     - Stop background server"
    echo "  help     - Show detailed help"
    echo ""
    
    # Interactive menu
    while true; do
        read -p "lynx> " command
        
        case $command in
            "demo")
                python cli.py demo
                ;;
            "parse")
                read -p "Enter file path: " filepath
                if [ -f "$filepath" ]; then
                    python cli.py parse "$filepath" --detailed
                else
                    echo "❌ File not found: $filepath"
                fi
                ;;
            "convert")
                read -p "Enter file path: " filepath
                if [ -f "$filepath" ]; then
                    echo "Converting balances to cryptocurrency..."
                    curl -X POST -F "file=@$filepath" http://localhost:5001/api/convert | python -m json.tool
                else
                    echo "❌ File not found: $filepath"
                fi
                ;;
            "api")
                echo "Opening API documentation..."
                if command -v xdg-open > /dev/null; then
                    xdg-open "http://localhost:5001/"
                elif command -v open > /dev/null; then
                    open "http://localhost:5001/"
                else
                    echo "🌐 API Documentation: http://localhost:5001/"
                    echo "📋 JSON API Docs: http://localhost:5001/api/docs"
                    echo "❤️  Health Check: http://localhost:5001/health"
                fi
                ;;
            "stop")
                echo "Stopping server..."
                kill $SERVER_PID 2>/dev/null
                echo "✅ Server stopped"
                break
                ;;
            "help")
                python cli.py --help
                ;;
            "exit"|"quit")
                kill $SERVER_PID 2>/dev/null
                break
                ;;
            *)
                echo "Unknown command. Type 'help' for available commands."
                ;;
        esac
    done
else
    echo "❌ Failed to start API server"
    echo "Check logs: tail -f logs/server.log"
    read -p "Press Enter to exit..."
fi

# Cleanup
kill $SERVER_PID 2>/dev/null
echo "👋 Goodbye!"