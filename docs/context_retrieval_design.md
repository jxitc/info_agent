# Context Retrieval Design & Evaluation

## Problem Statement
- Triple retrieval system combining relational database (SQLite) + vector database (ChromaDB) + knowledge graph (SQLite-based)
- Need intelligent threshold filtering and confidence ranking across three sources
- Require comprehensive evaluation framework for recall/coverage

## Triple Retrieval Architecture

### Database Strengths & Weaknesses

**Relational Database (SQLite):**
- ✅ Exact matching, fast performance, ACID compliance, complex queries
- ❌ Rigid schema, no semantic understanding, exact text matching only

**Vector Database (ChromaDB):**  
- ✅ Semantic understanding, fuzzy matching, natural language queries
- ❌ Approximation, expensive computation, no exact filtering

**Knowledge Graph (SQLite-based):**
- ✅ Rich relationship modeling, multi-hop queries, entity disambiguation, leverages existing infrastructure
- ❌ Complex SQL for graph traversal, limited graph algorithms, performance for deep queries

## Threshold & Ranking Strategies

### 1. Triple Source Adaptive Thresholds
```python
def get_adaptive_thresholds(query, result_counts):
    has_exact_terms = bool(re.search(r'\b(ID|id|\d{4}-\d{2}-\d{2})\b', query))
    is_broad_query = len(query.split()) < 3
    has_few_results = sum(result_counts.values()) < 5
    is_relationship_query = any(indicator in query.lower() 
                               for indicator in ["who", "with whom", "connected to", "met", "discussed with"])
    
    if has_exact_terms:
        return {"sql_threshold": 0.8, "vector_threshold": 0.6, "graph_threshold": 0.5}
    elif is_relationship_query:
        return {"sql_threshold": 0.3, "vector_threshold": 0.4, "graph_threshold": 0.7}
    elif is_broad_query:
        return {"sql_threshold": 0.2, "vector_threshold": 0.3, "graph_threshold": 0.4}  
    elif has_few_results:
        return {"sql_threshold": 0.1, "vector_threshold": 0.2, "graph_threshold": 0.2}
    else:
        return {"sql_threshold": 0.5, "vector_threshold": 0.4, "graph_threshold": 0.5}
```

### 2. Triple Source Confidence Scoring
```python
def calculate_triple_confidence(result):
    # Original factors
    semantic_score = result.vector_similarity
    exact_score = 1.0 if result.exact_match else 0.7
    recency_boost = calculate_recency_factor(result.created_date)
    
    # New KG-specific factors
    graph_centrality = result.graph_centrality if result.from_graph else 0.5
    relationship_strength = result.relationship_confidence if result.from_graph else 0.5
    entity_confidence = result.entity_extraction_confidence if result.from_graph else 0.5
    
    # Source reliability with triple sources
    source_weights = {'sql': 1.0, 'vector': 0.8, 'graph': 0.9}
    source_weight = source_weights.get(result.source, 0.7)
    
    # Weighted combination (expanded)
    confidence = (
        semantic_score * 0.25 + exact_score * 0.20 + recency_boost * 0.15 +
        graph_centrality * 0.15 + relationship_strength * 0.10 + 
        entity_confidence * 0.10 + source_weight * 0.05
    )
    return min(confidence, 1.0)
```

### 3. Triple RRF with KG Integration
```python
def triple_search_with_rrf(query, max_results=10):
    # Stage 1: Smart source routing
    sources = triple_source_routing(query)
    
    # Stage 2: Parallel retrieval from active sources
    results = {}
    if 'sql' in sources:
        results['sql'] = search_database(query, limit=20)
    if 'vector' in sources:
        results['vector'] = search_vectors(query, limit=20)
    if 'graph' in sources:
        results['graph'] = search_knowledge_graph(query, limit=20)
    
    # Stage 3: Apply adaptive thresholds
    thresholds = get_adaptive_thresholds(query, {k: len(v) for k, v in results.items()})
    filtered_results = {}
    for source, source_results in results.items():
        threshold_key = f"{source}_threshold"
        filtered_results[source] = [r for r in source_results 
                                   if r.score > thresholds[threshold_key]]
    
    # Stage 4: Triple RRF combination
    combined_results = triple_rrf(filtered_results.get('sql', []), 
                                 filtered_results.get('vector', []),
                                 filtered_results.get('graph', []))
    
    # Stage 5: Enhanced confidence scoring & final ranking
    for result in combined_results:
        result.confidence = calculate_triple_confidence(result)
        result.source_diversity = count_sources(result)
    
    return sorted(combined_results, key=lambda x: x.confidence, reverse=True)[:max_results]

def triple_source_routing(query):
    """Smart routing to appropriate retrieval sources"""
    sources = ['sql', 'vector']  # Default sources
    
    # Add KG for relationship/entity queries
    if should_use_knowledge_graph(query):
        sources.append('graph')
    
    return sources
```

