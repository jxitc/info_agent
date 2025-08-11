"""
Standard JSON response utilities for the Info Agent API.

This module provides consistent response formatting for success and error cases,
following the API specification format.
"""

from flask import jsonify
from typing import Any, Dict, Optional, Union


def success_response(data: Optional[Any] = None, message: Optional[str] = None, status: int = 200):
    """
    Create a standardized success response.
    
    Args:
        data: Response data to include
        message: Optional success message
        status: HTTP status code (default: 200)
    
    Returns:
        Flask JSON response with standard format
    """
    response = {"success": True}
    
    if data is not None:
        response["data"] = data
    
    if message:
        response["message"] = message
    
    return jsonify(response), status


def error_response(
    code: str, 
    message: str, 
    details: Optional[Dict[str, Any]] = None, 
    status: int = 400
):
    """
    Create a standardized error response.
    
    Args:
        code: Error code identifier (e.g., "MEMORY_NOT_FOUND")
        message: Human-readable error message
        details: Optional additional error details
        status: HTTP status code (default: 400)
    
    Returns:
        Flask JSON response with standard error format
    """
    response = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "details": details or {}
        }
    }
    
    return jsonify(response), status


def created_response(data: Any, message: Optional[str] = None):
    """
    Create a standardized 201 Created response.
    
    Args:
        data: Created resource data
        message: Optional creation message
    
    Returns:
        Flask JSON response with 201 status
    """
    return success_response(data=data, message=message, status=201)


def validation_error_response(field: str, constraint: str, message: str):
    """
    Create a standardized validation error response.
    
    Args:
        field: Field name that failed validation
        constraint: Validation constraint that was violated
        message: Human-readable error message
    
    Returns:
        Flask JSON response with 422 status
    """
    details = {
        "field": field,
        "constraint": constraint
    }
    
    return error_response(
        code="VALIDATION_ERROR",
        message=message,
        details=details,
        status=422
    )


def not_found_response(resource_type: str, resource_id: Union[str, int]):
    """
    Create a standardized 404 Not Found response.
    
    Args:
        resource_type: Type of resource (e.g., "Memory")
        resource_id: ID of the resource that wasn't found
    
    Returns:
        Flask JSON response with 404 status
    """
    return error_response(
        code=f"{resource_type.upper()}_NOT_FOUND",
        message=f"{resource_type} with ID {resource_id} not found",
        status=404
    )