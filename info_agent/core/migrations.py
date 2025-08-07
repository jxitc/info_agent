"""
Database initialization and migration system for Info Agent.

This module handles database schema creation, migrations, and version management
to ensure the database structure is always up-to-date.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from info_agent.core.schema import DatabaseSchema, SchemaConstants
from info_agent.utils.logging_config import get_logger


class MigrationError(Exception):
    """Exception for migration-related errors."""
    pass


class DatabaseInitializer:
    """
    Handles database initialization and schema migrations.
    
    Provides functionality to create initial database structure,
    apply migrations, and track schema versions.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database initializer.
        
        Args:
            db_path: Path to database file. If None, uses default.
        """
        self.logger = get_logger(__name__)
        
        # Set database path
        if db_path is None:
            db_dir = Path(SchemaConstants.DEFAULT_DB_PATH).expanduser()
            db_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = db_dir / SchemaConstants.DATABASE_NAME
        else:
            self.db_path = Path(db_path)
        
        self.logger.info(f"Database initializer for: {self.db_path}")
    
    def database_exists(self) -> bool:
        """Check if database file exists."""
        return self.db_path.exists() and self.db_path.stat().st_size > 0
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection for initialization."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as e:
            self.logger.error(f"Failed to connect for initialization: {e}")
            raise MigrationError(f"Cannot connect to database: {e}")
    
    def initialize_database(self, force: bool = False) -> bool:
        """
        Initialize database with complete schema.
        
        Args:
            force: If True, drop existing tables and recreate
            
        Returns:
            True if initialization was performed, False if already initialized
            
        Raises:
            MigrationError: If initialization fails
        """
        if self.database_exists() and not force and self.is_initialized():
            self.logger.info("Database already initialized")
            return False
        
        self.logger.info("Initializing database schema...")
        
        try:
            with self.get_connection() as conn:
                # Drop existing tables if force mode
                if force:
                    self._drop_all_tables(conn)
                
                # Create all tables
                self._create_tables(conn)
                
                # Create indexes
                self._create_indexes(conn) 
                
                # Create triggers
                self._create_triggers(conn)
                
                # Record initial migration
                self._record_migration(conn, DatabaseSchema.VERSION, "Initial schema creation")
                
                conn.commit()
                
            self.logger.info("Database initialization completed successfully")
            return True
            
        except sqlite3.Error as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise MigrationError(f"Initialization failed: {e}")
    
    def is_initialized(self) -> bool:
        """Check if database is properly initialized."""
        if not self.database_exists():
            return False
        
        try:
            with self.get_connection() as conn:
                # Check if core tables exist
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name IN ('memories', 'schema_migrations')
                """)
                tables = [row[0] for row in cursor.fetchall()]
                
                required_tables = ['memories', 'schema_migrations']
                return all(table in tables for table in required_tables)
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to check initialization: {e}")
            return False
    
    def get_current_version(self) -> Optional[str]:
        """Get current database schema version."""
        if not self.is_initialized():
            return None
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT version FROM schema_migrations 
                    ORDER BY applied_at DESC 
                    LIMIT 1
                """)
                row = cursor.fetchone()
                return row[0] if row else None
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get current version: {e}")
            return None
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """Get complete migration history."""
        if not self.is_initialized():
            return []
        
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT version, applied_at, description 
                    FROM schema_migrations 
                    ORDER BY applied_at DESC
                """)
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'version': row[0],
                        'applied_at': row[1],
                        'description': row[2]
                    })
                
                return history
                
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get migration history: {e}")
            return []
    
    def _drop_all_tables(self, conn: sqlite3.Connection):
        """Drop all existing tables (for force initialization)."""
        self.logger.warning("Dropping all existing tables...")
        
        # Get all table names
        cursor = conn.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        # Drop tables
        for table in tables:
            try:
                conn.execute(f"DROP TABLE IF EXISTS {table}")
                self.logger.debug(f"Dropped table: {table}")
            except sqlite3.Error as e:
                self.logger.warning(f"Failed to drop table {table}: {e}")
    
    def _create_tables(self, conn: sqlite3.Connection):
        """Create all database tables."""
        self.logger.info("Creating database tables...")
        
        for table_name, table_sql in DatabaseSchema.TABLES.items():
            try:
                conn.execute(table_sql)
                self.logger.debug(f"Created table: {table_name}")
            except sqlite3.Error as e:
                self.logger.error(f"Failed to create table {table_name}: {e}")
                raise MigrationError(f"Table creation failed: {table_name}")
    
    def _create_indexes(self, conn: sqlite3.Connection):
        """Create database indexes."""
        self.logger.info("Creating database indexes...")
        
        for index_name, index_sql in DatabaseSchema.INDEXES.items():
            try:
                conn.execute(index_sql)
                self.logger.debug(f"Created index: {index_name}")
            except sqlite3.Error as e:
                self.logger.warning(f"Failed to create index {index_name}: {e}")
                # Indexes are not critical, continue with warning
    
    def _create_triggers(self, conn: sqlite3.Connection):
        """Create database triggers."""
        self.logger.info("Creating database triggers...")
        
        for trigger_name, trigger_sql in DatabaseSchema.TRIGGERS.items():
            try:
                # Split multiple trigger statements
                statements = [stmt.strip() for stmt in trigger_sql.split(';') if stmt.strip()]
                
                for statement in statements:
                    if statement:
                        conn.execute(statement)
                
                self.logger.debug(f"Created trigger: {trigger_name}")
            except sqlite3.Error as e:
                self.logger.warning(f"Failed to create trigger {trigger_name}: {e}")
                # Triggers are not critical, continue with warning
    
    def _record_migration(self, conn: sqlite3.Connection, version: str, description: str):
        """Record a migration in the schema_migrations table."""
        try:
            conn.execute("""
                INSERT INTO schema_migrations (version, description, applied_at)
                VALUES (?, ?, ?)
            """, (version, description, datetime.now().isoformat()))
            
            self.logger.info(f"Recorded migration: {version} - {description}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to record migration: {e}")
            raise MigrationError(f"Migration recording failed: {e}")
    
    def verify_schema(self) -> Dict[str, Any]:
        """
        Verify database schema integrity.
        
        Returns:
            Dictionary with verification results
        """
        results = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'tables_found': [],
            'indexes_found': [],
            'current_version': None
        }
        
        if not self.database_exists():
            results['errors'].append("Database file does not exist")
            return results
        
        try:
            with self.get_connection() as conn:
                # Check tables
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name NOT LIKE 'sqlite_%'
                """)
                
                found_tables = [row[0] for row in cursor.fetchall()]
                results['tables_found'] = found_tables
                
                required_tables = list(DatabaseSchema.TABLES.keys())
                missing_tables = [t for t in required_tables if t not in found_tables]
                
                if missing_tables:
                    results['errors'].extend([f"Missing table: {t}" for t in missing_tables])
                
                # Check indexes
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND name NOT LIKE 'sqlite_%'
                """)
                
                found_indexes = [row[0] for row in cursor.fetchall()]
                results['indexes_found'] = found_indexes
                
                # Check version
                if 'schema_migrations' in found_tables:
                    results['current_version'] = self.get_current_version()
                
                # Schema is valid if no errors
                results['valid'] = len(results['errors']) == 0
                
        except sqlite3.Error as e:
            results['errors'].append(f"Verification failed: {e}")
        
        return results
    
    def reset_database(self) -> bool:
        """
        Reset database by dropping and recreating all structures.
        
        Returns:
            True if reset was successful
        """
        self.logger.warning("Resetting database...")
        
        try:
            # Remove database file if it exists
            if self.db_path.exists():
                self.db_path.unlink()
                self.logger.info("Removed existing database file")
            
            # Initialize fresh database
            return self.initialize_database(force=True)
            
        except Exception as e:
            self.logger.error(f"Database reset failed: {e}")
            raise MigrationError(f"Database reset failed: {e}")
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get comprehensive schema information."""
        return {
            'database_path': str(self.db_path),
            'exists': self.database_exists(),
            'initialized': self.is_initialized(),
            'current_version': self.get_current_version(),
            'schema_version': DatabaseSchema.VERSION,
            'migration_history': self.get_migration_history(),
            'verification': self.verify_schema()
        }


def initialize_database(db_path: Optional[str] = None, force: bool = False) -> bool:
    """
    Convenience function to initialize database.
    
    Args:
        db_path: Database file path
        force: Force reinitialization
        
    Returns:
        True if initialization was performed
    """
    initializer = DatabaseInitializer(db_path)
    return initializer.initialize_database(force=force)


def verify_database(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to verify database schema.
    
    Args:
        db_path: Database file path
        
    Returns:
        Verification results
    """
    initializer = DatabaseInitializer(db_path)
    return initializer.verify_schema()


def get_schema_info(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to get schema information.
    
    Args:
        db_path: Database file path
        
    Returns:
        Schema information dictionary
    """
    initializer = DatabaseInitializer(db_path)
    return initializer.get_schema_info()


# Export main classes and functions
__all__ = [
    'DatabaseInitializer',
    'MigrationError',
    'initialize_database',
    'verify_database', 
    'get_schema_info'
]