## Evaluation Framework

### Core Metrics
- **Traditional IR**: Recall@K, Precision@K, NDCG@K, MRR, MAP
- **RAG-Specific**: Context Precision, Context Recall, Faithfulness, Answer Relevance (RAGAS framework)
- **KG-Specific**: Entity Extraction Accuracy, Relation Extraction Accuracy, Path Quality, Graph Centrality Coverage
- **Custom**: Temporal Coverage, Category Diversity, Confidence Calibration, Source Diversity

## Implementation Architecture

### MCP Tool-Based Triple Retrieval System
```python
# MCP Tools for independent retrieval sources
@mcp_tool
def query_memories_structured(query_params) -> List[StructuredMemoryResult]:
    """SQLite-based structured queries with exact matching"""

@mcp_tool  
def query_memories_semantic(query_text, threshold) -> List[SemanticMemoryResult]:
    """ChromaDB-based semantic similarity search"""

@mcp_tool
def query_memories_graph(query_text, relationship_filters) -> List[GraphMemoryResult]:
    """SQLite-based knowledge graph relationship queries with recursive CTEs"""

@mcp_tool
def query_memories_hybrid(query_text, sources, use_rrf=True) -> List[RankedMemoryResult]:
    """Orchestrated triple retrieval with RRF ranking"""
```

### LangGraph Agent Orchestration
```python
from langgraph import StateGraph, END
from mcp import Client as MCPClient

class TripleRetrievalAgent:
    def __init__(self):
        self.mcp_client = MCPClient()
        self.graph = self.build_retrieval_workflow()
    
    def build_retrieval_workflow(self):
        workflow = StateGraph()
        
        # Core workflow nodes
        workflow.add_node("classify_query", self.classify_query_type)
        workflow.add_node("route_sources", self.determine_retrieval_sources)
        workflow.add_node("parallel_retrieval", self.execute_parallel_queries)
        workflow.add_node("rank_and_filter", self.apply_rrf_ranking)
        workflow.add_node("synthesize_response", self.create_user_response)
        
        # Workflow edges
        workflow.add_edge("classify_query", "route_sources")
        workflow.add_edge("route_sources", "parallel_retrieval")
        workflow.add_edge("parallel_retrieval", "rank_and_filter")
        workflow.add_edge("rank_and_filter", "synthesize_response")
        workflow.add_edge("synthesize_response", END)
        
        return workflow.compile()
    
    async def execute_parallel_queries(self, state):
        """Execute queries across selected sources in parallel"""
        query = state["user_query"]
        sources = state["selected_sources"]
        
        tasks = []
        if "structured" in sources:
            tasks.append(self.mcp_client.call_tool("query_memories_structured", query_params=query))
        if "semantic" in sources:
            tasks.append(self.mcp_client.call_tool("query_memories_semantic", query_text=query))
        if "graph" in sources:
            tasks.append(self.mcp_client.call_tool("query_memories_graph", query_text=query))
        
        results = await asyncio.gather(*tasks)
        return {"retrieval_results": results}
```

