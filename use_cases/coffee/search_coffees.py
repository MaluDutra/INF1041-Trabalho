"""Busca de cafés no catálogo (SCRUM-13)."""

from collections.abc import Sequence

from use_cases.coffee.search_criteria import (
    CriterionFactory,
    term_criterion,
)
from use_cases.dtos import CoffeeSummaryDTO, SearchCoffeesInput
from use_cases.ports.coffee_repository import CoffeeRepository

DEFAULT_CRITERION_FACTORIES: tuple[CriterionFactory, ...] = (term_criterion,)


class SearchCoffees:
    """Devolve os cafés que satisfazem todos os critérios do pedido.

    Os critérios vêm de fábricas injetadas (OCP): filtros novos entram
    como novas fábricas, sem alterar esta classe. Sem critério ativo
    (por exemplo, termo vazio), devolve o catálogo inteiro.
    """

    def __init__(
        self,
        coffee_repository: CoffeeRepository,
        criterion_factories: Sequence[
            CriterionFactory
        ] = DEFAULT_CRITERION_FACTORIES,
    ) -> None:
        self._coffee_repository = coffee_repository
        self._criterion_factories = tuple(criterion_factories)

    def execute(self, search: SearchCoffeesInput) -> list[CoffeeSummaryDTO]:
        criteria = [
            criterion
            for factory in self._criterion_factories
            if (criterion := factory(search)) is not None
        ]
        coffees = sorted(
            (
                coffee
                for coffee in self._coffee_repository.list_all()
                if all(criterion.matches(coffee) for criterion in criteria)
            ),
            key=lambda coffee: coffee.identity,
        )
        return [
            CoffeeSummaryDTO(
                id=coffee.id,
                name=coffee.name,
                roaster=coffee.roaster,
                origin=coffee.origin.value,
            )
            for coffee in coffees
        ]
