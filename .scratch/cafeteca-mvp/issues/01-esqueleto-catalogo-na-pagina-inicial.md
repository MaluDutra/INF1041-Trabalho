# 01: Esqueleto: catálogo na página inicial

**Status:** done

**Jira:** SCRUM-13 (parcial), SCRUM-12 (parcial)
**Histórias da spec:** 23 e 14 (parcial)

**O que construir:** o visitante abre a página inicial e vê a lista de
todos os cafés do catálogo, com nome, torrefação e origem, lidos do
SQLite. É o primeiro corte vertical: passa pelas quatro camadas e define
o padrão que os próximos tickets seguem.

- Domínio: a entidade Café com os campos obrigatórios (nome, torrefação,
  origem) e a data de entrada no catálogo; a função pura de normalização
  de texto (sem acentos, em minúsculas, sem espaços nas pontas); a
  identidade do café pelo par (nome, torrefação) normalizado (ADR 0003);
  a hierarquia de exceções do domínio (erro base, validação, não
  encontrado, conflito, credenciais inválidas, permissão negada).
- Origem já é um conjunto fechado (enum), com os países do seed mínimo.
  O ticket 02 completa a lista.
- Casos de uso: o port do repositório de cafés e um `SearchCoffees`
  mínimo, que, com o termo vazio, devolve o catálogo inteiro em DTOs
  imutáveis, em ordem alfabética do nome normalizado. Essa é a ordem que
  "Melhor avaliados" produz enquanto nenhum café tem review.
- Infra: a conexão SQLite, a criação do schema da tabela de cafés (com a
  restrição de unicidade do par normalizado) e o repositório SQLite.
- App: a composition root, a rota da página inicial, o template base e
  um comando documentado que cria o schema e roda o seed sobre um banco
  vazio.
- Testes: a pasta de fakes, com o fake em memória do repositório de
  cafés, que os outros tickets reaproveitam.

**Bloqueado por:** nenhum (pode começar já).

**Critérios de aceite:**

- [x] DADO QUE o catálogo tem cafés, QUANDO o visitante abre a página
      inicial, ENTÃO vê todos eles, com nome, torrefação e origem, sem
      digitar nada.
- [x] DADO QUE falta o nome, a torrefação ou a origem (ou o valor só tem
      espaços), QUANDO o Café é criado, ENTÃO o domínio lança um erro de
      validação.
- [x] A normalização transforma "  Sítio DA Torre " em "sitio da torre"
      (teste de domínio).
- [x] DADO QUE já existe "Sítio da Torre" da torrefação "Café Lá", QUANDO
      se tenta gravar "sitio da torre" da "CAFÉ LA", ENTÃO o repositório
      recusa com erro de conflito. O fake e o SQLite se comportam igual
      (no SQLite, por uma restrição de unicidade).
- [x] O Café guarda a data de entrada no catálogo.
- [x] `SearchCoffees` com o termo vazio devolve o catálogo inteiro em
      ordem alfabética do nome normalizado (teste com o fake, citando
      SCRUM-13).
- [x] A rota só converte a requisição em DTO, chama `execute()` e
      renderiza o template. A ligação entre casos de uso e implementações
      concretas acontece só na composition root.
- [x] O comando de inicialização cria o banco e um seed mínimo (alguns
      cafés), e a aplicação sobe com `flask --app app.main run`. Os dois
      comandos estão no README.
- [x] Os testes usam só fakes em memória (sem Flask, HTTP ou SQLite).
- [x] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.

**Fora deste ticket:** termo de busca, filtros, ordenações, nota
agregada e atributos opcionais do café.
