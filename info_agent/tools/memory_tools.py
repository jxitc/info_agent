"""
Direct LangChain Tools for Memory Operations

Simple, direct tool implementations that wrap the existing repository layer
for use with LangGraph agents. No unnecessary abstraction layers.
"""

import json
import logging
from typing import List, Optional, Dict, Any
from langchain_core.tools import tool
from ..core.repository import get_memory_service

logger = logging.getLogger(__name__)


def format_memory_result(result) -> Dict[str, Any]:
    """Format a MemorySearchResult for tool output with ranking transparency"""
    return {
        "memory_id": result.memory.id,
        "title": result.memory.title,
        "content": result.memory.content,
        "relevance_score": getattr(result, 'relevance_score', 1.0),
        "match_type": getattr(result, 'match_type', 'unknown'),
        "ranking_explanation": getattr(result, 'ranking_explanation', ''),
        "created_date": result.memory.created_at.isoformat() if hasattr(result.memory, 'created_at') and result.memory.created_at else None,
        "dynamic_fields": result.memory.dynamic_fields or {}
    }


@tool
def search_memories_structured(query: str, limit: int = 10) -> str:
    """
    Search memories using structured database queries with full-text search.
    
    Best for: Exact matches, specific terms, dates, IDs
    Performance: Fast
    
    Args:
        query: Text to search for in memory content and titles
        limit: Maximum number of results to return (1-50)
        
    Returns:
        JSON string with list of matching memories
    """
    try:
        logger.info(f"Structured search: '{query}' (limit: {limit})")
        
        memory_service = get_memory_service()
        results = memory_service.search_memories(query, limit=min(limit, 50))
        
        formatted_results = [format_memory_result(result) for result in results]
        
        logger.info(f"Found {len(formatted_results)} structured search results")
        return json.dumps({
            "method": "structured",
            "query": query,
            "count": len(formatted_results),
            "results": formatted_results
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Structured search failed: {e}")
        return json.dumps({
            "method": "structured",
            "query": query,
            "error": str(e),
            "count": 0,
            "results": []
        })


@tool
def search_memories_semantic(query: str, limit: int = 5, similarity_threshold: float = 0.7) -> str:
    """
    Search memories using semantic similarity with vector embeddings.
    
    Best for: Conceptual matches, synonyms, related topics
    Performance: Medium (requires AI processing)
    
    Args:
        query: Text to find semantically similar memories for
        limit: Maximum number of results to return (1-20)
        similarity_threshold: Minimum similarity score (0.0-1.0)
        
    Returns:
        JSON string with list of semantically similar memories
    """
    try:
        logger.info(f"Semantic search: '{query}' (limit: {limit}, threshold: {similarity_threshold})")
        
        memory_service = get_memory_service()
        results = memory_service.semantic_search_memories(query, limit=min(limit, 20))
        
        # Filter by similarity threshold
        filtered_results = []
        for result in results:
            score = getattr(result, 'relevance_score', 1.0)
            if score >= similarity_threshold:
                filtered_results.append(format_memory_result(result))
        
        logger.info(f"Found {len(filtered_results)} semantic search results (filtered from {len(results)})")
        return json.dumps({
            "method": "semantic",
            "query": query,
            "similarity_threshold": similarity_threshold,
            "count": len(filtered_results),
            "results": filtered_results
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        return json.dumps({
            "method": "semantic",
            "query": query,
            "error": str(e),
            "count": 0,
            "results": []
        })


@tool
def search_memories_hybrid(query: str, limit: int = 10) -> str:
    """
    Search memories using AI-enhanced hybrid approach combining multiple methods.
    
    Best for: Complex queries, natural language requests, comprehensive results
    Performance: Medium (includes AI query enhancement)
    
    Args:
        query: Natural language query for comprehensive memory search
        limit: Maximum number of results to return (1-50)
        
    Returns:
        JSON string with ranked results from multiple search methods
    """
    try:
        logger.info(f"Hybrid search: '{query}' (limit: {limit})")
        
        memory_service = get_memory_service()
        results = memory_service.hybrid_search_memories(query, limit=min(limit, 50))
        
        formatted_results = [format_memory_result(result) for result in results]
        
        logger.info(f"Found {len(formatted_results)} hybrid search results")
        return json.dumps({
            "method": "hybrid",
            "query": query,
            "count": len(formatted_results),
            "results": formatted_results
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Hybrid search failed: {e}")
        return json.dumps({
            "method": "hybrid", 
            "query": query,
            "error": str(e),
            "count": 0,
            "results": []
        })


@tool
def get_memory_by_id(memory_id: int) -> str:
    """
    Retrieve a specific memory by its ID.
    
    Args:
        memory_id: Unique identifier of the memory to retrieve
        
    Returns:
        JSON string with memory details or error message
    """
    try:
        logger.info(f"Getting memory by ID: {memory_id}")
        
        memory_service = get_memory_service()
        memory = memory_service.get_memory(memory_id)
        
        if memory:
            result = {
                "memory_id": memory.id,
                "title": memory.title,
                "content": memory.content,
                "created_date": memory.created_at.isoformat() if hasattr(memory, 'created_at') and memory.created_at else None,
                "updated_date": memory.updated_at.isoformat() if hasattr(memory, 'updated_at') and memory.updated_at else None,
                "dynamic_fields": memory.dynamic_fields or {},
                "word_count": len(memory.content.split()) if memory.content else 0
            }
            logger.info(f"Retrieved memory {memory_id}: '{memory.title}'")
            return json.dumps(result, indent=2)
        else:
            logger.warning(f"Memory {memory_id} not found")
            return json.dumps({
                "error": f"Memory with ID {memory_id} not found",
                "memory_id": memory_id
            })
            
    except Exception as e:
        logger.error(f"Failed to get memory {memory_id}: {e}")
        return json.dumps({
            "error": str(e),
            "memory_id": memory_id
        })


@tool
def get_recent_memories(limit: int = 20, offset: int = 0) -> str:
    """
    Get recent memories in chronological order.
    
    Args:
        limit: Maximum number of memories to return (1-50)
        offset: Number of memories to skip (for pagination)
        
    Returns:
        JSON string with list of recent memories
    """
    try:
        logger.info(f"Getting recent memories (limit: {limit}, offset: {offset})")
        
        memory_service = get_memory_service()
        memories = memory_service.list_recent_memories(limit=min(limit, 50), offset=offset)
        
        results = []
        for memory in memories:
            results.append({
                "memory_id": memory.id,
                "title": memory.title,
                "content": memory.content[:200] + "..." if len(memory.content) > 200 else memory.content,
                "created_date": memory.created_at.isoformat() if hasattr(memory, 'created_at') and memory.created_at else None,
                "dynamic_fields": memory.dynamic_fields or {},
                "word_count": len(memory.content.split()) if memory.content else 0
            })
        
        logger.info(f"Retrieved {len(results)} recent memories")
        return json.dumps({
            "count": len(results),
            "limit": limit,
            "offset": offset,
            "memories": results
        }, indent=2)
        
    except Exception as e:
        logger.error(f"Failed to get recent memories: {e}")
        return json.dumps({
            "error": str(e),
            "count": 0,
            "memories": []
        })


@tool  
def get_memory_statistics() -> str:
    """
    Get statistics about the memory system including counts and system status.
    
    Returns:
        JSON string with memory system statistics
    """
    try:
        logger.info("Getting memory statistics")
        
        memory_service = get_memory_service()
        stats = memory_service.get_service_statistics()
        
        logger.info(f"Retrieved memory statistics: {stats.get('total_memories', 0)} total memories")
        return json.dumps(stats, indent=2, default=str)
        
    except Exception as e:
        logger.error(f"Failed to get memory statistics: {e}")
        return json.dumps({
            "error": str(e),
            "total_memories": 0
        })


def get_all_memory_tools() -> List:
    """
    Get all available memory tools for binding to LangGraph agents.
    
    Returns:
        List of LangChain tools for memory operations
    """
    return [
        search_memories_structured,
        search_memories_semantic, 
        search_memories_hybrid,
        get_memory_by_id,
        get_recent_memories,
        get_memory_statistics
    ]


def get_search_tools() -> List:
    """
    Get only the search tools (subset for focused agents).
    
    Returns:
        List of search-specific tools
    """
    return [
        search_memories_structured,
        search_memories_semantic,
        search_memories_hybrid
    ]