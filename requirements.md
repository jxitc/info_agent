# AI Information Agent - Requirements Document

## Project Overview

An AI-powered system that accepts diverse human inputs (text, images, documents), processes and structures the information, stores it in a database, and enables natural language querying of the collected data.

Note that system development will be incremental and divided into several milestones:

- M0 (prototyping): Basic functionality validation build, could be CLI-based, for internal usage
- M1: On top of M0 prototype, add basic network endpoint implementation and allow very limited network-based access from a few test users 
- M2: To be defined later... 

In this document, each functionality will be marked with its corresponding milestone at the beginning.


## Core Functionality


### Input Processing
- **Text Input** (M0): Accept free-form text including chat history, notes, descriptions, and personal observations
- **Image Processing** (M1): OCR capabilities for extracting text from images (receipts, documents, IDs, handwritten notes, screenshots)
- **Document Upload** (M1): Support for common document formats (PDF, DOC, DOCX, images, email files, plain text files)
- **Multi-Source Processing** (M2): Extract structured data (booking information, personal details, contact info, financial transactions, meeting notes) from any input type (text, image, or document)


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
- **Information Extraction** (M0): Use AI to identify and extract key information from unstructured input and save it in a database
- **Dynamic Field Creation** (M0): AI agent creates new structured fields when encountering new data types
- **Database Storage** (M0): Persist memories with both structured fields (in relational DB) and vector embeddings for semantic search 


More advanced processing is on M1 and later:
- **Entity Recognition** (M1): Identify people, places, dates, amounts, and other relevant entities
- **Memory Deduplication** (M1): Detect and merge similar memories or create relationships
- **Version Management** (M1): Update existing memories with new information while preserving history
- **Data Validation** (M1): Ensure data integrity and handle edge cases


### Query Interface
- **Natural Language Queries** (M0): A CLI-based interface to allow users to search using conversational language
- **CLI Interface** (M0): The interface should start with CLI providing local access, for quick debugging and development purposes
- **Contextual Understanding** (M0): Understand intent and context in user queries
- **Result Presentation** (M0): Return relevant information in user-friendly format with proper formatting and relevance ranking


More advanced processing is on M1 and later:
- **RESTful API** (M1): Similar to CLI interface, provide RESTful API to allow access from different endpoints
- **Query History** (M1): Track and learn from user query patterns
- **Proactive event reminder** (M2): instead of reactively answer users' question, the system should be able to setup the proactive reminder at proper time point


### Scalability (M1)
(all scalability functionality starts from M1)
- Handle growing volumes of data and users with horizontal scaling capabilities
- Efficient storage and retrieval mechanisms with optimized indexing strategies
- Caching strategies for frequently accessed data and query results

### Security & Privacy (M2)
(all security functionality starts from M2 or even later)
- Data encryption at rest and in transit using industry-standard algorithms
- User authentication and authorization with role-based access control
- Audit logging for data access and system operations
- Compliance with privacy regulations (GDPR, CCPA) including data deletion and export capabilities
