"""Busca de cafés no catálogo (SCRUM-13)."""

from collections.abc import Sequence

from domain.value_objects.coffee_rating import CoffeeRating
from use_cases.coffee.search_criteria import (
    CriterionFactory,
    term_criterion,
)
from use_cases.coffee.search_sorting import (
    DEFAULT_SORT_STRATEGIES,
    SortStrategy,
)
from use_cases.dtos import CoffeeSummaryDTO, SearchCoffeesInput
from use_cases.ports.coffee_repository import CoffeeRepository
from use_cases.ports.review_repository import ReviewRepository
from use_cases.review.rating_dto import to_rating_dto

DEFAULT_CRITERION_FACTORIES: tuple[CriterionFactory, ...] = (term_criterion,)


class SearchCoffees:
    """Devolve os cafés que satisfazem todos os critérios do pedido.

    Os critérios vêm de fábricas injetadas e as ordenações, de
    estratégias injetadas (OCP): filtros e ordenações novos entram sem
    alterar esta classe. Sem critério ativo (por exemplo, termo vazio),
    devolve o catálogo inteiro. A primeira estratégia é a ordenação
    padrão, usada quando o pedido não escolhe uma conhecida.
    """

    def __init__(
        self,
        coffee_repository: CoffeeRepository,
        review_repository: ReviewRepository,
        criterion_factories: Sequence[
            CriterionFactory
        ] = DEFAULT_CRITERION_FACTORIES,
        sort_strategies: Sequence[SortStrategy] = DEFAULT_SORT_STRATEGIES,
    ) -> None:
        self._coffee_repository = coffee_repository
        self._review_repository = review_repository
        self._criterion_factories = tuple(criterion_factories)
        self._sort_strategies = {s.id: s for s in sort_strategies}
        self._default_sort = sort_strategies[0]

    def execute(self, search: SearchCoffeesInput) -> list[CoffeeSummaryDTO]:
        criteria = [
            criterion
            for factory in self._criterion_factories
            if (criterion := factory(search)) is not None
        ]
        catalog = self._coffee_repository.list_all()
        grouped = self._review_repository.list_ratings_by_coffees(
            [coffee.id for coffee in catalog]
        )
        ratings = {
            coffee.id: CoffeeRating.from_ratings(grouped.get(coffee.id, []))
            for coffee in catalog
        }
        matching = [
            coffee
            for coffee in catalog
            if all(
                criterion.matches(coffee, ratings[coffee.id])
                for criterion in criteria
            )
        ]
        strategy = self._sort_strategies.get(search.sort, self._default_sort)
        matching.sort(key=lambda c: strategy.key(c, ratings[c.id]))
        return [
            CoffeeSummaryDTO(
                id=coffee.id,
                name=coffee.name,
                roaster=coffee.roaster,
                origin=coffee.origin.value,
                rating=to_rating_dto(ratings[coffee.id]),
            )
            for coffee in matching
        ]
