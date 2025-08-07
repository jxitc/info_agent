"""
Enhanced help system and documentation for CLI commands.

This module provides extended help functionality and command documentation
beyond the basic Click help system.
"""

import click
from typing import Dict, List, Tuple


# Extended help content for commands
EXTENDED_HELP: Dict[str, Dict[str, str]] = {
    "add": {
        "description": "Store new information as a memory with AI-powered processing",
        "usage_tips": """
Tips for adding memories:
• Be specific and descriptive in your text
• The AI will automatically extract and structure key information
• Include context and relevant details for better searchability
• Natural language works best - write as you would speak
        """,
        "examples": """
Examples:
  # Simple memory
  info-agent add "Met with Sarah about the new project proposal"
  
  # Work-related information
  info-agent add "Deploy to production at 2pm Friday"
  
  # Long text (use quotes)
  info-agent add "Project requirements: 1) User authentication 2) Data export 3) Mobile responsive design"
        """
    },
    
    "search": {
        "description": "Find memories using natural language queries with AI-powered semantic search",
        "usage_tips": """
Search tips:
• Use natural language - ask questions or describe what you're looking for
• Combine keywords and concepts for better results
• Use --limit to control number of results
• The AI understands context and relationships between concepts
        """,
        "examples": """
Examples:
  # Natural language search
  info-agent search "meetings about the new project"
  
  # Keyword-based search
  info-agent search "deployment production" --limit 5
  
  # Conceptual search
  info-agent search "urgent tasks"
  
  # Broad search
  info-agent search "things I need to do this week"
        """
    },
    
    "list": {
        "description": "Display recent memories in chronological order",
        "usage_tips": """
Listing tips:
• Default shows 20 most recent memories
• Use --limit to show more or fewer results
• Memories are shown newest first with preview text
• Useful for browsing recent additions
        """,
        "examples": """
Examples:
  # Recent memories
  info-agent list
  
  # Last 5 memories
  info-agent list --limit 5
        """
    },
    
    "show": {
        "description": "Display complete details for a specific memory",
        "usage_tips": """
Show tips:
• Use the memory ID from search or list results
• Shows complete memory content and AI-extracted information
• Displays creation and modification timestamps
• Reveals all structured data extracted by AI processing
        """,
        "examples": """
Examples:
  # Show specific memory
  info-agent show 123
  
  # Get memory ID from search first
  info-agent search "project meeting"
  info-agent show 45
        """
    },
    
    "status": {
        "description": "Check system health and configuration",
        "usage_tips": """
Status information includes:
• Python version and environment
• Configuration file status
• Data directory location and permissions
• Database connectivity
• AI service availability
        """,
        "examples": """
Examples:
  # System status
  info-agent status
        """
    }
}


def get_command_help(command_name: str) -> str:
    """
    Get extended help for a specific command.
    
    Args:
        command_name: Name of the command
        
    Returns:
        Formatted help text
    """
    help_data = EXTENDED_HELP.get(command_name, {})
    
    if not help_data:
        return f"No extended help available for command '{command_name}'"
    
    help_text = []
    
    # Description
    if "description" in help_data:
        help_text.append(f"Description: {help_data['description']}")
        help_text.append("")
    
    # Usage tips
    if "usage_tips" in help_data:
        help_text.append(help_data["usage_tips"].strip())
        help_text.append("")
    
    # Examples
    if "examples" in help_data:
        help_text.append(help_data["examples"].strip())
    
    return "\n".join(help_text)


def get_getting_started_guide() -> str:
    """Get the getting started guide."""
    return """
🚀 Getting Started with Info Agent

Info Agent is an AI-powered personal memory system that helps you store, 
organize, and retrieve information using natural language.

Basic Workflow:
1. Add memories with 'info-agent add "your information here"'
2. Search memories with 'info-agent search "what you're looking for"'  
3. View details with 'info-agent show <id>'

Quick Start:
  # Add your first memory
  info-agent add "This is my first memory in Info Agent"
  
  # Search for it
  info-agent search "first memory"
  
  # Check system status
  info-agent status

Key Features:
• 🤖 AI-powered information extraction and processing
• 🔍 Semantic search with natural language understanding
• 📊 Automatic structuring of unstructured information
• 💾 Local data storage for privacy and control
• ⚡ Fast retrieval with hybrid search capabilities

Get help for any command:
  info-agent <command> --help
  
For detailed help:
  info-agent help <command>
"""


def get_troubleshooting_guide() -> str:
    """Get troubleshooting information."""
    return """
🔧 Troubleshooting Info Agent

Common Issues and Solutions:

1. Command not found
   • Make sure you're in the project directory
   • Activate the virtual environment: source venv/bin/activate
   • Run: python main.py <command> instead of info-agent

2. Database errors
   • Check data directory: ~/.info_agent/data/
   • Verify permissions: ls -la ~/.info_agent/
   • Run: info-agent status to check system health

3. AI service errors
   • Verify OpenAI API key: echo $OPENAI_API_KEY
   • Check network connection
   • Run: python tests/test_openai_api.py

4. Import errors
   • Ensure virtual environment is activated
   • Reinstall dependencies: pip install -r requirements.txt
   • Check Python version: python --version (needs 3.8+)

5. Permission errors
   • Check file permissions in project directory
   • Verify write access to ~/.info_agent/
   • Run with proper user permissions

Getting Help:
• Run 'info-agent status' for system diagnostics
• Check logs in ~/.info_agent/logs/
• Review setup documentation in docs/
"""


@click.group(invoke_without_command=True)
@click.argument('command_name', required=False)
@click.pass_context
def help(ctx, command_name: str = None):
    """
    Get detailed help and documentation.
    
    COMMAND_NAME: Optional command to get specific help for.
    
    Examples:
      info-agent help           # General help
      info-agent help add       # Help for add command
      info-agent help getting-started
      info-agent help troubleshooting
    """
    if command_name is None:
        # Show general help
        click.echo(get_getting_started_guide())
        return
    
    # Special help topics
    if command_name == "getting-started":
        click.echo(get_getting_started_guide())
        return
        
    if command_name == "troubleshooting":
        click.echo(get_troubleshooting_guide())
        return
    
    # Command-specific help
    help_text = get_command_help(command_name)
    click.echo(f"\n📖 Help for '{command_name}' command\n")
    click.echo(help_text)


# Additional help commands that can be added to main CLI
def add_help_commands(cli_group):
    """Add help-related commands to the main CLI group."""
    cli_group.add_command(help)
    
    @cli_group.command()
    def getting_started():
        """Show the getting started guide."""
        click.echo(get_getting_started_guide())
    
    @cli_group.command()  
    def troubleshooting():
        """Show troubleshooting information."""
        click.echo(get_troubleshooting_guide())
