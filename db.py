import importlib
import sqlite3
click = importlib.import_module("click")
from contextlib import contextmanager

flask = importlib.import_module("flask")
current_app = flask.current_app
g = flask.g

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("my_flask_app.sqlite", detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@contextmanager
def get_db_cursor():
    """
    Safely get a database cursor.
    Auto-commits on success, rolls back on error, and ALWAYS closes the connection.
    """
    db = get_db()
    cursor = db.cursor()
    try:
        yield cursor
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        cursor.close()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo("Initialized the database.")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)