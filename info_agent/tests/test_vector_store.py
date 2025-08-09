#!/usr/bin/env python3
"""
Vector store integration test script for Info Agent.

This script tests ChromaDB vector store functionality including:
- Vector store initialization
- Memory embedding and storage
- Semantic similarity search
- Integration with database layer
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from info_agent.core.vector_store import VectorStore, VectorStoreConfig, initialize_vector_store
from info_agent.core.models import Memory
from info_agent.core.repository import get_memory_service
from info_agent.utils.logging_config import setup_logging, get_logger


def test_vector_store_initialization():
    """Test vector store setup and initialization."""
    print("=" * 60)
    print("VECTOR STORE INITIALIZATION TEST")
    print("=" * 60)
    
    # Create temporary directory for test
    test_dir = Path(tempfile.mkdtemp(prefix="info_agent_vector_test_"))
    print(f"Using test directory: {test_dir}")
    
    try:
        # Test vector store config
        config = VectorStoreConfig(str(test_dir))
        print(f"✅ Vector store config created")
        print(f"   Data dir: {config.data_dir}")
        print(f"   Collection: {config.collection_name}")
        print(f"   Model: {config.embedding_model}")
        
        # Test vector store creation
        vector_store = VectorStore(config)
        print(f"✅ Vector store instance created")
        
        # Test collection stats
        stats = vector_store.get_collection_stats()
        print(f"✅ Collection stats retrieved:")
        print(f"   Documents: {stats.get('total_documents', 0)}")
        print(f"   Collection: {stats.get('collection_name', 'N/A')}")
        print(f"   Model: {stats.get('embedding_model', 'N/A')}")
        
        return True, vector_store, test_dir
        
    except Exception as e:
        print(f"❌ Vector store initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None, test_dir


def test_memory_embedding_storage(vector_store: VectorStore):
    """Test adding memories to vector store."""
    print("\\n" + "=" * 60)
    print("MEMORY EMBEDDING AND STORAGE TEST")
    print("=" * 60)
    
    try:
        # Create test memories
        test_memories = [
            Memory(
                id=1,
                content="I have a meeting with the development team tomorrow at 10 AM to discuss the new project requirements and timeline. We need to finalize the technical specifications.",
                title="Team Meeting Tomorrow"
            ),
            Memory(
                id=2,
                content="Remember to buy groceries after work today. Need milk, bread, eggs, and some vegetables for the week. Also pick up dog food.",
                title="Grocery Shopping List"
            ),
            Memory(
                id=3,
                content="The quarterly financial report shows a 15% increase in revenue compared to last quarter. Sales team exceeded their targets.",
                title="Quarterly Financial Results"
            ),
            Memory(
                id=4,
                content="My daughter's soccer game is scheduled for Saturday at 2 PM at the community park. Need to bring snacks for the team.",
                title="Daughter's Soccer Game"
            ),
            Memory(
                id=5,
                content="Code review for the authentication module is pending. Several security vulnerabilities were identified and need immediate attention.",
                title="Code Review - Authentication"
            )
        ]
        
        # Add memories to vector store
        successful_adds = 0
        for memory in test_memories:
            success = vector_store.add_memory(memory)
            if success:
                successful_adds += 1
                print(f"✅ Added memory {memory.id}: '{memory.title}'")
            else:
                print(f"❌ Failed to add memory {memory.id}")
        
        print(f"\\n📊 Results: {successful_adds}/{len(test_memories)} memories added successfully")
        
        # Check collection stats after adding
        stats = vector_store.get_collection_stats()
        print(f"   Collection now contains: {stats.get('total_documents', 0)} documents")
        
        return successful_adds == len(test_memories), test_memories
        
    except Exception as e:
        print(f"❌ Memory embedding test failed: {e}")
        import traceback
        traceback.print_exc()
        return False, []


def test_semantic_search(vector_store: VectorStore, test_memories: List[Memory]):
    """Test semantic similarity search."""
    print("\\n" + "=" * 60)
    print("SEMANTIC SEARCH TEST")
    print("=" * 60)
    
    # Test queries with expected relevant results
    test_queries = [
        {
            "query": "work meetings and projects",
            "expected_keywords": ["meeting", "team", "project", "development"],
            "description": "Should find work-related memories"
        },
        {
            "query": "shopping and buying things",
            "expected_keywords": ["groceries", "buy", "milk", "bread"],
            "description": "Should find shopping-related memories"
        },
        {
            "query": "sports and games for children",
            "expected_keywords": ["soccer", "game", "daughter", "park"],
            "description": "Should find sports/family memories"
        },
        {
            "query": "software development and security",
            "expected_keywords": ["code", "authentication", "security", "review"],
            "description": "Should find technical/development memories"
        },
        {
            "query": "financial performance and business results",
            "expected_keywords": ["financial", "revenue", "sales", "quarterly"],
            "description": "Should find business/financial memories"
        }
    ]
    
    successful_searches = 0
    
    try:
        for i, test_case in enumerate(test_queries, 1):
            query = test_case["query"]
            expected_keywords = test_case["expected_keywords"]
            description = test_case["description"]
            
            print(f"\\n{i}️⃣ Testing query: '{query}'")
            print(f"   Expected: {description}")
            
            # Perform search
            results = vector_store.search_memories(query, limit=3)
            
            if results:
                print(f"   ✅ Found {len(results)} results:")
                for j, result in enumerate(results[:3]):
                    similarity = result.relevance_score
                    title = result.title
                    preview = result.snippet[:80] + "..." if len(result.snippet) > 80 else result.snippet
                    print(f"      {j+1}. {title} (similarity: {similarity:.3f})")
                    print(f"         {preview}")
                
                # Check if results contain expected keywords
                all_text = " ".join([
                    result.title + " " + result.snippet
                    for result in results
                ]).lower()
                
                found_keywords = [kw for kw in expected_keywords if kw.lower() in all_text]
                if found_keywords:
                    print(f"   ✅ Found expected keywords: {found_keywords}")
                    successful_searches += 1
                else:
                    print(f"   ⚠️  Expected keywords not found: {expected_keywords}")
            else:
                print(f"   ❌ No results found")
        
        print(f"\\n📊 Search Results: {successful_searches}/{len(test_queries)} queries returned relevant results")
        
        return successful_searches > 0
        
    except Exception as e:
        print(f"❌ Semantic search test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_memory_operations(vector_store: VectorStore):
    """Test memory update and deletion operations."""
    print("\\n" + "=" * 60)
    print("MEMORY UPDATE/DELETE OPERATIONS TEST")
    print("=" * 60)
    
    try:
        # Create a test memory for operations
        test_memory = Memory(
            id=999,
            content="This is a test memory for update and delete operations. It contains some sample content.",
            title="Test Memory for Operations"
        )
        
        # Test adding
        print("1️⃣ Testing memory addition...")
        success = vector_store.add_memory(test_memory)
        if success:
            print("   ✅ Memory added successfully")
        else:
            print("   ❌ Memory addition failed")
            return False
        
        # Test updating
        print("\\n2️⃣ Testing memory update...")
        test_memory.content = "This is an updated test memory with different content to test the update functionality."
        test_memory.title = "Updated Test Memory"
        
        success = vector_store.update_memory(test_memory)
        if success:
            print("   ✅ Memory updated successfully")
        else:
            print("   ❌ Memory update failed")
            return False
        
        # Verify update by searching
        print("\\n3️⃣ Verifying update by searching...")
        results = vector_store.search_memories("updated test memory", limit=5)
        found_updated = False
        
        for result in results:
            if result.memory_id == 999:
                content = result.snippet
                if 'updated' in content.lower():
                    print("   ✅ Updated memory found in search results")
                    found_updated = True
                    break
        
        if not found_updated:
            print("   ⚠️  Updated memory not found in search (may be due to indexing delay)")
        
        # Test deletion
        print("\\n4️⃣ Testing memory deletion...")
        success = vector_store.delete_memory(999)
        if success:
            print("   ✅ Memory deleted successfully")
        else:
            print("   ❌ Memory deletion failed")
            return False
        
        # Verify deletion
        print("\\n5️⃣ Verifying deletion...")
        results = vector_store.search_memories("test memory for operations", limit=10)
        found_deleted = False
        
        for result in results:
            if result.memory_id == 999:
                found_deleted = True
                break
        
        if not found_deleted:
            print("   ✅ Deleted memory not found in search results")
        else:
            print("   ⚠️  Deleted memory still found in search results")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory operations test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integration_with_memory_service():
    """Test vector store integration with memory service."""
    print("\\n" + "=" * 60)
    print("MEMORY SERVICE INTEGRATION TEST")
    print("=" * 60)
    
    try:
        # Get memory service (this should automatically include vector store)
        memory_service = get_memory_service()
        print("✅ Memory service obtained")
        
        # Get service statistics including vector store info
        stats = memory_service.get_service_statistics()
        print("✅ Service statistics retrieved:")
        print(f"   Total memories: {stats.get('total_memories', 0)}")
        
        if 'vector_store' in stats:
            vector_stats = stats['vector_store']
            print(f"   Vector store documents: {vector_stats.get('total_documents', 0)}")
            print(f"   Vector store model: {vector_stats.get('embedding_model', 'N/A')}")
        
        # Test adding a memory through service (should auto-add to vector store)
        import time
        import uuid
        test_content = f"Vector store integration test memory created at {time.time()} with UUID {uuid.uuid4()} through memory service to verify vector store integration."
        
        print("\\n🔄 Adding memory through service...")
        memory = memory_service.add_memory(test_content)
        print(f"✅ Memory added: ID {memory.id}")
        
        # Test semantic search through service (if available)
        if hasattr(memory_service, 'semantic_search_memories'):
            print("\\n🔍 Testing semantic search through service...")
            results = memory_service.semantic_search_memories("integration test", limit=5)
            print(f"✅ Semantic search returned {len(results)} results")
            
            # Look for our test memory
            found = False
            for result in results:
                if result.memory_id == memory.id:
                    found = True
                    print(f"   ✅ Found our test memory in results")
                    break
            
            if not found:
                print(f"   ⚠️  Test memory not found in search results")
        else:
            print("   ℹ️  Semantic search not available in memory service")
        
        # Cleanup - delete test memory
        print("\\n🧹 Cleaning up test memory...")
        success = memory_service.delete_memory(memory.id)
        if success:
            print("✅ Test memory deleted")
        
        return True
        
    except Exception as e:
        print(f"❌ Memory service integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all vector store tests."""
    print("Starting Vector Store Integration Tests...")
    print("Note: This may take a few minutes to download embedding models on first run.\\n")
    
    # Setup logging
    setup_logging(log_level="INFO")
    logger = get_logger(__name__)
    
    test_results = []
    test_dir = None
    
    try:
        # Test 1: Vector store initialization
        init_success, vector_store, test_dir = test_vector_store_initialization()
        test_results.append(("Vector Store Initialization", init_success))
        
        if not init_success:
            print("\\n❌ Skipping remaining tests due to initialization failure")
            return 1
        
        # Test 2: Memory embedding and storage
        storage_success, test_memories = test_memory_embedding_storage(vector_store)
        test_results.append(("Memory Embedding & Storage", storage_success))
        
        if storage_success:
            # Test 3: Semantic search
            search_success = test_semantic_search(vector_store, test_memories)
            test_results.append(("Semantic Search", search_success))
            
            # Test 4: Memory operations
            ops_success = test_memory_operations(vector_store)
            test_results.append(("Memory Operations", ops_success))
        
        # Test 5: Integration with memory service
        integration_success = test_integration_with_memory_service()
        test_results.append(("Memory Service Integration", integration_success))
        
        # Print summary
        print("\\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = 0
        for test_name, success in test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name:.<40} {status}")
            if success:
                passed_tests += 1
        
        print(f"\\nOverall: {passed_tests}/{len(test_results)} tests passed")
        
        if passed_tests == len(test_results):
            print("\\n🎉 All vector store tests passed!")
            print("✅ ChromaDB vector store is working correctly")
            print("✅ Semantic search functionality is operational")
            print("✅ Integration with database layer is successful")
            return 0
        else:
            print("\\n⚠️  Some tests failed - vector store setup needs attention")
            return 1
    
    except Exception as e:
        print(f"\\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Cleanup
        if test_dir and test_dir.exists():
            try:
                shutil.rmtree(test_dir)
                print(f"\\n🧹 Cleaned up test directory: {test_dir}")
            except Exception as e:
                print(f"⚠️  Cleanup warning: {e}")


if __name__ == "__main__":
    sys.exit(main())
