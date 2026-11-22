"""Fake em memória do CoffeeRepository, reaproveitado pelos testes."""

from dataclasses import replace

from domain.entities.coffee import Coffee
from domain.exceptions import ConflictError
from use_cases.ports.coffee_repository import CoffeeRepository


class InMemoryCoffeeRepository(CoffeeRepository):
    def __init__(self) -> None:
        self._coffees: dict[int, Coffee] = {}
        self._next_id = 1

    def add(self, coffee: Coffee) -> Coffee:
        if any(c.identity == coffee.identity for c in self._coffees.values()):
            raise ConflictError(
                "Já existe um café com esse nome e torrefação."
            )
        stored = replace(coffee, id=self._next_id)
        self._coffees[self._next_id] = stored
        self._next_id += 1
        return stored

    def list_all(self) -> list[Coffee]:
        return list(self._coffees.values())
