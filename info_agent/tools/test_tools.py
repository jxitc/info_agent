#!/usr/bin/env python3
"""
Test script for direct LangChain tools

Simple test to verify our simplified tools work correctly.
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from info_agent.tools.memory_tools import (
    search_memories_structured,
    search_memories_semantic, 
    search_memories_hybrid,
    get_memory_by_id,
    get_recent_memories,
    get_memory_statistics,
    get_all_memory_tools
)


def test_direct_tools():
    """Test direct LangChain tools functionality"""
    print("🧪 Testing Direct LangChain Tools")
    print("=" * 50)
    
    try:
        # Test tool listing
        print("1. Getting all memory tools...")
        tools = get_all_memory_tools()
        print(f"   ✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"      - {tool.name}: {tool.description[:60]}...")
        
        # Test memory statistics
        print("\n2. Testing memory statistics...")
        stats_result = get_memory_statistics.invoke({})
        stats = json.loads(stats_result)
        if "error" not in stats:
            print(f"   ✅ Statistics successful: {stats.get('total_memories', 0)} total memories")
        else:
            print(f"   ⚠️  Statistics error: {stats['error']}")
        
        # Test recent memories
        print("\n3. Testing recent memories...")
        recent_result = get_recent_memories.invoke({"limit": 5})
        recent = json.loads(recent_result)
        if "error" not in recent:
            print(f"   ✅ Recent memories successful: {recent['count']} memories")
            if recent['memories']:
                print(f"      Latest: {recent['memories'][0]['title']}")
        else:
            print(f"   ⚠️  Recent memories error: {recent['error']}")
        
        # Test structured search
        print("\n4. Testing structured search...")
        search_result = search_memories_structured.invoke({"query": "test", "limit": 3})
        search = json.loads(search_result)
        if "error" not in search:
            print(f"   ✅ Structured search successful: {search['count']} results")
            if search['results']:
                print(f"      First result: {search['results'][0]['title']}")
        else:
            print(f"   ⚠️  Structured search error: {search['error']}")
        
        # Test semantic search
        print("\n5. Testing semantic search...")
        semantic_result = search_memories_semantic.invoke({"query": "test", "limit": 3})
        semantic = json.loads(semantic_result)
        if "error" not in semantic:
            print(f"   ✅ Semantic search successful: {semantic['count']} results")
            if semantic['results']:
                print(f"      First result: {semantic['results'][0]['title']}")
        else:
            print(f"   ⚠️  Semantic search error: {semantic['error']}")
        
        # Test hybrid search
        print("\n6. Testing hybrid search...")
        hybrid_result = search_memories_hybrid.invoke({"query": "test", "limit": 3})
        hybrid = json.loads(hybrid_result)
        if "error" not in hybrid:
            print(f"   ✅ Hybrid search successful: {hybrid['count']} results")
            if hybrid['results']:
                print(f"      First result: {hybrid['results'][0]['title']}")
                print(f"      Match type: {hybrid['results'][0]['match_type']}")
        else:
            print(f"   ⚠️  Hybrid search error: {hybrid['error']}")
        
        # Test get by ID (if we have memories)
        if recent['count'] > 0:
            print("\n7. Testing get memory by ID...")
            memory_id = recent['memories'][0]['memory_id']
            id_result = get_memory_by_id.invoke({"memory_id": memory_id})
            id_data = json.loads(id_result)
            if "error" not in id_data:
                print(f"   ✅ Get by ID successful: {id_data['title']}")
            else:
                print(f"   ⚠️  Get by ID error: {id_data['error']}")
        
        print("\n✅ Direct tools test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Direct tools test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_direct_tools()
    sys.exit(0 if success else 1)