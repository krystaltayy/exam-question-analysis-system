import sqlite3

connection = sqlite3.connect("database/exam_system.db")

with open("database/schema.sql") as f:
    connection.executescript(f.read())

connection.commit()
connection.close()

print("Database initialized successfully!")