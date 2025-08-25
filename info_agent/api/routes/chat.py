"""
Chat API routes for memory agent integration.

This module provides endpoints for real-time chat interaction with the memory agent,
supporting the ChatGPT-style web interface with RAG results display.
"""

import json
import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any, List

from info_agent.api.utils.responses import success_response, error_response
from info_agent.api.utils.validation import validate_json_body
from info_agent.cli.validators import validate_text_input
from info_agent.agents.memory_agent import create_memory_agent, MemoryAgent
from info_agent.utils.logging_config import get_logger

logger = get_logger(__name__)

# Create chat blueprint
chat_bp = Blueprint('chat', __name__)

# Global agent instance for the web server (singleton pattern)
_web_agent: MemoryAgent = None


def get_web_agent() -> MemoryAgent:
    """Get or create the singleton memory agent for web interface."""
    global _web_agent
    
    if _web_agent is None:
        logger.info("Initializing memory agent for web interface...")
        # Create agent optimized for web usage (fewer iterations for responsiveness)
        _web_agent = create_memory_agent(
            model="gpt-4o-mini", 
            max_iterations=3  # Limit iterations for web responsiveness
        )
        logger.info("Memory agent initialized successfully for web interface")
    
    return _web_agent


def format_search_results_for_frontend(search_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Format agent search results for the frontend RAG panel.
    
    Args:
        search_results: Raw search results from memory agent
        
    Returns:
        List of formatted results for frontend display
    """
    formatted_results = []
    
    for tool_name, tool_result in search_results.items():
        
        # Parse JSON string results if needed
        if isinstance(tool_result, str):
            try:
                tool_result = json.loads(tool_result)
            except json.JSONDecodeError:
                logger.warning(f"Tool '{tool_name}' returned non-JSON string: {tool_result}")
                continue
        
        # Skip error results
        if not isinstance(tool_result, dict):
            logger.warning(f"Tool '{tool_name}' returned non-dict result: {tool_result}")
            continue
            
        if "error" in tool_result:
            logger.warning(f"Tool '{tool_name}' returned error: {tool_result['error']}")
            continue
            
        # Handle different search tool result formats
        if tool_name in ["hybrid_search", "semantic_search", "database_search", 
                         "search_memories_hybrid", "search_memories_semantic", "search_memories_database",
                         "search_memories_structured"]:
            results = tool_result.get("results", [])
            logger.info(f"Tool '{tool_name}' returned {len(results)} results")
            
            for i, result in enumerate(results):
                if isinstance(result, dict):
                    # Handle both direct result format and nested format
                    memory_data = result.get("memory", result) if "memory" in result else result
                    
                    formatted_result = {
                        "memory_id": memory_data.get("memory_id") or memory_data.get("id"),
                        "title": memory_data.get("title", "Untitled Memory"),
                        "snippet": (memory_data.get("snippet") or 
                                  memory_data.get("content", ""))[:200] + ("..." if len(memory_data.get("content", "")) > 200 else ""),
                        "relevance_score": result.get("relevance_score") or result.get("score", 0.0),
                        "source": tool_name,
                        "metadata": {
                            "date": memory_data.get("created_at") or memory_data.get("date"),
                            "category": memory_data.get("category") or memory_data.get("dynamic_fields", {}).get("category"),
                            "word_count": memory_data.get("word_count"),
                        }
                    }
                    
                    # Remove None values from metadata
                    formatted_result["metadata"] = {
                        k: v for k, v in formatted_result["metadata"].items() 
                        if v is not None
                    }
                    
                    logger.info(f"Formatted result {i+1}: ID={formatted_result['memory_id']}, Score={formatted_result['relevance_score']}")
                    formatted_results.append(formatted_result)
        
        elif tool_name == "get_memory_stats":
            # Handle stats results (not memory results, but useful for context)
            logger.info(f"Skipping stats tool result")
            continue
            
        elif tool_name == "get_memories_by_ids":
            # Handle direct memory retrieval
            memories = tool_result.get("memories", [])
            logger.info(f"Tool '{tool_name}' returned {len(memories)} memories")
            
            for i, memory in enumerate(memories):
                if isinstance(memory, dict):
                    formatted_result = {
                        "memory_id": memory.get("id"),
                        "title": memory.get("title", "Untitled Memory"),
                        "snippet": memory.get("content", "")[:200] + ("..." if len(memory.get("content", "")) > 200 else ""),
                        "relevance_score": 1.0,  # Direct retrieval has perfect relevance
                        "source": "direct_retrieval",
                        "metadata": {
                            "date": memory.get("created_at"),
                            "category": memory.get("dynamic_fields", {}).get("category"),
                            "word_count": memory.get("word_count"),
                        }
                    }
                    
                    # Remove None values from metadata
                    formatted_result["metadata"] = {
                        k: v for k, v in formatted_result["metadata"].items() 
                        if v is not None
                    }
                    
                    logger.info(f"Formatted direct retrieval {i+1}: ID={formatted_result['memory_id']}")
                    formatted_results.append(formatted_result)
        else:
            # Handle unknown tool types
            logger.warning(f"Unknown tool type '{tool_name}' with result: {tool_result}")
    
    # Sort by relevance score (highest first) and limit to top 10
    formatted_results.sort(key=lambda x: x["relevance_score"], reverse=True)
    logger.info(f"Final formatted results: {len(formatted_results)} results")
    
    return formatted_results[:10]


@chat_bp.route('/chat', methods=['POST'])
def chat():
    """
    Process a chat message through the memory agent.
    
    Request Body:
        {
            "message": "What meetings did I have with Sarah?",
            "context": {...} // Optional conversation context
        }
    
    Response:
        {
            "success": true,
            "data": {
                "response": "Here are your meetings with Sarah...",
                "rag_results": [...],
                "metadata": {
                    "query": "What meetings did I have with Sarah?",
                    "operation_type": "search",
                    "iterations": 2,
                    "total_results": 4
                }
            }
        }
    """
    try:
        # Validate request
        is_valid, data, error = validate_json_body(required_fields=['message'])
        if not is_valid:
            return error_response("INVALID_REQUEST", error, status=400)
        
        # Validate message content
        try:
            message = validate_text_input(data['message'])
        except ValueError as e:
            return error_response("INVALID_REQUEST", f"Message validation failed: {str(e)}", status=400)
            
        context = data.get('context', {})  # Optional conversation context
        
        logger.info(f"Processing chat message: '{message[:100]}{'...' if len(message) > 100 else ''}'")
        
        # Get memory agent
        agent = get_web_agent()
        
        # Process query through agent
        result = agent.process_query(message)
        
        if not result.get("success", False):
            # Agent processing failed
            error_msg = result.get("error", "Agent processing failed")
            logger.error(f"Agent processing failed: {error_msg}")
            return error_response(
                "AGENT_ERROR", 
                f"Memory agent encountered an error: {error_msg}",
                status=500
            )
        
        # Format search results for frontend
        search_results = result.get("search_results", {})
        rag_results = format_search_results_for_frontend(search_results)
        logger.info(f"Formatted RAG results: {len(rag_results)} results")
        
        # Prepare response
        response_data = {
            "response": result.get("final_response", "I couldn't process your request."),
            "rag_results": rag_results,
            "metadata": {
                "query": result.get("query", message),
                "operation_type": result.get("operation_type", "search"),
                "iterations": result.get("iterations", 0),
                "total_results": len(rag_results),
                "agent_success": result.get("success", False)
            }
        }
        
        # Add context if provided (for future conversation state management)
        if context:
            response_data["metadata"]["context"] = context
        
        logger.info(f"Chat response generated: {len(response_data['response'])} chars, "
                   f"{len(rag_results)} RAG results, {result.get('iterations', 0)} iterations")
        
        return success_response(data=response_data)
        
    except ValueError as e:
        # Validation error
        logger.warning(f"Chat request validation failed: {str(e)}")
        return error_response("INVALID_REQUEST", str(e), status=400)
        
    except Exception as e:
        # Unexpected error
        logger.error(f"Unexpected error in chat endpoint: {str(e)}", exc_info=True)
        return error_response(
            "INTERNAL_ERROR", 
            "An unexpected error occurred while processing your message",
            status=500
        )


@chat_bp.route('/chat/status', methods=['GET'])
def chat_status():
    """
    Get the status of the memory agent for the chat interface.
    
    Response:
        {
            "success": true,
            "data": {
                "agent_initialized": true,
                "model": "gpt-4o-mini",
                "max_iterations": 3,
                "tools_available": 5,
                "langsmith_enabled": true
            }
        }
    """
    try:
        agent = get_web_agent()
        
        # Get agent configuration
        status_data = {
            "agent_initialized": True,
            "model": agent.model,
            "max_iterations": agent.max_iterations,
            "tools_available": len(agent.tools),
            "langsmith_enabled": agent.langsmith_enabled,
            "tool_names": [tool.name for tool in agent.tools]
        }
        
        logger.debug(f"Chat agent status: {status_data}")
        return success_response(data=status_data)
        
    except Exception as e:
        logger.error(f"Error getting chat agent status: {str(e)}", exc_info=True)
        return error_response(
            "INTERNAL_ERROR",
            "Failed to get agent status", 
            status=500
        )


@chat_bp.route('/chat/reset', methods=['POST'])  
def reset_chat():
    """
    Reset the chat agent (clear any cached state).
    This can be useful for starting a fresh conversation.
    
    Response:
        {
            "success": true,
            "data": {
                "message": "Chat agent reset successfully"
            }
        }
    """
    try:
        global _web_agent
        
        # Force recreation of agent instance
        _web_agent = None
        agent = get_web_agent()  # This will create a new instance
        
        logger.info("Chat agent reset successfully")
        return success_response(data={
            "message": "Chat agent reset successfully",
            "agent_reinitialized": True
        })
        
    except Exception as e:
        logger.error(f"Error resetting chat agent: {str(e)}", exc_info=True)
        return error_response(
            "INTERNAL_ERROR",
            "Failed to reset chat agent",
            status=500
        )