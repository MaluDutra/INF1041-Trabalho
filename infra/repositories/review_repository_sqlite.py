"""Repositório de reviews em SQLite."""

import sqlite3
from contextlib import closing
from dataclasses import replace
from datetime import datetime
from pathlib import Path

from domain.entities.review import Review
from domain.exceptions import ConflictError
from infra.db.database import connect
from use_cases.ports.review_repository import ReviewRepository

_COLUMNS = "id, user_id, coffee_id, rating, text, created_at, edited"


class SqliteReviewRepository(ReviewRepository):
    """Abre uma conexão por operação, o que é seguro com threads."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = db_path

    def add(self, review: Review) -> Review:
        try:
            with closing(connect(self._db_path)) as connection, connection:
                cursor = connection.execute(
                    "INSERT INTO reviews (user_id, coffee_id, rating, text,"
                    " created_at, edited) VALUES (?, ?, ?, ?, ?, ?)",
                    (
                        review.author_id,
                        review.coffee_id,
                        review.rating,
                        review.text,
                        review.created_at.isoformat(),
                        int(review.edited),
                    ),
                )
        except sqlite3.IntegrityError as error:
            if error.sqlite_errorcode != sqlite3.SQLITE_CONSTRAINT_UNIQUE:
                raise
            raise ConflictError("Você já avaliou este café.") from error
        return replace(review, id=cursor.lastrowid)

    def get_by_author_and_coffee(
        self, author_id: int, coffee_id: int
    ) -> Review | None:
        with closing(connect(self._db_path)) as connection:
            row = connection.execute(
                f"SELECT {_COLUMNS} FROM reviews"
                " WHERE user_id = ? AND coffee_id = ?",
                (author_id, coffee_id),
            ).fetchone()
        return None if row is None else self._to_review(row)

    def list_by_coffee(self, coffee_id: int) -> list[Review]:
        with closing(connect(self._db_path)) as connection:
            rows = connection.execute(
                f"SELECT {_COLUMNS} FROM reviews WHERE coffee_id = ?",
                (coffee_id,),
            ).fetchall()
        return [self._to_review(row) for row in rows]

    def list_ratings_by_coffee(self, coffee_id: int) -> list[int]:
        with closing(connect(self._db_path)) as connection:
            rows = connection.execute(
                "SELECT rating FROM reviews WHERE coffee_id = ?",
                (coffee_id,),
            ).fetchall()
        return [row["rating"] for row in rows]

    @staticmethod
    def _to_review(row: sqlite3.Row) -> Review:
        return Review(
            id=row["id"],
            author_id=row["user_id"],
            coffee_id=row["coffee_id"],
            rating=row["rating"],
            text=row["text"],
            created_at=datetime.fromisoformat(row["created_at"]),
            edited=bool(row["edited"]),
        )
