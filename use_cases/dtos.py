"""Dados de saída (e entrada) dos casos de uso, imutáveis."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class CoffeeSummaryDTO:
    """Café como aparece nos cards do catálogo."""

    id: int
    name: str
    roaster: str
    origin: str


@dataclass(frozen=True)
class BrewRecommendationDTO:
    """Recomendação de preparo; o que faltar vem como ``None``."""

    method: str
    ratio: str | None
    grind: str | None
    temperature: str | None


@dataclass(frozen=True)
class ReviewDTO:
    """Review como aparece na lista, com o nome de exibição do autor.

    Não leva o e-mail do autor, que nunca é público.
    """

    id: int
    author_id: int
    author_name: str
    rating: int
    text: str | None
    created_at: datetime
    edited: bool
    is_own: bool


@dataclass(frozen=True)
class RatingBucketDTO:
    """Faixa do histograma: quantas notas iguais a ``rating``."""

    rating: int
    count: int
    percentage: int


@dataclass(frozen=True)
class CoffeeRatingDTO:
    """Nota agregada de um café.

    ``average`` já vem com 1 casa decimal (meio para cima) e é ``None``
    quando não há reviews. ``histogram`` tem uma faixa por valor da
    escala, em ordem crescente.
    """

    average: Decimal | None
    count: int
    histogram: tuple[RatingBucketDTO, ...]


@dataclass(frozen=True)
class CoffeeDetailsDTO:
    """Café completo, como aparece na página dele.

    Atributos opcionais vazios vêm como ``None`` (ou tupla vazia): o
    texto "Não informado" é formatação do presenter. ``reviews`` vem do
    mais recente para o mais antigo, com o review do usuário logado (se
    houver) em primeiro.
    """

    id: int
    name: str
    roaster: str
    origin: str
    producer: str | None
    variety: str | None
    process: str | None
    altitude: int | None
    roast: str | None
    sensory_notes: tuple[str, ...]
    photo_url: str | None
    story: str | None
    brew_recommendations: tuple[BrewRecommendationDTO, ...]
    rating: CoffeeRatingDTO
    reviews: tuple[ReviewDTO, ...] = ()
    user_has_reviewed: bool = False


@dataclass(frozen=True)
class RegisterUserInput:
    """Dados do formulário de cadastro; a senha ainda em texto."""

    display_name: str
    email: str
    password: str


@dataclass(frozen=True)
class AuthenticateUserInput:
    """Dados do formulário de login; a senha ainda em texto."""

    email: str
    password: str


@dataclass(frozen=True)
class UserDTO:
    """Usuário como as camadas externas o enxergam.

    Não leva o e-mail nem o hash: só o que pode aparecer na interface.
    """

    id: int
    display_name: str


@dataclass(frozen=True)
class CreateReviewInput:
    """Dados do formulário de review; ``rating`` é ``None`` se faltou."""

    user_id: int
    coffee_id: int
    rating: int | None
    text: str | None


@dataclass(frozen=True)
class SavedReviewDTO:
    """Review criado ou editado, como o caso de uso o devolve."""

    id: int
    rating: int
    text: str | None
    created_at: datetime
    edited: bool


@dataclass(frozen=True)
class UpdateReviewInput:
    """Dados do formulário de edição; ``rating`` é ``None`` se faltou."""

    user_id: int
    coffee_id: int
    review_id: int
    rating: int | None
    text: str | None


@dataclass(frozen=True)
class DeleteReviewInput:
    """Pedido de exclusão do review de um café."""

    user_id: int
    coffee_id: int
    review_id: int
