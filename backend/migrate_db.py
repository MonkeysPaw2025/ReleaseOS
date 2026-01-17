#!/usr/bin/env python3
"""
Database migration script to add SoundCloud columns
Run this to update your existing database without losing data
"""

import sqlite3
import os

DB_PATH = "data/release_os.db"

def migrate():
    """Add SoundCloud-related columns to existing database"""

    if not os.path.exists(DB_PATH):
        print("No database found. Run the app first to create the database.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Starting database migration...")

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(projects)")
    columns = [col[1] for col in cursor.fetchall()]

    migrations_needed = []

    if 'soundcloud_url' not in columns:
        migrations_needed.append(('soundcloud_url', 'TEXT'))

    if 'soundcloud_uploaded_at' not in columns:
        migrations_needed.append(('soundcloud_uploaded_at', 'TIMESTAMP'))

    if migrations_needed:
        print(f"Adding {len(migrations_needed)} new columns...")
        for col_name, col_type in migrations_needed:
            try:
                cursor.execute(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type}")
                print(f"  ✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"  ⚠ Column {col_name} might already exist: {e}")
    else:
        print("Database already up to date!")

    # Create soundcloud_auth table if it doesn't exist
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS soundcloud_auth (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                access_token TEXT NOT NULL,
                refresh_token TEXT,
                expires_at TIMESTAMP,
                user_id TEXT,
                username TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("  ✓ Created soundcloud_auth table (if not exists)")
    except sqlite3.OperationalError as e:
        print(f"  ⚠ Table creation: {e}")

    conn.commit()
    conn.close()

    print("\n✅ Migration complete!")
    print("Restart Release OS to use SoundCloud integration.")


if __name__ == "__main__":
    migrate()
