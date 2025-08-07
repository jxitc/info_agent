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
from info_agent.core.repository import get_memory_service, RepositoryError


# Global context object for sharing state between commands
class InfoAgentContext:
    """Context object for sharing state between CLI commands."""
    
    def __init__(self):
        self.verbose = False
        self.logger = None
        self.memory_service = None
    
    def setup_logging(self, verbose: bool = False):
        """Setup logging based on verbosity level."""
        log_level = "DEBUG" if verbose else "INFO"
        setup_logging(log_level=log_level)
        self.logger = get_logger(__name__)
        self.verbose = verbose
        
        # Initialize memory service
        try:
            self.memory_service = get_memory_service()
            if verbose:
                self.logger.debug("Memory service initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize memory service: {e}")
            self.memory_service = None


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
        
        # Check if memory service is available
        if not ctx.obj.memory_service:
            click.echo("❌ Database service not available")
            click.echo("💡 Try running: python -m info_agent.core.migrations to initialize database")
            return
        
        # Create memory
        click.echo("🔄 Processing memory...")
        click.echo(f"📝 Text: {validated_text[:100]}{'...' if len(validated_text) > 100 else ''}")
        
        try:
            # Add memory using service (with simple mocked dynamic fields)
            memory = ctx.obj.memory_service.add_memory(
                content=validated_text,
                title=None  # Auto-generate title
            )
            
            # Mock some simple dynamic fields for testing
            if memory:
                memory.dynamic_fields = {
                    "category": "general",
                    "word_count": len(validated_text.split()),
                    "status": "created"
                }
                # Update with mocked fields
                ctx.obj.memory_service.update_memory(memory)
            
            click.echo("✅ Memory created successfully!")
            click.echo(f"📋 Memory ID: {memory.id}")
            click.echo(f"🏷️  Title: {memory.title}")
            click.echo(f"📊 Word count: {memory.word_count}")
            
        except RepositoryError as e:
            click.echo(f"❌ Failed to create memory: {e}")
            logger.error(f"Memory creation failed: {e}")
        
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
    
    # Check if memory service is available
    if not ctx.obj.memory_service:
        click.echo("❌ Database service not available")
        return
    
    try:
        # Get recent memories
        memories = ctx.obj.memory_service.list_recent_memories(limit=limit)
        
        if not memories:
            click.echo("📋 No memories found")
            click.echo("💡 Add your first memory with: info-agent add \"your text here\"")
            return
        
        click.echo(f"📋 Recent memories ({len(memories)} found):")
        click.echo()
        
        for memory in memories:
            # Simple display format
            preview = memory.get_preview(80)
            created_date = memory.created_at.strftime("%Y-%m-%d %H:%M") if memory.created_at else "unknown"
            
            click.echo(f"🆔 ID: {memory.id}")
            click.echo(f"🏷️  Title: {memory.title}")
            click.echo(f"📝 Preview: {preview}")
            click.echo(f"📅 Created: {created_date}")
            click.echo(f"📊 Words: {memory.word_count}")
            
            # Show simple dynamic fields if available
            if memory.dynamic_fields:
                category = memory.dynamic_fields.get('category', 'N/A')
                click.echo(f"📂 Category: {category}")
            
            click.echo("-" * 50)
        
    except Exception as e:
        click.echo(f"❌ Failed to list memories: {e}")
        logger.error(f"Memory listing failed: {e}")


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
    
    # Check if memory service is available
    if not ctx.obj.memory_service:
        click.echo("❌ Database service not available")
        return
    
    try:
        # Get memory by ID
        memory = ctx.obj.memory_service.get_memory(memory_id)
        
        if not memory:
            click.echo(f"❌ Memory with ID {memory_id} not found")
            return
        
        # Display memory details
        click.echo(f"📄 Memory Details (ID: {memory_id})")
        click.echo("=" * 60)
        click.echo()
        
        click.echo(f"🏷️  Title: {memory.title}")
        click.echo(f"📝 Content:")
        click.echo(f"   {memory.content}")
        click.echo()
        
        # Metadata
        created_date = memory.created_at.strftime("%Y-%m-%d %H:%M:%S") if memory.created_at else "unknown"
        updated_date = memory.updated_at.strftime("%Y-%m-%d %H:%M:%S") if memory.updated_at else "unknown"
        
        click.echo(f"📊 Statistics:")
        click.echo(f"   Word count: {memory.word_count}")
        click.echo(f"   Content hash: {memory.content_hash[:16]}...")
        click.echo(f"   Version: {memory.version}")
        click.echo()
        
        click.echo(f"📅 Timestamps:")
        click.echo(f"   Created: {created_date}")
        click.echo(f"   Updated: {updated_date}")
        
        # Dynamic fields (mocked data)
        if memory.dynamic_fields:
            click.echo()
            click.echo(f"🔧 Dynamic Fields:")
            for key, value in memory.dynamic_fields.items():
                click.echo(f"   {key}: {value}")
        
    except Exception as e:
        click.echo(f"❌ Failed to show memory: {e}")
        logger.error(f"Memory show failed: {e}")


