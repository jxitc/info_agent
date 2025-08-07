# CLI Usage Guide - Info Agent

This guide covers the command-line interface for Info Agent, showing how to manage your personal memories through simple CLI commands.

## Overview

Info Agent provides a command-line interface for storing, searching, and managing personal memories. The CLI automatically initializes the database on first use and provides intuitive commands for memory management.

## Installation & Setup

1. **Ensure dependencies are installed:**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Install dependencies (if not already done)
   pip install -r requirements.txt
   ```

2. **Initialize database (optional - happens automatically):**
   ```bash
   # Manual database initialization
   python -m info_agent.core
   ```

## Available Commands

### `status` - System Status
Check the current system status and database connection.

```bash
python main.py status
```

**Example Output:**
```
📊 Info Agent System Status
========================================
🐍 Python: 3.11.5
📁 Data directory: ✅ /Users/username/.info_agent/data
📦 Services:
   • Database: ✅ Connected
   • Total memories: 15
   • Added this week: 3
   • Database size: 0.1 MB

🎯 Available commands: add, list, show, delete, status
```

### `add` - Add New Memory
Store new information as a memory with automatic processing.

```bash
python main.py add "Your memory content here"
```

**Examples:**
```bash
# Simple memory
python main.py add "Meeting with Sarah about the project timeline"

# Longer content
python main.py add "Project requirements: user authentication, data export, mobile responsive design, and integration with existing APIs"

# Important information
python main.py add "Remember to backup database before deployment on Friday at 2pm"
```

**Example Output:**
```
🔄 Processing memory...
📝 Text: Meeting with Sarah about the project timeline
✅ Memory created successfully!
📋 Memory ID: 1
🏷️  Title: Meeting with Sarah about the project timeline
📊 Word count: 8
```

### `list` - List Recent Memories
Display recent memories in chronological order.

```bash
# List default number of memories (20)
python main.py list

# List specific number of memories
python main.py list --limit 5
```

**Example Output:**
```
📋 Recent memories (2 found):

🆔 ID: 2
🏷️  Title: Remember to backup database before deployment on Friday at 2pm
📝 Preview: Remember to backup database before deployment on Friday at 2pm
📅 Created: 2024-08-07 15:30
📊 Words: 10
📂 Category: general
--------------------------------------------------
🆔 ID: 1
🏷️  Title: Meeting with Sarah about the project timeline
📝 Preview: Meeting with Sarah about the project timeline
📅 Created: 2024-08-07 15:25
📊 Words: 8
📂 Category: general
--------------------------------------------------
```

### `show` - Display Memory Details
Show complete information about a specific memory.

```bash
python main.py show <memory_id>
```

**Examples:**
```bash
python main.py show 1
python main.py show 42
```

**Example Output:**
```
📄 Memory Details (ID: 1)
============================================================

🏷️  Title: Meeting with Sarah about the project timeline
📝 Content:
   Meeting with Sarah about the project timeline

📊 Statistics:
   Word count: 8
   Content hash: a1b2c3d4e5f6g7h8...
   Version: 1

📅 Timestamps:
   Created: 2024-08-07 15:25:43
   Updated: 2024-08-07 15:25:43

🔧 Dynamic Fields:
   category: general
   word_count: 8
   status: created
```

### `delete` - Remove Memory
Delete a memory by its ID (with confirmation prompt).

```bash
python main.py delete <memory_id>
```

**Examples:**
```bash
python main.py delete 1
python main.py delete 25
```

**Example Output:**
```
Are you sure you want to delete this memory? [y/N]: y
✅ Memory 1 deleted successfully
🏷️  Title: Meeting with Sarah about the project timeline
```

### `version` - Version Information
Display version information about Info Agent.

```bash
python main.py version
```

**Example Output:**
```
Info Agent v0.1.0
AI-powered personal memory and information management system
```

## Command Options

### Global Options
Available for all commands:

- `--verbose, -v`: Enable verbose output for debugging
- `--help`: Show help information for any command

```bash
# Verbose mode
python main.py --verbose add "Test memory"

# Get help for specific command
python main.py add --help
```

### Command-Specific Options

**`list` command:**
- `--limit, -l`: Number of memories to display (default: 20)

**`add` command:**
- None currently (content is provided as argument)

**`show` and `delete` commands:**
- Memory ID is required as argument

## Getting Help

### Command Help
Get help for any command:
```bash
python main.py --help              # General help
python main.py add --help          # Help for add command
python main.py list --help         # Help for list command
```

### Extended Help System
Access detailed help and guides:
```bash
python main.py help                    # General getting started guide
python main.py help add                # Detailed help for add command
python main.py getting-started         # Getting started guide
python main.py troubleshooting         # Troubleshooting information
```

## Typical Workflow

### First Time Setup
1. **Check system status:**
   ```bash
   python main.py status
   ```

2. **Add your first memory:**
   ```bash
   python main.py add "This is my first memory in Info Agent"
   ```

3. **Verify it was stored:**
   ```bash
   python main.py list
   ```

### Daily Usage
1. **Add new information:**
   ```bash
   python main.py add "Important meeting notes from today's standup"
   ```

2. **Review recent memories:**
   ```bash
   python main.py list --limit 5
   ```

3. **Get details on specific memory:**
   ```bash
   python main.py show 15
   ```

4. **Clean up old memories:**
   ```bash
   python main.py delete 12
   ```

## Data Storage

- **Database Location:** `~/.info_agent/data/info_agent.db`
- **Logs Location:** `~/.info_agent/logs/info_agent.log`
- **Database Type:** SQLite (no external dependencies)
- **Auto-backup:** Not yet implemented (coming in future versions)

## Troubleshooting

### Common Issues

1. **"Database service not available"**
   - Try: `python -m info_agent.core` to initialize database
   - Check permissions on `~/.info_agent/` directory

2. **Import errors**
   - Ensure virtual environment is activated: `source venv/bin/activate`
   - Reinstall dependencies: `pip install -r requirements.txt`

3. **Permission errors**
   - Check write permissions on home directory
   - Verify `~/.info_agent/` directory can be created

4. **Memory not found errors**
   - Use `python main.py list` to see available memory IDs
   - Remember that deleted memories cannot be recovered

### Getting Support

1. **Check system status:** `python main.py status`
2. **Run database tests:** `python info_agent/tests/test_memory_database.py`
3. **Check logs:** `~/.info_agent/logs/info_agent.log`
4. **Enable verbose mode:** `python main.py --verbose <command>`

## Current Limitations

**Note: This is the M0 prototype with basic functionality**

- **No AI processing yet:** Dynamic fields are simple placeholders
- **No search capability:** Full-text search not yet implemented  
- **No categories or tags:** Basic metadata only
- **No data export:** Import/export features not yet available
- **No configuration:** Uses default settings only

These features will be added in future development phases.

## Future Features (Coming Soon)

- **AI-powered information extraction**
- **Natural language search**
- **Smart categorization and tagging**
- **Vector-based semantic search**
- **Data import/export**
- **Configuration management**
- **Advanced query capabilities**

---

*This CLI provides the foundation for Info Agent's memory management capabilities. As development continues, more advanced features will be added while maintaining the same simple, intuitive command interface.*