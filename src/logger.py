"""
Logging utility for Lynx Crypto Converter
Provides structured logging with rotation
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


class ConverterLogger:
    """Centralized logging for the converter system"""
    
    def __init__(self, log_dir="logs", log_file="converter.log", max_bytes=10*1024*1024, backup_count=5):
        self.log_dir = log_dir
        self.log_file = log_file
        self.logger = self._setup_logger(max_bytes, backup_count)
    
    def _setup_logger(self, max_bytes, backup_count):
        """Setup logger with file rotation"""
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Create logger
        logger = logging.getLogger('lynx_converter')
        logger.setLevel(logging.DEBUG)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # File handler with rotation
        log_path = os.path.join(self.log_dir, self.log_file)
        file_handler = RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count
        )
        file_handler.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def info(self, message):
        """Log info message"""
        self.logger.info(message)
    
    def error(self, message):
        """Log error message"""
        self.logger.error(message)
    
    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)
    
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)
    
    def conversion_success(self, balance_count, total_amount):
        """Log successful conversion"""
        self.info(f"Conversion successful - {balance_count} balances, total: ${total_amount:,.2f}")
    
    def api_failure(self, error):
        """Log API failure"""
        self.error(f"API request failed: {error}")
    
    def fallback_rates_used(self):
        """Log fallback rates usage"""
        self.warning("Using offline rates - API unreachable")
    
    def invalid_wallet(self, currency, address):
        """Log invalid wallet address"""
        self.warning(f"Invalid wallet address format detected - {currency}: {address}")


# Global logger instance
converter_logger = ConverterLogger()