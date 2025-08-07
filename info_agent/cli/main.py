"""
Main CLI interface for Info Agent.

This module provides the primary command-line interface using Click framework.
"""

import click
import sys
import os
from typing import Optional

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from info_agent.utils.logging_config import setup_logging, get_logger
from info_agent.cli.validators import (
    MEMORY_ID, 
    validate_text_input, validate_search_query, validate_limit
)
from info_agent.cli.help import add_help_commands


# Global context object for sharing state between commands
class InfoAgentContext:
    """Context object for sharing state between CLI commands."""
    
    def __init__(self):
        self.verbose = False
        self.logger = None
    
    def setup_logging(self, verbose: bool = False):
        """Setup logging based on verbosity level."""
        log_level = "DEBUG" if verbose else "INFO"
        setup_logging(log_level=log_level)
        self.logger = get_logger(__name__)
        self.verbose = verbose


# Main CLI group
@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, verbose: bool):
    """
    Info Agent - AI-powered personal memory and information management system.
    
    A tool for storing, organizing, and retrieving information using AI-powered
    processing and semantic search capabilities.
    """
    # Create context object
    ctx.ensure_object(InfoAgentContext)
    ctx.obj.verbose = verbose
    # Setup logging
    ctx.obj.setup_logging(verbose)
    
    if verbose:
        ctx.obj.logger.info("Info Agent CLI started in verbose mode")


@cli.command()
@click.argument('text', required=True)
@click.pass_context
def add(ctx, text: str):
    """
    Add a new memory from text input.
    
    TEXT: The information to store as a memory.
    
    Examples:
    
        info-agent add "Meeting with John at 3pm tomorrow"
        
        info-agent add "Important project deadline"
    """
    logger = ctx.obj.logger
    
    try:
        # Validate input
        validated_text = validate_text_input(text)
        logger.info(f"Adding new memory with {len(validated_text)} characters")
        
        # TODO: Implement memory creation logic
        click.echo("🔄 Processing memory...")
        click.echo(f"📝 Text: {validated_text[:100]}{'...' if len(validated_text) > 100 else ''}")
        
        # Placeholder implementation
        click.echo("❌ Memory creation not yet implemented")
        click.echo("💡 This will be implemented in tasks 4.1 and 3.2")
        
    except click.BadParameter as e:
        logger.error(f"Input validation error: {e}")
        raise


@cli.command()
@click.argument('query', required=True)
@click.option('--limit', '-l', default=10, help='Maximum number of results to return')
@click.pass_context
def search(ctx, query: str, limit: int):
    """
    Search for memories using natural language.
    
    QUERY: The search query in natural language.
    
    Examples:
    
        info-agent search "meetings with John"
        
        info-agent search "project deadlines" --category work --limit 5
    """
    logger = ctx.obj.logger
    
    try:
        # Validate input
        validated_query = validate_search_query(query)
        validated_limit = validate_limit(limit, min_value=1, max_value=100)
        
        logger.info(f"Searching for: '{validated_query}' (limit: {validated_limit})")
        
        # TODO: Implement search logic
        click.echo(f"🔍 Searching for: '{validated_query}'")
        click.echo(f"📊 Limit: {validated_limit} results")
        
        # Placeholder implementation
        click.echo("❌ Search functionality not yet implemented")
        click.echo("💡 This will be implemented in tasks 4.2 and 3.1")
        
    except click.BadParameter as e:
        logger.error(f"Input validation error: {e}")
        raise


@cli.command()
@click.option('--limit', '-l', default=20, help='Number of recent memories to show')
@click.pass_context
def list(ctx, limit: int):
    """
    List recent memories.
    
    Examples:
    
        info-agent list
        
        info-agent list --limit 5
    """
    logger = ctx.obj.logger
    logger.info(f"Listing recent memories (limit: {limit})")
    
    # TODO: Implement list logic
    click.echo(f"📋 Recent memories (limit: {limit}):")
    
    
    # Placeholder implementation
    click.echo("❌ Memory listing not yet implemented")
    click.echo("💡 This will be implemented in tasks 4.1 and 2.1")


@cli.command()
@click.argument('memory_id', required=True, type=MEMORY_ID)
@click.pass_context
def show(ctx, memory_id: int):
    """
    Show detailed information about a specific memory.
    
    MEMORY_ID: The ID of the memory to display.
    
    Examples:
    
        info-agent show 123
    """
    logger = ctx.obj.logger
    logger.info(f"Showing memory ID: {memory_id}")
    
    # TODO: Implement show logic
    click.echo(f"📄 Memory Details (ID: {memory_id}):")
    
    # Placeholder implementation
    click.echo("❌ Memory display not yet implemented")
    click.echo("💡 This will be implemented in tasks 4.1 and 2.1")


@cli.command()
@click.pass_context
def status(ctx):
    """
    Show system status and configuration.
    """
    logger = ctx.obj.logger
    logger.info("Checking system status")
    
    click.echo("📊 Info Agent System Status")
    click.echo("=" * 40)
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    click.echo(f"🐍 Python: {python_version}")
    
    # Check configuration
    config_status = "✅ Loaded" if ctx.obj.config_path else "⚠️  Using defaults"
    click.echo(f"⚙️  Configuration: {config_status}")
    
    # Check data directory
    data_dir = os.path.expanduser("~/.info_agent/data")
    if os.path.exists(data_dir):
        click.echo(f"📁 Data directory: ✅ {data_dir}")
    else:
        click.echo(f"📁 Data directory: ❌ Not found ({data_dir})")
    
    # Check dependencies (placeholder)
    click.echo("📦 Dependencies:")
    click.echo("   • Database: ❌ Not connected")
    click.echo("   • Vector store: ❌ Not connected") 
    click.echo("   • AI services: ❌ Not connected")
    
    click.echo("\n💡 Run setup commands to initialize components")


@cli.command()
@click.pass_context 
def version(ctx):
    """Show version information."""
    # Import here to avoid circular imports
    try:
        from info_agent import __version__
        version_str = __version__
    except ImportError:
        version_str = "0.1.0"
    
    click.echo(f"Info Agent v{version_str}")
    click.echo("AI-powered personal memory and information management system")


# Add help commands to the CLI
add_help_commands(cli)


if __name__ == '__main__':
    cli()
