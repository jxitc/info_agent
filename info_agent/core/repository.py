"""
Repository pattern implementation for Info Agent.

This module provides high-level database operations through a repository
interface, abstracting database details from business logic.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta

from info_agent.core.models import Memory, MemorySearchResult
from info_agent.core.database import DatabaseConnection, get_database
from info_agent.core.migrations import DatabaseInitializer
from info_agent.utils.logging_config import get_logger


class RepositoryError(Exception):
    """Base exception for repository operations."""
    pass


class MemoryRepositoryInterface(ABC):
    """
    Abstract interface for memory repository operations.
    
    Defines the contract for memory data access operations,
    allowing for different implementations (SQLite, PostgreSQL, etc.)
    """
    
    @abstractmethod
    def create(self, memory: Memory) -> Memory:
        """Create a new memory."""
        pass
    
    @abstractmethod
    def get_by_id(self, memory_id: int) -> Optional[Memory]:
        """Get memory by ID."""
        pass
    
    @abstractmethod
    def update(self, memory: Memory) -> Memory:
        """Update existing memory."""
        pass
    
    @abstractmethod
    def delete(self, memory_id: int) -> bool:
        """Delete memory by ID."""
        pass
    
    @abstractmethod
    def get_recent(self, limit: int = 20, offset: int = 0) -> List[Memory]:
        """Get recent memories."""
        pass
    
    @abstractmethod
    def search(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """Search memories."""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get total memory count."""
        pass


