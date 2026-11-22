"""Dados de saída (e entrada) dos casos de uso, imutáveis."""

from dataclasses import dataclass


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
class CoffeeDetailsDTO:
    """Café completo, como aparece na página dele.

    Atributos opcionais vazios vêm como ``None`` (ou tupla vazia): o
    texto "Não informado" é formatação do presenter.
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
