"""Grammar Manager - Handles Tag ID to Name mappings"""
import csv
import json
from typing import Dict, Optional
from pathlib import Path


class GrammarManager:
    """
    Manages ASN.1 grammar files that map Tag IDs to human-readable names.
    
    Supports two formats:
    1. CSV: tag_id,name (e.g., "0x4F,Application Identifier")
    2. JSON: {"0x4F": "Application Identifier", ...}
    """
    
    def __init__(self):
        """Initialize grammar manager"""
        self.grammar: Dict[str, str] = {}
        self.file_path: Optional[Path] = None
    
    def load_csv(self, file_path: str) -> bool:
        """
        Load grammar from CSV file
        
        CSV Format:
        tag_id,name
        0x4F,Application Identifier
        0x50,Card Holder Name
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.grammar.clear()
            self.file_path = Path(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                # Skip header if present
                header = next(reader, None)
                if header and header[0].lower() != 'tag_id':
                    # First row is data, not header
                    tag_id, name = header[0].strip(), header[1].strip() if len(header) > 1 else ""
                    self._normalize_and_add(tag_id, name)
                
                for row in reader:
                    if len(row) >= 2:
                        tag_id = row[0].strip()
                        name = row[1].strip()
                        self._normalize_and_add(tag_id, name)
            
            return True
        except Exception as e:
            print(f"Error loading CSV grammar: {e}")
            return False
    
    def load_json(self, file_path: str) -> bool:
        """
        Load grammar from JSON file
        
        JSON Format:
        {
            "0x4F": "Application Identifier",
            "0x50": "Card Holder Name"
        }
        
        Args:
            file_path: Path to JSON file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.grammar.clear()
            self.file_path = Path(file_path)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                for tag_id, name in data.items():
                    self._normalize_and_add(tag_id, str(name))
            
            return True
        except Exception as e:
            print(f"Error loading JSON grammar: {e}")
            return False
    
    def load_file(self, file_path: str) -> bool:
        """
        Auto-detect and load grammar file
        
        Args:
            file_path: Path to grammar file
        
        Returns:
            True if successful, False otherwise
        """
        path = Path(file_path)
        
        if path.suffix.lower() == '.json':
            return self.load_json(file_path)
        elif path.suffix.lower() == '.csv':
            return self.load_csv(file_path)
        else:
            # Try CSV first, then JSON
            if not self.load_csv(file_path):
                return self.load_json(file_path)
            return True
    
    def _normalize_and_add(self, tag_id: str, name: str):
        """
        Normalize tag ID and add to grammar dictionary
        
        Handles various formats: 0x4F, 4F, 79, etc.
        
        Args:
            tag_id: Tag ID in various formats
            name: Human-readable name
        """
        try:
            # Try to parse as hex
            if tag_id.startswith('0x') or tag_id.startswith('0X'):
                value = int(tag_id, 16)
            else:
                # Try as hex without prefix
                try:
                    value = int(tag_id, 16)
                except ValueError:
                    # Try as decimal
                    value = int(tag_id, 10)
            
            # Store with normalized hex key
            key = f"0x{value:02X}"
            self.grammar[key] = name
        except ValueError:
            # Skip invalid entries
            pass
    
    def get_name(self, tag_id: int) -> Optional[str]:
        """
        Get human-readable name for a tag ID
        
        Args:
            tag_id: Tag ID as integer
        
        Returns:
            Name if found, None otherwise
        """
        key = f"0x{tag_id:02X}"
        return self.grammar.get(key)
    
    def get_name_by_hex_string(self, hex_str: str) -> Optional[str]:
        """
        Get name by hex string (e.g., "0x4F")
        
        Args:
            hex_str: Hex string representation
        
        Returns:
            Name if found, None otherwise
        """
        return self.grammar.get(hex_str)
    
    def has_grammar(self) -> bool:
        """Check if grammar is loaded"""
        return len(self.grammar) > 0
    
    def get_all_mappings(self) -> Dict[str, str]:
        """Get all grammar mappings"""
        return self.grammar.copy()
    
    def clear(self):
        """Clear all grammar"""
        self.grammar.clear()
        self.file_path = None
    
    def create_sample_grammar(self, output_path: str, format: str = 'csv'):
        """
        Create a sample grammar file for reference
        
        Args:
            output_path: Path to save sample file
            format: 'csv' or 'json'
        """
        sample_mappings = {
            '0x4F': 'Application Identifier',
            '0x50': 'Card Holder Name',
            '0x5A': 'Application PAN',
            '0x5F20': 'Cardholder Verification',
            '0x5F34': 'CVM Method',
            '0x5F63': 'CVM Results',
            '0x9A': 'Transaction Date',
            '0x9B': 'Transaction Status',
            '0x9C': 'Transaction Type',
            '0x9D': 'Transaction Category Code',
            '0x9F02': 'Amount',
            '0x9F03': 'Amount, Other',
            '0x9F10': 'IAD',
            '0x9F26': 'Cryptogram',
            '0x9F27': 'Cryptogram Information Data',
            '0x9F10': 'Issuer Application Data',
            '0x9F37': 'Unpredictable Number',
            '0x9F34': 'CVM Results',
            '0x9F35': 'Terminal Type',
            '0x9F1A': 'Terminal Country Code',
            '0x95': 'TVR (Terminal Verification Results)',
            '0x9A': 'Transaction Date (YYMMDD)',
        }
        
        if format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(sample_mappings, f, indent=2)
        else:  # CSV
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['tag_id', 'name'])
                for tag_id, name in sample_mappings.items():
                    writer.writerow([tag_id, name])
