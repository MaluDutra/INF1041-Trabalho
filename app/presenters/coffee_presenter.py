"""Formata o café para a view: só apresentação, sem regra de negócio."""

from dataclasses import dataclass

from use_cases.dtos import CoffeeDetailsDTO

NOT_INFORMED = "Não informado"


@dataclass(frozen=True)
class BrewRecommendationView:
    method: str
    ratio: str
    grind: str
    temperature: str


@dataclass(frozen=True)
class CoffeeDetailsView:
    id: int
    name: str
    roaster: str
    origin: str
    producer: str
    variety: str
    process: str
    altitude: str
    roast: str
    sensory_notes: str
    photo_url: str | None
    story: str
    brew_recommendations: tuple[BrewRecommendationView, ...]
    brew_empty_message: str | None


def present_details(details: CoffeeDetailsDTO) -> CoffeeDetailsView:
    return CoffeeDetailsView(
        id=details.id,
        name=details.name,
        roaster=details.roaster,
        origin=details.origin,
        producer=_or_not_informed(details.producer),
        variety=_or_not_informed(details.variety),
        process=_or_not_informed(details.process),
        altitude=_format_altitude(details.altitude),
        roast=_or_not_informed(details.roast),
        sensory_notes=_or_not_informed(", ".join(details.sensory_notes)),
        photo_url=details.photo_url,
        story=_or_not_informed(details.story),
        brew_recommendations=tuple(
            BrewRecommendationView(
                method=brew.method,
                ratio=_or_not_informed(brew.ratio),
                grind=_or_not_informed(brew.grind),
                temperature=_or_not_informed(brew.temperature),
            )
            for brew in details.brew_recommendations
        ),
        brew_empty_message=(
            None if details.brew_recommendations else NOT_INFORMED
        ),
    )


def _or_not_informed(value: str | None) -> str:
    return value if value else NOT_INFORMED


def _format_altitude(altitude: int | None) -> str:
    if altitude is None:
        return NOT_INFORMED
    return f"{altitude:,}".replace(",", ".") + " m"
