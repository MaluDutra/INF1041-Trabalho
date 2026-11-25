"""Usuários e reviews de demonstração (dados fictícios, não são segredos)."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from domain.entities.review import Review
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)
from infra.repositories.review_repository_sqlite import (
    SqliteReviewRepository,
)
from infra.repositories.user_repository_sqlite import SqliteUserRepository
from infra.security.werkzeug_password_hasher import WerkzeugPasswordHasher
from use_cases.dtos import RegisterUserInput
from use_cases.user.register_user import RegisterUser

# Senha comum a todos os usuários de demonstração (documentada no README).
# Só o hash vai para o banco.
DEMO_PASSWORD = "Cafeteca123"


@dataclass(frozen=True)
class DemoUser:
    display_name: str
    email: str


DEMO_USERS = (
    DemoUser("Ana Souza", "ana@cafeteca.demo"),
    DemoUser("Bruno Lima", "bruno@cafeteca.demo"),
    DemoUser("Carla Mendes", "carla@cafeteca.demo"),
    DemoUser("Diego Alves", "diego@cafeteca.demo"),
    DemoUser("Elisa Rocha", "elisa@cafeteca.demo"),
)


@dataclass(frozen=True)
class DemoReview:
    coffee_name: str
    user_email: str
    rating: int
    text: str | None = None
    edited: bool = False


# Cada review ganha uma data própria, em sequência a partir desta, para que
# a ordem "mais recente primeiro" seja determinística.
FIRST_REVIEW_AT = datetime(2026, 6, 15, 9, 30)
REVIEW_INTERVAL = timedelta(days=2, hours=3, minutes=17)

ANA = "ana@cafeteca.demo"
BRUNO = "bruno@cafeteca.demo"
CARLA = "carla@cafeteca.demo"
DIEGO = "diego@cafeteca.demo"
ELISA = "elisa@cafeteca.demo"

# Distribuição pensada para a demonstração (média exata entre parênteses):
# - Sítio da Torre (4,5; 4 reviews) e Fazenda Santa Inês (4,5; 2 reviews)
#   empatam na média: "Melhor avaliados" desempata pela quantidade.
# - Anaeróbico Sul de Minas (4,0; 3) e Huila Supremo, Nariño Alto (4,0; 1).
# - Kirinyaga AA (3,0; 5) tem uma nota de cada valor: histograma dividido.
# - Mandheling Sumatra, Butare Nyamasheke, Sidamo Guji, Atitlán Volcán e
#   Nyeri Peaberry ficam sem avaliações.
DEMO_REVIEWS = (
    DemoReview("Sítio da Torre", ANA, 5, "Doce e redondo, lembra chocolate."),
    DemoReview("Sítio da Torre", BRUNO, 5),
    DemoReview("Sítio da Torre", CARLA, 4, "Muito bom no V60."),
    DemoReview("Sítio da Torre", DIEGO, 4),
    DemoReview("Fazenda Santa Inês", ANA, 5, "Caramelo e acidez suave."),
    DemoReview("Fazenda Santa Inês", BRUNO, 4, edited=True),
    DemoReview("Huila Supremo", BRUNO, 4, "Equilibrado."),
    DemoReview("Yirgacheffe Aricha", ANA, 5, "Floral, lindo na xícara."),
    DemoReview("Yirgacheffe Aricha", BRUNO, 5),
    DemoReview("Yirgacheffe Aricha", CARLA, 5),
    DemoReview("Yirgacheffe Aricha", DIEGO, 5, "O melhor que provei."),
    DemoReview("Yirgacheffe Aricha", ELISA, 4),
    DemoReview("Antigua Pastores", CARLA, 3),
    DemoReview("Antigua Pastores", DIEGO, 4, "Achocolatado, corpo médio."),
    DemoReview("Antigua Pastores", ELISA, 3),
    DemoReview("Kirinyaga AA", ANA, 1, "Ácido demais para o meu gosto."),
    DemoReview("Kirinyaga AA", BRUNO, 2),
    DemoReview("Kirinyaga AA", CARLA, 3),
    DemoReview("Kirinyaga AA", DIEGO, 4, "Frutado e vivo.", edited=True),
    DemoReview("Kirinyaga AA", ELISA, 5, "Groselha na veia, adorei."),
    DemoReview("Cerrado Mineiro", ANA, 4),
    DemoReview("Cerrado Mineiro", CARLA, 4, "Bom para o dia a dia."),
    DemoReview("Cerrado Mineiro", ELISA, 3),
    DemoReview("Tarrazú Honey", DIEGO, 5, "Dulçor incrível."),
    DemoReview("Cajamarca Orgânico", ELISA, 2, "Achei sem graça."),
    DemoReview("Marcala Lenca", ANA, 3),
    DemoReview("Marcala Lenca", BRUNO, 4, "Suave e cremoso."),
    DemoReview("Anaeróbico Sul de Minas", BRUNO, 3),
    DemoReview("Anaeróbico Sul de Minas", CARLA, 4, "Estranho, mas bom."),
    DemoReview("Anaeróbico Sul de Minas", DIEGO, 5),
    DemoReview("Espresso Intenso", ANA, 2, "Amargo."),
    DemoReview("Espresso Intenso", DIEGO, 3),
    DemoReview("Nariño Alto", ELISA, 4),
    DemoReview("Blend da Casa", ANA, 4),
    DemoReview("Blend da Casa", BRUNO, 3, "Honesto, nada além."),
    DemoReview("Blend da Casa", CARLA, 5, "Meu café de todo dia."),
    DemoReview("Blend da Casa", DIEGO, 2),
    DemoReview("Blend da Casa", ELISA, 3, edited=True),
)


def seed_demo_users(db_path: str | Path) -> None:
    """Cadastra os usuários pelo mesmo caso de uso e hasher da aplicação."""
    register = RegisterUser(
        SqliteUserRepository(db_path), WerkzeugPasswordHasher()
    )
    for demo_user in DEMO_USERS:
        register.execute(
            RegisterUserInput(
                demo_user.display_name, demo_user.email, DEMO_PASSWORD
            )
        )


def seed_demo_reviews(db_path: str | Path) -> None:
    """Grava os reviews como entidades, que validam nota e texto."""
    users = SqliteUserRepository(db_path)
    coffees = {c.name: c for c in SqliteCoffeeRepository(db_path).list_all()}
    reviews = SqliteReviewRepository(db_path)
    for position, demo in enumerate(DEMO_REVIEWS):
        reviews.add(
            Review(
                author_id=users.get_by_email(demo.user_email).id,
                coffee_id=coffees[demo.coffee_name].id,
                rating=demo.rating,
                text=demo.text,
                created_at=FIRST_REVIEW_AT + position * REVIEW_INTERVAL,
                edited=demo.edited,
            )
        )
