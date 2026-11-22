"""Port do repositório de reviews."""

from abc import ABC, abstractmethod
from collections.abc import Collection

from domain.entities.review import Review


class ReviewRepository(ABC):
    @abstractmethod
    def add(self, review: Review) -> Review:
        """Grava o review e devolve a cópia com o id atribuído.

        Lança ``ConflictError`` se o autor já avaliou esse café
        (ADR 0002).
        """

    @abstractmethod
    def get_by_id(self, review_id: int) -> Review | None:
        """Devolve o review com esse id, ou ``None``."""

    @abstractmethod
    def get_by_author_and_coffee(
        self, author_id: int, coffee_id: int
    ) -> Review | None:
        """Devolve o review do autor sobre o café, ou ``None``."""

    @abstractmethod
    def list_by_coffee(self, coffee_id: int) -> list[Review]:
        """Devolve os reviews do café, sem ordem garantida."""

    @abstractmethod
    def list_by_author(self, author_id: int) -> list[Review]:
        """Devolve os reviews do autor, sem ordem garantida."""

    @abstractmethod
    def list_ratings_by_coffee(self, coffee_id: int) -> list[int]:
        """Devolve as notas dos reviews do café, sem ordem garantida."""

    @abstractmethod
    def list_ratings_by_coffees(
        self, coffee_ids: Collection[int]
    ) -> dict[int, list[int]]:
        """Devolve as notas de vários cafés numa só consulta.

        A chave é o id do café e o valor, as suas notas, sem ordem
        garantida. Café sem reviews pode faltar no resultado.
        """

    @abstractmethod
    def update(self, review: Review) -> Review:
        """Grava nota, texto e marcador de editado de um review já salvo.

        A data de criação, o autor e o café não mudam. Lança
        ``NotFoundError`` se o id não existe.
        """

    @abstractmethod
    def delete(self, review_id: int) -> None:
        """Remove o review, liberando o autor para avaliar de novo.

        Lança ``NotFoundError`` se o id não existe.
        """
