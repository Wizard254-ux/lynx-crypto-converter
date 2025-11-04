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
