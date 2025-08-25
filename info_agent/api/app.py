"""
Flask application factory for Info Agent API.

This module creates and configures the Flask application with all necessary
blueprints, error handlers, and middleware.
"""

import os
from flask import Flask, jsonify, send_from_directory, render_template_string
from flask_cors import CORS

from info_agent.utils.logging_config import setup_logging, get_logger
from info_agent.core.repository import RepositoryError
from info_agent.ai.processor import ProcessingError


def create_app(config=None):
    """Create and configure the Flask application."""
    # Set up template and static folders for web interface
    web_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'web')
    template_dir = os.path.join(web_dir, 'templates')
    static_dir = os.path.join(web_dir, 'static')
    
    app = Flask(__name__, 
                template_folder=template_dir,
                static_folder=static_dir)
    
    # Basic configuration
    app.config.update({
        'DEBUG': os.getenv('FLASK_DEBUG', 'False').lower() == 'true',
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'JSON_SORT_KEYS': False,  # Preserve JSON key order
        'JSONIFY_PRETTYPRINT_REGULAR': True,  # Pretty print JSON in debug mode
    })
    
    # Override with custom config if provided
    if config:
        app.config.update(config)
    
    # Setup logging
    log_level = "DEBUG" if app.config['DEBUG'] else "INFO"
    setup_logging(log_level=log_level)
    logger = get_logger(__name__)
    
    # Enable CORS for all domains (for development)
    # TODO: Restrict CORS domains in production
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Simple health check endpoint."""
        return jsonify({
            'status': 'healthy',
            'service': 'info-agent-api',
            'version': '0.1.0'
        })
    
    # Web interface routes
    @app.route('/')
    def index():
        """Serve the main web interface."""
        try:
            # Debug: log the paths being used
            logger.debug(f"Template dir: {template_dir}")
            logger.debug(f"Static dir: {static_dir}")
            logger.debug(f"Template exists: {os.path.exists(os.path.join(template_dir, 'index.html'))}")
            
            template_path = os.path.join(template_dir, 'index.html')
            if os.path.exists(template_path):
                with open(template_path, 'r') as f:
                    return f.read()
            else:
                logger.error(f"Template file not found at: {template_path}")
                raise FileNotFoundError(f"Template not found: {template_path}")
                
        except Exception as e:
            logger.error(f"Error serving web interface: {e}")
            return jsonify({
                'error': 'Web interface not found',
                'message': f'The web interface files are not available: {str(e)}. API endpoints are still accessible at /api/v1/',
                'template_path': template_dir,
                'static_path': static_dir
            }), 404
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files for the web interface."""
        try:
            static_path = os.path.join(static_dir, filename)
            logger.debug(f"Serving static file: {static_path}")
            logger.debug(f"File exists: {os.path.exists(static_path)}")
            return send_from_directory(static_dir, filename)
        except Exception as e:
            logger.error(f"Error serving static file {filename}: {e}")
            return jsonify({'error': f'Static file not found: {filename}'}), 404
    
    logger.info(f"Flask app created with debug={app.config['DEBUG']}")
    return app


def register_error_handlers(app):
    """Register custom error handlers for the Flask app."""
    from info_agent.api.utils.responses import error_response
    
    @app.errorhandler(RepositoryError)
    def handle_repository_error(error):
        """Handle repository errors."""
        return error_response("DATABASE_ERROR", str(error), status=500)
    
    @app.errorhandler(ProcessingError)
    def handle_processing_error(error):
        """Handle AI processing errors."""
        return error_response("AI_SERVICE_ERROR", str(error), status=503)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        return error_response("NOT_FOUND", "Resource not found", status=404)
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors."""
        return error_response("METHOD_NOT_ALLOWED", "Method not allowed", status=405)
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle internal server errors."""
        return error_response("INTERNAL_ERROR", "Internal server error", status=500)


def register_blueprints(app):
    """Register all API blueprints."""
    from info_agent.api.routes.memories import memories_bp
    from info_agent.api.routes.search import search_bp  
    from info_agent.api.routes.system import system_bp
    from info_agent.api.routes.chat import chat_bp
    
    # API version prefix
    api_prefix = '/api/v1'
    
    # Register blueprints with API prefix
    app.register_blueprint(memories_bp, url_prefix=api_prefix)
    app.register_blueprint(search_bp, url_prefix=api_prefix)
    app.register_blueprint(system_bp, url_prefix=api_prefix)
    app.register_blueprint(chat_bp, url_prefix=api_prefix)


if __name__ == '__main__':
    # Development server
    app = create_app()
    app.run(host='localhost', port=8000, debug=True)