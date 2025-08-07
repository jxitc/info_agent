#!/usr/bin/env python3
"""
Direct database initialization module for Info Agent.

This module can be run directly to initialize the database:
    python -m info_agent.core
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from info_agent.core.migrations import initialize_database, get_schema_info
from info_agent.utils.logging_config import setup_logging, get_logger


def main():
    """Initialize database and show status."""
    setup_logging(log_level="INFO")
    logger = get_logger(__name__)
    
    print("Info Agent - Database Initialization")
    print("=" * 40)
    
    try:
        # Initialize database
        print("Initializing database...")
        was_created = initialize_database()
        
        if was_created:
            print("✅ Database initialized successfully!")
        else:
            print("✅ Database already initialized")
        
        # Show schema info
        schema_info = get_schema_info()
        print(f"\n📋 Schema Information:")
        print(f"   Version: {schema_info['current_version'] or 'Not set'}")
        print(f"   Database: {schema_info['database_path']}")
        print(f"   Exists: {schema_info['exists']}")
        print(f"   Initialized: {schema_info['initialized']}")
        
        if schema_info['initialized']:
            verification = schema_info['verification']
            if verification['valid']:
                print(f"   Schema: ✅ Valid")
                print(f"   Tables: {len(verification['tables_found'])}")
            else:
                print(f"   Schema: ❌ Invalid")
                print(f"   Errors: {verification['errors']}")
        
        print(f"\n🎯 Ready to use CLI commands!")
        print(f"   Try: python main.py add \"Hello, World!\"")
        
        return 0
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())