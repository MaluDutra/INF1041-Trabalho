"""Controllers do catálogo de cafés."""

from flask import Blueprint, render_template

from use_cases.coffee.search_coffees import SearchCoffees


def create_coffee_blueprint(search_coffees: SearchCoffees) -> Blueprint:
    blueprint = Blueprint("coffees", __name__)

    @blueprint.get("/")
    def index() -> str:
        coffees = search_coffees.execute()
        return render_template("coffees/index.html", coffees=coffees)

    return blueprint
