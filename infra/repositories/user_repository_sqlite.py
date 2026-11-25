"""Repositório de usuários em SQLite."""

import sqlite3
from contextlib import closing
from dataclasses import replace
from pathlib import Path

from domain.entities.user import User
from domain.exceptions import ConflictError
from infra.db.database import connect
from use_cases.ports.user_repository import UserRepository


class SqliteUserRepository(UserRepository):
    """Abre uma conexão por operação, o que é seguro com threads."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = db_path

    def add(self, user: User) -> User:
        try:
            with closing(connect(self._db_path)) as connection, connection:
                cursor = connection.execute(
                    "INSERT INTO users (display_name, email, password_hash)"
                    " VALUES (?, ?, ?)",
                    (user.display_name, user.email, user.password_hash),
                )
        except sqlite3.IntegrityError as error:
            raise ConflictError("Este e-mail já está cadastrado.") from error
        return replace(user, id=cursor.lastrowid)

    def get_by_id(self, user_id: int) -> User | None:
        return self._find("id = ?", user_id)

    def get_by_email(self, email: str) -> User | None:
        return self._find("email = ?", email)

    def _find(self, condition: str, value: int | str) -> User | None:
        with closing(connect(self._db_path)) as connection:
            row = connection.execute(
                "SELECT id, display_name, email, password_hash"
                f" FROM users WHERE {condition}",
                (value,),
            ).fetchone()
        if row is None:
            return None
        return User(
            id=row["id"],
            display_name=row["display_name"],
            email=row["email"],
            password_hash=row["password_hash"],
        )
