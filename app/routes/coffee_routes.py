"""Controllers do catálogo de cafés."""

from collections.abc import Sequence

from flask import Blueprint, render_template, request

from app.presenters.catalog_presenter import (
    FILTER_FIELDS,
    has_active_filters,
    parse_min_rating,
    present_cards,
    present_filter_groups,
    present_min_rating_options,
    present_sort_options,
)
from app.routes.coffee_page import render_coffee_page
from app.routes.redirects import safe_next_path
from domain.exceptions import ValidationError
from use_cases.coffee.get_coffee_details import GetCoffeeDetails
from use_cases.coffee.search_coffees import SearchCoffees
from use_cases.coffee.search_sorting import SortStrategy
from use_cases.dtos import SearchCoffeesInput

OPEN_FORM_MARKER = "avaliar"
OPEN_EDIT_MARKER = "editar"
SORT_PARAM = "ordenar"
MIN_RATING_PARAM = "nota_minima"


def create_coffee_blueprint(
    search_coffees: SearchCoffees,
    get_coffee_details: GetCoffeeDetails,
    sort_strategies: Sequence[SortStrategy],
) -> Blueprint:
    blueprint = Blueprint("coffees", __name__)

    @blueprint.get("/")
    def index() -> str:
        term = request.args.get("q", "")
        sort = request.args.get(SORT_PARAM, "")
        selected = {
            field.param: tuple(request.args.getlist(field.param))
            for field in FILTER_FIELDS
        }
        filters = {
            field.input_field: selected[field.param] for field in FILTER_FIELDS
        }
        min_rating = parse_min_rating(request.args.get(MIN_RATING_PARAM, ""))
        filter_groups = present_filter_groups(selected)
        try:
            coffees = search_coffees.execute(
                SearchCoffeesInput(
                    term, sort, min_rating=min_rating, **filters
                )
            )
            warning = None
        except ValidationError as error:
            coffees, warning = [], str(error)
        return render_template(
            "coffees/index.html",
            coffees=present_cards(coffees),
            term=term,
            warning=warning,
            sort_param=SORT_PARAM,
            sort_options=present_sort_options(sort_strategies, sort),
            filter_groups=filter_groups,
            min_rating_param=MIN_RATING_PARAM,
            min_rating_options=present_min_rating_options(min_rating),
            has_filters=has_active_filters(filter_groups, min_rating),
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
