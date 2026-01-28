#!/usr/bin/env python3
"""
Initialize SQLite database with schema and seed data
"""

import sqlite3
from pathlib import Path


def init_database(db_path: str = "database/land_records.db"):
    """Initialize database with schema and seed data"""

    # Ensure database directory exists
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print(f"📊 Initializing database: {db_path}")

    # Load and execute schema
    schema_path = db_file.parent / "schema.sql"
    if schema_path.exists():
        print("  ✓ Loading schema...")
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)
        print("  ✓ Schema created")
    else:
        print(f"  ✗ Schema file not found: {schema_path}")
        return False

    # Load and execute seed data
    seed_path = db_file.parent / "seed_data.sql"
    if seed_path.exists():
        print("  ✓ Loading seed data...")
        with open(seed_path, 'r') as f:
            seed_sql = f.read()
        conn.executescript(seed_sql)
        print("  ✓ Seed data inserted")
    else:
        print(f"  ✗ Seed data file not found: {seed_path}")

    # Verify data
    cursor.execute("SELECT COUNT(*) FROM properties")
    count = cursor.fetchone()[0]
    print(f"  ✓ Total properties: {count}")

    # Show statistics
    cursor.execute("""
        SELECT locality, COUNT(*) as count
        FROM properties
        GROUP BY locality
        ORDER BY locality
    """)

    print("\n📈 Properties by locality:")
    for row in cursor.fetchall():
        print(f"  • {row[0]}: {row[1]}")

    conn.commit()
    conn.close()

    print(f"\n✅ Database initialized successfully!")
    return True


if __name__ == "__main__":
    init_database()
