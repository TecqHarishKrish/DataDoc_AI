"""
Script to migrate SQLite data to PostgreSQL
Run this locally to export your data before deployment
"""
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

def get_sqlite_connection():
    """Connect to SQLite database"""
    DB_PATH = "datadoc_demo.db"
    return sqlite3.connect(DB_PATH)

def get_postgres_connection():
    """Connect to PostgreSQL database"""
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "datadoc_ai"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        port=os.getenv("DB_PORT", "5432")
    )

def create_postgres_tables():
    """Create tables in PostgreSQL"""
    conn = get_postgres_connection()
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255),
            city VARCHAR(100),
            registration_date DATE
        );
    """)
    
    # Create orders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date DATE NOT NULL,
            total_amount DECIMAL(10,2) NOT NULL,
            shipping_address VARCHAR(255),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
    """)
    
    # Create payments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            payment_date DATE NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            payment_method VARCHAR(50),
            payment_status VARCHAR(20) NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );
    """)
    
    conn.commit()
    conn.close()
    print("✅ PostgreSQL tables created")

def migrate_table(table_name):
    """Migrate data from SQLite to PostgreSQL"""
    sqlite_conn = get_sqlite_connection()
    postgres_conn = get_postgres_connection()
    
    # Get data from SQLite
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute(f"SELECT * FROM {table_name}")
    columns = [description[0] for description in sqlite_cursor.description]
    rows = sqlite_cursor.fetchall()
    
    if not rows:
        print(f"⚠️ No data found in {table_name}")
        return
    
    # Insert into PostgreSQL
    postgres_cursor = postgres_conn.cursor()
    
    # Clear existing data
    postgres_cursor.execute(f"DELETE FROM {table_name}")
    
    # Prepare insert query
    placeholders = ', '.join(['%s'] * len(columns))
    insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    
    # Insert data
    postgres_cursor.executemany(insert_query, rows)
    
    postgres_conn.commit()
    sqlite_conn.close()
    postgres_conn.close()
    
    print(f"✅ Migrated {len(rows)} rows from {table_name}")

def main():
    print("🚀 Starting migration from SQLite to PostgreSQL...")
    
    # Check PostgreSQL connection
    try:
        conn = get_postgres_connection()
        conn.close()
        print("✅ PostgreSQL connection successful")
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("Please set DB_HOST, DB_NAME, DB_USER, DB_PASSWORD in .env file")
        return
    
    # Create tables
    create_postgres_tables()
    
    # Migrate data
    tables = ['customers', 'orders', 'payments']
    for table in tables:
        migrate_table(table)
    
    print("🎉 Migration completed!")

if __name__ == "__main__":
    main()
