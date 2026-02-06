import sqlite3
from db_connector import get_connection

conn = get_connection()
cursor = conn.cursor()

# ---- CREATE TABLES ----

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    city TEXT,
    created_at TEXT
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    order_date TEXT,
    total_amount REAL,
    shipping_address TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    payment_method TEXT,
    payment_status TEXT,
    paid_at TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
""")

# ---- INSERT FAKE DATA ----

cursor.executemany("""
INSERT INTO customers (name, email, city, created_at)
VALUES (?, ?, ?, ?)
""", [
    ("Alice Kumar", "alice@example.com", "Chennai", "2024-01-01"),
    ("Rahul Mehta", "rahul@example.com", "Mumbai", "2024-01-05"),
    ("Priya Nair", "priya@example.com", "Bangalore", "2024-01-10"),
    ("Arjun Reddy", "arjun@example.com", "Hyderabad", "2024-01-12"),
    ("Neha Sharma", None, "Delhi", "2024-01-15")
])

cursor.executemany("""
INSERT INTO orders (customer_id, order_date, total_amount, shipping_address)
VALUES (?, ?, ?, ?)
""", [
    (1, "2024-02-01", 2500.00, "Chennai"),
    (2, "2024-02-03", 1800.00, "Mumbai"),
    (3, "2024-02-05", 3200.00, None),
    (1, "2024-02-10", 1500.00, "Chennai"),
    (4, "2024-02-12", 5000.00, "Hyderabad"),
    (2, "2024-02-15", 2100.00, "Mumbai")
])

cursor.executemany("""
INSERT INTO payments (order_id, payment_method, payment_status, paid_at)
VALUES (?, ?, ?, ?)
""", [
    (1, "UPI", "SUCCESS", "2024-02-01 10:00:00"),
    (2, "CARD", "SUCCESS", "2024-02-03 12:30:00"),
    (3, "UPI", "FAILED", "2024-02-05 09:15:00"),
    (4, "NETBANKING", "SUCCESS", "2024-02-10 14:00:00"),
    (5, "UPI", "SUCCESS", "2024-02-12 16:45:00"),
    (6, "CARD", "SUCCESS", "2024-02-15 18:20:00")
])

conn.commit()
conn.close()

print("✅ Fake data inserted successfully into SQLite!")
