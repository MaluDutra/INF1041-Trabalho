"""Consulta da página de um café (SCRUM-12)."""

from domain.entities.coffee import Coffee
from domain.exceptions import NotFoundError
from use_cases.dtos import BrewRecommendationDTO, CoffeeDetailsDTO
from use_cases.ports.coffee_repository import CoffeeRepository


class GetCoffeeDetails:
    """Devolve o café pelo id ou lança ``NotFoundError``.

    Reviews e nota agregada entram nos próximos tickets.
    """

    def __init__(self, coffee_repository: CoffeeRepository) -> None:
        self._coffee_repository = coffee_repository

    def execute(self, coffee_id: int) -> CoffeeDetailsDTO:
        coffee = self._coffee_repository.get_by_id(coffee_id)
        if coffee is None:
            raise NotFoundError("Café não encontrado.")
        return self._to_dto(coffee)

    @staticmethod
    def _to_dto(coffee: Coffee) -> CoffeeDetailsDTO:
        return CoffeeDetailsDTO(
            id=coffee.id,
            name=coffee.name,
            roaster=coffee.roaster,
            origin=coffee.origin.value,
            producer=coffee.producer,
            variety=coffee.variety,
            process=coffee.process.value if coffee.process else None,
            altitude=coffee.altitude,
            roast=coffee.roast.value if coffee.roast else None,
            sensory_notes=tuple(note.value for note in coffee.sensory_notes),
            photo_url=coffee.photo_url,
            story=coffee.story,
            brew_recommendations=tuple(
                BrewRecommendationDTO(
                    method=brew.method,
                    ratio=brew.ratio,
                    grind=brew.grind,
                    temperature=brew.temperature,
                )
                for brew in coffee.brew_recommendations
            ),
        )
