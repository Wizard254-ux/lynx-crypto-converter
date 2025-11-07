"""
CLI Tool for Lynx Crypto Converter
Milestone 1: Parse balance files from command line
"""

import argparse
import sys
from parser import BalanceParser
from tabulate import tabulate
import json
import webbrowser
import subprocess
import requests


def print_banner():
    """Print CLI banner"""
    banner = """
╔══════════════════════════════════════════════════════╗
║     LYNX CRYPTO CONVERTER - CLI TOOL                 ║
║     Milestone 1: Balance Parser                      ║
╚══════════════════════════════════════════════════════╝
    """
    print(banner)


def format_balance_table(balances):
    """Format balances as a table"""
    if not balances:
        return "No balances found"
    
    table_data = []
    for idx, balance in enumerate(balances, 1):
        table_data.append([
            idx,
            f"${balance['value']:,.2f}",
            balance.get('currency_symbol', 'N/A'),
            balance['context'][:50] + '...' if len(balance['context']) > 50 else balance['context']
        ])
    
    return tabulate(
        table_data,
        headers=['#', 'Value', 'Symbol', 'Context'],
        tablefmt='grid'
    )


def format_summary_table(summary):
    """Format summary statistics as a table"""
    summary_data = [
        ['Total Values Found', summary['total_values_found']],
        ['Total Sum', f"${summary['total_sum']:,.2f}"],
        ['Minimum Value', f"${summary['min_value']:,.2f}"],
        ['Maximum Value', f"${summary['max_value']:,.2f}"],
        ['Average Value', f"${summary['avg_value']:,.2f}"]
    ]
    
    return tabulate(summary_data, headers=['Metric', 'Value'], tablefmt='grid')


def parse_command(args):
    """Handle parse command"""
    try:
        print(f"\n📄 Parsing file: {args.file}")
        print("=" * 60)
        
        parser = BalanceParser(args.file)
        balances = parser.parse()
        summary = parser.get_summary()
        
        print(f"\n✅ Successfully parsed {len(balances)} balance value(s)\n")
        
        # Show summary
        print("📊 SUMMARY STATISTICS")
        print(format_summary_table(summary))
        
        # Show detailed balances if requested
        if args.detailed:
            print("\n📋 DETAILED BALANCES")
            print(format_balance_table(balances))
        
        # Export to JSON if requested
        if args.output:
            export_data = {
                'balances': balances,
                'summary': summary
            }
            with open(args.output, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"\n💾 Results exported to: {args.output}")
        
        return 0
    
    except FileNotFoundError as e:
        print(f"\n❌ Error: File not found - {e}")
        return 1
    
    except ValueError as e:
        print(f"\n❌ Error: Invalid file - {e}")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def validate_command(args):
    """Handle validate command"""
    try:
        print(f"\n🔍 Validating file: {args.file}")
        print("=" * 60)
        
        parser = BalanceParser(args.file)
        balances = parser.parse()
        
        if len(balances) > 0:
            print("\n✅ File is valid!")
            print(f"   Found {len(balances)} balance value(s)")
            print(f"   Total amount: ${parser.get_total():,.2f}")
        else:
            print("\n⚠️  File is valid but no numeric values were found")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Validation failed: {e}")
        return 1


