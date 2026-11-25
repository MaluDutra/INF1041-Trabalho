"""Validação do destino de retorno (``next``) contra open redirect."""

from urllib.parse import urlsplit


def safe_next_path(target: str | None) -> str | None:
    """Devolve ``target`` se for um caminho interno relativo, senão ``None``.

    Aceita só caminhos que começam com uma única barra. Recusa URLs com
    esquema ou host, ``//host``, barras invertidas (que os navegadores
    tratam como barras) e caracteres de controle (que eles descartam).
    """
    if not target or not target.startswith("/"):
        return None
    if target.startswith("//") or "\\" in target:
        return None
    if any(ord(char) < 32 or ord(char) == 127 for char in target):
        return None
    parts = urlsplit(target)
    if parts.scheme or parts.netloc:
        return None
    return target
