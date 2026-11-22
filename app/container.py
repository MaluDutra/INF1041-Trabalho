"""Monta repositórios e casos de uso (injeção de dependências)."""

from dataclasses import dataclass
from pathlib import Path

from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)
from use_cases.coffee.search_coffees import SearchCoffees


@dataclass(frozen=True)
class Container:
    search_coffees: SearchCoffees


def build_container(db_path: str | Path) -> Container:
    coffee_repository = SqliteCoffeeRepository(db_path)
    return Container(search_coffees=SearchCoffees(coffee_repository))
