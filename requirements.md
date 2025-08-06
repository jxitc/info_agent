# AI Information Agent - Requirements Document

## Project Overview

An AI-powered system that accepts diverse human inputs (text, images, documents), processes and structures the information, stores it in a database, and enables natural language querying of the collected data.

Note the system development will be incremental and divdided into several milestones:

- M0 (protytoping): basic functionality validation build, could be on CLI, for internal own usage
- M1: on top of M0 prototype, add basic network endpoint implementation and allow very limited network based access from very few test users 
- M2: to be defined later ... 

In this doc, each functionality will be marked as one of the milestone in the very benginning.


## Core Functionality


### Input Processing
- **Text Input** (M0): Accept free-form text including chat history, notes, descriptions
- **Image Processing** (M1): OCR capabilities for extracting text from images (receipts, documents, IDs)
- **Document Upload** (M1): Support for common document formats (PDF, DOC, images, email files)
- **Multi-Source Processing** (M2): Extract structured data (booking information, personal details, contact info) from any input type (text, image, or document)


### Data Processing & Storage

#### Information Unit ("Memory") Structure (M0)

The core data structure is a **Memory** unit that contains:

**Core Fields:**
- **ID**: Unique identifier for the memory
- **Title**: AI-generated descriptive title for UI display
- **Description**: AI-generated summary for context and RAG embedding
- **Content**: Original input content (text, OCR result, etc.)
- **Creation Time**: Timestamp of memory creation
- **Last Modified**: Timestamp of last update
- **Version**: Version number for tracking updates
- **Source Type**: Input type (text, image, document, email)

**Dynamic Structured Fields:**
- **Entities**: Extracted people, places, dates, amounts (dynamically identified)
- **Categories**: AI-assigned categories/tags
- **Custom Fields**: AI can create new fields as needed (e.g., "meeting_participants", "expense_amount")
- **Relationships**: Links to related memories

**Search & Retrieval:**
- **Title/Description Embeddings**: Vector embeddings for semantic search (RAG)
- **Structured Query Support**: Enable filtering by entities, dates, categories
- **Hybrid Retrieval**: Combine embedding-based and structured field-based search

#### Processing Pipeline
- **Information Extraction** (M0): Use AI to identify and extract key information from unstructured input and saved in some database
- **Dynamic Field Creation** (M0): AI agent creates new structured fields when encountering new data types
- **Database Storage** (M0): Persist memories with both structured fields (in relational DB) and vector embeddings 


More advanced processing is on M1 and later:
- **Entity Recognition** (M1): Identify people, places, dates, amounts, and other relevant entities
- **Memory Deduplication** (M1): Detect and merge similar memories or create relationships
- **Version Management**: Update existing memories with new information while preserving history
- **Data Validation**: Ensure data integrity and handle edge cases


### Query Interface
- **Natural Language Queries** (M0): an CLI based database to allow users to search using conversational language
- **CLI interface** (M0): the interface should start with CLI providing local access, for quick debugging and development purpose
- **Contextual Understanding**: Understand intent and context in user queries
- **Result Presentation**: Return relevant information in user-friendly format


More advanced processing is on M1 and later:
- **RESTFul API** (M1): similar to CLI interface, provide RESTFul API to allow access from different end points
- **Query History** (M1): Track and learn from user query patterns


### Scalability (M1)
(all scalability functionality starts from M1)
- Handle growing volumes of data and users
- Efficient storage and retrieval mechanisms
- Caching strategies for frequently accessed data

### Security & Privacy (M2)
(all scalability functionality starts from M2 or even later)
- Data encryption at rest and in transit
- User authentication and authorization
- Audit logging for data access
- Compliance with privacy regulations
