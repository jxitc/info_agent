#!/usr/bin/env python3
"""
SQLite connection test script for Info Agent.

This script tests SQLite functionality including:
- Basic import and version check
- In-memory database operations
- File-based database creation
- Application data directory setup
"""

import sqlite3
import os
import sys
from pathlib import Path


def test_sqlite_import():
    """Test that SQLite can be imported and check version."""
    print("Testing SQLite import and version...")
    try:
        print(f"✅ SQLite module imported successfully")
        print(f"   SQLite version: {sqlite3.sqlite_version}")
        print(f"   Python sqlite3 module version: {sqlite3.version}")
        return True
    except ImportError as e:
        print(f"❌ Failed to import SQLite: {e}")
        return False


def test_memory_database():
    """Test basic SQLite operations with in-memory database."""
    print("\nTesting in-memory database operations...")
    try:
        # Create in-memory database
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Test table creation
        cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Test data insertion
        test_data = [
            ("Test Record 1",),
            ("Test Record 2",),
            ("Test Record 3",)
        ]
        cursor.executemany('INSERT INTO test_table (name) VALUES (?)', test_data)
        
        # Test data retrieval
        cursor.execute('SELECT * FROM test_table')
        results = cursor.fetchall()
        
        if len(results) == 3:
            print("✅ In-memory database operations successful")
            print(f"   Created and retrieved {len(results)} test records")
            for row in results:
                print(f"   Record: ID={row[0]}, Name={row[1]}")
        else:
            print(f"❌ Expected 3 records, got {len(results)}")
            return False
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ In-memory database test failed: {e}")
        return False


def test_file_database():
    """Test file-based database creation and operations."""
    print("\nTesting file-based database operations...")
    
    # Set up test directory
    data_dir = Path.home() / '.info_agent' / 'data'
    test_db_path = data_dir / 'test_connection.db'
    
    try:
        # Create data directory if it doesn't exist
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ Data directory created/verified: {data_dir}")
        
        # Remove test database if it exists
        if test_db_path.exists():
            test_db_path.unlink()
        
        # Create file-based database
        conn = sqlite3.connect(str(test_db_path))
        cursor = conn.cursor()
        
        # Test table creation
        cursor.execute('''
            CREATE TABLE memory_test (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                dynamic_fields TEXT,  -- JSON column for dynamic fields
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Test data insertion
        cursor.execute('''
            INSERT INTO memory_test (title, content, dynamic_fields) 
            VALUES (?, ?, ?)
        ''', (
            "Test Memory Entry",
            "This is a test content for the memory system",
            '{"category": "test", "priority": "high", "tags": ["sqlite", "test"]}'
        ))
        
        # Test data retrieval
        cursor.execute('SELECT * FROM memory_test')
        result = cursor.fetchone()
        
        if result:
            print("✅ File-based database operations successful")
            print(f"   Database file created: {test_db_path}")
            print(f"   Test record: ID={result[0]}, Title={result[1]}")
        else:
            print("❌ No data retrieved from file database")
            return False
        
        conn.close()
        
        # Verify file exists and has content
        if test_db_path.exists() and test_db_path.stat().st_size > 0:
            print(f"✅ Database file verified: {test_db_path.stat().st_size} bytes")
        else:
            print("❌ Database file not created or empty")
            return False
        
        # Clean up test database
        test_db_path.unlink()
        print("✅ Test database cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ File-based database test failed: {e}")
        # Clean up on error
        if test_db_path.exists():
            try:
                test_db_path.unlink()
            except:
                pass
        return False


def test_database_features():
    """Test advanced SQLite features that will be used in the application."""
    print("\nTesting advanced SQLite features...")
    
    try:
        conn = sqlite3.connect(':memory:')
        cursor = conn.cursor()
        
        # Test JSON operations (SQLite 3.38+)
        cursor.execute('SELECT sqlite_version()')
        version = cursor.fetchone()[0]
        print(f"   SQLite version: {version}")
        
        # Test basic JSON storage and retrieval
        cursor.execute('''
            CREATE TABLE json_test (
                id INTEGER PRIMARY KEY,
                data TEXT  -- JSON stored as text
            )
        ''')
        
        import json
        test_json = json.dumps({
            "field1": "value1",
            "field2": 42,
            "field3": ["a", "b", "c"]
        })
        
        cursor.execute('INSERT INTO json_test (data) VALUES (?)', (test_json,))
        cursor.execute('SELECT data FROM json_test')
        retrieved_json = cursor.fetchone()[0]
        parsed_json = json.loads(retrieved_json)
        
        if parsed_json["field2"] == 42:
            print("✅ JSON storage and retrieval working")
        else:
            print("❌ JSON data corruption detected")
            return False
        
        # Test full-text search capabilities
        cursor.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_test 
            USING fts5(title, content)
        ''')
        
        cursor.execute('''
            INSERT INTO fts_test (title, content) VALUES 
            ('Test Document', 'This is a test document for full-text search'),
            ('Another Document', 'This document contains different keywords')
        ''')
        
        cursor.execute("SELECT * FROM fts_test WHERE fts_test MATCH 'test'")
        fts_results = cursor.fetchall()
        
        if len(fts_results) > 0:
            print("✅ Full-text search (FTS5) working")
        else:
            print("⚠️  Full-text search not available (FTS5 extension may not be compiled)")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")
        return False


def main():
    """Run all SQLite tests."""
    print("=" * 60)
    print("INFO AGENT - SQLite Connection Test")
    print("=" * 60)
    
    tests = [
        ("SQLite Import", test_sqlite_import),
        ("Memory Database", test_memory_database),
        ("File Database", test_file_database),
        ("Advanced Features", test_database_features)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📊 Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All SQLite tests passed! Database setup is ready.")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())