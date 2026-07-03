import sqlite3

conn = sqlite3.connect("Database/exam_system.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE users ADD COLUMN reset_token TEXT")
cursor.execute("ALTER TABLE users ADD COLUMN reset_token_expiry TEXT")

conn.commit()
conn.close()

print("Columns added successfully.")