import json
import os
from backend.db_connector import get_connection
from backend.metadata_extractor import extract_metadata


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
METADATA_DIR = os.path.join(BASE_DIR, "metadata")

def analyze_quality():
    conn = get_connection()
    cursor = conn.cursor()

    # Make sure latest metadata exists
    metadata = extract_metadata()

    quality_results = {}

    for table, meta in metadata.items():
        table_quality = {}

        # 1) Total row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        total_rows = cursor.fetchone()[0]
        table_quality["total_rows"] = total_rows

        # 2) Column-level completeness
        column_quality = {}

        for col in meta["columns"]:
            col_name = col["column_name"]

            cursor.execute(f"SELECT COUNT({col_name}) FROM {table}")
            non_null_count = cursor.fetchone()[0]

            completeness = 0
            if total_rows > 0:
                completeness = round((non_null_count / total_rows) * 100, 2)

            column_quality[col_name] = {
                "non_null_count": non_null_count,
                "completeness_percent": completeness
            }

        table_quality["column_completeness"] = column_quality

        # 3) Primary key health (duplicates)
        pk = meta["primary_keys"][0] if meta["primary_keys"] else None
        duplicate_keys = 0

        if pk:
            cursor.execute(f"""
                SELECT COUNT(*) FROM (
                    SELECT {pk}
                    FROM {table}
                    GROUP BY {pk}
                    HAVING COUNT(*) > 1
                )
            """)
            duplicate_keys = cursor.fetchone()[0]

        table_quality["duplicate_primary_keys"] = duplicate_keys

        # 4) Simple freshness check (if a date-like column exists)
        freshness_column = None
        for col in meta["columns"]:
            if "date" in col["column_name"] or "at" in col["column_name"]:
                freshness_column = col["column_name"]
                break

        last_updated = None
        if freshness_column:
            cursor.execute(f"SELECT MAX({freshness_column}) FROM {table}")
            last_updated = cursor.fetchone()[0]

        table_quality["freshness_column"] = freshness_column
        table_quality["last_updated"] = last_updated

        # Save per-table quality report
        quality_results[table] = table_quality

        # Write to JSON file
        quality_file = os.path.join(METADATA_DIR, f"{table}_quality.json")
        with open(quality_file, "w") as f:
            json.dump(table_quality, f, indent=4)

    conn.close()
    print("✅ Data quality analysis completed for all tables.")
    return quality_results
