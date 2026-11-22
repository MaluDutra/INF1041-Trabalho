"""Critérios de busca plugáveis (OCP) do caso de uso SearchCoffees.

Cada critério decide se um café entra no resultado. Um novo filtro é
um novo critério mais a sua fábrica, registrada no container, sem mexer
em ``SearchCoffees``.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable

from domain.entities.coffee import Coffee
from domain.exceptions import ValidationError
from domain.text import normalize_text
from use_cases.dtos import SearchCoffeesInput

MIN_TERM_LENGTH = 2


class SearchCriterion(ABC):
    @abstractmethod
    def matches(self, coffee: Coffee) -> bool:
        """Diz se o café satisfaz o critério."""


# Cria o critério a partir do pedido; ``None`` quando o pedido não usa
# esse critério. Pode lançar ``ValidationError`` para um pedido inválido.
CriterionFactory = Callable[[SearchCoffeesInput], SearchCriterion | None]


class TermCriterion(SearchCriterion):
    """O termo, como frase inteira, está no nome, torrefação ou produtor.

    A normalização (sem acentos, sem maiúsculas) acontece aqui, em
    memória, com ``normalize_text`` do domínio. O repositório devolve
    o catálogo e não precisa saber de busca nem de acentos.
    """

    def __init__(self, normalized_term: str) -> None:
        self._term = normalized_term

    def matches(self, coffee: Coffee) -> bool:
        fields = (coffee.name, coffee.roaster, coffee.producer or "")
        return any(self._term in normalize_text(field) for field in fields)


def term_criterion(search: SearchCoffeesInput) -> SearchCriterion | None:
    """Fábrica do critério de termo.

    Termo vazio (ou só espaços) não filtra nada. Com um único caractere
    útil, o pedido é inválido: a busca exige pelo menos 2.
    """
    term = normalize_text(search.term)
    if not term:
        return None
    if len(term) < MIN_TERM_LENGTH:
        raise ValidationError(
            f"Digite pelo menos {MIN_TERM_LENGTH} caracteres para buscar."
        )
    return TermCriterion(term)
