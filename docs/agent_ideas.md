# AI Agent System Design - Info Agent

## Overview

Building on the existing memory storage foundation, we propose an AI Agent system that utilizes stored memories to assist users with daily life tasks through intelligent information retrieval and contextual assistance.

## Core Concept

The AI Agent acts as a personal assistant that:
1. **Understands user requests** in natural language
2. **Searches relevant memories** using both semantic and structured queries
3. **Provides contextual assistance** based on retrieved information
4. **Takes proactive actions** when appropriate

## Use Cases & Examples

### 1. Schedule Management
**User Request**: "I want to schedule a meeting with Sarah next Tuesday at 2pm"

**Agent Process**:
- Query memories for existing Tuesday appointments
- Check for conflicts around 2pm
- Retrieve Sarah's contact information and meeting preferences
- Suggest alternative times if conflicts exist

**Response**: "I found you have a dentist appointment at 1:30pm on Tuesday. Sarah prefers morning meetings based on your previous interactions. Would 10am work instead?"

### 2. Document & Information Retrieval
**User Request**: "What's my passport number?"

**Agent Process**:
- Search memories for documents containing "passport"
- Extract structured information (numbers, expiry dates)
- Present formatted results with context

**Response**: "Your passport number is ABC123456789, expires June 2029. I also found your renewal reminder memory from last month."

### 3. Contextual Reminders
**User Request**: "Remind me about the project deadline"

**Agent Process**:
- Search for memories containing "deadline" and "project"
- Identify relevant project context
- Present timeline and related tasks

**Response**: "The web redesign project deadline is Friday, August 15th. You have 3 pending tasks: final review, client approval, and deployment preparation."

## Technical Architecture

### MCP Tool-Based Design

Following the architectural discussion in `docs/discussion.md`, we implement independent MCP tools that agents can compose:

#### Triple Retrieval MCP Tools

```python
# 1. Structured Query Tool (Relational Database)
@mcp_tool
def query_memories_structured(
    date_range: Optional[DateRange] = None,
    categories: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    limit: int = 10,
    confidence_threshold: float = 0.5
) -> List[StructuredMemoryResult]:
    """Query memories using structured criteria from SQLite"""
    
# 2. Semantic Search Tool (Vector Database)
@mcp_tool
def query_memories_semantic(
    query_text: str,
    similarity_threshold: float = 0.7,
    limit: int = 5
) -> List[SemanticMemoryResult]:
    """Find semantically similar memories using ChromaDB embeddings"""
    
# 3. Knowledge Graph Query Tool (Neo4j)
@mcp_tool
def query_memories_graph(
    query_text: str,
    relationship_types: Optional[List[str]] = None,
    entity_filters: Optional[Dict[str, str]] = None,
    max_hops: int = 2,
    limit: int = 5
) -> List[GraphMemoryResult]:
    """Query memories using knowledge graph relationships and entities"""

# 4. Triple Retrieval Orchestrator Tool
@mcp_tool
def query_memories_hybrid(
    query_text: str,
    sources: List[str] = ["structured", "semantic", "graph"],
    use_adaptive_thresholds: bool = True,
    max_results: int = 10
) -> List[RankedMemoryResult]:
    """Orchestrate parallel queries across all three sources with RRF ranking"""

# 5. Entity Extraction & KG Construction Tool
@mcp_tool
def extract_and_store_entities(
    memory_text: str,
    memory_id: int,
    entity_types: List[str] = ["person", "location", "time", "organization"],
    store_in_graph: bool = True
) -> EntityExtractionResult:
    """Extract entities and relationships, store in knowledge graph"""
```

#### Specialized Assistant Tools

```python
# 4. Schedule Conflict Checker
@mcp_tool  
def check_schedule_conflicts(
    proposed_time: datetime,
    duration_minutes: int = 60,
    buffer_minutes: int = 15
) -> ScheduleConflictResult:
    """Check for scheduling conflicts and suggest alternatives"""
    
# 5. Document Retriever
@mcp_tool
def find_document_info(
    document_type: str,  # "passport", "license", "insurance", etc.
    info_requested: str  # "number", "expiry", "full_details"
) -> DocumentInfo:
    """Retrieve specific document information from memories"""
    
# 6. Contact Manager
@mcp_tool
def get_contact_context(
    person_name: str,
    context_type: str = "all"  # "contact_info", "meeting_history", "preferences"
) -> ContactContext:
    """Retrieve comprehensive context about a person"""
```

### Multi-Agent Architecture

