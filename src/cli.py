"""
CLI Tool for Lynx Crypto Converter
Milestone 1: Parse balance files from command line
"""

import argparse
import sys
from parser import BalanceParser
from tabulate import tabulate
import json


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
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
