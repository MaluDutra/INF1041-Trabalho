"""Repositório de cafés em SQLite."""

import sqlite3
from contextlib import closing
from dataclasses import replace
from datetime import date
from pathlib import Path

from domain.entities.coffee import Coffee
from domain.exceptions import ConflictError
from infra.db.database import connect
from use_cases.ports.coffee_repository import CoffeeRepository


class SqliteCoffeeRepository(CoffeeRepository):
    """Abre uma conexão por operação, o que é seguro com threads."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = db_path

    def add(self, coffee: Coffee) -> Coffee:
        normalized_name, normalized_roaster = coffee.identity
        try:
            with closing(connect(self._db_path)) as connection, connection:
                cursor = connection.execute(
                    "INSERT INTO coffees (name, roaster, origin, added_at,"
                    " normalized_name, normalized_roaster)"
                    " VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        coffee.name,
                        coffee.roaster,
                        coffee.origin.value,
                        coffee.added_at.isoformat(),
                        normalized_name,
                        normalized_roaster,
                    ),
                )
        except sqlite3.IntegrityError as error:
            raise ConflictError(
                "Já existe um café com esse nome e torrefação."
            ) from error
        return replace(coffee, id=cursor.lastrowid)

    def list_all(self) -> list[Coffee]:
        with closing(connect(self._db_path)) as connection:
            rows = connection.execute(
                "SELECT id, name, roaster, origin, added_at FROM coffees"
            ).fetchall()
        return [
            Coffee(
                id=row["id"],
                name=row["name"],
                roaster=row["roaster"],
                origin=row["origin"],
                added_at=date.fromisoformat(row["added_at"]),
            )
            for row in rows
        ]
