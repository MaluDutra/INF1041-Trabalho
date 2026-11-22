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
    producer TEXT,
    variety TEXT,
    process TEXT,
    altitude INTEGER,
    roast TEXT,
    photo_url TEXT,
    story TEXT,
    normalized_name TEXT NOT NULL,
    normalized_roaster TEXT NOT NULL,
    UNIQUE (normalized_name, normalized_roaster)
);

CREATE TABLE IF NOT EXISTS coffee_sensory_notes (
    coffee_id INTEGER NOT NULL REFERENCES coffees (id),
    position INTEGER NOT NULL,
    note TEXT NOT NULL,
    PRIMARY KEY (coffee_id, note)
);

CREATE TABLE IF NOT EXISTS coffee_brew_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coffee_id INTEGER NOT NULL REFERENCES coffees (id),
    position INTEGER NOT NULL,
    method TEXT NOT NULL,
    ratio TEXT,
    grind TEXT,
    temperature TEXT
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users (id),
    coffee_id INTEGER NOT NULL REFERENCES coffees (id),
    rating INTEGER NOT NULL,
    text TEXT,
    created_at TEXT NOT NULL,
    edited INTEGER NOT NULL DEFAULT 0,
    UNIQUE (user_id, coffee_id)
);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
