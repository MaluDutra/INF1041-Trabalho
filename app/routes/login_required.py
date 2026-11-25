"""Decorador que marca uma rota como "exige login"."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import g, redirect, request, url_for


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    """Manda o visitante para o login, com ``next`` igual ao caminho.

    Usa ``g.current_user``, preenchido a cada requisição pelo blueprint
    de autenticação.
    """

    @wraps(view)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if g.get("current_user") is None:
            destination = request.full_path.removesuffix("?")
            return redirect(url_for("auth.login_form", next=destination))
        return view(*args, **kwargs)

    return wrapper
