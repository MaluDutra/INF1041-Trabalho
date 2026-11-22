"""Busca de cafés no catálogo (SCRUM-13)."""

from use_cases.dtos import CoffeeSummaryDTO
from use_cases.ports.coffee_repository import CoffeeRepository


class SearchCoffees:
    """Com o termo vazio, devolve o catálogo inteiro.

    Termo, filtros e ordenações entram nos próximos tickets.
    """

    def __init__(self, coffee_repository: CoffeeRepository) -> None:
        self._coffee_repository = coffee_repository

    def execute(self) -> list[CoffeeSummaryDTO]:
        coffees = sorted(
            self._coffee_repository.list_all(),
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