### Evaluation Framework Implementation
```python
class TripleRetrievalEvaluator:
    def __init__(self):
        self.metrics = {
            # Traditional IR metrics
            'recall@k': [1, 3, 5, 10],
            'precision@k': [1, 3, 5, 10], 
            'ndcg@k': [1, 3, 5, 10],
            'mrr': True,
            'map': True,
            
            # RAG-specific metrics (RAGAS)
            'context_precision': True,
            'context_recall': True,
            'faithfulness': True,
            'answer_relevance': True,
            
            # KG-specific metrics
            'entity_extraction_accuracy': True,
            'relationship_extraction_accuracy': True,
            'path_quality': True,
            'graph_centrality_coverage': True,
            
            # Triple retrieval metrics
            'source_diversity': True,
            'confidence_calibration': True,
            'adaptive_threshold_effectiveness': True
        }
    
    def evaluate_triple_approach(self, approach, queries, ground_truth):
        results = {}
        
        for query, expected in zip(queries, ground_truth):
            # Execute retrieval
            retrieved = approach.retrieve(query)
            
            # Calculate standard IR metrics
            ir_metrics = self.calculate_ir_metrics(retrieved, expected)
            
            # Calculate RAG metrics using RAGAS
            rag_metrics = self.calculate_ragas_metrics(retrieved, expected, query)
            
            # Calculate KG-specific metrics if graph results present
            kg_metrics = {}
            if any(r.source == 'graph' for r in retrieved):
                kg_metrics = self.calculate_kg_metrics(retrieved, expected)
            
            # Calculate triple retrieval metrics
            triple_metrics = self.calculate_triple_metrics(retrieved, expected)
            
            results[query] = {**ir_metrics, **rag_metrics, **kg_metrics, **triple_metrics}
        
        return self.aggregate_results(results)
    
    def calculate_kg_metrics(self, retrieved, expected):
        """Calculate knowledge graph specific metrics"""
        graph_results = [r for r in retrieved if r.source == 'graph']
        
        if not graph_results:
            return {}
        
        # Entity extraction accuracy
        extracted_entities = set(r.entities for r in graph_results)
        true_entities = set(expected.entities) if hasattr(expected, 'entities') else set()
        entity_precision = len(extracted_entities & true_entities) / len(extracted_entities) if extracted_entities else 0
        entity_recall = len(extracted_entities & true_entities) / len(true_entities) if true_entities else 0
        
        # Relationship extraction accuracy
        extracted_relations = set(r.relationships for r in graph_results)
        true_relations = set(expected.relationships) if hasattr(expected, 'relationships') else set()
        relation_precision = len(extracted_relations & true_relations) / len(extracted_relations) if extracted_relations else 0
        relation_recall = len(extracted_relations & true_relations) / len(true_relations) if true_relations else 0
        
        # Path quality (average path length for multi-hop queries)
        avg_path_length = np.mean([r.path_length for r in graph_results if hasattr(r, 'path_length')]) if graph_results else 0
        
        return {
            'entity_precision': entity_precision,
            'entity_recall': entity_recall,
            'relation_precision': relation_precision,
            'relation_recall': relation_recall,
            'avg_path_length': avg_path_length
        }
```

### Ground Truth Generation
```python
def create_evaluation_dataset():
    test_scenarios = {
        'exact_match': ["Meeting with Sarah on August 10", "ID 123"],
        'semantic': ["project deadlines", "team discussions"],
        'temporal': ["last week meetings", "recent updates"],
        'multi_hop': ["who mentioned API testing", "John's project comments"]
    }
    
    # LLM-assisted annotation + human validation
    ground_truth = {}
    for scenario, queries in test_scenarios.items():
        ground_truth[scenario] = generate_ground_truth_with_llm(queries)
    
    return test_scenarios, ground_truth
```

### A/B Testing Framework
```python
def compare_retrieval_approaches():
    approaches = {
        'sql_only': SQLOnlyRetrieval(),
        'vector_only': VectorOnlyRetrieval(),
        'graph_only': GraphOnlyRetrieval(),
        'hybrid_rrf': RRFHybridRetrieval(),
        'triple_rrf': TripleRRFRetrieval(),
        'triple_adaptive': AdaptiveTripleRetrieval()
    }
    
    for name, approach in approaches.items():
        # Standard metrics work for all approaches
        standard_metrics = evaluator.evaluate_approach(approach, test_queries, ground_truth)
        
        # KG-specific metrics for graph-enabled approaches
        if 'graph' in approach.sources or name.startswith('triple'):
            kg_metrics = evaluate_knowledge_graph_quality(approach.graph_results, ground_truth)
            standard_metrics.update(kg_metrics)
        
        log_metrics(name, standard_metrics)
    
    return generate_comparison_report(approaches)
```

