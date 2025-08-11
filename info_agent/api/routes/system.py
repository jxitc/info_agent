"""
System status and utility API endpoints.

This blueprint provides system information and utility endpoints:
- GET /status - System health and status information
"""

import platform
import sys
from flask import Blueprint

from info_agent.utils.logging_config import get_logger
from info_agent.core.repository import get_memory_service, RepositoryError
from info_agent.core.vector_store import VectorStore, VectorStoreConfig
from info_agent.ai.client import OpenAIClient
from info_agent.api.utils.responses import success_response, error_response

# Create blueprint
system_bp = Blueprint('system', __name__)
logger = get_logger(__name__)


@system_bp.route('/status', methods=['GET'])
def get_system_status():
    """
    Get comprehensive system status information.
    
    Returns:
        JSON response with system health and service status
    """
    try:
        status_data = {
            "version": "0.1.0",
            "python_version": platform.python_version(),
            "platform": platform.system(),
            "services": {}
        }
        
        # Check database service
        try:
            memory_service = get_memory_service()
            total_memories = memory_service.get_memory_count()
            
            # Get database file size (approximate)
            database_size_mb = 0.1  # TODO: Calculate actual database size
            
            status_data["services"]["database"] = {
                "status": "connected",
                "total_memories": total_memories,
                "database_size_mb": database_size_mb
            }
            logger.debug("Database service: OK")
            
        except Exception as e:
            status_data["services"]["database"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"Database service error: {e}")
        
        # Check vector store service
        try:
            vector_config = VectorStoreConfig()
            vector_store = VectorStore(vector_config)
            
            # Get document count using vector store stats
            vector_stats = vector_store.get_collection_stats()
            document_count = vector_stats.get('total_documents', 0)
            
            status_data["services"]["vector_store"] = {
                "status": "available",
                "document_count": document_count,
                "collection_name": vector_config.collection_name
            }
            logger.debug("Vector store service: OK")
            
        except Exception as e:
            status_data["services"]["vector_store"] = {
                "status": "error", 
                "error": str(e)
            }
            logger.error(f"Vector store service error: {e}")
        
        # Check AI services
        try:
            ai_client = OpenAIClient()
            
            # Test connection by getting available models (lightweight operation)
            models = ai_client.get_available_models()
            default_model = ai_client.default_model
            
            status_data["services"]["ai_services"] = {
                "status": "available",
                "model": default_model,
                "available_models": len(models) if models else 0
            }
            logger.debug("AI services: OK")
            
        except Exception as e:
            status_data["services"]["ai_services"] = {
                "status": "error",
                "error": str(e)
            }
            logger.error(f"AI services error: {e}")
        
        # Determine overall system health
        service_statuses = [service.get("status") for service in status_data["services"].values()]
        all_healthy = all(status == "connected" or status == "available" for status in service_statuses)
        
        status_data["overall_status"] = "healthy" if all_healthy else "degraded"
        
        logger.info(f"System status check completed: {status_data['overall_status']}")
        return success_response(data=status_data)
        
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        return error_response("SYSTEM_ERROR", "Failed to get system status", status=500)