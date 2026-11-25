"""Funções puras de texto usadas pelo domínio."""

import unicodedata


def normalize_text(text: str) -> str:
    """Remove acentos, passa para minúsculas e tira espaços das pontas."""
    decomposed = unicodedata.normalize("NFD", text)
    without_accents = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return without_accents.casefold().strip()
