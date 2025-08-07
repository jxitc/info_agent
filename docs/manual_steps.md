# Setup Guide - M0 Implementation

This document provides step-by-step instructions for setting up the development environment for the AI Information Agent M0 prototype.

## Phase 1: Foundation Setup

### Prerequisites
- Python 3.8+ installed on your system
- Git configured
- Terminal/Command Line access

### Step 1: Virtual Environment Setup **[HUMAN REQUIRED]**

1. **Create virtual environment:**
   ```bash
   # Navigate to project directory
   cd /Users/xjiang/info_agent
   
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   # venv\Scripts\activate
   ```

2. **Verify virtual environment is active:**
   - Your terminal prompt should show `(venv)` prefix
   - Check Python path: `which python` should point to the venv directory

### Step 2: Dependencies Installation **[HUMAN REQUIRED]**

1. **Install Python packages:**
   ```bash
   # Make sure virtual environment is activated
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Verify installations:**
   ```bash
   # Test key dependencies
   python -c "import click; print('Click installed successfully')"
   python -c "import openai; print('OpenAI installed successfully')"
   python -c "import chromadb; print('ChromaDB installed successfully')"
   python -c "import sqlite3; print('SQLite installed successfully')"
   ```

### Step 3: OpenAI API Configuration **[HUMAN REQUIRED]**

1. **Set up OpenAI API key:**
   ```bash
   # Option 1: Environment variable (recommended)
   export OPENAI_API_KEY="your-api-key-here"
   
   # Option 2: Add to ~/.bashrc or ~/.zshrc for persistence
   echo 'export OPENAI_API_KEY="your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

2. **Test API connection:**
   ```bash
   # This will be available after we create the test script
   python -c "
   import openai
   import os
   client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
   print('OpenAI client configured successfully')
   "
   ```

### Step 4: SQLite Database Setup **[HUMAN REQUIRED]**

SQLite comes built-in with Python, but you should verify it's working properly:

1. **Test SQLite connection:**
   ```bash
   # Test basic SQLite functionality
   python -c "
   import sqlite3
   import os
   
   # Create test database in memory
   conn = sqlite3.connect(':memory:')
   cursor = conn.cursor()
   
   # Test basic operations
   cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)')
   cursor.execute('INSERT INTO test (name) VALUES (?)', ('Hello SQLite',))
   cursor.execute('SELECT * FROM test')
   result = cursor.fetchone()
   
   print('SQLite test successful:', result)
   conn.close()
   "
   ```

2. **Create application database directory:**
   ```bash
   # Create directory for application databases
   mkdir -p ~/.info_agent/data
   
   # Test file-based database creation
   python -c "
   import sqlite3
   import os
   
   db_path = os.path.expanduser('~/.info_agent/data/test.db')
   conn = sqlite3.connect(db_path)
   conn.execute('CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY)')
   conn.close()
   
   print(f'Database created successfully at: {db_path}')
   "
   ```

3. **Verify database file was created:**
   ```bash
   ls -la ~/.info_agent/data/
   # Should show test.db file
   ```

### Step 5: Directory Structure Creation **[AI TASK]**
- This will be handled automatically by the AI agent
- Creates the project structure as defined in system_architecture.md

### Step 6: Basic CLI Framework **[AI TASK]**
- Sets up Click CLI framework
- Creates basic command structure
- Enables testing of components as they're built

## Troubleshooting

### Common Issues

1. **Virtual environment not activating:**
   - Make sure you're in the correct directory
   - Check Python installation: `python --version`
   - Try `python3 -m venv venv` instead of `python -m venv venv`

2. **Package installation failures:**
   - Update pip: `pip install --upgrade pip`
   - Check Python version compatibility
   - Try installing packages individually

3. **OpenAI API issues:**
   - Verify API key is valid
   - Check rate limits and billing status
   - Ensure environment variable is set correctly

4. **SQLite issues:**
   - SQLite is included with Python by default
   - If import fails, reinstall Python
   - Check file permissions for ~/.info_agent/data/ directory
   - Verify disk space is available

### Getting Help
- Check project documentation in `docs/`
- Review error logs in terminal output
- Verify all prerequisites are met

---
*Last updated: $(date)*
