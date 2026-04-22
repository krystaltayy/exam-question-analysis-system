import sqlite3
import click
from flask import Flask, g

app = Flask(__name__)

# --- DATABASE SETUP ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("my_flask_app.sqlite", detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

# Close the database connection when the request finishes
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# The initialization script reader
def init_db():
    db = get_db()
    with app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# The terminal command to run the script
@app.cli.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the SQLite database.')


# --- WEB ROUTES ---
@app.route("/")
def home():
    return "<h1>Server is running!</h1><p>Your Flask app and SQLite database are ready.</p>"

if __name__ == "__main__":
    app.run(debug=True)