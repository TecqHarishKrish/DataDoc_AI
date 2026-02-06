from db_connector import get_connection

conn = get_connection()

if conn:
    print("✅ Connected to PostgreSQL successfully!")
    conn.close()
else:
    print("❌ Connection failed.")
