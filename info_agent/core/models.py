"""
Data models for Info Agent.

This module defines the Memory data model and related data structures
for representing memory records in the application.
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import hashlib


@dataclass
class Memory:
    """
    Represents a memory record in the Info Agent system.
    
    This class handles both database representation and business logic
    for memory objects, including serialization and validation.
    """
    
    # Core identification
    id: Optional[int] = None
    
    # Core content fields
    title: str = ""
    content: str = ""
    summary: Optional[str] = None
    
    # AI-extracted dynamic fields (stored as JSON in database)
    dynamic_fields: Dict[str, Any] = field(default_factory=dict)
    
    # Vector embedding for semantic search
    embedding_vector: Optional[List[float]] = None
    
    # Metadata
    content_hash: Optional[str] = None
    word_count: int = 0
    search_text: Optional[str] = None
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Version tracking
    version: int = 1
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Auto-generate content hash if not provided
        if self.content and not self.content_hash:
            self.content_hash = self._generate_content_hash()
        
        # Auto-calculate word count if not provided
        if self.content and self.word_count == 0:
            self.word_count = len(self.content.split())
        
        # Generate search text for FTS indexing
        if self.content and not self.search_text:
            self.search_text = self._generate_search_text()
    
    def _generate_content_hash(self) -> str:
        """Generate SHA256 hash of content for deduplication."""
        content_bytes = self.content.encode('utf-8')
        return hashlib.sha256(content_bytes).hexdigest()
    
    def _generate_search_text(self) -> str:
        """Generate processed text for full-text search indexing."""
        # Combine title, content, and summary for search
        search_parts = [self.title, self.content]
        if self.summary:
            search_parts.append(self.summary)
        
        # Join and clean for search
        search_text = " ".join(search_parts).strip()
        # Remove extra whitespace and normalize
        return " ".join(search_text.split())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert Memory to dictionary for database storage."""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'dynamic_fields': json.dumps(self.dynamic_fields) if self.dynamic_fields else '{}',
            'embedding_vector': json.dumps(self.embedding_vector) if self.embedding_vector else None,
            'content_hash': self.content_hash,
            'word_count': self.word_count,
            'search_text': self.search_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'version': self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Memory':
        """Create Memory from dictionary (database row)."""
        # Parse JSON fields
        dynamic_fields = {}
        if data.get('dynamic_fields'):
            try:
                dynamic_fields = json.loads(data['dynamic_fields'])
            except json.JSONDecodeError:
                dynamic_fields = {}
        
        embedding_vector = None
        if data.get('embedding_vector'):
            try:
                embedding_vector = json.loads(data['embedding_vector'])
            except json.JSONDecodeError:
                embedding_vector = None
        
        # Parse timestamps
        created_at = None
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except (ValueError, TypeError):
                created_at = None
        
        updated_at = None
        if data.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(data['updated_at'])
            except (ValueError, TypeError):
                updated_at = None
        
        return cls(
            id=data.get('id'),
            title=data.get('title', ''),
            content=data.get('content', ''),
            summary=data.get('summary'),
            dynamic_fields=dynamic_fields,
            embedding_vector=embedding_vector,
            content_hash=data.get('content_hash'),
            word_count=data.get('word_count', 0),
            search_text=data.get('search_text'),
            created_at=created_at,
            updated_at=updated_at,
            version=data.get('version', 1)
        )
    
    @classmethod
    def from_row(cls, row: tuple, columns: List[str]) -> 'Memory':
        """Create Memory from database row tuple."""
        data = dict(zip(columns, row))
        return cls.from_dict(data)
    
    def update_dynamic_fields(self, new_fields: Dict[str, Any]) -> None:
        """Update dynamic fields, preserving existing data."""
        if not self.dynamic_fields:
            self.dynamic_fields = {}
        self.dynamic_fields.update(new_fields)
    
    def get_dynamic_field(self, field_name: str, default: Any = None) -> Any:
        """Get a specific dynamic field value."""
        return self.dynamic_fields.get(field_name, default)
    
    def has_dynamic_field(self, field_name: str) -> bool:
        """Check if a dynamic field exists and has a value."""
        return field_name in self.dynamic_fields and self.dynamic_fields[field_name] is not None
    
    def is_duplicate_of(self, other: 'Memory') -> bool:
        """Check if this memory is a duplicate of another based on content hash."""
        return (self.content_hash is not None and 
                other.content_hash is not None and 
                self.content_hash == other.content_hash)
    
    def get_preview(self, max_length: int = 100) -> str:
        """Get a preview of the memory content."""
        if not self.content:
            return ""
        
        if len(self.content) <= max_length:
            return self.content
        
        # Find a good break point (word boundary)
        preview = self.content[:max_length]
        last_space = preview.rfind(' ')
        
        if last_space > max_length * 0.7:  # If we find a space in the last 30%
            preview = preview[:last_space]
        
        return preview + "..."
    
    def validate(self) -> List[str]:
        """
        Validate memory data and return list of validation errors.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Required fields
        if not self.content.strip():
            errors.append("Content cannot be empty")
        
        if not self.title.strip():
            errors.append("Title cannot be empty")
        
        # Length constraints
        from info_agent.core.schema import SchemaConstants
        
        if len(self.content) > SchemaConstants.MAX_CONTENT_LENGTH:
            errors.append(f"Content too long (max {SchemaConstants.MAX_CONTENT_LENGTH} chars)")
        
        if len(self.title) > SchemaConstants.MAX_TITLE_LENGTH:
            errors.append(f"Title too long (max {SchemaConstants.MAX_TITLE_LENGTH} chars)")
        
        if self.summary and len(self.summary) > SchemaConstants.MAX_SUMMARY_LENGTH:
            errors.append(f"Summary too long (max {SchemaConstants.MAX_SUMMARY_LENGTH} chars)")
        
        # Dynamic fields validation
        if self.dynamic_fields:
            from info_agent.core.schema import MemoryFieldTypes
            if not MemoryFieldTypes.validate_dynamic_fields(self.dynamic_fields):
                errors.append("Invalid dynamic fields structure")
        
        # Embedding vector validation
        if self.embedding_vector:
            if not isinstance(self.embedding_vector, list):
                errors.append("Embedding vector must be a list")
            elif len(self.embedding_vector) != SchemaConstants.EMBEDDING_DIMENSIONS:
                errors.append(f"Embedding vector must have {SchemaConstants.EMBEDDING_DIMENSIONS} dimensions")
        
        return errors
    
    def is_valid(self) -> bool:
        """Check if memory is valid."""
        return len(self.validate()) == 0
    
    def __str__(self) -> str:
        """String representation for debugging."""
        preview = self.get_preview(50)
        return f"Memory(id={self.id}, title='{self.title}', preview='{preview}')"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (f"Memory(id={self.id}, title='{self.title}', "
                f"content_length={len(self.content)}, "
                f"dynamic_fields_count={len(self.dynamic_fields)}, "
                f"created_at={self.created_at})")


@dataclass
class MemorySearchResult:
    """
    Represents a search result with relevance scoring.
    """
    memory: Memory
    relevance_score: float = 0.0
    match_type: str = "unknown"  # "fts", "vector", "hybrid"
    matched_fields: List[str] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"SearchResult(score={self.relevance_score:.3f}, {self.memory})"


# Export main classes
__all__ = ['Memory', 'MemorySearchResult']
