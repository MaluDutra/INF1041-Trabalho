"""Catálogo inicial de cafés."""

from datetime import date
from pathlib import Path

from domain.entities.coffee import Coffee
from domain.value_objects.brew_recommendation import BrewRecommendation
from domain.value_objects.origin import Origin
from domain.value_objects.process import Process
from domain.value_objects.roast import Roast
from domain.value_objects.sensory_note import SensoryNote
from infra.db.database import connect, init_schema
from infra.repositories.coffee_repository_sqlite import (
    SqliteCoffeeRepository,
)
from use_cases.ports.coffee_repository import CoffeeRepository

LIGHT_PHOTO = "/static/photos/torra-clara.svg"
MEDIUM_PHOTO = "/static/photos/torra-media.svg"
DARK_PHOTO = "/static/photos/torra-escura.svg"

SEED_COFFEES = [
    Coffee(
        name="Sítio da Torre",
        roaster="Café Lá",
        origin=Origin.BRAZIL,
        added_at=date(2026, 1, 10),
        producer="Sítio da Torre",
        variety="Bourbon Amarelo",
        process=Process.NATURAL,
        altitude=1100,
        roast=Roast.MEDIUM,
        sensory_notes=(
            SensoryNote.CHOCOLATE,
            SensoryNote.CARAMEL,
            SensoryNote.NUTS,
        ),
        photo_url=MEDIUM_PHOTO,
        story=(
            "Cultivado há três gerações na Mantiqueira, o café secou "
            "em terreiro suspenso e descansou 30 dias antes da torra."
        ),
        brew_recommendations=(
            BrewRecommendation("V60", "1:15", "Média", "92 °C"),
            BrewRecommendation("Prensa francesa", "1:12", "Grossa"),
        ),
    ),
    Coffee(
        name="Fazenda Santa Inês",
        roaster="Torra Cá",
        origin=Origin.BRAZIL,
        added_at=date(2026, 1, 17),
        producer="Família Resende",
        variety="Catuaí Vermelho",
        process=Process.WASHED,
        altitude=1250,
        roast=Roast.MEDIUM,
        sensory_notes=(SensoryNote.CARAMEL, SensoryNote.CITRUS),
        photo_url=MEDIUM_PHOTO,
        story="Lote do Sul de Minas colhido à mão e lavado em tanques.",
        brew_recommendations=(
            BrewRecommendation("Coador de pano", "1:14", "Média", "90 °C"),
        ),
    ),
    Coffee(
        name="Huila Supremo",
        roaster="Grão Nobre",
        origin=Origin.COLOMBIA,
        added_at=date(2026, 1, 24),
        producer="Cooperativa Huila Sur",
        variety="Caturra",
        process=Process.WASHED,
        altitude=1750,
        roast=Roast.MEDIUM,
        sensory_notes=(SensoryNote.CARAMEL, SensoryNote.RED_FRUITS),
        photo_url=MEDIUM_PHOTO,
        story=(
            "Reunido por pequenos produtores do departamento de Huila, "
            "no sul da Colômbia."
        ),
        brew_recommendations=(
            BrewRecommendation("Aeropress", "1:13", "Média-fina", "88 °C"),
            BrewRecommendation("V60", "1:16", "Média", "93 °C"),
        ),
    ),
    Coffee(
        name="Yirgacheffe Aricha",
        roaster="Café Lá",
        origin=Origin.ETHIOPIA,
        added_at=date(2026, 2, 3),
        producer="Estação Aricha",
        variety="Heirloom",
        process=Process.WASHED,
        altitude=1950,
        roast=Roast.LIGHT,
        sensory_notes=(SensoryNote.FLORAL, SensoryNote.CITRUS),
        photo_url=LIGHT_PHOTO,
        story=(
            "Das terras altas de Yirgacheffe, onde o café cresce à "
            "sombra de árvores nativas."
        ),
        brew_recommendations=(
            BrewRecommendation("V60", "1:16", "Média-fina", "94 °C"),
        ),
    ),
    Coffee(
        name="Antigua Pastores",
        roaster="Grão Nobre",
        origin=Origin.GUATEMALA,
        added_at=date(2026, 2, 12),
        producer="Finca Los Pastores",
        variety="Bourbon",
        process=Process.WASHED,
        altitude=1600,
        roast=Roast.MEDIUM_DARK,
        sensory_notes=(SensoryNote.SPICY, SensoryNote.CHOCOLATE),
        photo_url=MEDIUM_PHOTO,
        story="Cultivado entre vulcões, no vale de Antigua.",
        brew_recommendations=(
            BrewRecommendation("Espresso", "1:2", "Fina", "93 °C"),
            BrewRecommendation("Moka"),
        ),
    ),
    Coffee(
        name="Kirinyaga AA",
        roaster="Torra Cá",
        origin=Origin.KENYA,
        added_at=date(2026, 2, 20),
        producer="Cooperativa Kirinyaga",
        variety="SL28",
        process=Process.WASHED,
        altitude=1800,
        roast=Roast.LIGHT,
        sensory_notes=(SensoryNote.RED_FRUITS, SensoryNote.CITRUS),
        photo_url=LIGHT_PHOTO,
        story="Grãos graúdos (peneira AA) das encostas do monte Quênia.",
        brew_recommendations=(
            BrewRecommendation("Chemex", "1:15", "Média-grossa", "94 °C"),
        ),
    ),
    Coffee(
        name="Cerrado Mineiro",
        roaster="Aroma Serra",
        origin=Origin.BRAZIL,
        added_at=date(2026, 3, 1),
        producer="Fazenda Boa Vista",
        variety="Mundo Novo",
        process=Process.HONEY,
        altitude=1000,
        roast=Roast.MEDIUM,
        sensory_notes=(SensoryNote.HONEY, SensoryNote.NUTS),
        photo_url=MEDIUM_PHOTO,
        story=(
            "Cereja descascada seca com parte da polpa, o que adoça a xícara."
        ),
        brew_recommendations=(
            BrewRecommendation("Prensa francesa", "1:13", "Grossa"),
        ),
    ),
    Coffee(
        name="Tarrazú Honey",
        roaster="Café Lá",
        origin=Origin.COSTA_RICA,
        added_at=date(2026, 3, 9),
        producer="Micromill La Pastora",
        variety="Catuaí",
        process=Process.HONEY,
        altitude=1700,
        roast=Roast.MEDIUM,
        sensory_notes=(SensoryNote.HONEY, SensoryNote.FRUITY),
        photo_url=MEDIUM_PHOTO,
        story="Processado em microlote na região de Tarrazú.",
        brew_recommendations=(
            BrewRecommendation("V60", "1:15", None, "91 °C"),
        ),
    ),
    Coffee(
        name="Cajamarca Orgânico",
        roaster="Grão Nobre",
        origin=Origin.PERU,
        added_at=date(2026, 3, 18),
        producer="Cooperativa Cenfrocafe",
        variety="Typica",
        process=Process.WASHED,
        altitude=1600,
        roast=Roast.MEDIUM,
        sensory_notes=(SensoryNote.NUTS, SensoryNote.CARAMEL),
        photo_url=MEDIUM_PHOTO,
        story="Café orgânico certificado, cultivado no norte do Peru.",
        brew_recommendations=(
            BrewRecommendation("Coador de papel", "1:15", "Média"),
        ),
    ),
    Coffee(
        name="Marcala Lenca",
        roaster="Torra Cá",
        origin=Origin.HONDURAS,
        added_at=date(2026, 3, 27),
        producer="Produtores Lenca",
        variety="Pacas",
        process=Process.WASHED,
        altitude=1500,
        roast=Roast.MEDIUM_DARK,
        sensory_notes=(SensoryNote.CHOCOLATE, SensoryNote.CARAMEL),
        photo_url=MEDIUM_PHOTO,
        story="Região de Marcala, a primeira de Honduras com denominação.",
        brew_recommendations=(BrewRecommendation("Espresso", "1:2"),),
    ),
    Coffee(
        name="Mandheling Sumatra",
        roaster="Aroma Serra",
        origin=Origin.INDONESIA,
        added_at=date(2026, 4, 4),
        producer="Pequenos produtores Batak",
        variety="Typica",
        process=None,
        altitude=1300,
        roast=Roast.DARK,
        sensory_notes=(SensoryNote.HERBAL, SensoryNote.SPICY),
        photo_url=DARK_PHOTO,
        story=None,
        brew_recommendations=(
            BrewRecommendation("Prensa francesa", "1:12", "Grossa", "95 °C"),
        ),
    ),
    Coffee(
        name="Butare Nyamasheke",
        roaster="Café Lá",
        origin=Origin.RWANDA,
        added_at=date(2026, 4, 11),
        producer="Estação de lavagem Nyamasheke",
        variety="Bourbon Vermelho",
        process=Process.WASHED,
        altitude=1800,
        roast=Roast.LIGHT,
        sensory_notes=(
            SensoryNote.FLORAL,
            SensoryNote.RED_FRUITS,
            SensoryNote.HONEY,
        ),
        photo_url=LIGHT_PHOTO,
        story="Colhido por famílias de produtores perto do lago Kivu.",
        brew_recommendations=(
            BrewRecommendation("V60", "1:16", "Média-fina", "94 °C"),
            BrewRecommendation("Aeropress"),
        ),
    ),
    Coffee(
        name="Anaeróbico Sul de Minas",
        roaster="Aroma Serra",
        origin=Origin.BRAZIL,
        added_at=date(2026, 4, 19),
        producer="Sítio Recanto",
        variety="Catucaí",
        process=Process.FERMENTED,
        altitude=1300,
        roast=Roast.LIGHT,
        sensory_notes=(SensoryNote.FRUITY, SensoryNote.RED_FRUITS),
        photo_url=LIGHT_PHOTO,
        story="Fermentação anaeróbica de 72 horas em tanques selados.",
        brew_recommendations=(
            BrewRecommendation("V60", "1:15", "Média", "90 °C"),
        ),
    ),
    Coffee(
        name="Sidamo Guji",
        roaster="Torra Cá",
        origin=Origin.ETHIOPIA,
        added_at=date(2026, 4, 28),
        producer=None,
        variety="Heirloom",
        process=Process.NATURAL,
        altitude=None,
        roast=Roast.LIGHT,
        sensory_notes=(SensoryNote.FRUITY, SensoryNote.FLORAL),
        photo_url=LIGHT_PHOTO,
        story=None,
        brew_recommendations=(),
    ),
    Coffee(
        name="Espresso Intenso",
        roaster="Grão Nobre",
        origin=Origin.BRAZIL,
        added_at=date(2026, 5, 6),
        producer="Fazenda Três Pontas",
        variety=None,
        process=Process.NATURAL,
        altitude=900,
        roast=Roast.DARK,
        sensory_notes=(SensoryNote.CHOCOLATE,),
        photo_url=DARK_PHOTO,
        story="Café da casa para espresso, com corpo e crema marcantes.",
        brew_recommendations=(
            BrewRecommendation("Espresso", "1:2", "Fina", "93 °C"),
        ),
    ),
    Coffee(
        name="Atitlán Volcán",
        roaster="Aroma Serra",
        origin=Origin.GUATEMALA,
        added_at=date(2026, 5, 15),
        producer="Finca San Pedro",
        variety="Caturra",
        process=Process.WASHED,
        altitude=1550,
        roast=None,
        sensory_notes=(),
        photo_url=None,
        story="Cultivado às margens do lago Atitlán.",
        brew_recommendations=(BrewRecommendation("Chemex", "1:15"),),
    ),
    Coffee(
        name="Nariño Alto",
        roaster="Café Lá",
        origin=Origin.COLOMBIA,
        added_at=date(2026, 5, 23),
        producer="Associação Nariño",
        variety="Castillo",
        process=Process.HONEY,
        altitude=2000,
        roast=Roast.MEDIUM,
        sensory_notes=(SensoryNote.CARAMEL, SensoryNote.CITRUS),
        photo_url=MEDIUM_PHOTO,
        story=None,
        brew_recommendations=(),
    ),
    Coffee(
        name="Nyeri Peaberry",
        roaster="Grão Nobre",
        origin=Origin.KENYA,
        added_at=date(2026, 6, 2),
        producer="Cooperativa Gatomboya",
        variety="Ruiru 11",
        process=Process.WASHED,
        altitude=1700,
        roast=Roast.MEDIUM,
        sensory_notes=(SensoryNote.FRUITY, SensoryNote.SPICY),
        photo_url=MEDIUM_PHOTO,
        story="Grão único (peaberry), mais denso e de torra uniforme.",
        brew_recommendations=(
            BrewRecommendation("Aeropress", "1:14", "Média-fina", "89 °C"),
        ),
    ),
    Coffee(
        name="Blend da Casa",
        roaster="Café Lá",
        origin=Origin.BRAZIL,
        added_at=date(2026, 6, 10),
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
