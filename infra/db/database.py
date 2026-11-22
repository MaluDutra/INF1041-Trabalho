"""Conexão e criação do schema SQLite."""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS coffees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roaster TEXT NOT NULL,
    origin TEXT NOT NULL,
    added_at TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    normalized_roaster TEXT NOT NULL,
    UNIQUE (normalized_name, normalized_roaster)
);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
