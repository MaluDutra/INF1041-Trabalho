"""Port do hasher de senhas (separado do repositório, por ISP)."""

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> str:
        """Devolve o hash da senha em texto."""

    @abstractmethod
    def verify(self, password: str, password_hash: str) -> bool:
        """Diz se a senha em texto corresponde ao hash."""
