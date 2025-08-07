"""
Database schema definitions for Info Agent.

This module defines the SQLite database schema for storing memories
and related data structures.
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class DatabaseSchema:
    """Database schema configuration and SQL definitions."""
    
    # Schema version for migration tracking
    VERSION = "1.0.0"
    
    # Core tables SQL definitions
    TABLES = {
        "memories": """
            CREATE TABLE IF NOT EXISTS memories (
                -- Primary key and core identification
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                
                -- Core content fields
                title TEXT NOT NULL,                    -- AI-generated or user-provided title
                content TEXT NOT NULL,                  -- Original text content from user
                summary TEXT,                          -- AI-generated summary
                
                -- Dynamic fields stored as JSON
                dynamic_fields TEXT NOT NULL DEFAULT '{}',  -- JSON object for AI-extracted fields
                
                -- Vector embedding for semantic search
                embedding_vector TEXT,                  -- JSON array of embedding values
                
                -- Metadata and tracking
                content_hash TEXT UNIQUE,              -- Hash of content for deduplication
                word_count INTEGER DEFAULT 0,          -- Word count for analytics
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Indexing and performance
                search_text TEXT,                      -- Processed text for full-text search
                
                -- Version tracking for updates
                version INTEGER DEFAULT 1
            )
        """,
        
        "schema_migrations": """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version TEXT NOT NULL UNIQUE,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        """,
        
        "search_index": """
            CREATE VIRTUAL TABLE IF NOT EXISTS search_index 
            USING fts5(
                title, 
                content, 
                summary, 
                search_text,
                content=memories,
                content_rowid=id
            )
        """
    }
    
    # Indexes for performance optimization
    INDEXES = {
        "idx_memories_created_at": "CREATE INDEX IF NOT EXISTS idx_memories_created_at ON memories(created_at DESC)",
        "idx_memories_updated_at": "CREATE INDEX IF NOT EXISTS idx_memories_updated_at ON memories(updated_at DESC)", 
        "idx_memories_content_hash": "CREATE INDEX IF NOT EXISTS idx_memories_content_hash ON memories(content_hash)",
        "idx_memories_word_count": "CREATE INDEX IF NOT EXISTS idx_memories_word_count ON memories(word_count)",
    }
    
    # Triggers for automatic updates
    TRIGGERS = {
        "update_memories_timestamp": """
            CREATE TRIGGER IF NOT EXISTS update_memories_timestamp 
            AFTER UPDATE ON memories
            BEGIN
                UPDATE memories 
                SET updated_at = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
        """,
        
        "update_search_index": """
            CREATE TRIGGER IF NOT EXISTS update_search_index_insert
            AFTER INSERT ON memories
            BEGIN
                INSERT INTO search_index(rowid, title, content, summary, search_text)
                VALUES (NEW.id, NEW.title, NEW.content, NEW.summary, NEW.search_text);
            END;
            
            CREATE TRIGGER IF NOT EXISTS update_search_index_update
            AFTER UPDATE ON memories
            BEGIN
                UPDATE search_index 
                SET title = NEW.title, 
                    content = NEW.content, 
                    summary = NEW.summary,
                    search_text = NEW.search_text
                WHERE rowid = NEW.id;
            END;
            
            CREATE TRIGGER IF NOT EXISTS update_search_index_delete
            AFTER DELETE ON memories
            BEGIN
                DELETE FROM search_index WHERE rowid = OLD.id;
            END
        """
    }


class MemoryFieldTypes:
    """
    Definition of dynamic field types that can be extracted by AI.
    
    These define the structure of JSON data stored in the dynamic_fields column.
    """
    
    # Standard field types that AI can extract
    FIELD_DEFINITIONS = {
        "people": {
            "type": "list",
            "description": "Names of people mentioned",
            "example": ["John Smith", "Sarah Johnson"]
        },
        "locations": {
            "type": "list", 
            "description": "Places, addresses, or locations mentioned",
            "example": ["New York", "Conference Room B", "123 Main St"]
        },
        "dates": {
            "type": "list",
            "description": "Dates, times, or temporal references", 
            "example": ["2024-03-15", "next Friday", "2pm tomorrow"]
        },
        "organizations": {
            "type": "list",
            "description": "Companies, institutions, or groups",
            "example": ["OpenAI", "Stanford University", "Marketing Team"]
        },
        "actions": {
            "type": "list",
            "description": "Tasks, actions, or things to do",
            "example": ["Call client", "Review document", "Schedule meeting"]
        },
        "topics": {
            "type": "list", 
            "description": "Main topics or subjects discussed",
            "example": ["machine learning", "budget planning", "product launch"]
        },
        "urgency": {
            "type": "string",
            "description": "Urgency level extracted from content",
            "example": "high",
            "values": ["low", "medium", "high", "urgent"]
        },
        "sentiment": {
            "type": "string",
            "description": "Overall sentiment of the content", 
            "example": "positive",
            "values": ["negative", "neutral", "positive"]
        },
        "category": {
            "type": "string",
            "description": "AI-determined category",
            "example": "work",
            "values": ["work", "personal", "learning", "health", "finance", "other"]
        },
        "entities": {
            "type": "object",
            "description": "Named entities with types",
            "example": {
                "PERSON": ["John Smith"],
                "ORG": ["OpenAI"], 
                "DATE": ["March 15"],
                "MONEY": ["$1000"]
            }
        }
    }
    
    @classmethod
    def get_empty_fields(cls) -> Dict[str, Any]:
        """Get empty dynamic fields structure."""
        return {
            "people": [],
            "locations": [],
            "dates": [],
            "organizations": [], 
            "actions": [],
            "topics": [],
            "urgency": None,
            "sentiment": None,
            "category": None,
            "entities": {}
        }
    
    @classmethod
    def validate_dynamic_fields(cls, fields: Dict[str, Any]) -> bool:
        """Validate dynamic fields structure."""
        try:
            for field_name, field_value in fields.items():
                if field_name not in cls.FIELD_DEFINITIONS:
                    continue
                    
                field_def = cls.FIELD_DEFINITIONS[field_name]
                expected_type = field_def["type"]
                
                if expected_type == "list" and not isinstance(field_value, list):
                    return False
                elif expected_type == "string" and field_value is not None and not isinstance(field_value, str):
                    return False  
                elif expected_type == "object" and not isinstance(field_value, dict):
                    return False
                    
            return True
        except Exception:
            return False


class SchemaConstants:
    """Constants for database schema and operations."""
    
    # Database file configuration
    DATABASE_NAME = "info_agent.db"
    DEFAULT_DB_PATH = "~/.info_agent/data"
    
    # Content constraints
    MAX_TITLE_LENGTH = 200
    MAX_CONTENT_LENGTH = 100000  # 100KB max content
    MAX_SUMMARY_LENGTH = 1000
    
    # Performance limits
    MAX_SEARCH_RESULTS = 1000
    DEFAULT_SEARCH_LIMIT = 20
    
    # Hash algorithm for content deduplication
    CONTENT_HASH_ALGORITHM = "sha256"
    
    # Embedding vector dimensions (for text-embedding-3-small)
    EMBEDDING_DIMENSIONS = 1536


def get_schema_info() -> Dict[str, Any]:
    """
    Get comprehensive schema information for documentation and validation.
    
    Returns:
        Dictionary containing complete schema information
    """
    return {
        "version": DatabaseSchema.VERSION,
        "tables": list(DatabaseSchema.TABLES.keys()),
        "indexes": list(DatabaseSchema.INDEXES.keys()),
        "triggers": list(DatabaseSchema.TRIGGERS.keys()),
        "dynamic_fields": MemoryFieldTypes.FIELD_DEFINITIONS,
        "constants": {
            "database_name": SchemaConstants.DATABASE_NAME,
            "max_content_length": SchemaConstants.MAX_CONTENT_LENGTH,
            "embedding_dimensions": SchemaConstants.EMBEDDING_DIMENSIONS
        }
    }


# Export key components for easy imports
__all__ = [
    'DatabaseSchema',
    'MemoryFieldTypes', 
    'SchemaConstants',
    'get_schema_info'
]