from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from backend.metadata_extractor import extract_metadata
from backend.quality_engine import analyze_quality
from backend.ai_summarizer import generate_table_summary

# Load environment variables
load_dotenv()

app = FastAPI(title="DataDoc AI Backend", version="1.0.0")

# Enable CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Streamlit URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "datadoc_ai"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            port=os.getenv("DB_PORT", "5432")
        )
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.get("/")
async def root():
    return {"message": "DataDoc AI Backend is running!"}

@app.get("/health")
async def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.get("/tables")
async def get_tables():
    """Get list of all tables in the database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name;
        """)
        
        tables = [row["table_name"] for row in cursor.fetchall()]
        conn.close()
        
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch tables: {str(e)}")

@app.get("/tables/{table_name}/metadata")
async def get_table_metadata(table_name: str):
    """Get metadata for a specific table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get column information
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                column_default,
                character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = %s AND table_schema = 'public'
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = []
        for row in cursor.fetchall():
            columns.append({
                "column_name": row["column_name"],
                "data_type": row["data_type"],
                "is_nullable": row["is_nullable"],
                "default_value": row["column_default"],
                "max_length": row["character_maximum_length"]
            })
        
        # Get primary keys
        cursor.execute("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            WHERE tc.constraint_type = 'PRIMARY KEY'
                AND tc.table_name = %s
                AND tc.table_schema = 'public';
        """, (table_name,))
        
        primary_keys = [row["column_name"] for row in cursor.fetchall()]
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
        row_count = cursor.fetchone()["count"]
        
        conn.close()
        
        return {
            "table_name": table_name,
            "columns": columns,
            "primary_keys": primary_keys,
            "row_count": row_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metadata: {str(e)}")

@app.post("/tables/{table_name}/summary")
async def generate_summary(table_name: str):
    """Generate AI summary for a table"""
    try:
        summary = generate_table_summary(table_name)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")

@app.get("/tables/{table_name}/quality")
async def get_table_quality(table_name: str):
    """Get data quality metrics for a table"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get total row count
        cursor.execute(f"SELECT COUNT(*) as total_rows FROM {table_name};")
        total_rows = cursor.fetchone()["total_rows"]
        
        # Get column completeness
        cursor.execute(f"""
            SELECT 
                column_name,
                COUNT(*) as total_count,
                COUNT(CASE WHEN {table_name}.column_name IS NOT NULL THEN 1 END) as non_null_count
            FROM {table_name}
            CROSS JOIN information_schema.columns
            WHERE information_schema.columns.table_name = %s 
                AND information_schema.columns.table_schema = 'public'
                AND information_schema.columns.column_name = column_name
            GROUP BY column_name;
        """, (table_name,))
        
        column_completeness = {}
        for row in cursor.fetchall():
            completeness = (row["non_null_count"] / row["total_count"]) * 100 if row["total_count"] > 0 else 0
            column_completeness[row["column_name"]] = {
                "total_count": row["total_count"],
                "non_null_count": row["non_null_count"],
                "completeness_percent": round(completeness, 2)
            }
        
        conn.close()
        
        return {
            "table_name": table_name,
            "total_rows": total_rows,
            "column_completeness": column_completeness
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze quality: {str(e)}")

@app.post("/refresh-metadata")
async def refresh_metadata():
    """Refresh metadata for all tables"""
    try:
        result = extract_metadata()
        return {"message": "Metadata refreshed successfully", "tables": list(result.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh metadata: {str(e)}")

@app.post("/refresh-quality")
async def refresh_quality():
    """Refresh quality metrics for all tables"""
    try:
        result = analyze_quality()
        return {"message": "Quality metrics refreshed successfully", "tables": list(result.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh quality: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
