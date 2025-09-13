"""
Repository pattern implementation for Info Agent.

This module provides high-level database operations through a repository
interface, abstracting database details from business logic.
"""

import json
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta

from info_agent.core.models import Memory, MemorySearchResult
from info_agent.core.database import DatabaseConnection, get_database
from info_agent.core.migrations import DatabaseInitializer
from info_agent.core.vector_store import VectorStore, get_vector_store
from info_agent.core.ranking import get_enhanced_ranker
from info_agent.ai.processor import MemoryProcessor, ProcessingError
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
        """Search memories using text search."""
        pass
    
    @abstractmethod
    def semantic_search(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """Search memories using semantic/vector similarity."""
        pass
    
    @abstractmethod
    def hybrid_search(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """Search memories using combined text + semantic search."""
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
    
    def __init__(self, db_connection: Optional[DatabaseConnection] = None, 
                 vector_store: Optional[VectorStore] = None):
        """
        Initialize repository with database connection and vector store.
        
        Args:
            db_connection: Database connection. If None, uses global connection.
            vector_store: Vector store instance. If None, uses global instance.
        """
        self.logger = get_logger(__name__)
        self.db = db_connection or get_database()
        self.vector_store = vector_store or get_vector_store()
        
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
                    self.logger.info(f"Duplicate memory detected: {memory.content_hash}, returning existing memory (ID: {existing.id})")
                    return existing
            
            created_memory = self.db.create_memory(memory)
            
            # Add to vector store
            try:
                success = self.vector_store.add_memory(created_memory)
                if success:
                    self.logger.debug(f"Added memory {created_memory.id} to vector store")
                else:
                    self.logger.warning(f"Failed to add memory {created_memory.id} to vector store")
            except Exception as e:
                self.logger.error(f"Vector store add failed for memory {created_memory.id}: {e}")
                # Don't fail the entire operation if vector store fails
            
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
            
            # Update in vector store
            try:
                success = self.vector_store.update_memory(updated_memory)
                if success:
                    self.logger.debug(f"Updated memory {updated_memory.id} in vector store")
                else:
                    self.logger.warning(f"Failed to update memory {updated_memory.id} in vector store")
            except Exception as e:
                self.logger.error(f"Vector store update failed for memory {updated_memory.id}: {e}")
            
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
                # Delete from vector store
                try:
                    vector_success = self.vector_store.delete_memory(memory_id)
                    if vector_success:
                        self.logger.debug(f"Deleted memory {memory_id} from vector store")
                    else:
                        self.logger.warning(f"Failed to delete memory {memory_id} from vector store")
                except Exception as e:
                    self.logger.error(f"Vector store delete failed for memory {memory_id}: {e}")
                
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
    
    def semantic_search(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """
        Search memories using semantic/vector similarity.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of MemorySearchResult objects with similarity scores
        """
        try:
            vector_results = self.vector_store.search_memories(query, limit=limit)
            search_results = []
            
            # vector_results are already MemorySearchResult objects from the vector store
            search_results = vector_results
            
            self.logger.info(f"Semantic search '{query}' returned {len(search_results)} results")

            return search_results
            
        except Exception as e:
            self.logger.error(f"Semantic search failed for query '{query}': {e}")
            raise RepositoryError(f"Semantic search operation failed: {e}")
    
    def hybrid_search(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """
        Search memories using enhanced RRF-based hybrid search with adaptive ranking.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of MemorySearchResult objects from enhanced hybrid search
        """
        try:
            # Get enhanced ranker
            ranker = get_enhanced_ranker()
            
            # Get results from all search methods
            fts_results = self.search(query, limit=min(limit * 2, 100))  # Get more results for better fusion
            semantic_results = self.semantic_search(query, limit=min(limit * 2, 100))
            
            # Prepare source results for RRF
            source_results = {
                'structured': fts_results,
                'semantic': semantic_results
            }
            
            # Apply enhanced ranking with RRF, adaptive thresholds, and confidence scoring
            enhanced_results = ranker.rank_search_results(
                source_results=source_results,
                query=query,
                max_results=limit
            )
            
            # Log detailed result information with new ranking data
            self.logger.info(f"Enhanced hybrid search '{query}' returned {len(enhanced_results)} results")
            for i, result in enumerate(enhanced_results[:3], 1):  # Log first 3 results
                explanation = getattr(result, 'ranking_explanation', 'No explanation available')
                self.logger.info(f"  {i}. Memory {result.memory.id}: {result.match_type}, "
                               f"Score: {result.relevance_score:.3f}")
                self.logger.info(f"     → {explanation}")
            
            if len(enhanced_results) > 3:
                self.logger.debug(f"  ... and {len(enhanced_results) - 3} more results")
                
            return enhanced_results
            
        except Exception as e:
            self.logger.error(f"Enhanced hybrid search failed for query '{query}': {e}")
            # Fall back to original simple hybrid search if enhanced version fails
            self.logger.warning("Falling back to basic hybrid search")
            return self._basic_hybrid_search(query, limit)
    
    def _basic_hybrid_search(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """
        Fallback basic hybrid search implementation (original logic).
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of MemorySearchResult objects from basic hybrid search
        """
        try:
            # Get results from both search methods
            fts_results = self.search(query, limit=limit)
            semantic_results = self.semantic_search(query, limit=limit)
            
            # Combine and deduplicate results
            combined_results = []
            seen_ids = set()
            
            # Add FTS results first
            for result in fts_results:
                if result.memory.id not in seen_ids:
                    # Mark as text search result
                    result.match_type = "text"
                    combined_results.append(result)
                    seen_ids.add(result.memory.id)
            
            # Add semantic results that aren't already included
            for result in semantic_results:
                memory_id = result.memory.id
                if memory_id not in seen_ids:
                    # Mark as semantic search result
                    result.match_type = "semantic"
                    combined_results.append(result)
                    seen_ids.add(memory_id)
                else:
                    # Memory found in both searches - boost its score and mark as hybrid
                    for combined_result in combined_results:
                        if combined_result.memory.id == memory_id:
                            # Boost score for items found in both searches
                            combined_result.relevance_score = min(
                                1.0, 
                                combined_result.relevance_score + 0.2
                            )
                            combined_result.match_type = "hybrid"
                            break
            
            # Sort by relevance score (descending) and limit results
            combined_results.sort(key=lambda x: x.relevance_score, reverse=True)
            combined_results = combined_results[:limit]
            
            self.logger.info(f"Basic hybrid search returned {len(combined_results)} results")
            return combined_results
            
        except Exception as e:
            self.logger.error(f"Basic hybrid search failed: {e}")
            raise RepositoryError(f"Fallback hybrid search failed: {e}")
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        try:
            return self.vector_store.get_collection_stats()
        except Exception as e:
            self.logger.error(f"Failed to get vector store stats: {e}")
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
        
        # Initialize AI processor (gracefully handle unavailability)
        try:
            self.processor = MemoryProcessor()
            self.ai_available = True
            self.logger.info("AI processor initialized successfully")
        except Exception as e:
            self.processor = None
            self.ai_available = False
            self.logger.warning(f"AI processor unavailable: {e}")
            self.logger.info("Service will operate in basic mode without AI features")
    
    def add_memory(self, content: str, title: Optional[str] = None) -> Memory:
        """
        Add a new memory with automatic AI processing and vector storage.
        
        Args:
            content: Memory content text
            title: Optional title (will be AI-generated if not provided)
            
        Returns:
            Created Memory object with AI-extracted fields
        """
        try:
            self.logger.info(f"Adding memory with {len(content)} characters")
            
            if self.ai_available and self.processor:
                # Process text with AI to extract structured information
                processed_memory = self.processor.process_text_to_memory(
                    text=content.strip(),
                    force_title=title
                )
                self.logger.info(f"AI processing successful: '{processed_memory.title}'")
                
                # Log detailed processing results
                if processed_memory.dynamic_fields:
                    field_count = len(processed_memory.dynamic_fields)
                    field_names = list(processed_memory.dynamic_fields.keys())
                    self.logger.debug(f"Extracted {field_count} dynamic fields: {field_names}")
                    self.logger.debug(f"Full dynamic fields: {json.dumps(processed_memory.dynamic_fields, indent=2, default=str)}")
            else:
                # Create basic memory without AI processing
                self.logger.info("AI unavailable - creating basic memory without processing")
                from info_agent.core.models import Memory
                processed_memory = Memory(
                    content=content.strip(),
                    title=title or self._generate_title(content.strip())
                )
                # Add basic dynamic fields
                processed_memory.dynamic_fields = {
                    'category': 'general',
                    'ai_processed': False,
                    'created_method': 'basic'
                }
            
            # Create in database (this also adds to vector store automatically)
            created_memory = self.repository.create(processed_memory)
            self.logger.info(f"Memory stored in database with ID: {created_memory.id}")
            if self.ai_available:
                self.logger.info(f"Memory automatically added to vector store during creation")
            
            self.logger.info(f"Successfully added memory: '{created_memory.title}'")
            return created_memory
            
        except Exception as e:
            self.logger.error(f"Failed to add memory: {e}")
            raise RepositoryError(f"Failed to add memory: {e}")
    
    def get_memory(self, memory_id: int) -> Optional[Memory]:
        """Get memory by ID."""
        return self.repository.get_by_id(memory_id)
    
    def search_memories(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """Search memories using text search."""
        return self.repository.search(query, limit=limit)
    
    def semantic_search_memories(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """Search memories using semantic similarity."""
        return self.repository.semantic_search(query, limit=limit)
    
    def hybrid_search_memories(self, query: str, limit: int = 20) -> List[MemorySearchResult]:
        """Search memories using combined text + semantic search with AI query enhancement."""
        try:
            # Process query with AI to extract search criteria (required)
            search_analysis = self.processor.process_search_query(query)
            self.logger.info(f"Processing search query: '{query}'")
            self.logger.debug(f"Search intent: {search_analysis.get('search_intent', 'Unknown')}")
            
            # Log detailed search analysis results
            categories = search_analysis.get('categories', [])
            people = search_analysis.get('people', [])
            places = search_analysis.get('places', [])
            field_filters = search_analysis.get('field_filters', {})
            self.logger.debug(f"Extracted search criteria - Categories: {categories}, People: {people}, Places: {places}")
            self.logger.debug(f"Field filters: {field_filters}")
            self.logger.debug(f"Full search analysis: {json.dumps(search_analysis, indent=2, default=str)}")
            
            # Use original query for hybrid search (not enhanced query)
            results = self.repository.hybrid_search(query, limit=limit)
            
            # Apply additional filtering based on extracted criteria
            self.logger.debug(f"Applying filters to {len(results)} search results")
            filtered_results = self._apply_search_filters(results, search_analysis, limit)
            
            self.logger.info(f"Smart hybrid search returned {len(filtered_results)} results")
            return filtered_results
                
        except Exception as e:
            self.logger.error(f"Hybrid search failed: {e}")
            raise RepositoryError(f"Search operation failed: {e}")
    
    def _apply_search_filters(self, results: List[MemorySearchResult], analysis: Dict[str, Any], limit: int) -> List[MemorySearchResult]:
        """Apply AI-extracted filters to search results."""
        try:
            filtered_results = []
            
            # Extract filter criteria
            categories = analysis.get('categories', [])
            people = analysis.get('people', [])
            places = analysis.get('places', [])
            field_filters = analysis.get('field_filters', {})
            
            for result in results:
                should_include = True
                
                # Check category filters
                if categories and result.memory.dynamic_fields:
                    memory_categories = result.memory.dynamic_fields.get('categories', [])
                    memory_category = result.memory.dynamic_fields.get('category', '')
                    if memory_categories or memory_category:
                        # Check if any memory category matches search categories
                        all_memory_cats = memory_categories if isinstance(memory_categories, list) else []
                        if memory_category:
                            all_memory_cats.append(memory_category)
                        
                        category_match = any(
                            any(search_cat.lower() in mem_cat.lower() or mem_cat.lower() in search_cat.lower() 
                                for mem_cat in all_memory_cats)
                            for search_cat in categories
                        )
                        if not category_match:
                            should_include = False
                
                # Check people filters
                if people and result.memory.dynamic_fields and should_include:
                    memory_people = result.memory.dynamic_fields.get('people', [])
                    if memory_people and isinstance(memory_people, list):
                        people_match = any(
                            any(search_person.lower() in mem_person.lower() or mem_person.lower() in search_person.lower()
                                for mem_person in memory_people)
                            for search_person in people
                        )
                        if not people_match:
                            should_include = False
                
                # Check places filters
                if places and result.memory.dynamic_fields and should_include:
                    memory_places = result.memory.dynamic_fields.get('places', [])
                    if memory_places and isinstance(memory_places, list):
                        places_match = any(
                            any(search_place.lower() in mem_place.lower() or mem_place.lower() in search_place.lower()
                                for mem_place in memory_places)
                            for search_place in places
                        )
                        if not places_match:
                            should_include = False
                
                # Apply custom field filters
                if field_filters and result.memory.dynamic_fields and should_include:
                    for field_name, field_value in field_filters.items():
                        memory_value = result.memory.dynamic_fields.get(field_name)
                        if memory_value:
                            if isinstance(memory_value, str):
                                if field_value.lower() not in memory_value.lower():
                                    should_include = False
                                    break
                            elif memory_value != field_value:
                                should_include = False
                                break
                
                if should_include:
                    filtered_results.append(result)
            
            # Limit results and sort by relevance
            filtered_results = filtered_results[:limit]
            
            # Log detailed filtering results
            filtered_count = len(filtered_results)
            excluded_count = len(results) - len(filtered_results)
            self.logger.debug(f"Filter results: {filtered_count} included, {excluded_count} excluded")
            self.logger.debug(f"Applied filters - Categories: {categories}, People: {people}, Places: {places}")
            self.logger.debug(f"Field filters: {field_filters}")
            
            if filtered_results:
                result_ids = [r.memory_id for r in filtered_results]
                self.logger.debug(f"Final filtered memory IDs: {result_ids}")
            
            return filtered_results
            
        except Exception as e:
            self.logger.warning(f"Filter application failed, returning unfiltered results: {e}")
            return results[:limit]
    
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
        """Get service statistics including vector store info."""
        stats = {'total_memories': self.repository.count()}
        
        # Add repository stats if available
        if hasattr(self.repository, 'get_statistics'):
            repo_stats = self.repository.get_statistics()
            stats.update(repo_stats)
        
        # Add vector store stats if available
        if hasattr(self.repository, 'get_vector_store_stats'):
            vector_stats = self.repository.get_vector_store_stats()
            stats['vector_store'] = vector_stats
        
        return stats
    
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
