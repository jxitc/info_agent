# Info Agent 🧠

**AI-Powered Personal Memory and Information Management System**

Info Agent is an intelligent system that transforms how you capture, process, and retrieve personal information. It accepts diverse inputs (text, with future support for images and documents), uses AI to structure and understand the content, and enables natural language querying of your personal knowledge base.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenAI](https://img.shields.io/badge/AI-OpenAI-green.svg)](https://openai.com/)

## 🎯 Vision & Mission

**Transform unstructured personal information into an intelligent, queryable knowledge base.**

Info Agent bridges the gap between how we naturally capture information (messy, unstructured text) and how we want to retrieve it (precise, contextual queries). By leveraging AI to understand content and create dynamic knowledge structures, it serves as your personal memory extension.

### Key Principles
- **Intelligence-First**: AI processing is mandatory for all content, ensuring consistent structuring and semantic understanding
- **Hybrid Retrieval**: Combines vector similarity search with structured field queries for comprehensive results  
- **Dynamic Schema**: AI creates custom fields and relationships based on content, adapting to your unique information patterns
- **Natural Language Interface**: Query your memories conversationally, just like talking to an assistant

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Info Agent Architecture                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ CLI         │    │ Web         │    │ API         │
│ Interface   │    │ Interface   │    │ Endpoints   │
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                  │
       └──────────────────┼──────────────────┘
                          │
                   ┌──────▼──────┐
                   │  Service    │
                   │  Layer      │
                   └──────┬──────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
    ┌──────▼──────┐ ┌─────▼─────┐ ┌──────▼──────┐
    │ AI          │ │ Memory    │ │ LangGraph   │
    │ Processing  │ │ Management│ │ Agent       │
    │             │ │           │ │ Framework   │
    │ • LLM       │ │ • CRUD    │ │             │
    │ • Embedding │ │ • Models  │ │ • Query     │
    │ • Prompts   │ │ • Business│ │   Processing│
    └──────┬──────┘ │   Logic   │ │ • Tool      │
           │        └─────┬─────┘ │   Selection │
           │              │       │ • Reasoning │
           │              │       └──────┬──────┘
           │              │              │
           └──────────────┼──────────────┘
                          │
                   ┌──────▼──────┐
                   │ Data        │
                   │ Storage     │
                   │             │
        ┌──────────┼──────────────┼──────────┐
        │          │              │          │
  ┌─────▼─────┐ ┌──▼──┐    ┌─────▼─────┐ ┌──▼──┐
  │ SQLite    │ │JSON │    │ ChromaDB  │ │Vec. │
  │ Database  │ │Fields│    │ Vector    │ │Emb. │
  │           │ │     │    │ Store     │ │     │
  │• Memories │ │•Dyn.│    │           │ │•Sem.│
  │• Metadata │ │•Str.│    │• Embeddings│ │•Sim.│
  │• Relations│ │•Sch.│    │• Similarity│ │•Ret.│
  └───────────┘ └─────┘    └───────────┘ └─────┘

Data Flow:
Input → AI Processing → Memory Creation → Dual Storage → Hybrid Retrieval
```

### Architecture Highlights

**🔄 Hybrid RAG System**: Combines semantic vector search (ChromaDB) with structured SQL queries for comprehensive retrieval

**🤖 Agentic Framework**: LangGraph-powered agent system with intelligent tool selection and multi-step reasoning workflows

**🧠 AI-First Processing**: Mandatory OpenAI LLM processing extracts structure, generates titles, and creates dynamic fields

**📊 Dynamic Schema**: AI automatically creates custom JSON fields based on content patterns, adapting to personal information types

**🔍 Multi-Modal Search**: Vector similarity + structured field queries + future knowledge graph relationships

## ✨ Technical Highlights

### Current Implementation (M0 Complete)

#### 🏗️ **Full-Stack Architecture**
- **Backend**: Python with modular design (CLI, API, Core, AI layers)
- **Database**: SQLite with JSON dynamic fields for flexible schema
- **Vector Store**: ChromaDB for semantic embeddings and similarity search
- **Web Interface**: Responsive HTML/CSS/JavaScript with RESTful API integration

#### 🤖 **AI-Powered Processing Pipeline**
- **Information Extraction**: OpenAI GPT models automatically extract key information, generate titles/descriptions
- **Dynamic Field Generation**: AI creates custom structured fields based on content (categories, entities, metadata)
- **Semantic Understanding**: Text embeddings enable context-aware search beyond keyword matching
- **Natural Language Queries**: Conversational search interface with intelligent query processing

#### 🔍 **Advanced Search & Retrieval**
- **Hybrid Search Engine**: Combines vector similarity with structured field filtering
- **LangGraph Agent Framework**: Intelligent query classification and tool orchestration
- **Multi-Source Results**: Structured database queries + semantic vector search + AI reasoning
- **Relevance Ranking**: Time-based and similarity-based result scoring

#### 💻 **Multi-Interface Support**
- **Command Line Interface**: Full-featured CLI with 10+ commands for development and power users
- **RESTful API**: Complete API endpoints supporting all memory operations with JSON responses
- **Web Application**: Responsive interface with memory management, search, and real-time AI processing indicators
- **Development Tools**: Testing commands for vector operations, LLM debugging, and system diagnostics

#### ⚡ **Performance & Reliability**
- **Service Layer Architecture**: Shared business logic between CLI and API for consistency
- **Error Handling**: Comprehensive validation, graceful degradation, and user-friendly error messages  
- **Testing Suite**: Unit tests for all major components (AI, database, CLI, API)
- **Logging System**: Structured logging with optional LangSmith tracing integration

### Planned Enhancements (Future Phases)

#### 🔗 **Knowledge Graph Integration** (Phase 4)
- **Entity Extraction**: LLM-based identification of people, places, dates, concepts
- **Relationship Mapping**: Automatic discovery and storage of entity relationships
- **Triple Storage**: SQLite-based knowledge graph with recursive relationship queries
- **Multi-Hop Reasoning**: Complex queries spanning multiple relationship degrees

#### 🎯 **Advanced Ranking & Fusion** (Phase 4)
- **Reciprocal Rank Fusion (RRF)**: Intelligent combination of results from multiple search systems
- **Adaptive Thresholds**: Dynamic result filtering based on query characteristics and confidence scores
- **Source Diversity**: Deduplication and diversity scoring for comprehensive result sets
- **Evaluation Framework**: RAGAS metrics and A/B testing for retrieval optimization

#### 🧠 **Enhanced Agent Capabilities** (Phase 4)
- **Tool Ecosystem**: Extensible MCP-compatible tools for specialized queries and operations
- **Context Management**: Session-aware conversations with memory of previous interactions
- **Proactive Insights**: AI-driven suggestions and patterns recognition in personal data
- **Multi-Modal Input**: Image OCR, document parsing, and email integration

## 📊 Development Progress

### ✅ **Completed (M0 Prototype)**

| Component | Status | Features |
|-----------|--------|----------|
| **🏗️ Core Infrastructure** | ✅ Complete | Project setup, logging, database schema, migrations |
| **🤖 AI Integration** | ✅ Complete | OpenAI client, prompts, information extraction, embeddings |
| **💾 Data Layer** | ✅ Complete | SQLite database, ChromaDB vector store, repository pattern |
| **💻 CLI Interface** | ✅ Complete | 10+ commands, help system, testing tools, error handling |
| **🌐 Web Platform** | ✅ Complete | Flask API, responsive frontend, RESTful endpoints |
| **🔍 Search System** | ✅ Complete | Hybrid search, vector similarity, structured queries |
| **🧠 Agent Framework** | ✅ Complete | LangGraph integration, tool binding, query processing |

**Total: 48/48 M0 tasks completed** ✅

### 🚧 **In Progress (Phase 4 - Agent Enhancement)**

| Component | Status | Progress |
|-----------|--------|----------|
| **🔗 Knowledge Graph** | 🔄 Planning | Entity extraction, relationship mapping, SQLite graph schema |
| **🎯 Advanced Ranking** | 🔄 Planning | RRF implementation, confidence scoring, result fusion |
| **📈 Evaluation System** | 🔄 Planning | RAGAS metrics, A/B testing, performance monitoring |
| **🧠 Agent Improvements** | 🔄 Planning | Enhanced reasoning, better tool selection, conversation context |

**Progress: 11/20 Phase 4 tasks planned**

### 📋 **Future Milestones**

#### **M1 - Network & Multi-User (Planned)**
- User authentication and multi-tenancy
- Advanced entity recognition and deduplication
- PostgreSQL migration and caching layer
- Image processing and document upload

#### **M2 - Enterprise & Security (Planned)**
- Data encryption and privacy compliance
- Audit logging and role-based access
- Proactive reminders and notifications  
- Advanced AI reasoning and context management

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- OpenAI API key
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd info_agent
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key:
   # OPENAI_API_KEY=your_api_key_here
   ```

5. **Initialize the system:**
   ```bash
   python main.py status
   ```

### Basic Usage

#### CLI Interface
```bash
# Add a memory
python main.py add "Meeting with Sarah about project timeline next Tuesday"

# Search your memories
python main.py search "project meetings"

# List recent memories
python main.py list

# Get detailed view
python main.py show 1

# See all available commands
python main.py --help
```

#### Web Interface
```bash
# Start the web server
python -m info_agent.api

# Open browser to http://localhost:5000
# Use the web interface to add memories, search, and manage your data
```

#### API Usage
```bash
# Test API endpoints
curl -X POST http://localhost:5000/api/memories \
  -H "Content-Type: application/json" \
  -d '{"content": "Important project deadline next Friday"}'

curl "http://localhost:5000/api/search?q=project%20deadline"
```

## 🛠️ Development

### Testing
```bash
# Run all tests
python -m pytest info_agent/tests/

# Test specific components
python info_agent/tests/test_memory_database.py
python info_agent/tests/test_ai_client.py
```

### Development Commands
```bash
# Test AI processing
python main.py llm extract "Test content for AI processing"

# Test vector operations
python main.py vector add "Test content" --title "Test Memory"
python main.py vector search "test"

# System diagnostics
python main.py status
```

## 📁 Project Structure

```
info_agent/
├── info_agent/
│   ├── agents/          # LangGraph agent framework
│   ├── ai/              # AI processing (OpenAI, prompts, embeddings)
│   ├── api/             # Flask web API and routes
│   ├── cli/             # Command-line interface
│   ├── core/            # Database, models, repository layer
│   ├── tools/           # LangChain tools for agent system
│   ├── utils/           # Logging, LangSmith configuration
│   └── web/             # Static files and templates
├── docs/                # Documentation and specifications
├── tests/               # Test files
├── main.py              # Main CLI entry point
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests (`python -m pytest`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for powerful language models and embeddings
- **ChromaDB** for efficient vector storage and similarity search
- **LangChain/LangGraph** for agent framework and tool orchestration
- **Flask** for web API framework
- **Click** for CLI framework

---

**Info Agent** - Transforming personal information management through AI-powered intelligence and hybrid retrieval systems. Built with ❤️ and 🤖.