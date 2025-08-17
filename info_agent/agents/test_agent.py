#!/usr/bin/env python3
"""
Test script for LangGraph Memory Agent

Test the agent workflow with various query types.
"""

import sys
import os
import json

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from info_agent.agents.memory_agent import create_memory_agent, create_search_agent


def test_memory_agent():
    """Test Memory Agent functionality"""
    print("🤖 Testing LangGraph Memory Agent")
    print("=" * 50)
    
    try:
        # Create agent
        print("1. Creating Memory Agent...")
        agent = create_memory_agent()
        print("   ✅ Memory Agent created successfully")
        
        # Test queries
        test_queries = [
            "Show me my recent memories",
            "Find memories about meetings", 
            "Search for anything related to API project",
            "How many memories do I have?",
            "Get memory ID 1"
        ]
        
        for i, query in enumerate(test_queries, 2):
            print(f"\n{i}. Testing query: '{query}'")
            
            try:
                result = agent.process_query(query)
                
                if result["success"]:
                    print(f"   ✅ Query processed successfully")
                    print(f"   🔍 Operation type: {result['operation_type']}")
                    print(f"   🔄 Iterations: {result['iterations']}")
                    print(f"   💬 Response: {result['final_response'][:100]}...")
                    
                    # Show search results summary
                    if result['search_results']:
                        for tool_name, tool_result in result['search_results'].items():
                            if isinstance(tool_result, dict) and 'count' in tool_result:
                                print(f"   📊 {tool_name}: {tool_result['count']} results")
                else:
                    print(f"   ❌ Query failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Query failed with exception: {e}")
        
        print("\n✅ Memory Agent test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Memory Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_search_agent():
    """Test focused Search Agent"""
    print("\n🔍 Testing Focused Search Agent")
    print("=" * 40)
    
    try:
        # Create search agent
        print("1. Creating Search Agent...")
        search_agent = create_search_agent()
        print("   ✅ Search Agent created successfully")
        
        # Test search query
        query = "Find anything about testing or development"
        print(f"\n2. Testing search query: '{query}'")
        
        result = search_agent.process_query(query)
        
        if result["success"]:
            print(f"   ✅ Search successful")
            print(f"   🔍 Operation type: {result['operation_type']}")
            print(f"   🔄 Iterations: {result['iterations']}")
            print(f"   💬 Response: {result['final_response'][:150]}...")
        else:
            print(f"   ❌ Search failed: {result.get('error')}")
        
        print("\n✅ Search Agent test completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Search Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success1 = test_memory_agent()
    success2 = test_search_agent()
    
    overall_success = success1 and success2
    
    if overall_success:
        print("\n🎉 All agent tests passed!")
    else:
        print("\n💥 Some agent tests failed!")
    
    sys.exit(0 if overall_success else 1)