"""
Database Migration Script for AI Content Platform
This script adds missing columns to the existing SQLite database.
Run this if you're using an existing database that doesn't have the new columns.
"""

import sqlite3
import os

def migrate_database(db_path):
    """Add missing columns to existing database"""
    print(f"Migrating database at: {db_path}")
    
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        print("No migration needed - a new database will be created on first run.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    migrations = []
    
    # Check and add created_at to project table
    try:
        cursor.execute("PRAGMA table_info(project)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'created_at' not in columns:
            migrations.append(("project", "ALTER TABLE project ADD COLUMN created_at DATETIME"))
    except Exception as e:
        print(f"Error checking project table: {e}")
    
    # Check and add original_prompt and generated_content to content table
    try:
        cursor.execute("PRAGMA table_info(content)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'original_prompt' not in columns:
            migrations.append(("content", "ALTER TABLE content ADD COLUMN original_prompt TEXT"))
        if 'generated_content' not in columns:
            migrations.append(("content", "ALTER TABLE content ADD COLUMN generated_content TEXT"))
    except Exception as e:
        print(f"Error checking content table: {e}")
    
    # Check and add response and response_ref to content_version table
    try:
        cursor.execute("PRAGMA table_info(content_version)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'response' not in columns:
            migrations.append(("content_version", "ALTER TABLE content_version ADD COLUMN response TEXT"))
        if 'response_ref' not in columns:
            migrations.append(("content_version", "ALTER TABLE content_version ADD COLUMN response_ref VARCHAR(500)"))
    except Exception as e:
        print(f"Error checking content_version table: {e}")
    
    # Execute migrations
    if migrations:
        print(f"\nApplying {len(migrations)} migrations:")
        for table, sql in migrations:
            print(f"  - Adding column to {table}")
            try:
                cursor.execute(sql)
            except Exception as e:
                print(f"    Warning: {e}")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
    else:
        print("\n✅ Database is up to date - no migration needed.")
    
    conn.close()

if __name__ == "__main__":
    # Default path relative to this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "instance", "dev.db")
    
    migrate_database(db_path)