#### Primary Agent: Personal Assistant
- **Role**: Main interface, request understanding, response coordination
- **Capabilities**: Natural language processing, task routing, response synthesis
- **Tools**: All memory and assistant tools

#### Specialized Sub-Agents

1. **Schedule Agent**
   - **Role**: Calendar management, meeting coordination, conflict resolution
   - **Tools**: Triple retrieval hybrid, graph relationship queries, schedule conflict checker
   - **KG Capability**: "Who has availability for meetings with the API team next week?"
   
2. **Information Agent**  
   - **Role**: Document retrieval, fact finding, entity disambiguation
   - **Tools**: All three retrieval sources, entity extraction, document retriever
   - **KG Capability**: "Find my passport info and related travel documents"
   
3. **Context Agent**
   - **Role**: Relationship mapping, historical context, pattern discovery
   - **Tools**: Knowledge graph queries, semantic search, temporal analysis
   - **KG Capability**: "Show me connections between John, the API project, and recent meetings"

## Implementation Phases

### Phase 1: Triple Retrieval MCP Foundation (Post-M0)
- [ ] Refactor existing repository into triple retrieval MCP tools
- [ ] Implement structured query tool (SQLite) with advanced filtering
- [ ] Enhance semantic search tool (ChromaDB) with confidence scoring
- [ ] Add knowledge graph tool (Neo4j) with entity/relationship extraction
- [ ] Create hybrid orchestrator tool with RRF ranking

### Phase 2: Evaluation & Optimization Framework
- [ ] Implement comprehensive evaluation pipeline (RAGAS, NDCG, MRR)
- [ ] Create A/B testing framework for retrieval approaches
- [ ] Add KG-specific metrics (entity accuracy, relationship quality)
- [ ] Build ground truth generation with LLM assistance
- [ ] Implement adaptive threshold optimization

### Phase 3: Basic Agent Framework with Smart Routing
- [ ] Implement personal assistant agent with LangGraph orchestration
- [ ] Add intelligent source routing (when to use which retrieval method)
- [ ] Create request classification with relationship/entity detection
- [ ] Build response synthesis with confidence communication
- [ ] Test with complex use cases (multi-hop queries, relationship discovery)

### Phase 4: Specialized Multi-Agent System
- [ ] Implement schedule management agent with graph relationship queries
- [ ] Add information retrieval agent with entity disambiguation
- [ ] Create context agent for temporal relationship mapping
- [ ] Build proactive suggestion system using graph centrality

### Phase 5: Advanced Learning & Optimization
- [ ] Add continuous evaluation and model improvement
- [ ] Implement user feedback integration for ranking optimization
- [ ] Create cross-memory pattern recognition using graph algorithms
- [ ] Build conversational context with entity/relationship persistence

## Technical Considerations

### MCP Integration Strategy

```python
# Agent orchestration with triple retrieval MCP tools
class PersonalAssistantAgent:
    def __init__(self, mcp_client):
        self.mcp = mcp_client
        self.available_tools = [
            "query_memories_structured",
            "query_memories_semantic",
            "query_memories_graph", 
            "query_memories_hybrid",
            "extract_and_store_entities",
            "check_schedule_conflicts",
            "find_document_info",
            "get_contact_context"
        ]
    
    async def handle_request(self, user_input: str) -> AgentResponse:
        # 1. Classify request type
        request_type = await self.classify_request(user_input)
        
        # 2. Plan tool usage
        tool_plan = await self.plan_tool_usage(request_type, user_input)
        
        # 3. Execute tools via MCP
        results = await self.execute_tool_plan(tool_plan)
        
        # 4. Synthesize response
        return await self.synthesize_response(results, user_input)
```

### Multi-Agent Communication

```python
# Agent coordination protocol
class AgentCoordinator:
    def __init__(self):
        self.agents = {
            "schedule": ScheduleAgent(),
            "information": InformationAgent(),
            "context": ContextAgent()
        }
    
    async def delegate_request(self, request: UserRequest) -> AgentResponse:
        # Determine which specialized agents to involve
        relevant_agents = self.select_agents(request)
        
        # Coordinate parallel execution
        agent_results = await asyncio.gather(*[
            agent.process(request) for agent in relevant_agents
        ])
        
        # Merge and prioritize results
        return self.merge_agent_responses(agent_results)
```

### Triple Retrieval Data Flow Architecture

