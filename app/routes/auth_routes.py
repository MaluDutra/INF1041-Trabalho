"""Controllers de cadastro, login e logout (SCRUM-11)."""

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

from app.routes.redirects import safe_next_path
from domain.exceptions import (
    ConflictError,
    InvalidCredentialsError,
    NotFoundError,
    ValidationError,
)
from use_cases.dtos import AuthenticateUserInput, RegisterUserInput, UserDTO
from use_cases.user.authenticate_user import AuthenticateUser
from use_cases.user.get_user import GetUser
from use_cases.user.register_user import RegisterUser

SESSION_KEY = "user_id"


def create_auth_blueprint(
    register_user: RegisterUser,
    authenticate_user: AuthenticateUser,
    get_user: GetUser,
) -> Blueprint:
    blueprint = Blueprint("auth", __name__)

    def requested_next() -> str | None:
        """O ``next`` do formulário ou da URL, só se for interno."""
        target = request.form.get("next") or request.args.get("next")
        return safe_next_path(target)

    def start_session(user: UserDTO) -> Response:
        session.clear()
        session[SESSION_KEY] = user.id
        return redirect(requested_next() or url_for("coffees.index"))

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
        return render_template(
            "auth/signup.html", form={}, next_url=requested_next()
        )

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
                show_login_link=True,
                next_url=requested_next(),
            )
        except ValidationError as error:
            return render_template(
                "auth/signup.html",
                form=form,
                error=str(error),
                next_url=requested_next(),
            )
        return start_session(user)

    @blueprint.get("/entrar")
    def login_form() -> str:
        return render_template(
            "auth/login.html", form={}, next_url=requested_next()
        )

    @blueprint.post("/entrar")
    def login() -> str | Response:
        form = {"email": request.form.get("email", "")}
        try:
            user = authenticate_user.execute(
                AuthenticateUserInput(
                    email=form["email"],
                    password=request.form.get("password", ""),
                )
            )
        except InvalidCredentialsError as error:
            return render_template(
                "auth/login.html",
                form=form,
                error=str(error),
                next_url=requested_next(),
            )
        return start_session(user)

    @blueprint.post("/sair")
    def logout() -> Response:
        session.clear()
        return redirect(url_for("coffees.index"))

    return blueprint
