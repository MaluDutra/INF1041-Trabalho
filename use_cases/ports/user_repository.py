"""Port do repositório de usuários."""

from abc import ABC, abstractmethod

from domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> User:
        """Grava o usuário e devolve a cópia com o id atribuído.

        Lança ``ConflictError`` se o e-mail (já normalizado) está em uso.
        """

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        """Devolve o usuário com o id dado, ou ``None`` se não existir."""
