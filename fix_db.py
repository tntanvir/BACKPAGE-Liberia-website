import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
try:
    cursor.execute("UPDATE artist_music SET music_type = NULL")
    conn.commit()
    print("Successfully set music_type to NULL")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
