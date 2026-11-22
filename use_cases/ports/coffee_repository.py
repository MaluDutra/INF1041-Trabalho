"""Port do repositório de cafés."""

from abc import ABC, abstractmethod

from domain.entities.coffee import Coffee


class CoffeeRepository(ABC):
    @abstractmethod
    def add(self, coffee: Coffee) -> Coffee:
        """Grava o café e devolve a cópia com o id atribuído.

        Lança ``ConflictError`` se já existe um café com o mesmo par
        (nome, torrefação) normalizado.
        """

    @abstractmethod
    def list_all(self) -> list[Coffee]:
        """Devolve todos os cafés do catálogo, sem ordem garantida."""

    @abstractmethod
    def get_by_id(self, coffee_id: int) -> Coffee | None:
        """Devolve o café com o id dado, ou ``None`` se não existir."""
