# CLAUDE.md

Guia para o Claude Code trabalhar neste repositório.

## Contexto

Trabalho A2 de **INF1041 – Arquitetura e Projeto de Software**: uma aplicação web em
**Python + Flask** seguindo **Clean Architecture** e **SOLID**, com testes unitários em
**Pytest** e código em **PEP-8**. O enunciado está em
`Trabalho A2 - Arquiteutra e Projetos de Software.pdf`.

O tema é o **Cafeteca**, um web-app para amantes de café encontrarem, avaliarem e
discutirem cafés com a comunidade. O backlog está no Jira:
<https://mldutraga.atlassian.net> → projeto **Cafeteca** (chave `SCRUM`).

### Requisitos obrigatórios do enunciado

- Pelo menos **4 histórias de usuário** implementadas e pelo menos **2 entidades**.
- Camadas da Clean Architecture: entidades, casos de uso, adaptadores de interface,
  frameworks & drivers.
- SOLID aplicado de forma explícita nas classes e métodos.
- Testes unitários dos casos de uso, **isolados da infraestrutura** (sem Flask, sem banco).
- Persistência de dados real (SQLite é suficiente).

### Critérios de avaliação (10,0 + bônus)

| Critério | Peso |
| --- | --- |
| Aplicação funcional (≥ 3 casos de uso, ≥ 2 entidades) | 4,0 |
| Clean Architecture correta | 2,0 |
| SOLID correto | 2,0 |
| Testes unitários dos casos de uso | 1,0 |
| Estilo PEP-8 | 1,0 |
| Bônus: uso de IA justificado e com boa estratégia | 0,5 |

## Escopo a partir do Jira

O épico **SCRUM-7 (MVP)** tem as histórias abaixo. As marcadas como **A2** formam o escopo
do trabalho. As outras ficam fora, a menos que o grupo decida incluí-las.

| Issue | História | A2 |
| --- | --- | --- |
| SCRUM-11 | Criar conta e fazer login com segurança | ✅ |
| SCRUM-12 | Consultar a página de um café (ficha técnica, história, preparo) | ✅ |
| SCRUM-13 | Pesquisar cafés por texto e filtros | ✅ |
| SCRUM-14 | Avaliar um café com nota e review | ✅ |
| SCRUM-19 | Ver a nota agregada de cada café | ✅ |
| SCRUM-15 | Fazer amizades | opcional |
| SCRUM-17 | Comentar reviews | opcional |
| SCRUM-16 | Personalizar perfil | fora |
| SCRUM-18 | Cadastrar café pelo usuário + moderação | fora |

Os épicos SCRUM-8, 9 e 10 (incrementos pós-MVP) ficam fora do escopo.

Simplificações aceitas para o trabalho (itens do Jira que **não** serão implementados):
confirmação de e-mail, recuperação de senha, login social Google/Apple (SCRUM-72),
importação do RoastDB (SCRUM-38/75), URL amigável com preview, HTTPS e CI/CD de
homologação (SCRUM-25).

### Entidades do domínio

- **User**: nome de exibição, e-mail (único), hash da senha. Senha com no mínimo 8
  caracteres, com letras e números.
- **Coffee**: nome, torrefação e país de origem obrigatórios. Opcionais: produtor/fazenda,
  variedade, processo, altitude, torra, notas sensoriais, foto, história, recomendações
  de preparo. Campo vazio aparece como "Não informado".
- **Review**: autor (User), café (Coffee), nota e texto opcional. Só o autor edita ou exclui.
- **CoffeeRating** (objeto de valor): média, quantidade de avaliações e histograma das
  notas. É recalculado quando um review é criado, editado ou excluído.

### Regras de negócio vindas do Jira

- A busca considera nome, torrefação e produtor, ignora acentos e maiúsculas e exige pelo
  menos 2 caracteres. Os filtros (origem, processo, torra, notas sensoriais) podem ser
  combinados.
- Ordenação: melhor avaliados, mais avaliados ou mais recentes. Sem nota agregada, o card
  mostra "Sem avaliações".
- Visitantes navegam livremente. Avaliar exige login.
- A escala da nota ainda está em aberto no PBB. Usar **1 a 5** até o PO decidir, definida
  em uma única constante do domínio.

## Estrutura do projeto

Segue a sugestão do enunciado, ampliada para deixar as quatro camadas explícitas:

