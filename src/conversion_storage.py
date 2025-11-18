"""
Conversion Storage Service for Lynx Crypto Converter
Saves conversion results for later selection and sending
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from logger import converter_logger


class ConversionStorage:
    """Manages storage and retrieval of conversion results"""
    
    def __init__(self, storage_dir: str = "data/conversions"):
        self.storage_dir = storage_dir
        self.storage_file = os.path.join(storage_dir, "conversions.json")
        
        # Ensure storage directory exists
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize storage file if it doesn't exist
        if not os.path.exists(self.storage_file):
            self._save_conversions([])
    
    def save_conversion(self, conversion_data: Dict) -> str:
        """
        Save a conversion result with unique ID
        
        Args:
            conversion_data: Conversion result from crypto_converter
            
        Returns:
            Unique conversion ID
        """
        try:
            # Extract filename from source_file path
            source_file = conversion_data.get('source_file', 'unknown')
            if source_file != 'unknown':
                filename = os.path.basename(source_file)
                # Remove extension
                filename_no_ext = os.path.splitext(filename)[0]
                # Remove timestamp prefix if present (format: YYYYMMDD_HHMMSS_originalname)
                if '_' in filename_no_ext and len(filename_no_ext.split('_')[0]) == 8:
                    parts = filename_no_ext.split('_')
                    if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
                        # Remove first two parts (date and time)
                        filename_clean = '_'.join(parts[2:]).replace(' ', '_').replace('-', '_')
                    else:
                        filename_clean = filename_no_ext.replace(' ', '_').replace('-', '_')
                else:
                    filename_clean = filename_no_ext.replace(' ', '_').replace('-', '_')
            else:
                filename_clean = 'unknown'
            
            # Generate unique ID with filename and timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            conversion_id = f"{filename_clean}_{timestamp}"
            
            # Add metadata
            conversion_record = {
                'id': conversion_id,
                'timestamp': datetime.now().isoformat(),
                'source_file': conversion_data.get('source_file', 'unknown'),
                'total_usd_amount': conversion_data.get('total_usd_amount', 0),
                'conversions': conversion_data.get('conversions', {}),
                'wallet_info': conversion_data.get('wallet_info', {}),
                'rates': conversion_data.get('rates', {}),
                'sent': False  # Track if already sent
            }
            
            # Load existing conversions
            conversions = self._load_conversions()
            
            # Add new conversion
            conversions.append(conversion_record)
            
            # Save updated list
            self._save_conversions(conversions)
            
            converter_logger.info(f"Saved conversion {conversion_id} with ${conversion_record['total_usd_amount']:,.2f}")
            return conversion_id
            
        except Exception as e:
            converter_logger.error(f"Failed to save conversion: {e}")
            raise
    
    def get_conversion(self, conversion_id: str) -> Optional[Dict]:
        """Get a specific conversion by ID"""
        conversions = self._load_conversions()
        
        for conversion in conversions:
            if conversion['id'] == conversion_id:
                return conversion
        
        return None
    
    def list_conversions(self, include_sent: bool = True) -> List[Dict]:
        """
        List all saved conversions
        
        Args:
            include_sent: Whether to include already sent conversions
            
        Returns:
            List of conversion summaries
        """
        conversions = self._load_conversions()
        
        if not include_sent:
            conversions = [c for c in conversions if not c.get('sent', False)]
        
        # Return summary info
        summaries = []
        for conv in conversions:
            summary = {
                'id': conv['id'],
                'timestamp': conv['timestamp'],
                'source_file': conv.get('source_file', 'unknown'),
                'total_usd': conv.get('total_usd_amount', 0),
                'currencies': list(conv.get('conversions', {}).keys()),
                'sent': conv.get('sent', False)
            }
            summaries.append(summary)
        
        return sorted(summaries, key=lambda x: x['timestamp'], reverse=True)
    
    def mark_as_sent(self, conversion_id: str) -> bool:
        """Mark a conversion as sent"""
        try:
            conversions = self._load_conversions()
            
            for conversion in conversions:
                if conversion['id'] == conversion_id:
                    conversion['sent'] = True
                    conversion['sent_timestamp'] = datetime.now().isoformat()
                    break
            else:
                return False
            
            self._save_conversions(conversions)
            converter_logger.info(f"Marked conversion {conversion_id} as sent")
            return True
            
        except Exception as e:
            converter_logger.error(f"Failed to mark conversion as sent: {e}")
            return False
    
    def delete_conversion(self, conversion_id: str) -> bool:
        """Delete a conversion"""
        try:
            conversions = self._load_conversions()
            original_count = len(conversions)
            
            conversions = [c for c in conversions if c['id'] != conversion_id]
            
            if len(conversions) < original_count:
                self._save_conversions(conversions)
                converter_logger.info(f"Deleted conversion {conversion_id}")
                return True
            
            return False
            
        except Exception as e:
            converter_logger.error(f"Failed to delete conversion: {e}")
            return False
    
    def _load_conversions(self) -> List[Dict]:
        """Load conversions from storage file"""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _save_conversions(self, conversions: List[Dict]) -> None:
        """Save conversions to storage file"""
        with open(self.storage_file, 'w') as f:
            json.dump(conversions, f, indent=2)


# Global storage instance
conversion_storage = ConversionStorage()