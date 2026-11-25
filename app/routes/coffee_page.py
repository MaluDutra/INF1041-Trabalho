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
    open_edit: bool = False,
    review_form: dict | None = None,
    review_error: str | None = None,
    next_path: str | None = None,
) -> tuple[str, int]:
    """Monta a página do café (ou o 404 se ele não existir).

    ``open_form`` abre o formulário de review e ``open_edit`` o de edição
    do review próprio. Um erro de review abre o formulário de criação,
    e ``review_form`` devolve os valores digitados. ``next_path`` é o
    destino interno, já validado, que o formulário de edição devolve no
    envio (por exemplo, "Minhas avaliações").
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
        open_edit=open_edit,
        review_form=review_form or {},
        review_error=review_error,
        next_path=next_path,
    )
    return html, status
