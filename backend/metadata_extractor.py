import json
import os
from backend.db_connector import get_connection


# Path where metadata will be stored
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
METADATA_DIR = os.path.join(BASE_DIR, "metadata")

def extract_metadata():
    conn = get_connection()
    cursor = conn.cursor()

    # Get list of tables in SQLite
    cursor.execute("""
        SELECT name 
        FROM sqlite_master 
        WHERE type='table' AND name NOT LIKE 'sqlite_%';
    """)
    tables = [row[0] for row in cursor.fetchall()]

    all_metadata = {}

    for table in tables:
        # Get column details
        cursor.execute(f"PRAGMA table_info({table});")
        columns_info = cursor.fetchall()

        columns = []
        primary_keys = []

        for col in columns_info:
            col_dict = {
                "column_name": col[1],
                "data_type": col[2],
                "not_null": bool(col[3]),
                "default_value": col[4]
            }

            if col[5] == 1:  # PK flag in SQLite
                primary_keys.append(col[1])

            columns.append(col_dict)

        # Build table metadata
        table_metadata = {
            "table_name": table,
            "columns": columns,
            "primary_keys": primary_keys
        }

        # Save each table metadata as a separate JSON file
        file_path = os.path.join(METADATA_DIR, f"{table}.json")
        with open(file_path, "w") as f:
            json.dump(table_metadata, f, indent=4)

        all_metadata[table] = table_metadata

    conn.close()
    print(f"✅ Metadata extracted for tables: {tables}")
    return all_metadata
