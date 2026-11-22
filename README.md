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
alterado. O arquivo do banco fica em `instance/cafeteca.db`. Se ele foi
criado antes da issue 02 (schema antigo), apague o arquivo e rode o
`init-db` de novo. A tabela `users` (issue 03) é criada pelo `init-db` mesmo
em um banco que já tem cafés, sem apagar nada.

A sessão do Flask é assinada com a chave `CAFETECA_SECRET_KEY`. Sem a
variável de ambiente, vale uma chave fixa de desenvolvimento: defina a
variável em qualquer ambiente que não seja o seu computador.

## Testes e linters

```bash
pytest
ruff check .
ruff format --check .
lint-imports
```
