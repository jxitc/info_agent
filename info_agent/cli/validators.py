"""
Input validation utilities for CLI commands.

This module provides validation functions and custom Click parameter types
for ensuring proper input handling across CLI commands.
"""

import click
import re
from pathlib import Path
from typing import Any, Optional


class MemoryIdType(click.ParamType):
    """Custom Click parameter type for memory IDs."""
    
    name = "memory_id"
    
    def convert(self, value: Any, param: Optional[click.Parameter], ctx: Optional[click.Context]) -> int:
        """Convert and validate memory ID input."""
        if isinstance(value, int):
            return value
        
        try:
            memory_id = int(value)
            if memory_id <= 0:
                self.fail(f"Memory ID must be a positive integer, got {value}", param, ctx)
            return memory_id
        except ValueError:
            self.fail(f"Memory ID must be an integer, got {value}", param, ctx)




def validate_text_input(text: str) -> str:
    """
    Validate text input for memory content.
    
    This validator ensures the input text is appropriate for storing as a memory:
    - Removes leading/trailing whitespace while preserving internal formatting
    - Checks for minimum length (not empty)
    - Enforces maximum length limit for processing efficiency
    - Prevents null bytes that could cause database issues
    
    Args:
        text: Input text to validate (memory content)
        
    Returns:
        Cleaned and validated text ready for storage
        
    Raises:
        click.BadParameter: If text is invalid (empty, too long, contains null bytes)
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove leading/trailing whitespace but preserve internal formatting
    text = text.strip()
    
    # Check minimum length
    if len(text) < 1:
        raise click.BadParameter("Text cannot be empty")
    
    # Check maximum length (reasonable limit for processing)
    if len(text) > 50000:  # ~50KB of text
        raise click.BadParameter(f"Text is too long ({len(text)} characters). Maximum is 50,000 characters.")
    
    # Check for null bytes (can cause issues in databases)
    if '\x00' in text:
        raise click.BadParameter("Text contains null bytes which are not allowed")
    
    return text


def validate_search_query(query: str) -> str:
    """
    Validate search query input.
    
    Args:
        query: Search query to validate
        
    Returns:
        Cleaned and validated query
        
    Raises:
        click.BadParameter: If query is invalid
    """
    if not isinstance(query, str):
        query = str(query)
    
    query = query.strip()
    
    # Check minimum length
    if len(query) < 1:
        raise click.BadParameter("Search query cannot be empty")
    
    # Check maximum length
    if len(query) > 1000:
        raise click.BadParameter(f"Search query too long ({len(query)} characters). Maximum is 1,000 characters.")
    
    return query


def validate_limit(limit: int, min_value: int = 1, max_value: int = 1000) -> int:
    """
    Validate limit parameter for list operations.
    
    Args:
        limit: Limit value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Validated limit
        
    Raises:
        click.BadParameter: If limit is invalid
    """
    if not isinstance(limit, int):
        try:
            limit = int(limit)
        except (ValueError, TypeError):
            raise click.BadParameter(f"Limit must be an integer, got {type(limit).__name__}")
    
    if limit < min_value:
        raise click.BadParameter(f"Limit must be at least {min_value}, got {limit}")
    
    if limit > max_value:
        raise click.BadParameter(f"Limit must be no more than {max_value}, got {limit}")
    
    return limit




# Custom parameter types for use in CLI commands
MEMORY_ID = MemoryIdType()
