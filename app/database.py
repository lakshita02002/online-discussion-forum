"""
Low-level SQLite helpers. One connection per request via Flask's g proxy;
rows are sqlite3.Row objects (column access by name).
"""

import sqlite3
import os
from flask import g, current_app


def get_db():
    """Return the SQLite connection for the current request, opening it if needed."""
    if "db" not in g:
        db_path = current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row          # access columns by name
        g.db.execute("PRAGMA foreign_keys = ON") # enforce FK constraints
    return g.db


def close_db(exception=None):
    """Close the connection at request teardown (registered via teardown_appcontext)."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(app):
    """Execute schema.sql. Safe to call repeatedly — CREATE TABLE uses IF NOT EXISTS."""
    schema_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "schema.sql"
    )
    db_path = app.config["DATABASE"]

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def query_db(sql: str, args: tuple = (), one: bool = False):
    """Run a SELECT. Returns a single Row (or None) when one=True, else a list."""
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute_db(sql: str, args: tuple = ()):
    """Run an INSERT/UPDATE/DELETE, commit, and return lastrowid."""
    db = get_db()
    cur = db.execute(sql, args)
    db.commit()
    return cur.lastrowid

