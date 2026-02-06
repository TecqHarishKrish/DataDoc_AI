from db_connector import get_connection

conn = get_connection()
cursor = conn.cursor()

# --------- MORE REALISTIC CUSTOMERS ---------
cursor.executemany("""
INSERT INTO customers (name, email, city, created_at)
VALUES (?, ?, ?, ?)
""", [
    ("Vikram Iyer", "vikram.iyer@example.com", "Coimbatore", "2024-01-18"),
    ("Sandhya R", "sandhya.r@example.com", "Chennai", "2024-01-20"),
    ("Rohan Patel", "rohan.p@example.com", "Ahmedabad", "2024-01-22"),
    ("Meera Menon", None, "Kochi", "2024-01-23"),   # Missing email (quality test)
    ("Amit Shah", "amit.shah@example.com", "Delhi", "2024-01-25"),
    ("Priyanka N", "priyanka.n@example.com", "Bangalore", "2024-01-26"),
    ("Karthik S", None, "Madurai", "2024-01-28"),  # Missing email
    ("Arun Kumar", "arun.k@example.com", "Trichy", "2024-01-30"),
    ("Neeraj Gupta", "neeraj.g@example.com", "Jaipur", "2024-02-01"),
    ("Ananya Rao", "ananya.rao@example.com", "Hyderabad", "2024-02-02")
])

# --------- MORE REALISTIC ORDERS ---------
cursor.executemany("""
INSERT INTO orders (customer_id, order_date, total_amount, shipping_address)
VALUES (?, ?, ?, ?)
""", [
    (6, "2024-02-18", 4200.00, "Bangalore"),
    (7, "2024-02-19", 980.00, None),           # Missing address
    (8, "2024-02-20", 2750.00, "Trichy"),
    (9, "2024-02-21", 15000.00, "Jaipur"),
    (10, "2024-02-22", 3200.00, "Hyderabad"),
    (6, "2024-02-23", 5100.00, "Bangalore"),
    (2, "2024-02-24", 650.00, "Mumbai"),
    (3, "2024-02-25", 7600.00, None),          # Edge case
    (1, "2024-02-26", 1200.00, "Chennai"),
    (4, "2024-02-27", 8900.00, "Hyderabad")
])

# --------- MORE REALISTIC PAYMENTS ---------
cursor.executemany("""
INSERT INTO payments (order_id, payment_method, payment_status, paid_at)
VALUES (?, ?, ?, ?)
""", [
    (7, "UPI", "SUCCESS", "2024-02-19 11:15:00"),
    (8, "CARD", "SUCCESS", "2024-02-20 09:40:00"),
    (9, "NETBANKING", "PENDING", "2024-02-21 14:10:00"),
    (10, "UPI", "SUCCESS", "2024-02-22 18:55:00"),
    (11, "CARD", "FAILED", "2024-02-23 08:30:00"),
    (12, "UPI", "SUCCESS", "2024-02-24 16:20:00"),
    (13, "CARD", "SUCCESS", "2024-02-25 21:05:00"),
    (14, "NETBANKING", "SUCCESS", "2024-02-26 10:45:00"),
    (15, "UPI", "PENDING", "2024-02-27 13:25:00"),
    (16, "CARD", "SUCCESS", "2024-02-27 19:50:00")
])

conn.commit()
conn.close()

print("✅ More realistic data inserted successfully!")
