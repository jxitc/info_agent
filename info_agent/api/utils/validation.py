"""
Request validation utilities for the Info Agent API.

This module provides validation functions for API request parameters,
reusing validation logic from the CLI module where possible.
"""

from typing import Any, Dict, Optional, Tuple
from flask import request

from info_agent.cli.validators import (
    validate_text_input,
    validate_search_query,
    validate_limit
)


def validate_json_body(required_fields: Optional[list] = None) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate JSON request body and extract required fields.
    
    Args:
        required_fields: List of required field names
    
    Returns:
        Tuple of (is_valid, data, error_message)
    """
    if not request.is_json:
        return False, {}, "Request must be JSON"
    
    try:
        data = request.get_json()
    except Exception as e:
        return False, {}, f"Invalid JSON: {str(e)}"
    
    if data is None:
        return False, {}, "Request body cannot be empty"
    
    # Check required fields
    if required_fields:
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return False, {}, f"Missing required fields: {', '.join(missing_fields)}"
    
    return True, data, None


def validate_memory_create_request() -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate memory creation request body.
    
    Returns:
        Tuple of (is_valid, validated_data, error_message)
    """
    is_valid, data, error = validate_json_body(required_fields=['content'])
    if not is_valid:
        return False, {}, error
    
    try:
        # Validate content using CLI validator
        validated_content = validate_text_input(data['content'])
        
        # Optional title validation
        validated_title = None
        if 'title' in data and data['title']:
            validated_title = validate_text_input(data['title'])
        
        validated_data = {
            'content': validated_content,
            'title': validated_title
        }
        
        return True, validated_data, None
        
    except ValueError as e:
        return False, {}, str(e)


def validate_search_request() -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate search request parameters.
    
    Returns:
        Tuple of (is_valid, validated_params, error_message)
    """
    try:
        # Get query parameter
        query = request.args.get('q', '').strip()
        if not query:
            return False, {}, "Query parameter 'q' is required"
        
        validated_query = validate_search_query(query)
        
        # Get and validate limit parameter
        limit = request.args.get('limit', '10')
        try:
            limit_int = int(limit)
            validated_limit = validate_limit(limit_int, min_value=1, max_value=50)
        except (ValueError, TypeError):
            return False, {}, "Limit parameter must be a valid integer"
        
        validated_params = {
            'query': validated_query,
            'limit': validated_limit
        }
        
        return True, validated_params, None
        
    except ValueError as e:
        return False, {}, str(e)


def validate_list_request() -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Validate memory list request parameters.
    
    Returns:
        Tuple of (is_valid, validated_params, error_message)
    """
    try:
        # Get and validate limit parameter
        limit = request.args.get('limit', '20')
        try:
            limit_int = int(limit)
            validated_limit = validate_limit(limit_int, min_value=1, max_value=100)
        except (ValueError, TypeError):
            return False, {}, "Limit parameter must be a valid integer between 1 and 100"
        
        # Get and validate offset parameter
        offset = request.args.get('offset', '0')
        try:
            offset_int = int(offset)
            if offset_int < 0:
                return False, {}, "Offset parameter must be non-negative"
            validated_offset = offset_int
        except (ValueError, TypeError):
            return False, {}, "Offset parameter must be a valid integer"
        
        validated_params = {
            'limit': validated_limit,
            'offset': validated_offset
        }
        
        return True, validated_params, None
        
    except Exception as e:
        return False, {}, str(e)


def validate_memory_id(memory_id: str) -> Tuple[bool, int, Optional[str]]:
    """
    Validate memory ID parameter.
    
    Args:
        memory_id: Memory ID as string
    
    Returns:
        Tuple of (is_valid, validated_id, error_message)
    """
    try:
        validated_id = int(memory_id)
        if validated_id <= 0:
            return False, 0, "Memory ID must be a positive integer"
        return True, validated_id, None
    except (ValueError, TypeError):
        return False, 0, "Memory ID must be a valid integer"