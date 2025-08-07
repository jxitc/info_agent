# Database Schema Design - Info Agent

This document describes the SQLite database schema for the Info Agent M0 prototype.

## Overview

The database uses SQLite with a hybrid approach:
- **Structured fields** for core memory metadata and indexing
- **JSON dynamic_fields** for AI-extracted information that varies by content
- **Full-text search** using SQLite FTS5 for semantic queries
- **Vector storage** for embeddings (as JSON arrays)

## Core Tables

### `memories` Table

The primary table storing all memory records:

```sql
CREATE TABLE memories (
    -- Primary key and identification
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Core content (always present)
    title TEXT NOT NULL,                    -- AI-generated or user title
    content TEXT NOT NULL,                  -- Original user input
    summary TEXT,                          -- AI-generated summary
    
    -- Dynamic AI-extracted data (JSON)
    dynamic_fields TEXT NOT NULL DEFAULT '{}',
    
    -- Vector embedding for semantic search
    embedding_vector TEXT,                  -- JSON array [0.1, 0.2, ...]
    
    -- Metadata
    content_hash TEXT UNIQUE,              -- SHA256 for deduplication  
    word_count INTEGER DEFAULT 0,
    search_text TEXT,                      -- Preprocessed for FTS
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Versioning
    version INTEGER DEFAULT 1
);
```

### `schema_migrations` Table

Tracks database schema versions:

```sql
CREATE TABLE schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);
```

### `search_index` (FTS5 Virtual Table)

Full-text search index:

```sql
CREATE VIRTUAL TABLE search_index USING fts5(
    title, 
    content, 
    summary, 
    search_text,
    content=memories,
    content_rowid=id
);
```

## Dynamic Fields Structure

The `dynamic_fields` column stores JSON with AI-extracted information:

```json
{
    "people": ["John Smith", "Sarah Johnson"],
    "locations": ["New York", "Conference Room B"],
    "dates": ["2024-03-15", "next Friday"],
    "organizations": ["OpenAI", "Marketing Team"],
    "actions": ["Call client", "Review document"],
    "topics": ["machine learning", "budget planning"],
    "urgency": "high",
    "sentiment": "positive", 
    "category": "work",
    "entities": {
        "PERSON": ["John Smith"],
        "ORG": ["OpenAI"],
        "DATE": ["March 15"]
    }
}
```

## Indexes

Performance indexes on frequently queried columns:

- `idx_memories_created_at` - For chronological listing
- `idx_memories_updated_at` - For recent updates
- `idx_memories_content_hash` - For deduplication
- `idx_memories_word_count` - For analytics

## Triggers

Automatic database maintenance:

1. **Timestamp Updates** - Auto-update `updated_at` on record changes
2. **Search Index Sync** - Keep FTS5 index synchronized with main table

## Design Decisions

### Why JSON for Dynamic Fields?

1. **Flexibility** - AI can extract different fields per memory
2. **Schema Evolution** - Can add new field types without migrations  
3. **SQLite JSON Support** - Native JSON functions in SQLite 3.38+
4. **Query Capability** - Can query within JSON: `JSON_EXTRACT(dynamic_fields, '$.people')`

### Why Hybrid Search?

1. **Full-Text Search** - Natural language queries via FTS5
2. **Structured Queries** - Search within dynamic fields
3. **Vector Search** - Semantic similarity (future enhancement)
4. **Performance** - Each method optimized for different query types

### Vector Storage Strategy

- Store embeddings as JSON arrays in TEXT column
- Convert to binary format for similarity calculations
- Separate vector table possible in future for performance

## Example Queries

### Basic Operations
```sql
-- Insert new memory
INSERT INTO memories (title, content, dynamic_fields) 
VALUES ('Meeting Notes', 'Met with John...', '{"people": ["John"]}');

-- Get recent memories
SELECT * FROM memories ORDER BY created_at DESC LIMIT 10;

-- Search by content hash (deduplication)
SELECT * FROM memories WHERE content_hash = ?;
```

### Dynamic Field Queries
```sql
-- Find memories mentioning specific person
SELECT * FROM memories 
WHERE JSON_EXTRACT(dynamic_fields, '$.people') LIKE '%John%';

-- Get high urgency items
SELECT * FROM memories 
WHERE JSON_EXTRACT(dynamic_fields, '$.urgency') = 'high';

-- Work-related memories
SELECT * FROM memories 
WHERE JSON_EXTRACT(dynamic_fields, '$.category') = 'work';
```

### Full-Text Search
```sql
-- Natural language search
SELECT m.* FROM memories m 
JOIN search_index s ON m.id = s.rowid 
WHERE search_index MATCH 'project deadline';
```

## Storage Considerations

- **Content Limits**: 100KB max per memory content
- **Embedding Size**: ~6KB per 1536-dimension vector
- **JSON Overhead**: ~1-2KB per dynamic_fields object
- **Estimated Size**: ~10KB average per memory record

## Migration Strategy

The schema supports versioned migrations:
1. Check current version in `schema_migrations`
2. Apply incremental migration scripts
3. Record new version and timestamp

This design provides flexibility for AI-extracted data while maintaining performance for common queries.