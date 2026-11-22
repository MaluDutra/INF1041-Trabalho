"""Repositório de cafés em SQLite."""

import sqlite3
from collections import defaultdict
from contextlib import closing
from dataclasses import replace
from datetime import date
from pathlib import Path

from domain.entities.coffee import Coffee
from domain.exceptions import ConflictError
from domain.value_objects.brew_recommendation import BrewRecommendation
from infra.db.database import connect
from use_cases.ports.coffee_repository import CoffeeRepository

_COFFEE_COLUMNS = (
    "id, name, roaster, origin, added_at, producer, variety, process,"
    " altitude, roast, photo_url, story"
)


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
                    " producer, variety, process, altitude, roast,"
                    " photo_url, story, normalized_name,"
                    " normalized_roaster)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        coffee.name,
                        coffee.roaster,
                        coffee.origin.value,
                        coffee.added_at.isoformat(),
                        coffee.producer,
                        coffee.variety,
                        coffee.process.value if coffee.process else None,
                        coffee.altitude,
                        coffee.roast.value if coffee.roast else None,
                        coffee.photo_url,
                        coffee.story,
                        normalized_name,
                        normalized_roaster,
                    ),
                )
                self._insert_children(connection, cursor.lastrowid, coffee)
        except sqlite3.IntegrityError as error:
            raise ConflictError(
                "Já existe um café com esse nome e torrefação."
            ) from error
        return replace(coffee, id=cursor.lastrowid)

    def get_by_id(self, coffee_id: int) -> Coffee | None:
        with closing(connect(self._db_path)) as connection:
            rows = connection.execute(
                f"SELECT {_COFFEE_COLUMNS} FROM coffees WHERE id = ?",
                (coffee_id,),
            ).fetchall()
            coffees = self._build_coffees(connection, rows)
        return coffees[0] if coffees else None

    def list_all(self) -> list[Coffee]:
        with closing(connect(self._db_path)) as connection:
            rows = connection.execute(
                f"SELECT {_COFFEE_COLUMNS} FROM coffees"
            ).fetchall()
            return self._build_coffees(connection, rows)

    @staticmethod
    def _insert_children(
        connection: sqlite3.Connection, coffee_id: int, coffee: Coffee
    ) -> None:
        connection.executemany(
            "INSERT INTO coffee_sensory_notes (coffee_id, position, note)"
            " VALUES (?, ?, ?)",
            [
                (coffee_id, position, note.value)
                for position, note in enumerate(coffee.sensory_notes)
            ],
        )
        connection.executemany(
            "INSERT INTO coffee_brew_recommendations (coffee_id, position,"
            " method, ratio, grind, temperature) VALUES (?, ?, ?, ?, ?, ?)",
            [
                (
                    coffee_id,
                    position,
                    brew.method,
                    brew.ratio,
                    brew.grind,
                    brew.temperature,
                )
                for position, brew in enumerate(coffee.brew_recommendations)
            ],
        )

    @staticmethod
    def _build_coffees(
        connection: sqlite3.Connection, rows: list[sqlite3.Row]
    ) -> list[Coffee]:
        ids = [row["id"] for row in rows]
        marks = ", ".join("?" for _ in ids)
        notes = defaultdict(list)
        for row in connection.execute(
            "SELECT coffee_id, note FROM coffee_sensory_notes"
            f" WHERE coffee_id IN ({marks}) ORDER BY coffee_id, position",
            ids,
        ):
            notes[row["coffee_id"]].append(row["note"])
        brews = defaultdict(list)
        for row in connection.execute(
            "SELECT coffee_id, method, ratio, grind, temperature"
            " FROM coffee_brew_recommendations"
            f" WHERE coffee_id IN ({marks}) ORDER BY coffee_id, position",
            ids,
        ):
            brews[row["coffee_id"]].append(
                BrewRecommendation(
                    method=row["method"],
                    ratio=row["ratio"],
                    grind=row["grind"],
                    temperature=row["temperature"],
                )
            )
        return [
            Coffee(
                id=row["id"],
                name=row["name"],
                roaster=row["roaster"],
                origin=row["origin"],
                added_at=date.fromisoformat(row["added_at"]),
                producer=row["producer"],
                variety=row["variety"],
                process=row["process"],
                altitude=row["altitude"],
                roast=row["roast"],
                sensory_notes=notes[row["id"]],
                photo_url=row["photo_url"],
                story=row["story"],
                brew_recommendations=brews[row["id"]],
            )
            for row in rows
        ]
