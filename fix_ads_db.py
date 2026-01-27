import sqlite3
import os

DB_PATH = 'db.sqlite3'

def fix_db():
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        print("Removing 'ads' from django_migrations...")
        cursor.execute("DELETE FROM django_migrations WHERE app='ads'")
        print(f"Deleted {cursor.rowcount} rows from django_migrations.")

        print("Dropping 'ads_ads' table...")
        cursor.execute("DROP TABLE IF EXISTS ads_ads")
        
        print("Dropping 'ads_adspage' table...")
        cursor.execute("DROP TABLE IF EXISTS ads_adspage")

        conn.commit()
        print("Database cleanup successful.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_db()
