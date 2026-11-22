"""Controllers de avaliação de cafés (SCRUM-14).

Destino do ``next`` de um POST: se a sessão expira antes do envio, o
``login_required`` manda o usuário ao login com ``next`` igual ao caminho
do POST. Depois de entrar, o navegador faz um GET nesse caminho, que
leva de volta à página do café (o texto digitado se perde, mas nenhuma
ação é repetida sem o usuário ver):

- criar: a página com o formulário de criação aberto;
- editar: a página com o formulário de edição aberto;
- excluir: a página do café, sem excluir nada. A exclusão só acontece
  num POST, depois da confirmação na própria página.

Editar e excluir aceitam um ``next`` interno (validado por
``safe_next_path``), usado por "Minhas avaliações" para voltar a ela
depois da ação. Sem ``next`` válido, o destino é a página do café. No
editar, o ``next`` vai na URL do GET e segue num campo oculto do
formulário até o POST.
"""

from flask import (
    Blueprint,
    Response,
    g,
    redirect,
    render_template,
    request,
    url_for,
)

from app.presenters.user_reviews_presenter import present_user_reviews
from app.routes.coffee_page import render_coffee_page
from app.routes.login_required import login_required
from app.routes.redirects import safe_next_path
from domain.exceptions import (
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from use_cases.coffee.get_coffee_details import GetCoffeeDetails
from use_cases.dtos import (
    CreateReviewInput,
    DeleteReviewInput,
    UpdateReviewInput,
)
from use_cases.review.create_review import CreateReview
from use_cases.review.delete_review import DeleteReview
from use_cases.review.list_user_reviews import ListUserReviews
from use_cases.review.update_review import UpdateReview

OWN_REVIEW_ANCHOR = "minha-avaliacao"
FORM_ANCHOR = "avaliar"
EDIT_ANCHOR = "editar"
MY_REVIEWS_PATH = "/minhas-avaliacoes"
ERROR_STATUS = {ValidationError: 400, ConflictError: 409}


def create_review_blueprint(
    create_review: CreateReview,
    update_review: UpdateReview,
    delete_review: DeleteReview,
    get_coffee_details: GetCoffeeDetails,
    list_user_reviews: ListUserReviews,
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

    def requested_next() -> str | None:
        """O ``next`` do formulário, só se for um caminho interno."""
        return safe_next_path(request.form.get("next"))

    def read_form() -> dict[str, str]:
        return {
            "rating": request.form.get("rating", ""),
            "text": request.form.get("text", ""),
        }

    def not_found_page(error: NotFoundError) -> tuple[str, int]:
        return render_template("not_found.html", title=str(error)), 404

    def forbidden_page(error: PermissionDeniedError) -> tuple[str, int]:
        return render_template("forbidden.html", message=str(error)), 403

    @blueprint.get(MY_REVIEWS_PATH)
    @login_required
    def my_reviews() -> str:
        reviews = list_user_reviews.execute(g.current_user.id)
        return render_template(
            "reviews/mine.html", reviews=present_user_reviews(reviews)
        )

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
        form = read_form()
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

    @blueprint.get("/cafes/<int:coffee_id>/avaliacoes/<int:review_id>/editar")
    @login_required
    def edit_form(coffee_id: int, review_id: int) -> Response:
        """Leva à página do café com o formulário de edição aberto.

        Um ``next`` interno na URL segue junto, para o envio voltar ao
        lugar de onde a edição começou.
        """
        values = {"editar": "1"}
        target = safe_next_path(request.args.get("next"))
        if target:
            values["next"] = target
        return redirect(
            coffee_page_url(coffee_id, _anchor=EDIT_ANCHOR, **values)
        )

    @blueprint.post("/cafes/<int:coffee_id>/avaliacoes/<int:review_id>/editar")
    @login_required
    def edit(coffee_id: int, review_id: int) -> Response | tuple[str, int]:
        form = read_form()
        try:
            update_review.execute(
                UpdateReviewInput(
                    user_id=g.current_user.id,
                    coffee_id=coffee_id,
                    review_id=review_id,
                    rating=parse_rating(form["rating"]),
                    text=form["text"],
                )
            )
        except NotFoundError as error:
            return not_found_page(error)
        except PermissionDeniedError as error:
            return forbidden_page(error)
        except ValidationError as error:
            return render_coffee_page(
                get_coffee_details,
                coffee_id,
                status=400,
                open_edit=True,
                review_form=form,
                review_error=str(error),
                next_path=requested_next(),
            )
        return redirect(
            requested_next()
            or coffee_page_url(coffee_id, _anchor=OWN_REVIEW_ANCHOR)
        )

    @blueprint.get("/cafes/<int:coffee_id>/avaliacoes/<int:review_id>/excluir")
    @login_required
    def delete_form(coffee_id: int, review_id: int) -> Response:
        """Volta à página do café; excluir exige o POST confirmado."""
        return redirect(coffee_page_url(coffee_id))

    @blueprint.post(
        "/cafes/<int:coffee_id>/avaliacoes/<int:review_id>/excluir"
    )
    @login_required
    def delete(coffee_id: int, review_id: int) -> Response | tuple[str, int]:
        try:
            delete_review.execute(
                DeleteReviewInput(
                    user_id=g.current_user.id,
                    coffee_id=coffee_id,
                    review_id=review_id,
                )
            )
        except NotFoundError as error:
            return not_found_page(error)
        except PermissionDeniedError as error:
            return forbidden_page(error)
        return redirect(requested_next() or coffee_page_url(coffee_id))

    return blueprint
