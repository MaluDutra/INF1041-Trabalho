# Cafeteca

Web-app para amantes de café encontrarem, avaliarem e discutirem cafés com a
comunidade. Trabalho A2 de INF1041 (Flask, Clean Architecture e SOLID).

## Como rodar

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (bash: source .venv/Scripts/activate)
pip install -r requirements-dev.txt

flask --app app.main init-db      # cria o banco SQLite com os dados de demo
flask --app app.main run --debug  # sobe a aplicação em http://127.0.0.1:5000
```

O `init-db` roda sobre um banco vazio: se o banco já tem cafés, nada é
alterado. O arquivo do banco fica em `instance/cafeteca.db`. Se ele foi
criado antes da issue 02 (schema antigo), apague o arquivo e rode o
`init-db` de novo. As tabelas `users` (issue 03) e `reviews` (issue 05) são
criadas pelo `init-db` mesmo em um banco que já tem cafés, sem apagar nada.

### Dados de demonstração

Num banco vazio, o `init-db` carrega 19 cafés, 5 usuários e 38 reviews, o
bastante para demonstrar a nota agregada, o histograma, as ordenações (com
desempate), o filtro de nota mínima e o "Sem avaliações". Os usuários são
fictícios e todos usam a senha `Cafeteca123` (só o hash vai para o banco):

| Usuário | E-mail |
| --- | --- |
| Ana Souza | `ana@cafeteca.demo` |
| Bruno Lima | `bruno@cafeteca.demo` |
| Carla Mendes | `carla@cafeteca.demo` |
| Diego Alves | `diego@cafeteca.demo` |
| Elisa Rocha | `elisa@cafeteca.demo` |

Alguns pontos da distribuição: Sítio da Torre e Fazenda Santa Inês empatam
na média (4,5) com 4 e 2 reviews; Kirinyaga AA tem uma nota de cada valor;
Mandheling Sumatra, Butare Nyamasheke, Sidamo Guji, Atitlán Volcán e Nyeri
Peaberry ficam sem avaliações. As datas dos reviews são fixas.

**Bancos antigos:** o seed só roda quando o banco não tem cafés. Um
`instance/cafeteca.db` criado antes da issue 13 (só com cafés) não ganha
usuários nem reviews: apague o arquivo e rode o `init-db` de novo.

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
