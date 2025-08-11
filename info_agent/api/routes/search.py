"""
Search API endpoints for Info Agent.

This blueprint provides search functionality through HTTP endpoints:
- GET /search - Search memories using natural language
"""

from flask import Blueprint

from info_agent.utils.logging_config import get_logger
from info_agent.core.repository import get_memory_service, RepositoryError
from info_agent.ai.processor import ProcessingError
from info_agent.api.utils.responses import (
    success_response,
    error_response,
    validation_error_response
)
from info_agent.api.utils.validation import validate_search_request

# Create blueprint
search_bp = Blueprint('search', __name__)
logger = get_logger(__name__)


@search_bp.route('/search', methods=['GET'])
def search_memories():
    """
    Search for memories using natural language query.
    
    Query Parameters:
        q (str): Search query (required)
        limit (int): Maximum number of results (default: 10, max: 50)
    
    Returns:
        JSON response with search results
    """
    # Validate request parameters
    is_valid, params, error = validate_search_request()
    if not is_valid:
        return validation_error_response("query", "required", error)
    
    try:
        # Get memory service
        memory_service = get_memory_service()
        
        logger.info(f"Searching for: '{params['query']}' (limit: {params['limit']})")
        
        # Perform hybrid search (semantic + structured)
        search_results = memory_service.hybrid_search_memories(
            query=params['query'],
            limit=params['limit']
        )
        
        # Convert search results to API format
        results_list = []
        for result in search_results:
            result_dict = {
                "memory_id": result.memory_id,
                "title": result.title,
                "snippet": result.snippet,
                "relevance_score": round(result.relevance_score, 3) if result.relevance_score else None,
                "match_type": getattr(result, 'search_type', 'hybrid')
            }
            results_list.append(result_dict)
        
        # Prepare response data
        response_data = {
            "query": params['query'],
            "results": results_list,
            "total_found": len(results_list),
            "search_time_ms": 0  # TODO: Add timing information
        }
        
        logger.info(f"Search completed: found {len(results_list)} results for '{params['query']}'")
        return success_response(data=response_data)
        
    except ProcessingError as e:
        logger.error(f"AI processing error during search: {e}")
        return error_response("AI_SERVICE_ERROR", str(e), status=503)
    except RepositoryError as e:
        logger.error(f"Repository error during search: {e}")
        return error_response("DATABASE_ERROR", str(e), status=500)
    except Exception as e:
        logger.error(f"Unexpected error during search: {e}")
        return error_response("SEARCH_ERROR", "Search operation failed", status=500)