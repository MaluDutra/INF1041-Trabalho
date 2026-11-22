"""Controllers do catálogo de cafés."""

from flask import Blueprint, render_template, request

from app.routes.coffee_page import render_coffee_page
from app.routes.redirects import safe_next_path
from domain.exceptions import ValidationError
from use_cases.coffee.get_coffee_details import GetCoffeeDetails
from use_cases.coffee.search_coffees import SearchCoffees
from use_cases.dtos import SearchCoffeesInput

OPEN_FORM_MARKER = "avaliar"
OPEN_EDIT_MARKER = "editar"


def create_coffee_blueprint(
    search_coffees: SearchCoffees, get_coffee_details: GetCoffeeDetails
) -> Blueprint:
    blueprint = Blueprint("coffees", __name__)

    @blueprint.get("/")
    def index() -> str:
        term = request.args.get("q", "")
        try:
            coffees = search_coffees.execute(SearchCoffeesInput(term))
            warning = None
        except ValidationError as error:
            coffees, warning = [], str(error)
        return render_template(
            "coffees/index.html", coffees=coffees, term=term, warning=warning
        )

    @blueprint.get("/cafes/<int:coffee_id>")
    def detail(coffee_id: int) -> tuple[str, int]:
        return render_coffee_page(
            get_coffee_details,
            coffee_id,
            open_form=request.args.get(OPEN_FORM_MARKER) == "1",
            open_edit=request.args.get(OPEN_EDIT_MARKER) == "1",
            next_path=safe_next_path(request.args.get("next")),
        )

    return blueprint
