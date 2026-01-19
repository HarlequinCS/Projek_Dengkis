"""
ZERO-COPY PROCESSING - High-speed data handling
Uses mmap for wordlists and ujson for fast JSON parsing.
"""
import mmap
from typing import List, Optional
from pathlib import Path

try:
    import ujson as json
    UJSON_AVAILABLE = True
except ImportError:
    import json
    UJSON_AVAILABLE = False


class ZeroCopyProcessor:
    """
    Zero-copy processing for maximum performance.
    Uses mmap for wordlists and ujson for JSON parsing.
    """
    
    def __init__(self):
        self.mmap_files = {}
    
    def load_wordlist_mmap(self, filepath: str) -> mmap.mmap:
        """
        Load wordlist using memory mapping for zero-copy access.
        
        Args:
            filepath: Path to wordlist file
            
        Returns:
            Memory-mapped file object
        """
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Wordlist not found: {filepath}")
        
        with open(path, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            self.mmap_files[filepath] = mm
            return mm
    
    def parse_json_fast(self, data: str) -> dict:
        """
        Parse JSON using ujson if available, fallback to standard json.
        
        Args:
            data: JSON string
            
        Returns:
            Parsed dictionary
        """
        if UJSON_AVAILABLE:
            return json.loads(data)
        else:
            return json.loads(data)
    
    def dump_json_fast(self, obj: dict) -> str:
        """
        Serialize JSON using ujson if available.
        
        Args:
            obj: Dictionary to serialize
            
        Returns:
            JSON string
        """
        if UJSON_AVAILABLE:
            return json.dumps(obj)
        else:
            return json.dumps(obj)
    
    def close_mmap(self, filepath: str):
        """Close memory-mapped file."""
        if filepath in self.mmap_files:
            self.mmap_files[filepath].close()
            del self.mmap_files[filepath]
    
    def close_all(self):
        """Close all memory-mapped files."""
        for filepath in list(self.mmap_files.keys()):
            self.close_mmap(filepath)
