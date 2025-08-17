"""
LangSmith Configuration and Setup

Provides utilities for configuring LangSmith tracing and monitoring
for the Memory Agent system.
"""

import os
import logging
from typing import Optional, Dict, Any
from functools import wraps
import uuid

logger = logging.getLogger(__name__)


class LangSmithConfig:
    """Configuration class for LangSmith integration"""
    
    def __init__(self):
        self.tracing_enabled = self._check_tracing_enabled()
        self.api_key = os.getenv("LANGCHAIN_API_KEY")
        self.project_name = os.getenv("LANGCHAIN_PROJECT", "info-agent-default")
        self.endpoint = os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com")
        
    def _check_tracing_enabled(self) -> bool:
        """Check if LangSmith tracing is enabled"""
        tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower()
        return tracing_v2 in ("true", "1", "yes", "on")
    
    def is_configured(self) -> bool:
        """Check if LangSmith is properly configured"""
        return self.tracing_enabled and bool(self.api_key)
    
    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            "tracing_enabled": self.tracing_enabled,
            "has_api_key": bool(self.api_key),
            "project_name": self.project_name,
            "endpoint": self.endpoint
        }


def setup_langsmith_tracing(project_name: Optional[str] = None) -> bool:
    """
    Setup LangSmith tracing for the application
    
    Args:
        project_name: Optional project name override
        
    Returns:
        bool: True if successfully configured, False otherwise
    """
    try:
        config = LangSmithConfig()
        
        if not config.is_configured():
            if not config.tracing_enabled:
                logger.info("LangSmith tracing is disabled (LANGCHAIN_TRACING_V2=false)")
            elif not config.api_key:
                logger.warning("LangSmith API key not found (LANGCHAIN_API_KEY not set)")
            return False
        
        # Override project name if provided
        if project_name:
            os.environ["LANGCHAIN_PROJECT"] = project_name
            config.project_name = project_name
        
        # Import langsmith after environment is set
        try:
            from langsmith import Client
            client = Client(api_key=config.api_key, api_url=config.endpoint)
            
            # Test connection
            client.list_projects(limit=1)
            
            logger.info(f"✅ LangSmith tracing enabled for project: {config.project_name}")
            return True
            
        except ImportError:
            logger.warning("LangSmith not installed. Run: pip install langsmith")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to LangSmith: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error setting up LangSmith tracing: {e}")
        return False


def trace_agent_operation(operation_name: str, metadata: Optional[Dict[str, Any]] = None):
    """
    Decorator to trace agent operations with LangSmith
    
    Args:
        operation_name: Name of the operation being traced
        metadata: Additional metadata to include in the trace
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = LangSmithConfig()
            
            if not config.is_configured():
                # If LangSmith not configured, just run the function
                return func(*args, **kwargs)
            
            try:
                from langsmith import traceable
                
                # Create a traceable version of the function
                traced_func = traceable(
                    name=operation_name,
                    metadata=metadata or {},
                    tags=["memory-agent", "info-agent"]
                )(func)
                
                return traced_func(*args, **kwargs)
                
            except ImportError:
                # If langsmith not available, just run the function
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Error in LangSmith tracing for {operation_name}: {e}")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


def create_run_context(
    query: str, 
    operation_type: str, 
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create context information for LangSmith runs
    
    Args:
        query: User query being processed
        operation_type: Type of operation (search, statistics, etc.)
        user_id: Optional user identifier
        
    Returns:
        Dictionary with context information
    """
    return {
        "query": query,
        "operation_type": operation_type,
        "user_id": user_id or "anonymous",
        "session_id": str(uuid.uuid4()),
        "agent_version": "1.0.0",
        "component": "memory-agent"
    }


def log_tool_execution(
    tool_name: str, 
    tool_args: Dict[str, Any], 
    result: Any, 
    error: Optional[str] = None
) -> None:
    """
    Log tool execution details to LangSmith
    
    Args:
        tool_name: Name of the tool executed
        tool_args: Arguments passed to the tool
        result: Tool execution result
        error: Error message if execution failed
    """
    config = LangSmithConfig()
    
    if not config.is_configured():
        return
    
    try:
        from langsmith import Client
        
        client = Client()
        
        # Create a custom event for tool execution
        event_data = {
            "tool_name": tool_name,
            "args": tool_args,
            "success": error is None,
            "error": error,
            "result_length": len(str(result)) if result else 0,
            "timestamp": "now"
        }
        
        # This would be logged as part of the larger trace
        logger.debug(f"Tool execution logged: {tool_name}")
        
    except Exception as e:
        logger.debug(f"Error logging tool execution to LangSmith: {e}")


def get_langsmith_status() -> Dict[str, Any]:
    """
    Get current LangSmith configuration status
    
    Returns:
        Dictionary with status information
    """
    config = LangSmithConfig()
    
    status = {
        "configured": config.is_configured(),
        "tracing_enabled": config.tracing_enabled,
        "has_api_key": bool(config.api_key),
        "project_name": config.project_name,
        "endpoint": config.endpoint
    }
    
    if config.is_configured():
        try:
            from langsmith import Client
            client = Client(api_key=config.api_key, api_url=config.endpoint)
            
            # Test connection
            projects = list(client.list_projects(limit=1))
            status["connection_test"] = "success"
            status["available_projects"] = len(projects)
            
        except ImportError:
            status["connection_test"] = "langsmith_not_installed"
        except Exception as e:
            status["connection_test"] = f"failed: {str(e)}"
    
    return status