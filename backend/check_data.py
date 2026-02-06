from db_connector import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SELECT * FROM customers;")
print("Customers:")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT * FROM orders;")
print("\nOrders:")
for row in cursor.fetchall():
    print(row)

cursor.execute("SELECT * FROM payments;")
print("\nPayments:")
for row in cursor.fetchall():
    print(row)

conn.close()
