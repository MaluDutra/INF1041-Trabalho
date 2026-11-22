"""Renderização da página do café, compartilhada pelas rotas."""

from flask import g, render_template

from app.presenters.coffee_presenter import present_details
from domain.entities.review import RATING_SCALE
from domain.exceptions import NotFoundError
from use_cases.coffee.get_coffee_details import GetCoffeeDetails


def render_coffee_page(
    get_coffee_details: GetCoffeeDetails,
    coffee_id: int,
    *,
    status: int = 200,
    open_form: bool = False,
    review_form: dict | None = None,
    review_error: str | None = None,
) -> tuple[str, int]:
    """Monta a página do café (ou o 404 se ele não existir).

    ``open_form`` abre o formulário de review; um erro de review também
    o abre e devolve os valores digitados em ``review_form``.
    """
    current_user = g.get("current_user")
    try:
        details = get_coffee_details.execute(
            coffee_id, current_user.id if current_user else None
        )
    except NotFoundError as error:
        return render_template("not_found.html", title=str(error)), 404
    html = render_template(
        "coffees/detail.html",
        coffee=present_details(details),
        rating_scale=RATING_SCALE,
        open_form=open_form or review_error is not None,
        review_form=review_form or {},
        review_error=review_error,
    )
    return html, status
