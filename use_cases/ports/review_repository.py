"""Port do repositório de reviews."""

from abc import ABC, abstractmethod

from domain.entities.review import Review


class ReviewRepository(ABC):
    @abstractmethod
    def add(self, review: Review) -> Review:
        """Grava o review e devolve a cópia com o id atribuído.

        Lança ``ConflictError`` se o autor já avaliou esse café
        (ADR 0002).
        """

    @abstractmethod
    def get_by_author_and_coffee(
        self, author_id: int, coffee_id: int
    ) -> Review | None:
        """Devolve o review do autor sobre o café, ou ``None``."""

    @abstractmethod
    def list_by_coffee(self, coffee_id: int) -> list[Review]:
        """Devolve os reviews do café, sem ordem garantida."""

    @abstractmethod
    def list_ratings_by_coffee(self, coffee_id: int) -> list[int]:
        """Devolve as notas dos reviews do café, sem ordem garantida."""
