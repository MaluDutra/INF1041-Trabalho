"""Filtro de nota mínima como critério de busca plugável (OCP).

Entra na busca só pela fábrica registrada no container: ``SearchCoffees``
e a interface ``SearchCriterion`` não mudam.
"""

from decimal import Decimal

from domain.entities.coffee import Coffee
from domain.entities.review import RATING_SCALE
from domain.value_objects.coffee_rating import CoffeeRating
from use_cases.coffee.search_criteria import SearchCriterion
from use_cases.dtos import SearchCoffeesInput

# Opções do filtro, da maior para a menor, derivadas da escala de notas
# (ex.: 4, 3, 2). Ficam de fora os extremos da escala: "1+" só excluiria
# os cafés sem avaliações, "5+" só deixaria as médias perfeitas, e
# "Qualquer" já é a ausência do filtro.
MIN_RATING_OPTIONS: tuple[int, ...] = tuple(
    sorted(RATING_SCALE, reverse=True)[1:-1]
)


class MinRatingCriterion(SearchCriterion):
    """A média arredondada do café é igual ou maior que a mínima.

    Compara com a média arredondada (1 casa), a mesma que o card mostra:
    um café exibido como "4,0" passa em "4+". Sem avaliações não há média
    e o café não passa.
    """

    def __init__(self, minimum: int) -> None:
        self._minimum = Decimal(minimum)

    def matches(self, coffee: Coffee, rating: CoffeeRating) -> bool:
        average = rating.rounded_average
        return average is not None and average >= self._minimum


def min_rating_criterion(
    search: SearchCoffeesInput,
) -> SearchCriterion | None:
    """Fábrica do critério de nota mínima.

    Sem nota mínima, ou com um valor fora de ``MIN_RATING_OPTIONS``, não
    filtra (valor desconhecido é ignorado, como nos outros filtros).
    """
    if search.min_rating not in MIN_RATING_OPTIONS:
        return None
    return MinRatingCriterion(search.min_rating)
