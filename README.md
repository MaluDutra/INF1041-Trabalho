# Cafeteca

Web-app para amantes de café encontrarem, avaliarem e discutirem cafés com a
comunidade. Trabalho A2 de INF1041 (Flask, Clean Architecture e SOLID).

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (bash: source .venv/Scripts/activate)
pip install -r requirements-dev.txt

flask --app app.main init-db      # cria o banco SQLite e o catálogo inicial
flask --app app.main run --debug  # sobe a aplicação em http://127.0.0.1:5000
```

O `init-db` roda sobre um banco vazio: se o banco já tem cafés, nada é
alterado. O arquivo do banco fica em `instance/cafeteca.db`.

## Testes e linters

```bash
pytest
ruff check .
ruff format --check .
lint-imports
```
