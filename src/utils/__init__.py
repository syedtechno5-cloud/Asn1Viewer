"""Utility Helper Functions"""
import os
from typing import List, Tuple
from pathlib import Path


def format_hex_string(data: bytes, bytes_per_line: int = 16) -> str:
    """
    Format binary data as hex string with line breaks
    
    Args:
        data: Binary data
        bytes_per_line: Number of bytes per output line
    
    Returns:
        Formatted hex string
    """
    lines = []
    for i in range(0, len(data), bytes_per_line):
        chunk = data[i:i + bytes_per_line]
        hex_part = ' '.join(f'{b:02x}' for b in chunk)
        # Also show ASCII representation
        ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
        lines.append(f"{i:08x}  {hex_part:<{bytes_per_line * 3}}  {ascii_part}")
    return '\n'.join(lines)


def bytes_to_hex_display(data: bytes, max_length: int = 100) -> str:
    """
    Convert bytes to readable hex display
    
    Args:
        data: Binary data
        max_length: Maximum number of bytes to display
    
    Returns:
        Hex string representation
    """
    if len(data) > max_length:
        return data[:max_length].hex() + "..."
    return data.hex()


def highlight_hex_regions(hex_display: str, start_offset: int, end_offset: int) -> List[Tuple[int, int]]:
    """
    Calculate character ranges to highlight in hex display
    
    Args:
        hex_display: The hex display string (with spaces)
        start_offset: Byte offset to start highlighting
        end_offset: Byte offset to end highlighting
    
    Returns:
        List of (char_start, char_end) tuples for highlighting
    """
    # This is a placeholder - actual implementation would be more complex
    # and calculate exact character positions based on byte offsets
    return [(0, len(hex_display))]


def format_size(size: int) -> str:
    """
    Format byte size in human-readable format
    
    Args:
        size: Size in bytes
    
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def get_file_size(file_path: str) -> int:
    """Get file size in bytes"""
    try:
        return os.path.getsize(file_path)
    except:
        return 0


def is_large_file(file_path: str, threshold: int = 10 * 1024 * 1024) -> bool:
    """
    Check if file is larger than threshold
    
    Args:
        file_path: Path to file
        threshold: Size threshold in bytes (default 10MB)
    
    Returns:
        True if file is larger than threshold
    """
    return get_file_size(file_path) > threshold


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe saving
    
    Args:
        filename: Original filename
    
    Returns:
        Sanitized filename
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename
