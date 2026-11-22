from domain.text import normalize_text


def test_normalize_text_strips_accents_case_and_edge_spaces():
    assert normalize_text("  Sítio DA Torre ") == "sitio da torre"
