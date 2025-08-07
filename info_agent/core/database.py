"""
Database connection and operations for Info Agent.

This module provides SQLite database connectivity and basic CRUD operations
for Memory objects, with connection pooling and error handling.
"""

import sqlite3
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from contextlib import contextmanager
from datetime import datetime

from info_agent.core.models import Memory, MemorySearchResult
from info_agent.core.schema import DatabaseSchema, SchemaConstants
from info_agent.utils.logging_config import get_logger


class DatabaseError(Exception):
    """Base exception for database operations."""
    pass


class ConnectionError(DatabaseError):
    """Exception for database connection issues."""
    pass


class ValidationError(DatabaseError):
    """Exception for data validation issues."""
    pass


class DatabaseConnection:
    """
    SQLite database connection manager with CRUD operations.
    
    Provides connection pooling, transaction management, and basic
    CRUD operations for Memory objects.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default.
        """
        self.logger = get_logger(__name__)
        self._lock = threading.Lock()
        self._connection: Optional[sqlite3.Connection] = None
        
        # Set database path
        if db_path is None:
            db_dir = Path(SchemaConstants.DEFAULT_DB_PATH).expanduser()
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = db_dir / SchemaConstants.DATABASE_NAME
        else:
            self.db_path = Path(db_path)
        
        self.logger.info(f"Database path: {self.db_path}")
    
    def connect(self) -> sqlite3.Connection:
        """
        Get or create database connection.
        
        Returns:
            SQLite connection object
            
        Raises:
            ConnectionError: If connection cannot be established
        """
        with self._lock:
            if self._connection is None:
                try:
                    self._connection = sqlite3.connect(
                        self.db_path,
                        check_same_thread=False,
                        timeout=30.0
                    )
                    
                    # Configure connection
                    self._connection.row_factory = sqlite3.Row
                    self._connection.execute("PRAGMA foreign_keys = ON")
                    self._connection.execute("PRAGMA journal_mode = WAL")
                    
                    self.logger.info("Database connection established")
                    
                except sqlite3.Error as e:
                    self.logger.error(f"Failed to connect to database: {e}")
                    raise ConnectionError(f"Cannot connect to database: {e}")
            
            return self._connection
    
    def close(self):
        """Close database connection."""
        with self._lock:
            if self._connection:
                try:
                    self._connection.close()
                    self.logger.info("Database connection closed")
                except sqlite3.Error as e:
                    self.logger.error(f"Error closing database: {e}")
                finally:
                    self._connection = None
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions.
        
        Usage:
            with db.transaction():
                db.create_memory(memory)
                db.update_memory(other_memory)
        """
        conn = self.connect()
        try:
            yield conn
            conn.commit()
            self.logger.debug("Transaction committed")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Transaction rolled back: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """
        Execute a SQL query with parameters.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Cursor with query results
        """
        conn = self.connect()
        try:
            cursor = conn.execute(query, params)
            self.logger.debug(f"Query executed: {query[:100]}...")
            return cursor
        except sqlite3.Error as e:
            self.logger.error(f"Query failed: {query[:100]}... Error: {e}")
            raise DatabaseError(f"Query execution failed: {e}")
    
    def execute_many(self, query: str, params_list: List[tuple]) -> sqlite3.Cursor:
        """Execute a query multiple times with different parameters."""
        conn = self.connect()
        try:
            cursor = conn.executemany(query, params_list)
            conn.commit()
            self.logger.debug(f"Batch query executed: {len(params_list)} operations")
            return cursor
        except sqlite3.Error as e:
            self.logger.error(f"Batch query failed: {e}")
            raise DatabaseError(f"Batch execution failed: {e}")
    
    # CRUD Operations for Memory
    
    def create_memory(self, memory: Memory) -> Memory:
        """
        Create a new memory in the database.
        
        Args:
            memory: Memory object to create
            
        Returns:
            Memory object with assigned ID and timestamps
            
        Raises:
            ValidationError: If memory data is invalid
            DatabaseError: If creation fails
        """
        # Validate memory
        errors = memory.validate()
        if errors:
            raise ValidationError(f"Memory validation failed: {', '.join(errors)}")
        
        # Set timestamps
        now = datetime.now()
        memory.created_at = now
        memory.updated_at = now
        
        # Prepare data for insertion
        data = memory.to_dict()
        columns = [k for k in data.keys() if k != 'id']  # Exclude ID (auto-increment)
        values = [data[k] for k in columns]
        placeholders = ', '.join(['?' for _ in columns])
        
        query = f"""
            INSERT INTO memories ({', '.join(columns)})
            VALUES ({placeholders})
        """
        
        try:
            with self.transaction():
                cursor = self.execute_query(query, tuple(values))
                memory.id = cursor.lastrowid
                
                self.logger.info(f"Created memory with ID: {memory.id}")
                return memory
                
        except sqlite3.IntegrityError as e:
            if "content_hash" in str(e):
                raise ValidationError("Memory with this content already exists")
            raise DatabaseError(f"Memory creation failed: {e}")
    
    def get_memory_by_id(self, memory_id: int) -> Optional[Memory]:
        """
        Retrieve a memory by ID.
        
        Args:
            memory_id: Memory ID to retrieve
            
        Returns:
            Memory object or None if not found
        """
        query = "SELECT * FROM memories WHERE id = ?"
        
        try:
            cursor = self.execute_query(query, (memory_id,))
            row = cursor.fetchone()
            
            if row:
                return Memory.from_dict(dict(row))
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get memory {memory_id}: {e}")
            raise DatabaseError(f"Failed to retrieve memory: {e}")
    
    def get_memory_by_hash(self, content_hash: str) -> Optional[Memory]:
        """
        Retrieve a memory by content hash.
        
        Args:
            content_hash: Content hash to search for
            
        Returns:
            Memory object or None if not found
        """
        query = "SELECT * FROM memories WHERE content_hash = ?"
        
        try:
            cursor = self.execute_query(query, (content_hash,))
            row = cursor.fetchone()
            
            if row:
                return Memory.from_dict(dict(row))
            return None
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get memory by hash: {e}")
            raise DatabaseError(f"Failed to retrieve memory by hash: {e}")
    
    def update_memory(self, memory: Memory) -> Memory:
        """
        Update an existing memory.
        
        Args:
            memory: Memory object with updated data
            
        Returns:
            Updated Memory object
            
        Raises:
            ValidationError: If memory data is invalid
            DatabaseError: If update fails
        """
        if not memory.id:
            raise ValidationError("Cannot update memory without ID")
        
        # Validate memory
        errors = memory.validate()
        if errors:
            raise ValidationError(f"Memory validation failed: {', '.join(errors)}")
        
        # Update timestamp and version
        memory.updated_at = datetime.now()
        memory.version += 1
        
        # Prepare update data
        data = memory.to_dict()
        set_clauses = []
        values = []
        
        for key, value in data.items():
            if key != 'id':  # Don't update ID
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        values.append(memory.id)  # Add ID for WHERE clause
        
        query = f"""
            UPDATE memories 
            SET {', '.join(set_clauses)}
            WHERE id = ?
        """
        
        try:
            with self.transaction():
                cursor = self.execute_query(query, tuple(values))
                
                if cursor.rowcount == 0:
                    raise DatabaseError(f"Memory with ID {memory.id} not found")
                
                self.logger.info(f"Updated memory ID: {memory.id}")
                return memory
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to update memory {memory.id}: {e}")
            raise DatabaseError(f"Memory update failed: {e}")
    
    def delete_memory(self, memory_id: int) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: Memory ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        query = "DELETE FROM memories WHERE id = ?"
        
        try:
            with self.transaction():
                cursor = self.execute_query(query, (memory_id,))
                
                if cursor.rowcount > 0:
                    self.logger.info(f"Deleted memory ID: {memory_id}")
                    return True
                return False
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise DatabaseError(f"Memory deletion failed: {e}")
    
    def get_recent_memories(self, limit: int = 20, offset: int = 0) -> List[Memory]:
        """
        Get recent memories in chronological order.
        
        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            
        Returns:
            List of Memory objects
        """
        query = """
            SELECT * FROM memories 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """
        
        try:
            cursor = self.execute_query(query, (limit, offset))
            memories = []
            
            for row in cursor.fetchall():
                memories.append(Memory.from_dict(dict(row)))
            
            self.logger.debug(f"Retrieved {len(memories)} recent memories")
            return memories
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get recent memories: {e}")
            raise DatabaseError(f"Failed to retrieve recent memories: {e}")
    
    def search_memories_fts(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """
        Search memories using full-text search.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of MemorySearchResult objects
        """
        sql_query = """
            SELECT m.*, 
                   rank as relevance_score
            FROM memories m
            JOIN search_index s ON m.id = s.rowid
            WHERE search_index MATCH ?
            ORDER BY rank
            LIMIT ?
        """
        
        try:
            cursor = self.execute_query(sql_query, (query, limit))
            results = []
            
            for row in cursor.fetchall():
                row_dict = dict(row)
                relevance_score = row_dict.pop('relevance_score', 0.0)
                
                memory = Memory.from_dict(row_dict)
                result = MemorySearchResult(
                    memory=memory,
                    relevance_score=float(relevance_score),
                    match_type="fts",
                    matched_fields=["content", "title", "summary"]
                )
                results.append(result)
            
            self.logger.debug(f"FTS search returned {len(results)} results")
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"FTS search failed: {e}")
            raise DatabaseError(f"Full-text search failed: {e}")
    
    def count_memories(self) -> int:
        """Get total count of memories."""
        query = "SELECT COUNT(*) FROM memories"
        
        try:
            cursor = self.execute_query(query)
            return cursor.fetchone()[0]
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to count memories: {e}")
            raise DatabaseError(f"Failed to count memories: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database information and statistics."""
        try:
            info = {
                "database_path": str(self.db_path),
                "database_size": self.db_path.stat().st_size if self.db_path.exists() else 0,
                "total_memories": self.count_memories(),
                "connection_status": "connected" if self._connection else "disconnected"
            }
            
            # Get SQLite version
            cursor = self.execute_query("SELECT sqlite_version()")
            info["sqlite_version"] = cursor.fetchone()[0]
            
            return info
            
        except Exception as e:
            self.logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None
_db_lock = threading.Lock()


def get_database() -> DatabaseConnection:
    """
    Get global database connection instance (singleton pattern).
    
    Returns:
        DatabaseConnection instance
    """
    global _db_connection
    
    with _db_lock:
        if _db_connection is None:
            _db_connection = DatabaseConnection()
        return _db_connection


def close_database():
    """Close global database connection."""
    global _db_connection
    
    with _db_lock:
        if _db_connection:
            _db_connection.close()
            _db_connection = None


# Export main classes and functions
__all__ = [
    'DatabaseConnection',
    'DatabaseError',
    'ConnectionError', 
    'ValidationError',
    'get_database',
    'close_database'
]