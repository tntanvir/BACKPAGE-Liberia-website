import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

try:
    # Set category to NULL for all rows in market_product
    # Note: If the column is NOT NULL constraint, this might fail, but currently it's likely just CharField from previous model state.
    # We update it to NULL so that when we migrate, the column is empty (or we can delete rows).
    # Since we are converting to ForeignKey, old string values are invalid.
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='market_product';")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='market_productimage';")
    if cursor.fetchone():
        print("Table market_productimage found. Deleting all rows...")
        cursor.execute("DELETE FROM market_productimage;")
        conn.commit()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='market_product';")
    if cursor.fetchone():
        print("Table market_product found. Deleting all rows...")
        cursor.execute("DELETE FROM market_product;")
        conn.commit()
        print("Deleted all rows successfully.")
    else:
        print("Table market_product not found.")

except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