## Industry Best Practices (2024)

### Key Frameworks
- **RAGAS**: Reference-free RAG evaluation with automated metrics
- **RankRAG**: Instruction-tuned LLM for context ranking + generation
- **Azure RRF**: Production-grade hybrid search implementation
- **Neo4j GraphRAG**: LLM-powered knowledge graph construction and retrieval
- **GraphRAG**: Microsoft's global/local retrieval with community summaries

## Knowledge Graph Implementation

### SQLite-Based Graph Storage
```sql
-- Extend existing SQLite schema with relationship tables
CREATE TABLE entities (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL, -- 'person', 'location', 'organization', 'time'
    memory_id INTEGER,
    confidence REAL DEFAULT 1.0,
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

CREATE TABLE relationships (
    id INTEGER PRIMARY KEY,
    from_entity_id INTEGER,
    to_entity_id INTEGER,
    relation_type TEXT NOT NULL, -- 'MEETS', 'LOCATED_AT', 'WORKS_ON'
    memory_id INTEGER,
    confidence REAL DEFAULT 1.0,
    FOREIGN KEY (from_entity_id) REFERENCES entities(id),
    FOREIGN KEY (to_entity_id) REFERENCES entities(id),
    FOREIGN KEY (memory_id) REFERENCES memories(id)
);

CREATE INDEX idx_entities_name ON entities(name);
CREATE INDEX idx_relationships_from ON relationships(from_entity_id);
CREATE INDEX idx_relationships_to ON relationships(to_entity_id);
```

### KG Construction Pipeline
```python
class SQLiteKnowledgeGraph:
    def __init__(self, db_connection):
        self.db = db_connection
        self.llm_client = OpenAIClient()
    
    def extract_and_store_memory(self, memory_text, memory_id):
        # LLM-based entity/relation extraction
        extraction_prompt = f"""
        Extract entities and relationships from: "{memory_text}"
        Example: "Xiao will meet Lijie at college hall tomorrow"
        
        Return JSON:
        {{
            "entities": [
                {{"name": "Xiao", "type": "person"}},
                {{"name": "Lijie", "type": "person"}},
                {{"name": "college_hall", "type": "location"}}
            ],
            "relationships": [
                {{"from": "Xiao", "relation": "MEETS", "to": "Lijie"}},
                {{"from": "meeting", "relation": "LOCATED_AT", "to": "college_hall"}}
            ]
        }}
        """
        
        extracted_data = self.llm_client.extract(extraction_prompt)
        self._store_entities_and_relationships(extracted_data, memory_id)
    
    def search_knowledge_graph(self, query):
        strategies = [
            self._entity_match_search(query),      # Direct entity matching
            self._relationship_traversal_search(query),  # Multi-hop SQL queries
            self._entity_co_occurrence_search(query)     # Entities appearing together
        ]
        return self._combine_and_rank(strategies)
    
    def _relationship_traversal_search(self, query, max_hops=2):
        """Multi-hop relationship search using recursive CTEs"""
        
        # Extract entities from query
        query_entities = self._extract_entities_from_text(query)
        
        results = []
        for entity in query_entities:
            # Recursive CTE for multi-hop traversal
            sql = """
            WITH RECURSIVE entity_connections(entity_id, related_entity_id, relation_path, hop_count) AS (
                -- Base case: direct connections
                SELECT e1.id, e2.id, r.relation_type, 1
                FROM entities e1
                JOIN relationships r ON e1.id = r.from_entity_id
                JOIN entities e2 ON r.to_entity_id = e2.id
                WHERE e1.name = ?
                
                UNION ALL
                
                -- Recursive case: extend path
                SELECT ec.entity_id, e.id, 
                       ec.relation_path || '->' || r.relation_type, 
                       ec.hop_count + 1
                FROM entity_connections ec
                JOIN relationships r ON ec.related_entity_id = r.from_entity_id
                JOIN entities e ON r.to_entity_id = e.id
                WHERE ec.hop_count < ?
            )
            SELECT DISTINCT 
                e.name as related_entity,
                ec.relation_path,
                ec.hop_count,
                m.id as memory_id,
                m.title,
                m.content
            FROM entity_connections ec
            JOIN entities e ON ec.related_entity_id = e.id
            JOIN memories m ON e.memory_id = m.id
            ORDER BY ec.hop_count, e.name;
            """
            
            cursor = self.db.execute(sql, (entity, max_hops))
            results.extend(cursor.fetchall())
        
        return results
```