def convert_command(args):
    """Handle convert command"""
    print(f"\n🔄 Converting file: {args.file}")
    print("=" * 60)
    
    api_url = "http://localhost:5001/api/convert"
    health_url = "http://localhost:5001/health"
    
    try:
        # Check if server is running
        response = requests.get(health_url, timeout=3)
        if response.status_code != 200:
            print("❌ API server is not running")
            print("💡 Start the server first with: python app.py")
            return 1
        
        print("✅ API server is running")
        
        # Check if file exists
        import os
        if not os.path.exists(args.file):
            print(f"❌ File not found: {args.file}")
            return 1
        
        # Send file to API
        with open(args.file, 'rb') as f:
            files = {'file': f}
            data = {}
            if args.currency:
                data['target_currency'] = args.currency
            
            print(f"🚀 Sending file to API for conversion...")
            response = requests.post(api_url, files=files, data=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ Conversion completed successfully!")
            print(json.dumps(result, indent=2))
        else:
            error = response.json() if response.headers.get('content-type') == 'application/json' else {'error': response.text}
            print(f"\n❌ Conversion failed: {error.get('error', 'Unknown error')}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        print("💡 Start the server first with: python app.py")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


def api_command(args):
    """Handle api command"""
    print("\n🌐 Opening API Documentation...")
    print("=" * 60)
    
    api_url = "http://localhost:5001/"
    health_url = "http://localhost:5001/health"
    
    try:
        # Check if server is running
        response = requests.get(health_url, timeout=3)
        if response.status_code == 200:
            print("✅ API server is running")
            
            # Try to open in browser
            if webbrowser.open(api_url):
                print(f"🌐 Opened API documentation in browser: {api_url}")
            else:
                print(f"🌐 Please open in browser: {api_url}")
                
            print(f"📋 JSON API Docs: {api_url}api/docs")
            print(f"❤️  Health Check: {health_url}")
            
        else:
            print("❌ API server responded with error")
            return 1
            
    except requests.exceptions.ConnectionError:
        print("❌ API server is not running")
        print("💡 Start the server first with: python app.py")
        print("💡 Or use the launcher: ./lynx-launcher.sh")
        return 1
    except Exception as e:
        print(f"❌ Error connecting to API: {e}")
        return 1
    
    return 0


def demo_command(args):
    """Handle demo command"""
    print("\n🎬 DEMO MODE - Creating sample balance file...")
    print("=" * 60)
    
    try:
        from docx import Document
        
        # Create sample document
        doc = Document()
        doc.add_heading('Account Balances - November 2024', 0)
        
        doc.add_paragraph('Checking Account: $5,250.00')
        doc.add_paragraph('Savings Account: $12,800.50')
        doc.add_paragraph('Investment Portfolio: $45,000.00')
        doc.add_paragraph('Emergency Fund: $8,500.00')
        doc.add_paragraph('Crypto Wallet: $3,275.25')
        
        filename = 'demo_balances.docx'
        doc.save(filename)
        
        print(f"✅ Created sample file: {filename}")
        
        # Parse it
        print(f"\n📄 Parsing demo file...")
        parser = BalanceParser(filename)
        balances = parser.parse()
        summary = parser.get_summary()
        
        print("\n📊 DEMO RESULTS")
        print(format_summary_table(summary))
        
        print("\n📋 DEMO BALANCES")
        print(format_balance_table(balances))
        
        print(f"\n✅ Demo completed! You can now test with: python cli.py parse {filename}")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1


def main():
    """Main CLI entry point"""
    print_banner()
    
    parser = argparse.ArgumentParser(
        description='Lynx Crypto Converter - Balance File Parser',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Parse a balance file:
    python cli.py parse balances.docx
  
  Parse with detailed output:
    python cli.py parse balances.docx --detailed
  
  Parse and export to JSON:
    python cli.py parse balances.docx --output results.json
  
  Validate a file:
    python cli.py validate balances.docx
  
  Run demo:
    python cli.py demo
  
  Convert balance file:
    python cli.py convert balances.docx
  
  Convert to specific currency:
    python cli.py convert balances.docx --currency EUR
  
  Open API documentation:
    python cli.py api
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse balance file')
    parse_parser.add_argument('file', help='Path to balance file (.docx or .dox)')
    parse_parser.add_argument('-d', '--detailed', action='store_true', help='Show detailed balance list')
    parse_parser.add_argument('-o', '--output', help='Export results to JSON file')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate balance file')
    validate_parser.add_argument('file', help='Path to balance file')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demo with sample data')
    
    # Convert command
    convert_parser = subparsers.add_parser('convert', help='Convert balance file using API')
    convert_parser.add_argument('file', help='Path to balance file (.docx or .dox)')
    convert_parser.add_argument('-c', '--currency', help='Target currency (default: USD)')
    
    # API command
    api_parser = subparsers.add_parser('api', help='Open API documentation')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    if args.command == 'parse':
        return parse_command(args)
    elif args.command == 'validate':
        return validate_command(args)
    elif args.command == 'demo':
        return demo_command(args)
    elif args.command == 'convert':
        return convert_command(args)
    elif args.command == 'api':
        return api_command(args)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
