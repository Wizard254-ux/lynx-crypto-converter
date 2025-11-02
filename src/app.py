"""
Flask API Server for Lynx Crypto Converter
Milestone 1: Balance file upload and parsing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from parser import BalanceParser
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


@app.route('/api/parse', methods=['POST'])
def parse_balance_file():
    """
    Parse balance file and extract numeric values
    
    Request:
        - file: Balance file (.docx or .dox)
    
    Response:
        - balances: List of extracted balance values
        - summary: Statistics summary
        - metadata: File information
    """
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file provided',
                'message': 'Please upload a balance file'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'Only {", ".join(ALLOWED_EXTENSIONS)} files are allowed'
            }), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        logger.info(f"File uploaded: {unique_filename}")
        
        # Parse file
        parser = BalanceParser(filepath)
        balances = parser.parse()
        summary = parser.get_summary()
        
        logger.info(f"Parsed {len(balances)} values from {filename}")
        
        # Prepare response
        response = {
            'success': True,
            'message': 'File parsed successfully',
            'data': {
                'balances': balances,
                'summary': summary
            },
            'metadata': {
                'filename': filename,
                'upload_time': timestamp,
                'file_size': os.path.getsize(filepath)
            }
        }
        
        return jsonify(response), 200
    
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return jsonify({
            'error': 'File not found',
            'message': str(e)
        }), 404
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'error': 'Validation error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Parsing error: {str(e)}")
        return jsonify({
            'error': 'Processing error',
            'message': str(e)
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate_file():
    """
    Quick validation endpoint to check if file can be parsed
    Returns only summary without full balance details
    """
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file'}), 400
        
        # Save temporarily
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"validate_{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        
        # Parse and get summary only
        parser = BalanceParser(filepath)
        parser.parse()
        summary = parser.get_summary()
        
        # Clean up temporary file
        os.remove(filepath)
        
        return jsonify({
            'valid': True,
            'summary': summary,
            'message': 'File is valid and can be parsed'
        }), 200
    
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 400


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
    logger.info("Milestone 1: Setup & Validation")
    app.run(host='0.0.0.0', port=5000, debug=True)