```
INF1041-Trabalho/
├── domain/                        # Entidades (não depende de nada)
│   ├── entities/
│   │   ├── user.py
│   │   ├── coffee.py
│   │   └── review.py
│   ├── value_objects/
│   │   └── coffee_rating.py
│   └── exceptions.py              # DomainError, ValidationError, NotFoundError...
│
├── use_cases/                     # Regras de aplicação (depende só de domain)
│   ├── ports/                     # Interfaces (ABC) que a infra implementa
│   │   ├── user_repository.py
│   │   ├── coffee_repository.py
│   │   ├── review_repository.py
│   │   └── password_hasher.py
│   ├── dtos.py                    # Dados de entrada e saída dos casos de uso
│   ├── user/
│   │   ├── register_user.py       # SCRUM-11
│   │   └── authenticate_user.py   # SCRUM-11
│   ├── coffee/
│   │   ├── get_coffee_details.py  # SCRUM-12
│   │   └── search_coffees.py      # SCRUM-13
│   └── review/
│       ├── create_review.py       # SCRUM-14
│       ├── update_review.py       # SCRUM-14
│       ├── delete_review.py       # SCRUM-14
│       └── get_coffee_rating.py   # SCRUM-19
│
├── infra/                         # Frameworks & drivers: persistência e segurança
│   ├── db/
│   │   ├── database.py            # Conexão e criação do schema SQLite
│   │   └── seed.py                # Catálogo inicial de cafés
│   ├── repositories/
│   │   ├── user_repository_sqlite.py
│   │   ├── coffee_repository_sqlite.py
│   │   └── review_repository_sqlite.py
│   └── security/
│       └── werkzeug_password_hasher.py
│
├── app/                           # Adaptadores de interface + Flask
│   ├── main.py                    # create_app(): composition root (injeta dependências)
│   ├── container.py               # Monta repositórios e casos de uso
│   ├── routes/                    # Controllers: HTTP -> DTO -> caso de uso -> resposta
│   │   ├── auth_routes.py
│   │   ├── coffee_routes.py
│   │   └── review_routes.py
│   ├── presenters/                # Formata a saída dos casos de uso para as views
│   ├── templates/                 # Jinja2
│   └── static/
│
├── tests/
│   ├── fakes/                     # Repositórios em memória que implementam os ports
│   ├── domain/
│   └── use_cases/
│
├── requirements.txt
├── README.md
└── CLAUDE.md
```

### Regra de dependência (não pode ser quebrada)

`app` → `use_cases` → `domain`, e `infra` → `use_cases.ports` / `domain`.

- `domain/` não importa nada de `use_cases`, `infra`, `app`, Flask ou sqlite3.
- `use_cases/` importa apenas `domain/` e os próprios `ports`. Nunca importa Flask, sqlite3
  ou `infra/`.
- `infra/` implementa as interfaces de `use_cases/ports/`.
- `app/` é o único lugar que conhece todas as camadas. A ligação entre casos de uso e
  implementações concretas acontece só em `app/main.py` / `app/container.py`.
- Rotas não têm regra de negócio. Elas convertem a requisição em DTO, chamam
  `use_case.execute(...)` e traduzem o resultado ou a exceção em resposta HTTP.

## Convenções de código

- **Um caso de uso por classe**, com um único método público `execute(...)`. As
  dependências entram pelo construtor, tipadas pelos ports (ABC).
- **SOLID**, para mostrar no código e citar no README:
  - SRP: um caso de uso por classe. Entidades só validam o próprio estado.
  - OCP: novos filtros ou ordenações de busca entram como novas estratégias, sem alterar
    `SearchCoffees`.
  - LSP: os fakes de teste e os repositórios SQLite são substituíveis entre si.
  - ISP: ports pequenos e específicos (`PasswordHasher` separado de `UserRepository`).
  - DIP: casos de uso dependem de abstrações (`use_cases/ports`), não de SQLite.
- Entidades validam invariantes no construtor ou em métodos de fábrica e lançam exceções
  de `domain/exceptions.py`.
- PEP-8: nomes em `snake_case`, classes em `PascalCase`, linhas com até 79 caracteres,
  type hints em código público. Identificadores em inglês. Mensagens ao usuário em
  português.
- Senhas nunca são armazenadas em texto puro (`werkzeug.security`).

## Testes

- Cada caso de uso tem testes em `tests/use_cases/`, usando os **fakes em memória** de
  `tests/fakes/`. Os testes de casos de uso não usam Flask nem banco.
- Os testes de entidades e objetos de valor ficam em `tests/domain/`.
- Escrever os testes a partir dos critérios de aceitação das issues
  (DADO QUE / QUANDO / ENTÃO), citando a issue no nome ou na docstring, por exemplo
  `test_register_user_rejects_duplicate_email  # SCRUM-11`.
- Meta de cobertura (DoD do Jira): **≥ 70%** no código novo.

## Comandos

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (bash: source .venv/Scripts/activate)
pip install -r requirements.txt

flask --app app.main run --debug   # sobe a aplicação
pytest                             # roda os testes
pytest --cov=domain --cov=use_cases --cov-report=term-missing
flake8 .                           # verifica PEP-8
```

Dependências esperadas em `requirements.txt`: `flask`, `pytest`, `pytest-cov`, `flake8`.

## Fluxo de trabalho

- Branches e commits citam a issue do Jira: `feature/SCRUM-14-create-review`,
  `SCRUM-14: adiciona caso de uso CreateReview`.
- Integração na `main` por pull request revisado por pelo menos 1 pessoa (DoD do Jira).
- Uso de IA (bônus): registrar no README onde e como o Claude foi usado e qual foi a
  estratégia (por exemplo: geração de esqueleto e testes a partir dos critérios de
  aceitação, sempre com revisão humana).
