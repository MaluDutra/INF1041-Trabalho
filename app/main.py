"""Composition root: cria a aplicação Flask e liga as dependências."""

from pathlib import Path

import click
from flask import Flask, render_template

from app.container import build_container
from app.routes.coffee_routes import create_coffee_blueprint
from infra.db.seed import init_database

NOT_FOUND_PAGE = "Página não encontrada."


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DATABASE"] = str(Path(app.instance_path) / "cafeteca.db")
    if config:
        app.config.update(config)

    container = build_container(app.config["DATABASE"])
    app.register_blueprint(
        create_coffee_blueprint(
            container.search_coffees, container.get_coffee_details
        )
    )

    @app.errorhandler(404)
    def page_not_found(error: Exception) -> tuple[str, int]:
        return render_template("not_found.html", title=NOT_FOUND_PAGE), 404

    @app.cli.command("init-db")
    def init_db_command() -> None:
        """Cria o banco e carrega o catálogo inicial (banco vazio)."""
        Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
        if init_database(app.config["DATABASE"]):
            click.echo("Banco criado e catálogo inicial carregado.")
        else:
            click.echo("O banco já tem cafés; nada foi alterado.")

    return app
