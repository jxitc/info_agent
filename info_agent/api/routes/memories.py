"""
Memory CRUD operations API endpoints.

This blueprint provides RESTful endpoints for memory operations:
- GET /memories - List memories
- GET /memories/{id} - Get specific memory
- POST /memories - Create new memory  
- DELETE /memories/{id} - Delete memory
"""

from flask import Blueprint
from typing import Dict, Any

from info_agent.utils.logging_config import get_logger
from info_agent.core.repository import get_memory_service, RepositoryError
from info_agent.ai.processor import ProcessingError
from info_agent.api.utils.responses import (
    success_response, 
    error_response, 
    created_response,
    not_found_response,
    validation_error_response
)
from info_agent.api.utils.validation import (
    validate_memory_create_request,
    validate_list_request,
    validate_memory_id
)

# Create blueprint
memories_bp = Blueprint('memories', __name__)
logger = get_logger(__name__)


@memories_bp.route('/memories', methods=['GET'])
def list_memories():
    """
    List recent memories.
    
    Query Parameters:
        limit (int): Number of memories to return (default: 20, max: 100)
        offset (int): Number of memories to skip (default: 0)
    
    Returns:
        JSON response with list of memories
    """
    # Validate request parameters
    is_valid, params, error = validate_list_request()
    if not is_valid:
        return validation_error_response("limit/offset", "range", error)
    
    try:
        # Get memory service
        memory_service = get_memory_service()
        
        # List memories using repository
        memories = memory_service.list_recent_memories(
            limit=params['limit'],
            offset=params['offset']
        )
        
        # Get total count for pagination info
        total_memories = memory_service.get_memory_count()
        
        # Convert memories to API format
        memory_list = []
        for memory in memories:
            memory_dict = {
                "id": memory.id,
                "title": memory.title,
                "content": memory.content,
                "word_count": memory.word_count,
                "created_at": memory.created_at.isoformat() + 'Z',
                "updated_at": memory.updated_at.isoformat() + 'Z',
                "dynamic_fields": memory.dynamic_fields
            }
            memory_list.append(memory_dict)
        
        # Prepare response data
        response_data = {
            "memories": memory_list,
            "total": total_memories,
            "has_more": (params['offset'] + len(memory_list)) < total_memories
        }
        
        logger.info(f"Listed {len(memory_list)} memories (offset: {params['offset']}, limit: {params['limit']})")
        return success_response(data=response_data)
        
    except RepositoryError as e:
        logger.error(f"Repository error in list_memories: {e}")
        return error_response("DATABASE_ERROR", str(e), status=500)
    except Exception as e:
        logger.error(f"Unexpected error in list_memories: {e}")
        return error_response("INTERNAL_ERROR", "Internal server error", status=500)


@memories_bp.route('/memories/<memory_id>', methods=['GET'])
def get_memory(memory_id):
    """
    Get specific memory details.
    
    Path Parameters:
        memory_id (int): Memory ID
    
    Returns:
        JSON response with memory details
    """
    # Validate memory ID
    is_valid, validated_id, error = validate_memory_id(memory_id)
    if not is_valid:
        return validation_error_response("memory_id", "format", error)
    
    try:
        # Get memory service
        memory_service = get_memory_service()
        
        # Get memory by ID
        memory = memory_service.get_memory(validated_id)
        
        if not memory:
            return not_found_response("Memory", validated_id)
        
        # Convert memory to API format
        memory_data = {
            "id": memory.id,
            "title": memory.title,
            "content": memory.content,
            "word_count": memory.word_count,
            "content_hash": memory.content_hash,
            "version": memory.version,
            "created_at": memory.created_at.isoformat() + 'Z',
            "updated_at": memory.updated_at.isoformat() + 'Z',
            "dynamic_fields": memory.dynamic_fields
        }
        
        logger.info(f"Retrieved memory {validated_id}")
        return success_response(data=memory_data)
        
    except RepositoryError as e:
        logger.error(f"Repository error in get_memory: {e}")
        return error_response("DATABASE_ERROR", str(e), status=500)
    except Exception as e:
        logger.error(f"Unexpected error in get_memory: {e}")
        return error_response("INTERNAL_ERROR", "Internal server error", status=500)


@memories_bp.route('/memories', methods=['POST'])
def create_memory():
    """
    Create a new memory.
    
    Request Body:
        {
            "content": "Memory content text (required)",
            "title": "Optional custom title"
        }
    
    Returns:
        JSON response with created memory details
    """
    # Validate request body
    is_valid, data, error = validate_memory_create_request()
    if not is_valid:
        return validation_error_response("content", "required", error)
    
    try:
        # Get memory service
        memory_service = get_memory_service()
        
        # Create memory with AI processing
        logger.info(f"Creating memory with content length: {len(data['content'])}")
        
        memory = memory_service.add_memory(
            content=data['content'],
            title=data['title']  # None if not provided
        )
        
        # Convert memory to API format
        memory_data = {
            "id": memory.id,
            "title": memory.title,
            "content": memory.content,
            "word_count": memory.word_count,
            "created_at": memory.created_at.isoformat() + 'Z',
            "dynamic_fields": memory.dynamic_fields
        }
        
        logger.info(f"Created memory {memory.id} with title: {memory.title}")
        return created_response(
            data=memory_data,
            message="Memory created successfully"
        )
        
    except ProcessingError as e:
        logger.error(f"AI processing error in create_memory: {e}")
        return error_response("AI_SERVICE_ERROR", str(e), status=503)
    except RepositoryError as e:
        logger.error(f"Repository error in create_memory: {e}")
        return error_response("DATABASE_ERROR", str(e), status=500)
    except Exception as e:
        logger.error(f"Unexpected error in create_memory: {e}")
        return error_response("INTERNAL_ERROR", "Internal server error", status=500)


@memories_bp.route('/memories/<memory_id>', methods=['DELETE'])
def delete_memory(memory_id):
    """
    Delete a memory.
    
    Path Parameters:
        memory_id (int): Memory ID to delete
    
    Returns:
        JSON response confirming deletion
    """
    # Validate memory ID
    is_valid, validated_id, error = validate_memory_id(memory_id)
    if not is_valid:
        return validation_error_response("memory_id", "format", error)
    
    try:
        # Get memory service
        memory_service = get_memory_service()
        
        # Check if memory exists first
        memory = memory_service.get_memory(validated_id)
        if not memory:
            return not_found_response("Memory", validated_id)
        
        # Store title for response
        deleted_title = memory.title
        
        # Delete memory
        success = memory_service.delete_memory(validated_id)
        
        if not success:
            return error_response("DELETE_FAILED", f"Failed to delete memory {validated_id}", status=500)
        
        # Prepare response data
        response_data = {
            "deleted_id": validated_id,
            "title": deleted_title
        }
        
        logger.info(f"Deleted memory {validated_id}: {deleted_title}")
        return success_response(
            data=response_data,
            message="Memory deleted successfully"
        )
        
    except RepositoryError as e:
        logger.error(f"Repository error in delete_memory: {e}")
        return error_response("DATABASE_ERROR", str(e), status=500)
    except Exception as e:
        logger.error(f"Unexpected error in delete_memory: {e}")
        return error_response("INTERNAL_ERROR", "Internal server error", status=500)