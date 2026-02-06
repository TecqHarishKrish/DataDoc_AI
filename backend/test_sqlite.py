from db_connector import get_connection

conn = get_connection()

if conn:
    print("✅ SQLite database created / connected successfully!")
    conn.close()
else:
    print("❌ Connection failed.")
