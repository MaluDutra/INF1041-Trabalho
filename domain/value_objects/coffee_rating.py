"""Nota agregada de um café (CoffeeRating)."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from decimal import Decimal

from domain.entities.review import RATING_RULE, RATING_SCALE
from domain.exceptions import ValidationError


@dataclass(frozen=True)
class CoffeeRating:
    """Resumo das notas de um café: média, quantidade e histograma.

    É calculada a partir das notas atuais e nunca é gravada. O
    histograma tem uma faixa por valor de ``RATING_SCALE``, em ordem
    crescente. Sem notas não há média ("Sem avaliações").
    """

    histogram: Mapping[int, int]

    @classmethod
    def from_ratings(cls, ratings: Iterable[int]) -> "CoffeeRating":
        histogram = {value: 0 for value in RATING_SCALE}
        for value in ratings:
            if value not in histogram:
                raise ValidationError(RATING_RULE)
            histogram[value] += 1
        return cls(histogram)

    @property
    def count(self) -> int:
        return sum(self.histogram.values())

    @property
    def average(self) -> float | None:
        """Média exata, ou ``None`` se não há notas."""
        if self.count == 0:
            return None
        return self._total / self.count

    @property
    def rounded_average(self) -> Decimal | None:
        """Média com 1 casa decimal, arredondada para cima no meio.

        Usa aritmética inteira: 4,25 vira 4,3 (o ``round`` do Python
        arredonda para o par e erra por causa do ponto flutuante).
        """
        if self.count == 0:
            return None
        tenths = (20 * self._total + self.count) // (2 * self.count)
        return Decimal(tenths).scaleb(-1)

    def percentage(self, rating: int) -> int:
        """Porcentagem inteira (meio para cima) das notas ``rating``."""
        if self.count == 0:
            return 0
        return (200 * self.histogram[rating] + self.count) // (2 * self.count)

    @property
    def _total(self) -> int:
        return sum(value * n for value, n in self.histogram.items())
