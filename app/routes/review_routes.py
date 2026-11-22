"""Controllers de avaliação de cafés (SCRUM-14).

Destino do ``next`` de um POST: se a sessão expira antes do envio, o
``login_required`` manda o usuário ao login com ``next`` igual ao caminho
do POST. Depois de entrar, o navegador faz um GET nesse caminho, que
leva de volta à página do café com o formulário aberto (o texto digitado
se perde, mas nenhuma ação é repetida sem o usuário ver).
"""

from flask import Blueprint, Response, g, redirect, request, url_for

from app.routes.coffee_page import render_coffee_page
from app.routes.login_required import login_required
from domain.exceptions import ConflictError, NotFoundError, ValidationError
from use_cases.coffee.get_coffee_details import GetCoffeeDetails
from use_cases.dtos import CreateReviewInput
from use_cases.review.create_review import CreateReview

OWN_REVIEW_ANCHOR = "minha-avaliacao"
FORM_ANCHOR = "avaliar"
ERROR_STATUS = {ValidationError: 400, ConflictError: 409}


def create_review_blueprint(
    create_review: CreateReview, get_coffee_details: GetCoffeeDetails
) -> Blueprint:
    blueprint = Blueprint("reviews", __name__)

    def parse_rating(raw: str) -> int | None:
        """Número inteiro digitado, ou ``None`` (o domínio recusa)."""
        try:
            return int(raw.strip())
        except ValueError:
            return None

    def coffee_page_url(coffee_id: int, **values: str) -> str:
        return url_for("coffees.detail", coffee_id=coffee_id, **values)

    @blueprint.get("/cafes/<int:coffee_id>/avaliar")
    @login_required
    def review_form(coffee_id: int) -> Response | tuple[str, int]:
        """Leva à página do café: formulário aberto ou review próprio."""
        try:
            details = get_coffee_details.execute(coffee_id, g.current_user.id)
        except NotFoundError:
            return render_coffee_page(get_coffee_details, coffee_id)
        if details.user_has_reviewed:
            return redirect(
                coffee_page_url(coffee_id, _anchor=OWN_REVIEW_ANCHOR)
            )
        return redirect(
            coffee_page_url(coffee_id, avaliar="1", _anchor=FORM_ANCHOR)
        )

    @blueprint.post("/cafes/<int:coffee_id>/avaliar")
    @login_required
    def create(coffee_id: int) -> Response | tuple[str, int]:
        form = {
            "rating": request.form.get("rating", ""),
            "text": request.form.get("text", ""),
        }
        try:
            create_review.execute(
                CreateReviewInput(
                    user_id=g.current_user.id,
                    coffee_id=coffee_id,
                    rating=parse_rating(form["rating"]),
                    text=form["text"],
                )
            )
        except NotFoundError:
            return render_coffee_page(get_coffee_details, coffee_id)
        except (ValidationError, ConflictError) as error:
            return render_coffee_page(
                get_coffee_details,
                coffee_id,
                status=ERROR_STATUS[type(error)],
                review_form=form,
                review_error=str(error),
            )
        return redirect(coffee_page_url(coffee_id, _anchor=OWN_REVIEW_ANCHOR))

    return blueprint
