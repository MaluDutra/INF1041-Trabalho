# Cafeteca

Web-app para amantes de café encontrarem, avaliarem e discutirem cafés com a
comunidade. Trabalho A2 de INF1041 (Arquitetura e Projeto de Software):
Flask, Clean Architecture, SOLID, testes com Pytest e código em PEP-8.

Sumário: [Como rodar](#como-rodar) · [Testes, cobertura e
linters](#testes-cobertura-e-linters) · [Arquitetura](#arquitetura) ·
[Histórias e casos de uso](#histórias-do-jira-e-casos-de-uso) ·
[SOLID no código](#solid-no-código) · [Uso de IA](#uso-de-ia)

## Como rodar

Requer Python 3.12 ou mais novo.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows (bash: source .venv/Scripts/activate)
pip install -r requirements-dev.txt

flask --app app.main init-db      # cria o banco SQLite com os dados de demo
flask --app app.main run --debug  # sobe a aplicação em http://127.0.0.1:5000
```

Depois de subir, abra <http://127.0.0.1:5000>, clique em entrar e use um dos
usuários de demonstração abaixo. O catálogo, a busca e a página de cada café
funcionam sem login; avaliar um café e ver "Minhas avaliações" exigem login.

O `requirements.txt` tem só a dependência de execução (Flask); o
`requirements-dev.txt` inclui também pytest, pytest-cov, ruff, import-linter
e pre-commit. Para ativar os linters a cada commit, rode `pre-commit install`
uma vez.

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

Também é possível criar uma conta nova em `/cadastro`: a senha precisa de pelo
menos 8 caracteres, com letras e números.

### Banco de dados e configuração

- O arquivo do banco fica em `instance/cafeteca.db`. O `init-db` roda sobre
  um banco vazio: se o banco já tem cafés, nada é alterado.
- **Bancos antigos:** o seed só roda quando o banco não tem cafés. Um
  `instance/cafeteca.db` criado antes da issue 02 (schema antigo) ou antes da
  issue 13 (só cafés, sem usuários nem reviews) não é atualizado: apague o
  arquivo e rode o `init-db` de novo. As tabelas `users` e `reviews` são
  criadas pelo `init-db` mesmo em um banco que já tem cafés, sem apagar nada.
- A sessão do Flask é assinada com a chave `CAFETECA_SECRET_KEY`. Sem a
  variável de ambiente, vale uma chave fixa de desenvolvimento: defina a
  variável em qualquer ambiente que não seja o seu computador.
- As senhas nunca são gravadas em texto puro: o banco guarda o hash gerado
  pelo `werkzeug.security`.

## Testes, cobertura e linters

```bash
pytest                                   # 493 testes
pytest --cov --cov-report=term-missing   # cobertura de domain e use_cases
ruff check .                             # PEP-8, imports, nomes (--fix corrige)
ruff format --check .                    # formatação (sem --check, aplica)
lint-imports                             # regra de dependência da arquitetura
```

**Cobertura medida (`pytest --cov`):** 99% no total de `domain` e
`use_cases` (754 instruções, 1 não coberta: uma linha de
`domain/entities/review.py`), acima dos 70% exigidos. Todos os módulos dos
casos de uso estão em 100%. A configuração (`[tool.coverage.run]`, com
`source = ["domain", "use_cases"]`) fica em `pyproject.toml`, junto com a do
Ruff, do import-linter e do pytest.

Organização dos testes, que espelha as camadas:

| Pasta | O que testa | Usa Flask ou banco? |
| --- | --- | --- |
| `tests/domain/` | Entidades e objetos de valor | Não |
| `tests/use_cases/` | Casos de uso, com os fakes de `tests/fakes/` | Não |
| `tests/infra/` | Repositórios SQLite, hasher, relógio e seed | SQLite (arquivo temporário) |
| `tests/app/` | Rotas, presenters e o fluxo do seed de demo | Flask (test client) |

Os testes dos casos de uso são escritos a partir dos critérios de aceite das
histórias (DADO QUE / QUANDO / ENTÃO) e citam a história no nome ou no
comentário, por exemplo `test_repository_rejects_same_normalized_name_and_roaster
# SCRUM-13`.

O GitHub Actions (`.github/workflows/ci.yml`) roda Ruff, `lint-imports` e
`pytest --cov` a cada push na `main` e a cada pull request. O pre-commit
(`.pre-commit-config.yaml`) roda Ruff e `lint-imports` a cada commit.

## Arquitetura

O projeto tem as quatro camadas da Clean Architecture, uma pasta por camada:

| Camada | Pasta | O que tem |
| --- | --- | --- |
| Entidades | `domain/` | `User`, `Coffee`, `Review`, o objeto de valor `CoffeeRating`, conjuntos fechados (`Origin`, `Process`, `Roast`, `SensoryNote`) e as exceções de domínio |
| Casos de uso | `use_cases/` | Um caso de uso por classe, os DTOs e os ports (`use_cases/ports/`), as interfaces que a infraestrutura implementa |
| Adaptadores de interface | `app/routes/`, `app/presenters/` | Controllers (HTTP para DTO para caso de uso para resposta) e presenters que formatam a saída para as views |
| Frameworks e drivers | `infra/`, `app/main.py`, `app/templates/` | SQLite, hash de senha com Werkzeug, relógio do sistema e o Flask |

```
domain/       entities/ value_objects/ exceptions.py text.py
use_cases/    ports/ coffee/ review/ user/ dtos.py
infra/        db/ repositories/ security/ clock/
app/          main.py container.py routes/ presenters/ templates/ static/
tests/        domain/ use_cases/ infra/ app/ fakes/
```

### Regra de dependência

As dependências só apontam para dentro: `app` conhece `infra`, `use_cases` e
`domain`; `infra` implementa os ports de `use_cases` e usa `domain`;
`use_cases` usa só `domain`; `domain` não conhece ninguém. Na prática:

- `domain/` não importa `use_cases`, `infra`, `app`, Flask nem sqlite3.
- `use_cases/` importa apenas `domain/` e os próprios ports. Nunca importa
  Flask, Werkzeug, sqlite3 nem `infra/`.
- `infra/` implementa as interfaces de `use_cases/ports/`.
- `app/` é o único lugar que conhece todas as camadas. A ligação entre casos
  de uso e implementações concretas acontece só em `app/main.py` (composition
  root) e `app/container.py`.
- As rotas não têm regra de negócio: convertem a requisição em DTO, chamam
  `use_case.execute(...)` e traduzem o resultado ou a exceção em resposta
  HTTP.

### Como o `lint-imports` verifica

O import-linter lê os imports dos pacotes `domain`, `use_cases`, `infra` e
`app` e compara com os contratos declarados em `pyproject.toml`
(`[tool.importlinter]`). O comando `lint-imports` sai com erro se algum
import quebrar um contrato. Há dois:

1. **Camadas da Clean Architecture** (`type = "layers"`, com
   `layers = ["app", "infra", "use_cases", "domain"]`): de cima para baixo,
   uma camada só pode importar as que estão abaixo dela. Por isso `domain` não
   importa `use_cases`, `use_cases` não importa `infra` nem `app`, e `infra`
   não importa `app`.
2. **domain e use_cases independentes de framework e banco**
   (`type = "forbidden"`): os módulos de `domain` e `use_cases` não podem
   importar `flask`, `werkzeug` nem `sqlite3` (a opção
   `include_external_packages = true` faz o linter enxergar também os
   pacotes externos).

Saída atual: `Contracts: 2 kept, 0 broken.` O mesmo comando roda no
pre-commit e no CI. Quando um import novo quebra um contrato, a correção é
mudar o código (normalmente criando um port em `use_cases/ports/`), nunca
afrouxar o contrato.

## Histórias do Jira e casos de uso

O escopo do A2 são as histórias SCRUM-11, 12, 13, 14 e 19 do épico SCRUM-7.
A spec completa está em `.scratch/cafeteca-mvp/spec.md`, as decisões em
`docs/adr/` e o vocabulário em `GLOSSARY.md`. O que ficou de fora de
propósito (e-mail de confirmação, login social, amizades etc.) está no
[ADR 0004](docs/adr/0004-recortes-de-escopo-do-a2.md).

| História | Casos de uso (`use_cases/`) | Entidades e rotas principais |
| --- | --- | --- |
| SCRUM-11: criar conta e fazer login | `user/register_user.py` (`RegisterUser`), `user/authenticate_user.py` (`AuthenticateUser`), `user/get_user.py` (`GetUser`, usuário da sessão) | `User`; `/cadastro`, `/entrar`, `/sair` |
| SCRUM-12: página de um café | `coffee/get_coffee_details.py` (`GetCoffeeDetails`) | `Coffee`; `/cafes/<id>` |
| SCRUM-13: pesquisar por texto e filtros | `coffee/search_coffees.py` (`SearchCoffees`), com critérios em `search_criteria.py`, `search_filters.py` e `search_min_rating.py` e ordenações em `search_sorting.py` | `/` (catálogo, busca, filtros e ordenação) |
| SCRUM-14: avaliar um café com nota e review | `review/create_review.py` (`CreateReview`), `review/update_review.py` (`UpdateReview`), `review/delete_review.py` (`DeleteReview`), `review/list_user_reviews.py` (`ListUserReviews`, "Minhas avaliações") | `Review`; `/cafes/<id>/avaliar`, edição e exclusão, `/minhas-avaliacoes` |
| SCRUM-19: nota agregada de cada café | `review/get_coffee_rating.py` (`GetCoffeeRating`); na página e nos cards o mesmo cálculo vem de `CoffeeRating` | `CoffeeRating` (objeto de valor) |

Observação sobre o SCRUM-19: a nota agregada (média, quantidade e
histograma) é calculada a cada leitura pelo objeto de valor
`CoffeeRating.from_ratings`, a partir dos reviews atuais, e nunca é gravada.
Assim criar, editar ou excluir um review recalcula a nota sem nenhuma
atualização extra. A página do café (`GetCoffeeDetails`) e a busca
(`SearchCoffees`) usam esse cálculo diretamente. O caso de uso
`GetCoffeeRating` existe, tem testes próprios (incluindo o recálculo depois de
criar, editar e excluir) e não está ligado a nenhuma rota, porque a página
do café já recebe a nota dentro do `GetCoffeeDetails`.

## SOLID no código

Cada princípio abaixo aponta classes e módulos que existem no repositório.

**SRP (responsabilidade única).** Cada caso de uso é uma classe com um único
método público, `execute(...)`: `RegisterUser`, `AuthenticateUser`,
`GetCoffeeDetails`, `SearchCoffees`, `CreateReview`, `UpdateReview`,
`DeleteReview`, `ListUserReviews`, `GetCoffeeRating`. As entidades só
validam o próprio estado (`User`, `Coffee`, `Review` lançam exceções de
`domain/exceptions.py`), e a formatação para a tela fica em
`app/presenters/`, fora das regras de negócio.

**OCP (aberto para extensão, fechado para modificação).** `SearchCoffees`
recebe por injeção uma lista de fábricas de `SearchCriterion`
(`use_cases/coffee/search_criteria.py`) e uma lista de `SortStrategy`
(`use_cases/coffee/search_sorting.py`: `BestRated`, `MostReviewed`,
`MostRecent`). Os filtros de origem, processo, torra e nota sensorial
(`search_filters.py`) e o de nota mínima (`search_min_rating.py`, com
`MinRatingCriterion` e `min_rating_criterion`) são classes novas, registradas
só em `app/container.py`. Um filtro ou ordenação novo é uma classe nova mais o
registro, sem editar a lógica de `SearchCoffees`. Uma ressalva honesta: o
`SearchCoffees` foi editado nas issues 10 (ordenações e nota nos cards) e 11
(filtros): nesta última o contrato
`SearchCriterion.matches(coffee, rating)` passou a receber a nota agregada e,
para isso, a classe passou a calcular as notas de todo o catálogo antes de
filtrar. Depois dessa mudança de contrato, o filtro de nota mínima (issue 12)
entrou sem alterar `SearchCoffees` nem `SearchCriterion`: o commit só criou
`search_min_rating.py` e registrou a fábrica no container.

**LSP (substituição de Liskov).** Os fakes de `tests/fakes/`
(`InMemoryCoffeeRepository`, `InMemoryReviewRepository`,
`InMemoryUserRepository`, `FakePasswordHasher`, `FixedClock`) e as
implementações reais de `infra/` (`SqliteCoffeeRepository`,
`SqliteReviewRepository`, `SqliteUserRepository`, `WerkzeugPasswordHasher`,
`SystemClock`) cumprem os mesmos ports e são intercambiáveis. Isso é
verificado: `tests/infra/test_review_repository_contract.py` roda os mesmos
testes, parametrizados, contra o fake em memória e contra o SQLite, e
`tests/use_cases/test_coffee_repository_contract.py` fixa o contrato do
`CoffeeRepository`.

**ISP (segregação de interfaces).** Os ports em `use_cases/ports/` são
pequenos e específicos: `PasswordHasher` (`hash` e `verify`) é separado de
`UserRepository`, e `Clock` (só `now`) é separado dos repositórios. Um caso de
uso depende só do que usa: `UpdateReview` e `DeleteReview` precisam apenas de
`ReviewRepository`, e `GetUser` apenas de `UserRepository`.

**DIP (inversão de dependência).** Os casos de uso recebem no construtor
abstrações de `use_cases/ports/` (por exemplo,
`CreateReview(review_repository, coffee_repository, clock)`) e nunca
importam `infra/`, o que o contrato do `lint-imports` garante. A ligação com
as implementações concretas (SQLite, Werkzeug, `SystemClock`) acontece só na
composition root: `create_app()` em `app/main.py` chama `build_container()`
em `app/container.py`, que instancia os repositórios e injeta nos casos de
uso. Os testes usam os mesmos casos de uso com os fakes no lugar.

## Uso de IA

O trabalho usou o Claude (Claude Code) como ferramenta ao longo de todo o
fluxo, com uma estratégia de especificar antes de codar e de verificar
automaticamente depois. As etapas, na ordem, e onde cada uma deixa rastro no
repositório:

1. **Contexto para o agente.** O `CLAUDE.md` descreve o enunciado, o escopo
   vindo do Jira, a estrutura de pastas, a regra de dependência e as
   convenções, para o Claude seguir as mesmas regras em toda a sessão. As
   skills de apoio ficam em `.claude/skills/` (`grilling`, `grill-with-docs`,
   `domain-modeling`, `to-spec`, `to-tickets`, `tdd`, `implement` e
   `pocock-code-review`).
2. **Grilling da spec.** O Claude entrevistou o grupo, pergunta a pergunta,
   sobre as histórias SCRUM-11, 12, 13, 14 e 19 até fechar as decisões em
   aberto (a spec cita 21 perguntas, Q1 a Q21, em 22/11/2026). Resultado:
   `.scratch/cafeteca-mvp/spec.md`.
3. **Glossário e ADRs.** As decisões viraram vocabulário e registros:
   `GLOSSARY.md` e `docs/adr/0001` a `0004` (nota inteira de 1 a 5, um review
   por usuário por café, identidade do café e recortes de escopo).
4. **Quebra em issues.** A spec foi dividida em 14 issues verticais em
   `.scratch/cafeteca-mvp/issues/`, com critérios de aceite e um grafo de
   dependências (`.scratch/cafeteca-mvp/dag.md`) que define a ordem e o que
   pode rodar em paralelo.
5. **Implementação issue a issue com TDD.** Cada issue foi implementada pelo
   Claude, com testes escritos primeiro a partir dos critérios de aceite
   (DADO QUE / QUANDO / ENTÃO), código mínimo para passar e refatoração. Cada
   issue é um commit (`... (issue NN)`) com a linha `Co-Authored-By: Claude`.
   As issues foram implementadas por subagentes do Claude, seguindo a ordem
   do grafo de dependências.
6. **Verificação automática.** Em cada issue, pytest, `ruff check`,
   `ruff format --check` e `lint-imports` precisam passar, localmente
   (pre-commit) e no CI. As ferramentas, e não o Claude, decidem se o resultado está de
   acordo com o PEP-8 e com a Clean Architecture.
7. **Revisão humana.** O resultado de cada etapa é lido e aprovado por uma
   pessoa do grupo antes de seguir: a spec e as decisões do grilling, os
   critérios de aceite das issues e a integração na `main` por pull request,
   com o CI verde.
8. **Revisão de código assistida.** Ao final de cada etapa foi usada a
   skill `pocock-code-review`, que compara o código com as convenções do
   projeto (Standards) e com a issue (Spec).

O que a IA não decide: o escopo (cabe ao grupo e ao Jira), as regras de
negócio em aberto (a escala de notas virou o ADR 0001 por decisão do grupo no
grilling) e a aprovação final. A IA acelerou o esqueleto, os testes a partir
dos critérios de aceite e a documentação; as decisões de arquitetura ficaram
registradas em ADRs, e a regra de dependência é cobrada por ferramenta, não
por confiança.
