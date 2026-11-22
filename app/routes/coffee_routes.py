"""Controllers do catálogo de cafés."""

from flask import Blueprint, render_template, request

from app.routes.coffee_page import render_coffee_page
from use_cases.coffee.get_coffee_details import GetCoffeeDetails
from use_cases.coffee.search_coffees import SearchCoffees

OPEN_FORM_MARKER = "avaliar"


def create_coffee_blueprint(
    search_coffees: SearchCoffees, get_coffee_details: GetCoffeeDetails
) -> Blueprint:
    blueprint = Blueprint("coffees", __name__)

    @blueprint.get("/")
    def index() -> str:
        coffees = search_coffees.execute()
        return render_template("coffees/index.html", coffees=coffees)

    @blueprint.get("/cafes/<int:coffee_id>")
    def detail(coffee_id: int) -> tuple[str, int]:
        return render_coffee_page(
            get_coffee_details,
            coffee_id,
            open_form=request.args.get(OPEN_FORM_MARKER) == "1",
        )

    return blueprint
