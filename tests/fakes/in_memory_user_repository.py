"""Fake em memória do UserRepository, reaproveitado pelos testes."""

from dataclasses import replace

from domain.entities.user import User
from domain.exceptions import ConflictError
from use_cases.ports.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[int, User] = {}
        self._next_id = 1

    def add(self, user: User) -> User:
        if any(u.email == user.email for u in self._users.values()):
            raise ConflictError("Este e-mail já está cadastrado.")
        stored = replace(user, id=self._next_id)
        self._users[self._next_id] = stored
        self._next_id += 1
        return stored

    def get_by_id(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def list_all(self) -> list[User]:
        return list(self._users.values())
