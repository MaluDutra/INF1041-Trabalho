"""Ordenações plugáveis (OCP) do caso de uso SearchCoffees.

Cada ordenação é uma estratégia que produz a chave de ordenação de um
café, a partir dele e da sua Nota agregada. Uma ordenação nova é uma
classe nova, registrada no container, sem mexer em ``SearchCoffees``.
"""

from abc import ABC, abstractmethod
from typing import ClassVar

from domain.entities.coffee import Coffee
from domain.value_objects.coffee_rating import CoffeeRating

SortKey = tuple


class SortStrategy(ABC):
    """Produz a chave que ordena os cafés do menor para o maior."""

    id: ClassVar[str]
    label: ClassVar[str]

    @abstractmethod
    def key(self, coffee: Coffee, rating: CoffeeRating) -> SortKey:
        """Devolve a chave de ordenação do café."""


class BestRated(SortStrategy):
    """Maior média exata, depois mais reviews, depois o nome.

    Cafés sem avaliações vão para o fim, em ordem alfabética. A média
    usada é a exata, não a arredondada que aparece no card.
    """

    id = "melhor-avaliados"
    label = "Melhor avaliados"

    def key(self, coffee: Coffee, rating: CoffeeRating) -> SortKey:
        if rating.average is None:
            return (1, coffee.identity)
        return (0, -rating.average, -rating.count, coffee.identity)


class MostReviewed(SortStrategy):
    """Mais reviews, depois a maior média exata, depois o nome.

    Cafés sem avaliações vão para o fim, em ordem alfabética.
    """

    id = "mais-avaliados"
    label = "Mais avaliados"

    def key(self, coffee: Coffee, rating: CoffeeRating) -> SortKey:
        if rating.average is None:
            return (1, coffee.identity)
        return (0, -rating.count, -rating.average, coffee.identity)


class MostRecent(SortStrategy):
    """Entrada mais recente no catálogo primeiro, depois o nome."""

    id = "mais-recentes"
    label = "Mais recentes"

    def key(self, coffee: Coffee, rating: CoffeeRating) -> SortKey:
        return (-coffee.added_at.toordinal(), coffee.identity)


# A primeira é a ordenação padrão; a ordem também é a das opções na tela.
DEFAULT_SORT_STRATEGIES: tuple[SortStrategy, ...] = (
    BestRated(),
    MostReviewed(),
    MostRecent(),
)
