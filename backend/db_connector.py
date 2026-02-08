import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Get database connection (PostgreSQL for production, SQLite for local dev)"""
    try:
        # Try PostgreSQL first (production)
        if os.getenv("DB_HOST"):
            conn = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME", "datadoc_ai"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASSWORD", ""),
                port=os.getenv("DB_PORT", "5432")
            )
            return conn
        else:
            # Fallback to SQLite for local development
            import sqlite3
            DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "datadoc_demo.db")
            conn = sqlite3.connect(DB_PATH)
            return conn
    except Exception as e:
        print("❌ Database Connection Error:", e)
        return None