@cli.command()
@click.argument('memory_id', required=True, type=MEMORY_ID)
@click.confirmation_option(prompt='Are you sure you want to delete this memory?')
@click.pass_context
def delete(ctx, memory_id: int):
    """
    Delete a memory by ID.
    
    MEMORY_ID: The ID of the memory to delete.
    
    Examples:
    
        info-agent delete 123
    """
    logger = ctx.obj.logger
    logger.info(f"Deleting memory ID: {memory_id}")
    
    # Check if memory service is available
    if not ctx.obj.memory_service:
        click.echo("❌ Database service not available")
        return
    
    try:
        # Check if memory exists first
        memory = ctx.obj.memory_service.get_memory(memory_id)
        if not memory:
            click.echo(f"❌ Memory with ID {memory_id} not found")
            return
        
        # Delete the memory
        success = ctx.obj.memory_service.delete_memory(memory_id)
        
        if success:
            click.echo(f"✅ Memory {memory_id} deleted successfully")
            click.echo(f"🏷️  Title: {memory.title}")
        else:
            click.echo(f"❌ Failed to delete memory {memory_id}")
        
    except Exception as e:
        click.echo(f"❌ Failed to delete memory: {e}")
        logger.error(f"Memory deletion failed: {e}")


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
    
    # Check data directory
    data_dir = os.path.expanduser("~/.info_agent/data")
    if os.path.exists(data_dir):
        click.echo(f"📁 Data directory: ✅ {data_dir}")
    else:
        click.echo(f"📁 Data directory: ❌ Not found ({data_dir})")
    
    # Check database connection and statistics
    if ctx.obj.memory_service:
        try:
            stats = ctx.obj.memory_service.get_service_statistics()
            total_memories = stats.get('total_memories', 0)
            
            click.echo("📦 Services:")
            click.echo(f"   • Database: ✅ Connected")
            click.echo(f"   • Total memories: {total_memories}")
            
            # Show recent activity if available
            if 'memories_last_week' in stats:
                click.echo(f"   • Added this week: {stats['memories_last_week']}")
            
            # Database info
            if 'database_info' in stats:
                db_info = stats['database_info']
                if 'database_size' in db_info:
                    size_mb = db_info['database_size'] / (1024 * 1024)
                    click.echo(f"   • Database size: {size_mb:.1f} MB")
            
        except Exception as e:
            click.echo("📦 Services:")
            click.echo(f"   • Database: ⚠️  Connected but error getting stats: {e}")
    else:
        click.echo("📦 Services:")
        click.echo("   • Database: ❌ Not connected")
        click.echo("   • Vector store: ❌ Not implemented") 
        click.echo("   • AI services: ❌ Not implemented")
        click.echo("\n💡 Database initialization may be needed")
    
    click.echo("\n🎯 Available commands: add, list, show, delete, status")


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