class SQLiteMemoryRepository(MemoryRepositoryInterface):
    """
    SQLite implementation of the memory repository.
    
    Provides high-level database operations for Memory objects,
    with automatic initialization and error handling.
    """
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None):
        """
        Initialize repository with database connection.
        
        Args:
            db_connection: Database connection. If None, uses global connection.
        """
        self.logger = get_logger(__name__)
        self.db = db_connection or get_database()
        
        # Ensure database is initialized
        self._ensure_initialized()
    
    def _ensure_initialized(self):
        """Ensure database is properly initialized."""
        try:
            initializer = DatabaseInitializer(str(self.db.db_path))
            if not initializer.is_initialized():
                self.logger.info("Database not initialized, initializing now...")
                initializer.initialize_database()
                self.logger.info("Database initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {e}")
            raise RepositoryError(f"Database initialization failed: {e}")
    
    def create(self, memory: Memory) -> Memory:
        """
        Create a new memory.
        
        Args:
            memory: Memory object to create
            
        Returns:
            Created memory with assigned ID
            
        Raises:
            RepositoryError: If creation fails
        """
        try:
            # Check for duplicates by content hash
            if memory.content_hash:
                existing = self.db.get_memory_by_hash(memory.content_hash)
                if existing:
                    self.logger.warning(f"Duplicate memory detected: {memory.content_hash}")
                    raise RepositoryError(f"Memory with this content already exists (ID: {existing.id})")
            
            created_memory = self.db.create_memory(memory)
            self.logger.info(f"Created memory: {created_memory.id}")
            return created_memory
            
        except Exception as e:
            self.logger.error(f"Failed to create memory: {e}")
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError(f"Memory creation failed: {e}")
    
    def get_by_id(self, memory_id: int) -> Optional[Memory]:
        """
        Get memory by ID.
        
        Args:
            memory_id: Memory ID to retrieve
            
        Returns:
            Memory object or None if not found
        """
        try:
            memory = self.db.get_memory_by_id(memory_id)
            if memory:
                self.logger.debug(f"Retrieved memory: {memory_id}")
            return memory
            
        except Exception as e:
            self.logger.error(f"Failed to get memory {memory_id}: {e}")
            raise RepositoryError(f"Failed to retrieve memory: {e}")
    
    def update(self, memory: Memory) -> Memory:
        """
        Update existing memory.
        
        Args:
            memory: Memory object with updated data
            
        Returns:
            Updated memory object
            
        Raises:
            RepositoryError: If update fails
        """
        try:
            updated_memory = self.db.update_memory(memory)
            self.logger.info(f"Updated memory: {updated_memory.id}")
            return updated_memory
            
        except Exception as e:
            self.logger.error(f"Failed to update memory: {e}")
            raise RepositoryError(f"Memory update failed: {e}")
    
    def delete(self, memory_id: int) -> bool:
        """
        Delete memory by ID.
        
        Args:
            memory_id: Memory ID to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            RepositoryError: If deletion fails
        """
        try:
            success = self.db.delete_memory(memory_id)
            if success:
                self.logger.info(f"Deleted memory: {memory_id}")
            else:
                self.logger.warning(f"Memory not found for deletion: {memory_id}")
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise RepositoryError(f"Memory deletion failed: {e}")
    
    def get_recent(self, limit: int = 20, offset: int = 0) -> List[Memory]:
        """
        Get recent memories in chronological order.
        
        Args:
            limit: Maximum number of memories to return
            offset: Number of memories to skip
            
        Returns:
            List of recent Memory objects
        """
        try:
            memories = self.db.get_recent_memories(limit=limit, offset=offset)
            self.logger.debug(f"Retrieved {len(memories)} recent memories")
            return memories
            
        except Exception as e:
            self.logger.error(f"Failed to get recent memories: {e}")
            raise RepositoryError(f"Failed to retrieve recent memories: {e}")
    
    def search(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """
        Search memories using full-text search.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of MemorySearchResult objects
        """
        try:
            results = self.db.search_memories_fts(query, limit=limit)
            self.logger.debug(f"Search '{query}' returned {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"Search failed for query '{query}': {e}")
            raise RepositoryError(f"Search operation failed: {e}")
    
    def count(self) -> int:
        """
        Get total count of memories.
        
        Returns:
            Total number of memories
        """
        try:
            count = self.db.count_memories()
            self.logger.debug(f"Total memories count: {count}")
            return count
            
        except Exception as e:
            self.logger.error(f"Failed to count memories: {e}")
            raise RepositoryError(f"Count operation failed: {e}")
    
    def get_by_content_hash(self, content_hash: str) -> Optional[Memory]:
        """
        Get memory by content hash.
        
        Args:
            content_hash: Content hash to search for
            
        Returns:
            Memory object or None if not found
        """
        try:
            memory = self.db.get_memory_by_hash(content_hash)
            if memory:
                self.logger.debug(f"Found memory by hash: {memory.id}")
            return memory
            
        except Exception as e:
            self.logger.error(f"Failed to get memory by hash: {e}")
            raise RepositoryError(f"Hash lookup failed: {e}")
    
    def search_by_dynamic_field(self, field_name: str, field_value: Any, limit: int = 20) -> List[Memory]:
        """
        Search memories by dynamic field value.
        
        Args:
            field_name: Name of the dynamic field
            field_value: Value to search for
            limit: Maximum number of results
            
        Returns:
            List of Memory objects matching the criteria
        """
        try:
            # Use JSON_EXTRACT to search within dynamic_fields
            query = f"""
                SELECT * FROM memories 
                WHERE JSON_EXTRACT(dynamic_fields, '$.{field_name}') = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            
            cursor = self.db.execute_query(query, (str(field_value), limit))
            memories = []
            
            for row in cursor.fetchall():
                memories.append(Memory.from_dict(dict(row)))
            
            self.logger.debug(f"Dynamic field search returned {len(memories)} results")
            return memories
            
        except Exception as e:
            self.logger.error(f"Dynamic field search failed: {e}")
            raise RepositoryError(f"Dynamic field search failed: {e}")
    
    def get_memories_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Memory]:
        """
        Get memories within a date range.
        
        Args:
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            List of Memory objects within the date range
        """
        try:
            query = """
                SELECT * FROM memories 
                WHERE created_at BETWEEN ? AND ?
                ORDER BY created_at DESC
            """
            
            cursor = self.db.execute_query(query, (
                start_date.isoformat(),
                end_date.isoformat()
            ))
            
            memories = []
            for row in cursor.fetchall():
                memories.append(Memory.from_dict(dict(row)))
            
            self.logger.debug(f"Date range search returned {len(memories)} results")
            return memories
            
        except Exception as e:
            self.logger.error(f"Date range search failed: {e}")
            raise RepositoryError(f"Date range search failed: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get repository statistics and information.
        
        Returns:
            Dictionary with repository statistics
        """
        try:
            stats = {
                'total_memories': self.count(),
                'database_info': self.db.get_database_info()
            }
            
            # Add recent activity stats
            now = datetime.now()
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)
            
            stats['memories_last_week'] = len(self.get_memories_by_date_range(week_ago, now))
            stats['memories_last_month'] = len(self.get_memories_by_date_range(month_ago, now))
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {'error': str(e)}


class MemoryService:
    """
    High-level service class for memory operations.
    
    Provides business logic and workflow management on top of the repository layer.
    This is the main interface that CLI commands and other components should use.
    """
    
    def __init__(self, repository: Optional[MemoryRepositoryInterface] = None):
        """
        Initialize memory service.
        
        Args:
            repository: Memory repository. If None, uses SQLite implementation.
        """
        self.logger = get_logger(__name__)
        self.repository = repository or SQLiteMemoryRepository()
    
    def add_memory(self, content: str, title: Optional[str] = None) -> Memory:
        """
        Add a new memory with automatic processing.
        
        Args:
            content: Memory content text
            title: Optional title (will be generated if not provided)
            
        Returns:
            Created Memory object
        """
        try:
            # Create memory object
            memory = Memory(
                content=content.strip(),
                title=title or self._generate_title(content)
            )
            
            # TODO: Add AI processing for dynamic fields and summary
            # This will be implemented in tasks 3.1 and 3.2
            
            # Create in repository
            created_memory = self.repository.create(memory)
            self.logger.info(f"Added memory: '{created_memory.title}'")
            
            return created_memory
            
        except Exception as e:
            self.logger.error(f"Failed to add memory: {e}")
            raise RepositoryError(f"Failed to add memory: {e}")
    
    def get_memory(self, memory_id: int) -> Optional[Memory]:
        """Get memory by ID."""
        return self.repository.get_by_id(memory_id)
    
    def search_memories(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """Search memories."""
        return self.repository.search(query, limit=limit)
    
    def list_recent_memories(self, limit: int = 20, offset: int = 0) -> List[Memory]:
        """Get recent memories."""
        return self.repository.get_recent(limit=limit, offset=offset)
    
    def update_memory(self, memory: Memory) -> Memory:
        """Update existing memory."""
        return self.repository.update(memory)
    
    def delete_memory(self, memory_id: int) -> bool:
        """Delete memory by ID."""
        return self.repository.delete(memory_id)
    
    def get_memory_count(self) -> int:
        """Get total memory count."""
        return self.repository.count()
    
    def get_service_statistics(self) -> Dict[str, Any]:
        """Get service statistics."""
        if hasattr(self.repository, 'get_statistics'):
            return self.repository.get_statistics()
        return {'total_memories': self.repository.count()}
    
    def _generate_title(self, content: str, max_length: int = 50) -> str:
        """
        Generate a title from content.
        
        Args:
            content: Content text
            max_length: Maximum title length
            
        Returns:
            Generated title
        """
        # Simple title generation - take first sentence or truncate
        content = content.strip()
        
        # Find first sentence
        sentence_endings = ['.', '!', '?']
        min_pos = len(content)
        
        for ending in sentence_endings:
            pos = content.find(ending)
            if pos != -1 and pos < min_pos:
                min_pos = pos + 1
        
        # Use first sentence or truncate
        if min_pos < max_length and min_pos < len(content):
            title = content[:min_pos].strip()
        else:
            title = content[:max_length].strip()
            if len(content) > max_length:
                # Find last space to avoid cutting words
                last_space = title.rfind(' ')
                if last_space > max_length * 0.7:
                    title = title[:last_space]
                title += "..."
        
        return title if title else "Untitled Memory"


# Global service instance
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """
    Get global memory service instance (singleton pattern).
    
    Returns:
        MemoryService instance
    """
    global _memory_service
    
    if _memory_service is None:
        _memory_service = MemoryService()
    
    return _memory_service


# Export main classes and functions
__all__ = [
    'MemoryRepositoryInterface',
    'SQLiteMemoryRepository', 
    'MemoryService',
    'RepositoryError',
    'get_memory_service'
]