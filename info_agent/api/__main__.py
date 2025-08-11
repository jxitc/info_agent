"""
Entry point for running Info Agent API server.

This module allows running the Flask API server directly:
    python -m info_agent.api
"""

import os
import sys
import socket

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from info_agent.api.app import create_app
from info_agent.utils.logging_config import get_logger

def check_port_available(host, port):
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0  # Port is available if connection fails
    except Exception:
        return False

def main():
    """Main entry point for API server."""
    logger = get_logger(__name__)
    
    # Create Flask app
    app = create_app()
    
    # Configuration
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 8001))  # Default to 8001 to avoid conflicts
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Check if port is available, try alternatives if not
    original_port = port
    max_attempts = 5
    for attempt in range(max_attempts):
        if check_port_available(host, port):
            break
        logger.warning(f"Port {port} is in use, trying {port + 1}")
        port += 1
    else:
        logger.error(f"No available ports found after checking {original_port}-{port-1}")
        sys.exit(1)
    
    logger.info(f"Starting Info Agent API server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"API base URL: http://{host}:{port}/api/v1")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("API server stopped by user")
    except Exception as e:
        logger.error(f"API server error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()