### Scalability Assessment
- **Feasible Scale**: 1K-100K memories, 10K-1M entities
- **Query Types**: 2-3 hop relationship traversals
- **Use Cases**: "Who have I met through John?", "What projects involve Sarah and APIs?"

### Implementation Priority & Technology Evolution

#### Phase 1: SQLite-Based Graph (Recommended Start)
1. **Phase 1A**: Basic dual RRF (SQL + Vector) with fixed thresholds
2. **Phase 1B**: Add SQLite-based KG with entity/relation extraction
3. **Phase 1C**: Triple RRF with adaptive thresholds and smart routing
4. **Phase 1D**: Enhanced confidence scoring with KG factors

**Advantages**: 
- Builds on existing SQLite infrastructure
- No additional dependencies or database management
- Sufficient for personal scale (1K-100K memories)
- Easy deployment and backup

#### Phase 2: Neo4j Migration (Future Enhancement)
5. **Phase 2A**: Evaluate SQLite KG performance at scale
6. **Phase 2B**: Migrate to Neo4j if complex graph algorithms needed
7. **Phase 2C**: Leverage Neo4j LLM Graph Builder ecosystem
8. **Phase 2D**: Advanced graph analytics and community detection

**Migration Triggers**:
- Multi-hop queries become performance bottlenecks (>3 hops)
- Need for advanced graph algorithms (PageRank, community detection)
- Desire to use Neo4j's LLM ecosystem tools
- Scale exceeds 100K memories with complex relationships

## Next Steps

### Immediate Implementation (Phase 1)
- Implement basic dual RRF hybrid search in `info_agent/core/search_engine.py`
- Add SQLite schema extensions for entities and relationships tables
- Create LLM-based entity/relation extraction pipeline
- Build SQLite-based KG query functions with recursive CTEs
- Create triple retrieval evaluation module in `info_agent/evaluation/`
- Add enhanced confidence scoring with KG-specific factors
- Integration with existing CLI/API endpoints for triple search

### Future Considerations (Phase 2)
- Evaluate Neo4j migration based on performance and complexity needs
- Leverage Neo4j LLM Graph Builder if migrating
- Advanced graph algorithms for community detection and centrality
- Integration with GraphRAG ecosystem tools

## Technology Comparison

| Aspect | SQLite-based KG | Neo4j KG |
|---------|-----------------|----------|
| **Setup Complexity** | Minimal (extend existing) | High (new database) |
| **Dependencies** | None (existing SQLite) | Neo4j server + drivers |
| **Query Complexity** | High (complex SQL CTEs) | Low (intuitive Cypher) |
| **Performance (1K-10K)** | Excellent | Good |
| **Performance (100K+)** | Limited | Excellent |
| **Graph Algorithms** | Manual implementation | Built-in library |
| **LLM Integration** | Manual | Rich ecosystem |
| **Deployment** | Simple | Complex |
| **Migration Path** | Export to Neo4j later | N/A |

## References
- **SQLite Graph Techniques**: Recursive CTEs, graph traversal in SQL
- **Traditional KG**: Named Entity Recognition, Relation Extraction, crowdsourcing approaches
- **Modern LLM-KG**: Neo4j LLM Graph Builder, GraphRAG (Microsoft), LangChain LLMGraphTransformer
- **Evaluation**: RAGAS framework, ARES, Azure RRF, NDCG/MRR metrics
- **Research**: Google Context Sufficiency, RankRAG instruction-tuned ranking