```
User Request ("Who did I meet about the API project last week?")
    ↓
Personal Assistant Agent (LangGraph orchestration)
    ↓
Smart Source Routing & Query Classification
    ↓ (parallel execution)
┌──────────────────┬──────────────────┬──────────────────┐
│  MCP Tool 1      │  MCP Tool 2      │  MCP Tool 3      │
│  (SQL Structured │  (Vector Semantic│  (Neo4j Graph    │
│   Query)         │   Search)        │   Relationships) │
│  - time filters  │  - "API project" │  - Person→MEETS  │
│  - last week     │  - meetings      │  - Project→API   │
└──────────────────┴──────────────────┴──────────────────┘
    ↓
Triple RRF Ranking & Confidence Scoring
    ↓
Result Synthesis with Source Diversity & Entity Context
    ↓
Formatted Response: "You met with Sarah and John about the API project last Tuesday. 
Sarah discussed authentication features (high confidence), John mentioned testing concerns (medium confidence)."
```

## Example Interactions

### Complex Schedule Management
```
User: "Set up a 1-hour meeting with the development team next week to discuss the API project"

Agent Process:
1. Extract entities: "development team", "next week", "1 hour", "API project"
2. Query memories for team member contacts
3. Check availability for all team members next week
4. Find relevant API project context
5. Suggest optimal meeting time
6. Prepare meeting agenda based on project memories

Response: "I found 3 development team members: Alice, Bob, and Charlie. Based on their previous availability patterns, Tuesday 10am-11am works for everyone. I've also pulled together the latest API project status from your memories to create an agenda."
```

### Proactive Information Management
```
User: "I need to travel next month"

Agent Process:
1. Search memories for travel documents
2. Check passport expiry date
3. Look for previous travel preferences
4. Identify potential requirements (visas, vaccinations)

Response: "Your passport expires in 3 months - you might want to renew it before traveling. Based on your previous trips, you prefer window seats and usually book hotels near city centers. Do you need me to check visa requirements for your destination?"
```

## Success Metrics

1. **Response Accuracy**: Correct information retrieval rate
2. **Context Relevance**: User satisfaction with suggested context
3. **Time Savings**: Reduction in manual information lookup
4. **Proactive Value**: Successful prevention of conflicts/issues
5. **Learning Effectiveness**: Improvement in suggestions over time

## Integration with Existing System

### Backward Compatibility
- Maintain all existing CLI and web interface functionality
- Add agent capabilities as optional enhancement layer
- Ensure MCP tools work independently and with agents

### Gradual Enhancement
- Start with simple document retrieval scenarios
- Add complexity incrementally (schedule management, proactive suggestions)
- Preserve user control and transparency throughout

### Configuration Options
```yaml
agent_settings:
  enabled: true
  proactive_suggestions: true
  confidence_threshold: 0.8
  max_context_memories: 20
  specialized_agents:
    schedule: true
    information: true
    context: true
```

## Future Enhancements

1. **Cross-Platform Integration**: Calendar apps, email, contacts
2. **Voice Interface**: Natural language voice commands
3. **Mobile Notifications**: Proactive alerts and reminders
4. **Collaborative Features**: Shared memories and agent assistance
5. **Advanced Learning**: Pattern recognition and predictive assistance

## Framework Selection & Technology Stack

### Recommended Open-Source Framework

**Primary Choice: LangGraph + MCP**

Based on comprehensive research of 2025 agent frameworks, we recommend:

- **LangGraph**: Graph-based workflow orchestration with stateful management
- **MCP (Model Context Protocol)**: Standardized tool connectivity layer
- **Benefits**: Industry standard adoption, visual debugging, precise control over complex workflows

### Framework Comparison Analysis

| Framework | Pros | Cons | Best For |
|-----------|------|------|----------|
| **LangGraph** ✅ | Complex workflows, visual debugging, MCP support | Steeper learning curve | Schedule conflict + document retrieval scenarios |
| **CrewAI** | Simple setup, role-based agents | No parallel execution, sequential only | Quick prototyping |
| **Semantic Kernel** | Enterprise ready, Microsoft ecosystem | .NET-focused | Production deployment |
| **AutoGen** | Natural conversation flow | Not production-ready, rapid changes | Research/experimentation |

### MCP Integration Advantage

**Critical 2025 Industry Trend**: MCP is rapidly becoming the standard for AI agent tool connectivity:

- **Major Adoption**: OpenAI (March 2025), Google DeepMind (April 2025), Microsoft (May 2025)
- **Framework Compatibility**: Works seamlessly with LangChain, LangGraph, CrewAI as tool layer
- **Perfect Fit**: Our memory tools (structured query, semantic search, entity extraction) align exactly with MCP's design purpose
- **Ecosystem Growth**: Over 1,000 MCP servers available by February 2025

