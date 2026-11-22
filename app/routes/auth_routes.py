"""Controllers de cadastro e logout (SCRUM-11)."""

from flask import (
    Blueprint,
    Response,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from domain.exceptions import ConflictError, NotFoundError, ValidationError
from use_cases.dtos import RegisterUserInput
from use_cases.user.get_user import GetUser
from use_cases.user.register_user import RegisterUser

SESSION_KEY = "user_id"
LOGIN_PATH = "/entrar"  # tela de login: ticket 04


def create_auth_blueprint(
    register_user: RegisterUser, get_user: GetUser
) -> Blueprint:
    blueprint = Blueprint("auth", __name__)

    @blueprint.before_app_request
    def load_current_user() -> None:
        g.current_user = None
        user_id = session.get(SESSION_KEY)
        if user_id is None:
            return
        try:
            g.current_user = get_user.execute(user_id)
        except NotFoundError:
            session.clear()

    @blueprint.app_context_processor
    def inject_current_user() -> dict:
        return {"current_user": g.get("current_user")}

    @blueprint.get("/cadastro")
    def signup_form() -> str:
        return render_template("auth/signup.html", form={})

    @blueprint.post("/cadastro")
    def signup() -> str | Response:
        form = {
            "display_name": request.form.get("display_name", ""),
            "email": request.form.get("email", ""),
        }
        try:
            user = register_user.execute(
                RegisterUserInput(
                    display_name=form["display_name"],
                    email=form["email"],
                    password=request.form.get("password", ""),
                )
            )
        except ConflictError as error:
            return render_template(
                "auth/signup.html",
                form=form,
                error=str(error),
                login_path=LOGIN_PATH,
            )
        except ValidationError as error:
            return render_template(
                "auth/signup.html", form=form, error=str(error)
            )
        session.clear()
        session[SESSION_KEY] = user.id
        return redirect(url_for("coffees.index"))

    @blueprint.post("/sair")
    def logout() -> Response:
        session.clear()
        return redirect(url_for("coffees.index"))

    return blueprint
