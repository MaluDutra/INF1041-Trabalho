"""Catálogo inicial de cafés."""

from datetime import date
from pathlib import Path

from domain.entities.coffee import Coffee
from domain.value_objects.origin import Origin
from infra.db.database import connect, init_schema
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)
from use_cases.ports.coffee_repository import CoffeeRepository

SEED_COFFEES = [
    Coffee(
        name="Sítio da Torre",
        roaster="Café Lá",
        origin=Origin.BRAZIL,
        added_at=date(2026, 1, 10),
    ),
    Coffee(
        name="Fazenda Santa Inês",
        roaster="Torra Cá",
        origin=Origin.BRAZIL,
        added_at=date(2026, 2, 3),
    ),
    Coffee(
        name="Huila Supremo",
        roaster="Grão Nobre",
        origin=Origin.COLOMBIA,
        added_at=date(2026, 2, 21),
    ),
    Coffee(
        name="Yirgacheffe Aricha",
        roaster="Café Lá",
        origin=Origin.ETHIOPIA,
        added_at=date(2026, 3, 8),
    ),
    Coffee(
        name="Antigua Pastores",
        roaster="Grão Nobre",
        origin=Origin.GUATEMALA,
        added_at=date(2026, 3, 30),
    ),
    Coffee(
        name="Kirinyaga AA",
        roaster="Torra Cá",
        origin=Origin.KENYA,
        added_at=date(2026, 4, 12),
    ),
]


def seed_catalog(repository: CoffeeRepository) -> None:
    """Grava o catálogo inicial. Só deve rodar sobre um banco vazio."""
    for coffee in SEED_COFFEES:
        repository.add(coffee)


def init_database(db_path: str | Path) -> bool:
    """Cria o schema e roda o seed se o banco estiver vazio.

    Devolve ``True`` quando o seed foi aplicado.
    """
    connection = connect(db_path)
    try:
        init_schema(connection)
    finally:
        connection.close()
    repository = SqliteCoffeeRepository(db_path)
    if repository.list_all():
        return False
    seed_catalog(repository)
    return True
