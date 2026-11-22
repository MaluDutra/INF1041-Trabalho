"""Controllers do catálogo de cafés."""

from flask import Blueprint, render_template

from app.presenters.coffee_presenter import present_details
from domain.exceptions import NotFoundError
from use_cases.coffee.get_coffee_details import GetCoffeeDetails
from use_cases.coffee.search_coffees import SearchCoffees


def create_coffee_blueprint(
    search_coffees: SearchCoffees, get_coffee_details: GetCoffeeDetails
) -> Blueprint:
    blueprint = Blueprint("coffees", __name__)

    @blueprint.get("/")
    def index() -> str:
        coffees = search_coffees.execute()
        return render_template("coffees/index.html", coffees=coffees)

    @blueprint.get("/cafes/<int:coffee_id>")
    def detail(coffee_id: int) -> str | tuple[str, int]:
        try:
            details = get_coffee_details.execute(coffee_id)
        except NotFoundError as error:
            return (
                render_template("not_found.html", title=str(error)),
                404,
            )
        return render_template(
            "coffees/detail.html", coffee=present_details(details)
        )

    return blueprint
