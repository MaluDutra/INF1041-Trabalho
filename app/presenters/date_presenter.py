"""Formata datas para a interface, no padrão brasileiro."""

from datetime import date


def format_date(value: date) -> str:
    """Devolve a data como ``dd/mm/aaaa``."""
    return value.strftime("%d/%m/%Y")
