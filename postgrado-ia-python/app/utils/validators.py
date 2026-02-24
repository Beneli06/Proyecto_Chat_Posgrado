"""
Validators for input validation and security
"""

import os
import mimetypes
from typing import Tuple


def validate_pdf_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate that the file is a legitimate PDF.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check file exists
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    # Check file extension
    if not file_path.lower().endswith('.pdf'):
        return False, "File must have .pdf extension"
    
    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type != 'application/pdf':
        return False, "File MIME type is not PDF"
    
    # Check file size (max 50MB)
    file_size = os.path.getsize(file_path)
    if file_size > 52428800:  # 50MB
        return False, "File size exceeds 50MB limit"
    
    # Check file is not empty
    if file_size == 0:
        return False, "File is empty"
    
    return True, ""


def validate_query(query: str, max_length: int = 1000) -> Tuple[bool, str]:
    """
    Validate user query.
    
    Args:
        query: User query string
        max_length: Maximum allowed query length
        
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    # Check if query is provided
    if not query or not isinstance(query, str):
        return False, "Query must be a non-empty string"
    
    # Strip whitespace
    query = query.strip()
    
    # Check minimum length
    if len(query) < 3:
        return False, "Query must be at least 3 characters long"
    
    # Check maximum length
    if len(query) > max_length:
        return False, f"Query must not exceed {max_length} characters"
    
    return True, ""