### Recommended Architecture Implementation

```python
# Hybrid approach: LangGraph for orchestration + MCP for tools
from langgraph import StateGraph, END
from mcp import Client as MCPClient

class InfoAgentWorkflow:
    def __init__(self):
        self.mcp_client = MCPClient()  # Connect to memory MCP tools
        self.graph = self.build_workflow_graph()
    
    def build_workflow_graph(self):
        workflow = StateGraph()
        workflow.add_node("classify_request", self.classify_request)
        workflow.add_node("query_memories", self.query_memories_via_mcp) 
        workflow.add_node("synthesize_response", self.synthesize_response)
        
        # Define workflow edges
        workflow.add_edge("classify_request", "query_memories")
        workflow.add_edge("query_memories", "synthesize_response")
        workflow.add_edge("synthesize_response", END)
        
        return workflow.compile()
    
    async def query_memories_via_mcp(self, state):
        # Use MCP tools for memory operations
        results = await self.mcp_client.call_tool(
            "find_similar_memories",
            query_text=state["user_query"],
            limit=5
        )
        return {"memory_results": results}
```

### Alternative Framework Options

**For Different Development Priorities:**

1. **Quick MVP/Prototyping**: CrewAI
   - Simple team-based setup
   - Rapid development
   - Limited to sequential workflows

