"""
Flask API Server for Lynx Crypto Converter
Complete cryptocurrency conversion with wallet integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from dotenv import load_dotenv
from converter import crypto_converter
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'docx', 'dox'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('../logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ensure required directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('logs', exist_ok=True)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Lynx Crypto Converter',
        'milestone': '1 - Setup & Validation',
        'timestamp': datetime.now().isoformat()
    }), 200


@app.route('/api/docs', methods=['GET'])
def api_documentation():
    """API Documentation endpoint"""
    docs = {
        'title': 'Lynx Crypto Converter API',
        'version': '3.0',
        'description': 'Complete cryptocurrency conversion with wallet integration',
        'base_url': 'http://localhost:5001',
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint',
                'response': {
                    'status': 'healthy',
                    'service': 'Lynx Crypto Converter',
                    'timestamp': 'ISO datetime'
                }
            },
            '/api/convert': {
                'method': 'POST',
                'description': 'Convert cryptocurrency balances with wallet integration',
                'content_type': 'multipart/form-data',
                'parameters': {
                    'file': 'Balance file (.docx or .dox) - Required',
                    'target_currency': 'Target currency (optional, default: USD)'
                },
                'response': {
                    'conversions': 'Converted amounts',
                    'wallet_info': 'Associated wallet addresses',
                    'total_value': 'Total portfolio value'
                }
            },
            '/api/portfolio': {
                'method': 'POST',
                'description': 'Get complete portfolio summary with wallet validation',
                'content_type': 'multipart/form-data',
                'parameters': {
                    'file': 'Balance file (.docx or .dox) - Required'
                },
                'response': {
                    'portfolio_summary': 'Complete portfolio analysis',
                    'wallet_validation': 'Wallet address validation results'
                }
            },
            '/api/convert-single': {
                'method': 'POST',
                'description': 'Convert a single amount between currencies',
                'content_type': 'application/json',
                'parameters': {
                    'amount': 'Amount to convert (number) - Required',
                    'from_currency': 'Source currency (string) - Required',
                    'to_currency': 'Target currency (string, optional, default: USD)'
                },
                'response': {
                    'converted_amount': 'Converted value',
                    'exchange_rate': 'Current exchange rate',
                    'timestamp': 'Conversion timestamp'
                }
            },
            '/api/send-to-wallet': {
                'method': 'POST',
                'description': 'Convert balances and send to client wallet',
                'content_type': 'multipart/form-data',
                'parameters': {
                    'file': 'Balance file (.docx or .dox) - Required',
                    'wallet_id': 'Wallet ID (optional, defaults to client address)'
                },
                'response': {
                    'conversions': 'Converted amounts',
                    'wallet_transactions': 'Transaction records',
                    'sent_to_wallet': 'Boolean confirmation'
                }
            }
        },
        'supported_formats': ['.docx', '.dox'],
        'max_file_size': '10MB',
        'examples': {
            'curl_convert': 'curl -X POST -F "file=@balances.docx" http://localhost:5001/api/convert',
            'curl_single': 'curl -X POST -H "Content-Type: application/json" -d \'{"amount": 1.5, "from_currency": "BTC", "to_currency": "USD"}\' http://localhost:5001/api/convert-single'
        }
    }
    return jsonify(docs), 200


@app.route('/', methods=['GET'])
def api_docs_html():
    """Serve HTML API documentation"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Lynx Crypto Converter API Documentation</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 30px; }}
            .endpoint {{ background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #3498db; }}
            .method {{ background: #3498db; color: white; padding: 3px 8px; border-radius: 3px; font-size: 12px; }}
            .path {{ font-family: monospace; font-weight: bold; margin-left: 10px; }}
            .description {{ margin: 10px 0; color: #555; }}
            .params {{ background: #fff; padding: 10px; border-radius: 3px; margin: 5px 0; }}
            .example {{ background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 5px; font-family: monospace; overflow-x: auto; }}
            .status {{ background: #27ae60; color: white; padding: 5px 10px; border-radius: 3px; display: inline-block; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🦌 Lynx Crypto Converter API v3.0</h1>
            <div class="status">Server Status: Online</div>
            <p><strong>Base URL:</strong> http://localhost:5001</p>
            <p><strong>Description:</strong> Complete cryptocurrency conversion with wallet integration</p>
            
            <h2>📋 Available Endpoints</h2>
            
            <div class="endpoint">
                <span class="method">GET</span><span class="path">/health</span>
                <div class="description">Health check endpoint to verify server status</div>
                <div class="params"><strong>Response:</strong> Server status and timestamp</div>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span><span class="path">/api/convert</span>
                <div class="description">Convert cryptocurrency balances with wallet integration</div>
                <div class="params">
                    <strong>Parameters:</strong><br>
                    • file: Balance file (.docx or .dox) - Required<br>
                    • target_currency: Target currency (optional, default: USD)
                </div>
                <div class="example">curl -X POST -F "file=@balances.docx" http://localhost:5001/api/convert</div>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span><span class="path">/api/portfolio</span>
                <div class="description">Get complete portfolio summary with wallet validation</div>
                <div class="params">
                    <strong>Parameters:</strong><br>
                    • file: Balance file (.docx or .dox) - Required
                </div>
                <div class="example">curl -X POST -F "file=@balances.docx" http://localhost:5001/api/portfolio</div>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span><span class="path">/api/convert-single</span>
                <div class="description">Convert a single amount between currencies</div>
                <div class="params">
                    <strong>JSON Parameters:</strong><br>
                    • amount: Amount to convert (number) - Required<br>
                    • from_currency: Source currency - Required<br>
                    • to_currency: Target currency (optional, default: USD)
                </div>
                <div class="example">curl -X POST -H "Content-Type: application/json" -d '{{"amount": 1.5, "from_currency": "BTC", "to_currency": "USD"}}' http://localhost:5001/api/convert-single</div>
            </div>
            
            <div class="endpoint">
                <span class="method">POST</span><span class="path">/api/send-to-wallet</span>
                <div class="description">Convert balances and send to client wallet</div>
                <div class="params">
                    <strong>Parameters:</strong><br>
                    • file: Balance file (.docx or .dox) - Required<br>
                    • wallet_id: Wallet ID (optional, defaults to client address)
                </div>
                <div class="example">curl -X POST -F "file=@balances.docx" http://localhost:5001/api/send-to-wallet</div>
            </div>
            
            <div class="endpoint">
                <span class="method">GET</span><span class="path">/api/docs</span>
                <div class="description">Get API documentation in JSON format</div>
                <div class="params"><strong>Response:</strong> Complete API specification</div>
            </div>
            
            <h2>📝 File Requirements</h2>
            <ul>
                <li>Supported formats: .docx, .dox</li>
                <li>Maximum file size: 10MB</li>
                <li>Files should contain cryptocurrency balance information</li>
            </ul>
            
            <h2>🔗 Quick Links</h2>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/api/docs">JSON Documentation</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
    return html


@app.route('/api/convert', methods=['POST'])
def convert_balances():
    """
    Convert cryptocurrency balances with wallet integration
    
    Request:
        - file: Balance file (.docx or .dox)
        - target_currency: Target currency (optional, default: USD)
    
    Response:
        - conversions: Converted amounts
        - wallet_info: Associated wallet addresses
        - total_value: Total portfolio value
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        logger.info(f"File uploaded: {unique_filename}")
        
        # Get target currency from request
        target_currency = request.form.get('target_currency', 'USD')
        
        # Convert balances
        result = crypto_converter.convert_balances(filepath, target_currency)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.route('/api/portfolio', methods=['POST'])
def get_portfolio_summary():
    """
    Get complete portfolio summary with wallet validation
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        
        # Get portfolio summary
        result = crypto_converter.get_portfolio_summary(filepath)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Portfolio error: {str(e)}")
        return jsonify({'error': f'Portfolio analysis failed: {str(e)}'}), 500


@app.route('/api/convert-single', methods=['POST'])
def convert_single_amount():
    """
    Convert a single amount between currencies
    
    Request JSON:
        - amount: Amount to convert
        - from_currency: Source currency
        - to_currency: Target currency (optional, default: USD)
    """
    try:
        data = request.get_json()
        
        if not data or 'amount' not in data or 'from_currency' not in data:
            return jsonify({'error': 'Missing required fields: amount, from_currency'}), 400
        
        amount = float(data['amount'])
        from_currency = data['from_currency'].upper()
        to_currency = data.get('to_currency', 'USD').upper()
        
        result = crypto_converter.convert_single_amount(amount, from_currency, to_currency)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except ValueError:
        return jsonify({'error': 'Invalid amount value'}), 400
    except Exception as e:
        logger.error(f"Single conversion error: {str(e)}")
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500


@app.route('/api/send-to-wallet', methods=['POST'])
def send_to_wallet():
    """
    Convert balances and send to client wallet
    
    Request:
        - file: Balance file (.docx or .dox)
        - wallet_id: Wallet ID (optional, defaults to client address)
    
    Response:
        - conversions: Converted amounts
        - wallet_transactions: Transaction records
        - sent_to_wallet: Boolean confirmation
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        logger.info(f"File uploaded for wallet sending: {unique_filename}")
        
        # Get wallet ID from request
        wallet_id = request.form.get('wallet_id')
        
        # Convert and send to wallet
        result = crypto_converter.send_converted_amounts_to_wallet(filepath, wallet_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        logger.info(f"Successfully sent converted amounts to wallet")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Wallet send error: {str(e)}")
        return jsonify({'error': f'Wallet send failed: {str(e)}'}), 500


@app.route('/api/list-conversions', methods=['GET'])
def list_saved_conversions():
    """
    List all saved conversions
    
    Query Parameters:
        - include_sent: Whether to include sent conversions (default: true)
    """
    try:
        include_sent = request.args.get('include_sent', 'true').lower() == 'true'
        
        result = crypto_converter.list_saved_conversions(include_sent)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"List conversions error: {str(e)}")
        return jsonify({'error': f'List failed: {str(e)}'}), 500


@app.route('/api/send-saved', methods=['POST'])
def send_saved_conversion():
    """
    Send a previously saved conversion to wallet
    
    Request JSON:
        - conversion_id: ID of saved conversion
        - wallet_id: Wallet ID (optional, defaults to client address)
    """
    try:
        data = request.get_json()
        
        if not data or 'conversion_id' not in data:
            return jsonify({'error': 'Missing required field: conversion_id'}), 400
        
        conversion_id = data['conversion_id']
        wallet_id = data.get('wallet_id')
        
        result = crypto_converter.send_saved_conversion(conversion_id, wallet_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        logger.info(f"Successfully sent saved conversion {conversion_id}")
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Send saved conversion error: {str(e)}")
        return jsonify({'error': f'Send failed: {str(e)}'}), 500


@app.errorhandler(413)
def file_too_large(e):
    """Handle file size exceeded error"""
    return jsonify({
        'error': 'File too large',
        'message': f'Maximum file size is {MAX_FILE_SIZE / (1024*1024)}MB'
    }), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


if __name__ == '__main__':
    logger.info("Starting Lynx Crypto Converter API...")
    logger.info("Complete cryptocurrency conversion with wallet integration")
    app.run(host='0.0.0.0', port=5001, debug=True)
