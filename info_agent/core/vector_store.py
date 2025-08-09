"""
Vector store implementation using ChromaDB for semantic search capabilities.

This module provides vector storage and similarity search functionality
for the Info Agent system using ChromaDB as the backend.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import hashlib

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions

from .models import Memory, MemorySearchResult


logger = logging.getLogger(__name__)


class VectorStoreConfig:
    """Configuration for ChromaDB vector store."""
    
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize vector store configuration.
        
        Args:
            data_dir: Directory for persistent storage. If None, uses default.
        """
        if data_dir is None:
            data_dir = os.path.expanduser("~/.info_agent/data")
        
        self.data_dir = Path(data_dir)
        self.collection_name = "memories"
        self.embedding_model = "all-MiniLM-L6-v2"  # Lightweight, good performance
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)


class VectorStore:
    """ChromaDB-based vector store for semantic search."""
    
    def __init__(self, config: Optional[VectorStoreConfig] = None):
        """Initialize the vector store.
        
        Args:
            config: Vector store configuration. If None, uses defaults.
        """
        self.config = config or VectorStoreConfig()
        self._client = None
        self._collection = None
        self._embedding_function = None
        
        logger.info(f"Vector store initialized with data dir: {self.config.data_dir}")
    
    def _get_client(self) -> chromadb.ClientAPI:
        """Get or create ChromaDB client."""
        if self._client is None:
            try:
                # Create persistent client
                self._client = chromadb.PersistentClient(
                    path=str(self.config.data_dir / "chromadb"),
                    settings=Settings(
                        anonymized_telemetry=False,  # Disable telemetry for privacy
                        allow_reset=True
                    )
                )
                logger.debug("ChromaDB client created successfully")
            except Exception as e:
                logger.error(f"Failed to create ChromaDB client: {e}")
                raise
        
        return self._client
    
    def _get_embedding_function(self):
        """Get or create embedding function."""
        if self._embedding_function is None:
            try:
                # Use sentence transformers embedding function
                self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=self.config.embedding_model
                )
                logger.debug(f"Embedding function created with model: {self.config.embedding_model}")
            except Exception as e:
                logger.error(f"Failed to create embedding function: {e}")
                # Fallback to default embedding function
                self._embedding_function = embedding_functions.DefaultEmbeddingFunction()
                logger.warning("Using default embedding function as fallback")
        
        return self._embedding_function
    
    def _get_collection(self):
        """Get or create the memories collection."""
        if self._collection is None:
            try:
                client = self._get_client()
                embedding_function = self._get_embedding_function()
                
                # Try to get existing collection first
                try:
                    self._collection = client.get_collection(
                        name=self.config.collection_name,
                        embedding_function=embedding_function
                    )
                    logger.debug(f"Retrieved existing collection: {self.config.collection_name}")
                except Exception as e:
                    # Collection doesn't exist, create it
                    logger.debug(f"Collection doesn't exist, creating: {e}")
                    try:
                        self._collection = client.create_collection(
                            name=self.config.collection_name,
                            embedding_function=embedding_function,
                            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
                        )
                        logger.info(f"Created new collection: {self.config.collection_name}")
                    except Exception as create_error:
                        logger.error(f"Failed to create collection: {create_error}")
                        raise
                    
            except Exception as e:
                logger.error(f"Failed to get/create collection: {e}")
                raise
        
        return self._collection
    
    def _create_metadata_for_chromadb(self, memory: Memory) -> Dict[str, Any]:
        """Create ChromaDB-compatible metadata from Memory object.
        
        ChromaDB metadata values must be strings, numbers, or booleans.
        This method flattens the Memory object into compatible format.
        """
        metadata = {
            "memory_id": memory.id,
            "title": memory.title or "",
            "word_count": memory.word_count,
            "version": memory.version,
            "created_at": memory.created_at.isoformat() if memory.created_at else "",
            "updated_at": memory.updated_at.isoformat() if memory.updated_at else "",
            "content_hash": memory.content_hash or ""
        }
        
        # Add dynamic fields to metadata if available
        if memory.dynamic_fields:
            for key, value in memory.dynamic_fields.items():
                # ChromaDB metadata values must be strings, numbers, or booleans
                if isinstance(value, (str, int, float, bool)):
                    metadata[f"dynamic_{key}"] = value
                else:
                    metadata[f"dynamic_{key}"] = str(value)
        
        return metadata
    
    def _create_memory_from_metadata(self, metadata: Dict[str, Any], document: str) -> Memory:
        """Create a Memory object from ChromaDB metadata and document.
        
        Args:
            metadata: ChromaDB metadata dictionary
            document: The stored document text
            
        Returns:
            Memory object reconstructed from stored data
        """
        from datetime import datetime
        
        # Parse timestamps
        created_at = None
        if metadata.get('created_at'):
            try:
                created_at = datetime.fromisoformat(metadata['created_at'])
            except (ValueError, TypeError):
                pass
                
        updated_at = None
        if metadata.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(metadata['updated_at'])
            except (ValueError, TypeError):
                pass
        
        # Extract dynamic fields (they're prefixed with 'dynamic_')
        dynamic_fields = {}
        for key, value in metadata.items():
            if key.startswith('dynamic_'):
                field_name = key[8:]  # Remove 'dynamic_' prefix
                dynamic_fields[field_name] = value
        
        # Extract title and content from document
        # Document format is "title\ncontent" or just "content"
        lines = document.split('\n', 1)
        if len(lines) > 1 and lines[0] == metadata.get('title', ''):
            title = lines[0]
            content = lines[1]
        else:
            title = metadata.get('title', '')
            content = document
        
        return Memory(
            id=metadata.get('memory_id'),
            title=title,
            content=content,
            dynamic_fields=dynamic_fields,
            content_hash=metadata.get('content_hash'),
            word_count=metadata.get('word_count', 0),
            created_at=created_at,
            updated_at=updated_at,
            version=metadata.get('version', 1)
        )
    
    def add_memory(self, memory: Memory) -> bool:
        """Add a memory to the vector store.
        
        Args:
            memory: Memory object to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            collection = self._get_collection()
            
            # Create document ID (use memory ID for consistency)
            doc_id = f"memory_{memory.id}"
            
            # Prepare content for embedding (title + content)
            content_text = f"{memory.title}\n{memory.content}" if memory.title else memory.content
            
            # Create metadata for ChromaDB (flattened, no complex types)
            metadata = self._create_metadata_for_chromadb(memory)
            
            # Add to collection
            collection.add(
                documents=[content_text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.debug(f"Added memory {memory.id} to vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add memory {memory.id} to vector store: {e}")
            return False
    
    def update_memory(self, memory: Memory) -> bool:
        """Update an existing memory in the vector store.
        
        Args:
            memory: Updated memory object
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # For ChromaDB, we need to delete and re-add to update
            doc_id = f"memory_{memory.id}"
            collection = self._get_collection()
            
            # Check if document exists
            try:
                collection.get(ids=[doc_id])
                # If we get here, document exists, so delete it first
                collection.delete(ids=[doc_id])
                logger.debug(f"Deleted existing memory {memory.id} from vector store")
            except Exception:
                # Document doesn't exist, that's fine
                pass
            
            # Add the updated memory
            return self.add_memory(memory)
            
        except Exception as e:
            logger.error(f"Failed to update memory {memory.id} in vector store: {e}")
            return False
    
    def delete_memory(self, memory_id: int) -> bool:
        """Delete a memory from the vector store.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            collection = self._get_collection()
            doc_id = f"memory_{memory_id}"
            
            collection.delete(ids=[doc_id])
            logger.debug(f"Deleted memory {memory_id} from vector store")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete memory {memory_id} from vector store: {e}")
            return False
    
    def search_memories(
        self, 
        query: str, 
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[MemorySearchResult]:
        """Search for memories using semantic similarity.
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of MemorySearchResult objects with metadata and similarity scores
        """
        try:
            collection = self._get_collection()
            
            # Prepare where clause for filtering
            where_clause = None
            if filters:
                where_clause = {}
                for key, value in filters.items():
                    if key.startswith('dynamic_'):
                        where_clause[key] = value
                    else:
                        where_clause[key] = value
            
            # Perform similarity search
            results = collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_clause,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results as MemorySearchResult objects
            search_results = []
            if results['ids'] and results['ids'][0]:  # Check if we have results
                for i in range(len(results['ids'][0])):
                    metadata = results['metadatas'][0][i]
                    document = results['documents'][0][i]
                    distance = results['distances'][0][i]
                    
                    # Create a minimal Memory object from metadata
                    memory = self._create_memory_from_metadata(metadata, document)
                    
                    # Create content preview
                    content_preview = document[:200] + "..." if len(document) > 200 else document
                    
                    # Create search result
                    search_result = MemorySearchResult(
                        memory=memory,
                        relevance_score=1.0 - distance,  # Convert distance to similarity
                        match_type="semantic",
                        matched_fields=["content", "title"],
                        snippet=content_preview
                    )
                    search_results.append(search_result)
            
            logger.debug(f"Vector search for '{query}' returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search memories with query '{query}': {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self._get_collection()
            count = collection.count()
            
            return {
                "total_documents": count,
                "collection_name": self.config.collection_name,
                "embedding_model": self.config.embedding_model,
                "data_directory": str(self.config.data_dir)
            }
            
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {
                "total_documents": 0,
                "collection_name": self.config.collection_name,
                "embedding_model": self.config.embedding_model,
                "data_directory": str(self.config.data_dir),
                "error": str(e)
            }
    
    def reset_collection(self) -> bool:
        """Reset (delete all data from) the collection.
        
        WARNING: This will delete all stored vectors!
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            client = self._get_client()
            
            # Delete existing collection
            try:
                client.delete_collection(name=self.config.collection_name)
                logger.info(f"Deleted collection: {self.config.collection_name}")
            except ValueError:
                # Collection doesn't exist, that's fine
                pass
            
            # Reset internal references
            self._collection = None
            
            # Create new collection
            self._get_collection()
            logger.info(f"Reset collection: {self.config.collection_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset collection: {e}")
            return False


# Global vector store instance
_vector_store_instance = None


def get_vector_store(config: Optional[VectorStoreConfig] = None) -> VectorStore:
    """Get the global vector store instance (singleton pattern).
    
    Args:
        config: Optional configuration for first initialization
        
    Returns:
        VectorStore instance
    """
    global _vector_store_instance
    
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore(config)
        logger.info("Global vector store instance created")
    
    return _vector_store_instance


def initialize_vector_store(config: Optional[VectorStoreConfig] = None) -> bool:
    """Initialize the vector store (useful for setup/testing).
    
    Args:
        config: Optional configuration
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        vector_store = get_vector_store(config)
        stats = vector_store.get_collection_stats()
        logger.info(f"Vector store initialized successfully: {stats}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize vector store: {e}")
        return False