2. **Enterprise Production**: Semantic Kernel
   - Microsoft-backed stability
   - Enterprise security features
   - Multi-language support (Python, C#, Java)

3. **Research/Experimentation**: AutoGen
   - Conversational multi-agent approach
   - Natural language agent communication
   - **Warning**: Not production-ready, undergoing rapid changes

### Technology Stack Summary

```yaml
Recommended Stack:
  orchestration: LangGraph
  tool_connectivity: MCP (Model Context Protocol)  
  llm_client: OpenAI SDK / Anthropic SDK
  memory_backend: SQLite + ChromaDB (existing)
  web_interface: Flask (existing)
  
Alternative Stacks:
  quick_prototype: CrewAI + MCP
  enterprise: Semantic Kernel + MCP
  research: AutoGen (with migration plan to Semantic Kernel)
```

### Implementation Strategy

**Phase 1**: Start with LangGraph + MCP foundation
- Leverage existing memory infrastructure  
- Build MCP tools for current memory operations
- Create simple workflow graphs for basic agent behavior

**Phase 2**: Expand with specialized agents
- Implement schedule, information, and context agents
- Use LangGraph's multi-agent coordination capabilities
- Maintain MCP tool independence

**Phase 3**: Advanced features
- Add conversational memory and context persistence
- Implement proactive suggestions and learning
- Scale with additional MCP tools and agent specializations

This approach positions Info Agent at the forefront of 2025 AI agent architecture while building on proven, industry-standard technologies.

## LangGraph Learning Ramp-Up Plan

### 📚 Step 1: Core Concepts and Introduction

**Official Documentation & Getting Started**
- **Main Documentation**: https://langchain-ai.github.io/langgraph/
- **Official GitHub Repository**: https://github.com/langchain-ai/langgraph
- **Quick Start Guide**: https://langchain-ai.github.io/langgraph/concepts/why-langgraph/

**Key Concepts to Understand First:**
- Graph structure and state management
- Node and edge definitions
- Stateful workflow orchestration
- Streaming support for real-time agent reasoning

### 🎥 Step 2: Video Learning Resources

**Primary Video Tutorials (2024-2025):**

1. **LangChain Academy Course** (Most Recommended)
   - **URL**: https://academy.langchain.com/courses/intro-to-langgraph
   - **Focus**: Official structured course for building agents with LangGraph orchestration
   - **Duration**: Self-paced, comprehensive

2. **Tech with Tim Advanced Tutorial** (47 minutes)
   - **Focus**: Advanced AI agent systems, production-ready applications
   - **Coverage**: Core features, environment setup, API tokens, simple & complex chatbots
   - **Why Useful**: Explains why LangGraph is more professional than LangChain/LlamaIndex

3. **IBM Practical Tutorial** (25 minutes)
   - **Focus**: Build AI agent for transcription/summarization
   - **Tech Stack**: JavaScript, Next.js, wxflows, Ollama integration
   - **Useful For**: Understanding real-world application patterns

### 📖 Step 3: Hands-On Written Tutorials

**Beginner-Friendly Tutorials:**

1. **DataCamp Tutorial** (June 2024)
   - **URL**: https://www.datacamp.com/tutorial/langgraph-tutorial
   - **Focus**: Core concepts with practical examples
   - **Strengths**: Structured approach to graph coordination

2. **Analytics Vidhya Tutorial** (May 2025)
   - **URL**: https://www.analyticsvidhya.com/blog/2025/05/langgraph-tutorial-for-beginners/
   - **Focus**: Complete code examples, managing multiple LLMs
   - **Benefits**: Hands-on approach with full implementations

3. **Data Science Dojo Tutorial** (February 2025)
   - **Focus**: Building chatbots and AI agent workflows
   - **Practical**: Detailed implementation guide

### 🎯 Step 4: How LangGraph Specifically Helps Your Info Agent Project

#### **Problem-Solution Mapping for Your Use Case:**

**1. Complex Decision Workflows**
```
Your Challenge: "Should I schedule this meeting based on existing appointments?"

LangGraph Solution:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Parse Request   │ →  │ Query Memories  │ →  │ Check Conflicts │
│ (extract time,  │    │ (find existing  │    │ (analyze and    │
│  person, topic) │    │  appointments)  │    │  suggest alts)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**2. Multi-Step Information Retrieval**
```
Your Challenge: "Find my passport number and check if it expires soon"

LangGraph Solution:
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Classify Query  │ →  │ Search Documents│ →  │ Extract & Warn  │
│ (document type: │    │ (semantic +     │    │ (parse number,  │
│  passport)      │    │  structured)    │    │  check expiry)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**3. Parallel Information Gathering**
```
Your Challenge: "Plan a team meeting about the API project"

LangGraph Parallel Processing:
                    ┌─────────────────┐
                    │ Parse Request   │
                    └─────────┬───────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
┌───────▼───────┐    ┌────────▼────────┐    ┌──────▼──────┐
│ Find Team      │    │ Get Availability│    │ Get Project │
│ Members        │    │ (calendar check)│    │ Context     │
└───────┬───────┘    └────────┬────────┘    └──────┬──────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼───────┐
                    │ Synthesize Plan │
                    └─────────────────┘
```

#### **Key LangGraph Benefits for Info Agent:**

1. **State Management**: Perfect for tracking conversation context across multiple memory queries
2. **Visual Debugging**: See exactly how your agent makes decisions (crucial for debugging memory retrieval)
3. **Streaming Support**: Real-time feedback as agent searches through memories
4. **Tool Integration**: Natural fit for your MCP memory tools
5. **Conditional Logic**: Handle different request types with different workflows

#### **Your Learning Path for Info Agent Context:**

**Week 1**: Basic concepts and simple linear workflows
```python
# Simple Info Agent workflow
from langgraph import StateGraph, END

workflow = StateGraph()
workflow.add_node("understand_request", parse_user_input)
workflow.add_node("search_memories", query_memory_database)  
workflow.add_node("format_response", create_user_response)

workflow.add_edge("understand_request", "search_memories")
workflow.add_edge("search_memories", "format_response")
workflow.add_edge("format_response", END)
```

**Week 2**: Conditional flows and decision making
```python
# Add conditional logic for different request types
def route_request(state):
    if "schedule" in state["request"]:
        return "schedule_agent"
    elif "document" in state["request"]:
        return "document_agent"
    else:
        return "general_search"

workflow.add_conditional_edges("understand_request", route_request)
```

**Week 3**: Multi-agent coordination and parallel processing
```python
# Parallel memory search (semantic + structured)
workflow.add_node("semantic_search", semantic_memory_search)
workflow.add_node("structured_search", structured_memory_search)

# Run both searches in parallel, then combine results
from langgraph import START
workflow.add_edge(START, "semantic_search")
workflow.add_edge(START, "structured_search")
workflow.add_edge(["semantic_search", "structured_search"], "combine_results")
```

### 🚀 Quick Start Implementation Plan

**Phase 1 (Week 1)**: Replace one existing CLI command with LangGraph
```python
# Convert your current `search` command to use LangGraph
# Start with: User input → Memory query → Response formatting
```

**Phase 2 (Week 2)**: Add conditional logic for different request types
```python  
# Handle: schedule queries, document queries, general queries differently
# Use LangGraph's conditional edges
```

**Phase 3 (Week 3)**: Implement parallel memory searches
```python
# Run semantic and structured searches simultaneously
# Combine results intelligently
```

This learning plan is specifically tailored to your Info Agent project, focusing on the exact workflows you'll need to implement: memory querying, decision making, and multi-modal information retrieval.

---

This agent system transforms Info Agent from a passive memory storage into an active personal assistant that leverages stored knowledge to provide intelligent, contextual assistance for daily life management.