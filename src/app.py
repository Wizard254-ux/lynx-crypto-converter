"""
Flask API Server for Lynx Crypto Converter
Complete cryptocurrency conversion with wallet integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from converter import crypto_converter
import logging

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
    app.run(host='0.0.0.0', port=5000, debug=True)
