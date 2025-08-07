#!/usr/bin/env python3
"""
Info Agent - AI-powered personal memory and information management system.

This is the main entry point for the Info Agent CLI application.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from info_agent.utils.logging_config import setup_logging, get_logger


def main():
    """Main entry point for the Info Agent application."""
    # Set up logging
    setup_logging(log_level="INFO")
    logger = get_logger(__name__)
    
    logger.info("Starting Info Agent...")
    
    try:
        # Import and initialize CLI
        from info_agent.cli.main import cli
        cli()
        
        logger.info("Info Agent CLI session ended")
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
