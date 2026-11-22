"""Conversão da Nota agregada (domínio) em DTO, usada pelos casos de uso."""

from domain.value_objects.coffee_rating import CoffeeRating
from use_cases.dtos import CoffeeRatingDTO, RatingBucketDTO


def to_rating_dto(rating: CoffeeRating) -> CoffeeRatingDTO:
    return CoffeeRatingDTO(
        average=rating.rounded_average,
        count=rating.count,
        histogram=tuple(
            RatingBucketDTO(
                rating=value,
                count=count,
                percentage=rating.percentage(value),
            )
            for value, count in rating.histogram.items()
        ),
    )
