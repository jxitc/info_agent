# Architecture Discussions - Info Agent

This document captures architectural discussions and design decisions for future reference.

## Agentic MCP Tool Architecture Refactoring

### Problem
Current implementation tightly couples database and vector store operations in the repository layer. This goes against proper agentic design principles.

### Better Approach
Separate into independent MCP tools that agents can choose from:

1. **Database Memory Tool**:
   ```python
   @tool
   def query_structured_memories(filters, limit):
       """Query memories by structured fields (dates, categories, metadata)"""
       return db.search_by_fields(filters)
   ```

2. **Vector Similarity Tool**:
   ```python
   @tool  
   def find_similar_memories(query_text, limit):
       """Find semantically similar memories using embeddings"""
       return vector_store.semantic_search(query_text)
   ```

### Benefits
- **Tool Independence**: Each tool has single responsibility
- **Agent Choice**: LLM decides which tool(s) to use based on query type
- **Flexible Combination**: Agent can combine results intelligently
- **MCP Compliance**: Each tool independently callable
- **Reasoning Transparency**: Agent explains tool selection

### Example Agent Behavior
```
User: "Find memories about meetings last week"
Agent: 
1. "last week" = time filter → use Database Tool (structured query)
2. "meetings" = semantic concept → use Vector Tool (similarity search)  
3. Combine and rank results based on both relevance and recency
```

### Implementation Timing
This refactoring should be done after M0 prototype completion to avoid disrupting current implementation schedule.

### Discussion Context
- Date: August 8, 2025
- Context: After completing Section 2.2 Vector Store Setup
- Participants: User feedback on tight coupling concerns
- Decision: Defer to post-M0 for proper agentic architecture