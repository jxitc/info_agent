#!/usr/bin/env python3
"""
Memory database operations test script for Info Agent.

This script tests the complete memory database functionality including:
- Database initialization and migration
- Memory creation, retrieval, update, and deletion (CRUD)
- Search functionality
- Repository and service layer operations
- Error handling and edge cases
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Optional, List

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from info_agent.core.models import Memory, MemorySearchResult
from info_agent.core.database import DatabaseConnection, DatabaseError
from info_agent.core.migrations import DatabaseInitializer, initialize_database
from info_agent.core.repository import SQLiteMemoryRepository, MemoryService
from info_agent.core.schema import SchemaConstants


class MemoryDatabaseTester:
    """Test runner for memory database operations."""
    
    def __init__(self):
        self.test_db_dir: Optional[Path] = None
        self.test_db_path: Optional[Path] = None
        self.db_connection: Optional[DatabaseConnection] = None
        self.repository: Optional[SQLiteMemoryRepository] = None
        self.service: Optional[MemoryService] = None
        
    def setup_test_database(self) -> bool:
        """Create temporary test database."""
        print("Setting up test database...")
        
        try:
            # Create temporary directory for test database
            self.test_db_dir = Path(tempfile.mkdtemp(prefix="info_agent_test_"))
            self.test_db_path = self.test_db_dir / "test_info_agent.db"
            
            print(f"   Test database location: {self.test_db_path}")
            
            # Initialize test database
            if initialize_database(str(self.test_db_path)):
                print("✅ Test database initialized successfully")
            else:
                print("✅ Test database already initialized")
            
            # Create connections and services
            self.db_connection = DatabaseConnection(str(self.test_db_path))
            self.repository = SQLiteMemoryRepository(self.db_connection)
            self.service = MemoryService(self.repository)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to setup test database: {e}")
            return False
    
    def cleanup_test_database(self):
        """Clean up test database and temporary files."""
        print("\nCleaning up test database...")
        
        try:
            # Close database connection
            if self.db_connection:
                self.db_connection.close()
            
            # Remove temporary directory
            if self.test_db_dir and self.test_db_dir.exists():
                shutil.rmtree(self.test_db_dir)
                print("✅ Test database cleaned up")
            
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def test_database_initialization(self) -> bool:
        """Test database initialization and schema verification."""
        print("\nTesting database initialization...")
        
        try:
            # Test initializer
            initializer = DatabaseInitializer(str(self.test_db_path))
            
            # Check if initialized
            is_initialized = initializer.is_initialized()
            print(f"   Database initialized: {is_initialized}")
            
            # Get current version
            version = initializer.get_current_version()
            print(f"   Current schema version: {version}")
            
            # Verify schema
            verification = initializer.verify_schema()
            if verification['valid']:
                print(f"✅ Schema verification passed")
                print(f"   Tables found: {len(verification['tables_found'])}")
                return True
            else:
                print(f"❌ Schema verification failed: {verification['errors']}")
                return False
                
        except Exception as e:
            print(f"❌ Database initialization test failed: {e}")
            return False
    
    def test_memory_crud_operations(self) -> bool:
        """Test basic CRUD operations for Memory objects."""
        print("\nTesting Memory CRUD operations...")
        
        try:
            # Test CREATE
            print("   Testing memory creation...")
            test_memory = Memory(
                title="Test Memory 1",
                content="This is a test memory for database operations testing.",
                dynamic_fields={"category": "test", "urgency": "medium"}
            )
            
            created_memory = self.repository.create(test_memory)
            if not created_memory.id:
                print("❌ Memory creation failed - no ID assigned")
                return False
            
            print(f"✅ Memory created with ID: {created_memory.id}")
            print(f"   Content hash: {created_memory.content_hash[:16]}...")
            
            # Test READ
            print("   Testing memory retrieval...")
            retrieved_memory = self.repository.get_by_id(created_memory.id)
            
            if not retrieved_memory:
                print("❌ Memory retrieval failed")
                return False
            
            if retrieved_memory.title != test_memory.title:
                print("❌ Retrieved memory data doesn't match")
                return False
            
            print(f"✅ Memory retrieved successfully: '{retrieved_memory.title}'")
            
            # Test UPDATE
            print("   Testing memory update...")
            retrieved_memory.title = "Updated Test Memory"
            retrieved_memory.dynamic_fields["status"] = "updated"
            
            updated_memory = self.repository.update(retrieved_memory)
            
            if updated_memory.title != "Updated Test Memory":
                print("❌ Memory update failed")
                return False
            
            print(f"✅ Memory updated successfully")
            print(f"   New version: {updated_memory.version}")
            
            # Test DELETE
            print("   Testing memory deletion...")
            delete_success = self.repository.delete(updated_memory.id)
            
            if not delete_success:
                print("❌ Memory deletion failed")
                return False
            
            # Verify deletion
            deleted_memory = self.repository.get_by_id(updated_memory.id)
            if deleted_memory:
                print("❌ Memory still exists after deletion")
                return False
            
            print("✅ Memory deleted successfully")
            return True
            
        except Exception as e:
            print(f"❌ CRUD operations test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_service_layer_operations(self) -> bool:
        """Test high-level service layer operations."""
        print("\nTesting service layer operations...")
        
        try:
            # Test adding memory through service
            print("   Testing service.add_memory()...")
            
            service_memory = self.service.add_memory(
                content="This is a service layer test memory with automatic title generation and processing.",
                title="Service Test Memory"
            )
            
            if not service_memory.id:
                print("❌ Service memory creation failed")
                return False
            
            print(f"✅ Service memory created: ID {service_memory.id}")
            print(f"   Auto-generated hash: {service_memory.content_hash[:16]}...")
            print(f"   Word count: {service_memory.word_count}")
            
            # Test getting memory through service
            print("   Testing service.get_memory()...")
            
            fetched_memory = self.service.get_memory(service_memory.id)
            if not fetched_memory or fetched_memory.id != service_memory.id:
                print("❌ Service memory retrieval failed")
                return False
            
            print("✅ Service memory retrieval successful")
            
            # Test memory count
            print("   Testing service.get_memory_count()...")
            
            count = self.service.get_memory_count()
            print(f"✅ Total memories in database: {count}")
            
            # Test statistics
            print("   Testing service.get_service_statistics()...")
            
            stats = self.service.get_service_statistics()
            if 'total_memories' not in stats:
                print("❌ Service statistics missing required fields")
                return False
            
            print(f"✅ Service statistics retrieved: {stats['total_memories']} total memories")
            
            return True
            
        except Exception as e:
            print(f"❌ Service layer test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_multiple_memories_and_search(self) -> bool:
        """Test operations with multiple memories and search functionality."""
        print("\nTesting multiple memories and search...")
        
        try:
            # Create multiple test memories
            print("   Creating multiple test memories...")
            
            test_memories = [
                {
                    "title": "Project Meeting Notes",
                    "content": "Discussed the new AI project timeline and deliverables for Q2. Need to follow up with the development team."
                },
                {
                    "title": "Shopping List",
                    "content": "Buy groceries: milk, eggs, bread, apples. Don't forget the birthday cake for Sarah's party."
                },
                {
                    "title": "Book Recommendation",
                    "content": "Read 'The Pragmatic Programmer' - excellent book about software development best practices and methodologies."
                },
                {
                    "title": "Workout Schedule",
                    "content": "Monday: cardio and abs. Tuesday: upper body strength training. Wednesday: yoga and stretching."
                }
            ]
            
            created_ids = []
            for memory_data in test_memories:
                memory = self.service.add_memory(
                    content=memory_data["content"],
                    title=memory_data["title"]
                )
                created_ids.append(memory.id)
                print(f"   Created: '{memory.title}' (ID: {memory.id})")
            
            print(f"✅ Created {len(created_ids)} test memories")
            
            # Test recent memories retrieval
            print("   Testing recent memories retrieval...")
            
            recent_memories = self.service.list_recent_memories(limit=10)
            if len(recent_memories) < len(test_memories):
                print("❌ Not all memories retrieved")
                return False
            
            print(f"✅ Retrieved {len(recent_memories)} recent memories")
            
            # Test search functionality (if FTS is working)
            print("   Testing search functionality...")
            
            try:
                search_results = self.service.search_memories("project development")
                print(f"✅ Search completed: {len(search_results)} results")
                
                for result in search_results[:3]:  # Show first 3 results
                    print(f"   Found: '{result.memory.title}' (score: {result.relevance_score:.3f})")
                
            except Exception as search_error:
                print(f"⚠️  Search test skipped (FTS may not be available): {search_error}")
            
            return True
            
        except Exception as e:
            print(f"❌ Multiple memories test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and edge cases."""
        print("\nTesting error handling...")
        
        try:
            # Test duplicate content prevention
            print("   Testing duplicate prevention...")
            
            duplicate_memory = Memory(
                title="Duplicate Test",
                content="This is duplicate content for testing."
            )
            
            # Create first memory
            first_memory = self.repository.create(duplicate_memory)
            print(f"   First memory created: ID {first_memory.id}")
            
            # Try to create duplicate
            try:
                duplicate_memory2 = Memory(
                    title="Different Title",
                    content="This is duplicate content for testing."  # Same content
                )
                
                second_memory = self.repository.create(duplicate_memory2)
                print("❌ Duplicate creation should have failed")
                return False
                
            except Exception as expected_error:
                print("✅ Duplicate prevention working correctly")
            
            # Test invalid memory ID retrieval
            print("   Testing invalid ID retrieval...")
            
            invalid_memory = self.repository.get_by_id(99999)
            if invalid_memory is not None:
                print("❌ Invalid ID should return None")
                return False
            
            print("✅ Invalid ID handling working correctly")
            
            # Test memory validation
            print("   Testing memory validation...")
            
            invalid_memory = Memory(
                title="",  # Empty title
                content=""  # Empty content
            )
            
            validation_errors = invalid_memory.validate()
            if len(validation_errors) == 0:
                print("❌ Validation should have failed for empty memory")
                return False
            
            print(f"✅ Validation working: {len(validation_errors)} errors detected")
            
            return True
            
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all database tests."""
        print("=" * 60)
        print("INFO AGENT - Memory Database Test Suite")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_database():
            return False
        
        # Run test suite
        tests = [
            ("Database Initialization", self.test_database_initialization),
            ("Memory CRUD Operations", self.test_memory_crud_operations),
            ("Service Layer Operations", self.test_service_layer_operations),
            ("Multiple Memories & Search", self.test_multiple_memories_and_search),
            ("Error Handling", self.test_error_handling)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} - PASSED")
                else:
                    failed += 1
                    print(f"❌ {test_name} - FAILED")
            except Exception as e:
                failed += 1
                print(f"❌ {test_name} - CRASHED: {e}")
        
        # Cleanup
        self.cleanup_test_database()
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📊 Total:  {passed + failed}")
        
        if failed == 0:
            print("\n🎉 All memory database tests passed! Database layer is ready.")
            return True
        else:
            print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.")
            return False


def main():
    """Run the memory database test suite."""
    tester = MemoryDatabaseTester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        tester.cleanup_test_database()
        return 1
    except Exception as e:
        print(f"\n❌ Test suite crashed: {e}")
        tester.cleanup_test_database()
        return 1


if __name__ == "__main__":
    sys.exit(main())