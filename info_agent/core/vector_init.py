#!/usr/bin/env python3
"""
Vector store initialization module for Info Agent.

This module can be run directly to initialize the vector store:
    python -m info_agent.core.vector_init
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from info_agent.core.vector_store import initialize_vector_store, get_vector_store
from info_agent.utils.logging_config import setup_logging, get_logger


def main():
    """Initialize vector store and show status."""
    setup_logging(log_level="INFO")
    logger = get_logger(__name__)
    
    print("Info Agent - Vector Store Initialization")
    print("=" * 45)
    
    try:
        # Initialize vector store
        print("Initializing vector store...")
        success = initialize_vector_store()
        
        if success:
            print("✅ Vector store initialized successfully!")
            
            # Show stats
            vector_store = get_vector_store()
            stats = vector_store.get_collection_stats()
            print(f"\n📋 Vector Store Information:")
            print(f"   Collection: {stats.get('collection_name', 'N/A')}")
            print(f"   Documents: {stats.get('total_documents', 0)}")
            print(f"   Embedding Model: {stats.get('embedding_model', 'N/A')}")
            print(f"   Data Directory: {stats.get('data_directory', 'N/A')}")
            
            print(f"\n🎯 Vector store is ready for semantic search!")
        else:
            print("❌ Vector store initialization failed")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Vector store initialization failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())