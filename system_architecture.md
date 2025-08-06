# System Architecture - M0 (Prototype)

## Overview

This document defines the high-level system architecture for the AI Information Agent M0 prototype. The focus is on basic functionality validation with CLI-based interface for internal usage.

## Core Components

### 1. CLI Interface Layer
- **Command Parser**: Interprets user commands and input text
- **Context Manager**: Maintains conversation context within a single CLI session (simplified for single-user M0 prototype)
- **Output Formatter**: Formats query results for display
- **Basic Configuration**: Simple config file handling (advanced configuration management deferred to M1)

### 2. AI Processing Engine
- **LLM Integration**: Interface to large language model for text processing
- **Information Extractor**: Extracts key information from unstructured text
- **Field Generator**: Creates dynamic structured fields based on content
- **Query Understanding**: Built into LLM Integration for natural language query interpretation
- **Embedding Generator**: Creates vector embeddings for semantic search 

### 3. Memory Management System
- **Memory Creator**: Constructs Memory units from processed input
- **Field Handler**: Simple dynamic field processing integrated into Memory Creator (no dedicated schema management needed)
- **Relationship Tracker**: Manages links between related memories (deferred to M1, basic version stores relationships in JSON field)

### 4. Data Storage Layer
- **Relational Database**: Stores structured memory fields and metadata
  - Single table: memories (with JSON column for dynamic fields)
- **Vector Store**: Stores embeddings for semantic search
- **Database Interface**: Critical abstraction layer for data operations, enabling future storage backend changes without code refactoring

### 5. Search and Retrieval System
- **Hybrid Search Engine**: Combines semantic and structured search
- **Query Optimizer**: Optimizes search queries for performance
- **Result Ranker**: Ranks results by relevance and recency

## Data Flow Architecture

```
[User Input] → [CLI Interface] → [AI Processing Engine]
                                        ↓
[Memory Management] ← [AI Processing Engine]
        ↓
[Data Storage Layer] ← [Memory Management]
        ↓
[Search & Retrieval] ← [Query from CLI]
        ↓
[CLI Interface] ← [Formatted Results]
```

## Core Data Structures

### Memory Schema (M0)
```
Memory {
  id: UUID
  title: String (AI-generated)
  description: String (AI-generated summary)
  content: String (original input)
  created_at: Timestamp
  updated_at: Timestamp
  version: Integer
  source_type: Enum(text)
  
  // Dynamic fields stored as JSON in single column
  dynamic_fields: JSON
  
  // Vector embedding for semantic search
  embedding: Vector<Float>
}
```

## Technology Stack (M0)

### Core Components
- **Programming Language**: Python 
- **CLI Framework**: Click or argparse
- **Database**: SQLite (simple, local storage)
- **Vector Store**: ChromaDB or FAISS (embedded)
- **AI/ML**: OpenAI API 

### Development Tools
- **Testing**: pytest
- **Logging**: Python logging module
- **Configuration**: YAML or JSON config files

## File Structure
```
info_agent/
├── cli/
│   ├── __init__.py
│   ├── commands.py
│   └── interface.py
├── core/
│   ├── __init__.py
│   ├── memory.py
│   ├── processor.py
│   └── search.py
├── storage/
│   ├── __init__.py
│   ├── database.py
│   └── vector_store.py
├── ai/
│   ├── __init__.py
│   ├── llm_client.py
│   └── embeddings.py
├── tests/
└── main.py
```

## Key Interfaces

### CLI Commands (M0)
- `add <text>`: Add new memory from text input
- `search <query>`: Search memories using natural language
- `list`: List recent memories
- `show <id>`: Display specific memory details

### Internal APIs
- `MemoryManager.create(content, source_type)`
- `SearchEngine.query(text, filters)`
- `AIProcessor.extract_info(content)`
- `VectorStore.similarity_search(embedding, k)`

## Deployment Model (M0)

### Local Installation
- Single-user desktop application
- SQLite database in user directory
- Configuration files in user home
- Local AI model or API key configuration

### Data Storage
- Local SQLite database: `~/.info_agent/memories.db`
- Vector embeddings: `~/.info_agent/vectors/`
- Basic configuration: `~/.info_agent/config.yaml`
- Logs: `~/.info_agent/logs/`

## Performance Considerations (M0)

### Optimization Goals
- Sub-second response time for search queries
- Handle up to 10,000 memories efficiently (single user in M0)
- Minimal memory footprint
- Fast startup time

## Error Handling and Reliability (M0)

### Error Recovery
- Graceful degradation when AI services unavailable
- Local data backup and recovery
- Input validation and sanitization
- Clear error messages for user guidance

### Logging Strategy
- Debug logs for development
- User action logs for troubleshooting
- Error logs with stack traces
- Performance metrics logging

## Future Expansion Notes

The M0 architecture is designed with extensibility in mind to support future milestones:

### M1 Extension Points
- **Network Layer**: Add REST API server alongside CLI interface
- **Multi-user Support**: Extend database schema for user separation
- **Advanced Processing**: Add entity recognition and deduplication modules
- **Scalability**: Replace SQLite with PostgreSQL, add Redis caching

### M2+ Extension Points
- **Security Layer**: Authentication, authorization, and encryption modules
- **Multi-source Input**: Image processing and document upload components
- **Advanced AI**: Proactive reminder system and enhanced query understanding
- **Enterprise Features**: Role-based access control and audit logging

The modular design ensures that new components can be added without major refactoring of the core M0 functionality.
