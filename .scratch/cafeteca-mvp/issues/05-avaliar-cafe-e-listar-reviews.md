# 05: Avaliar um café e ver os reviews na página do café

**Status:** ready-for-agent

**Jira:** SCRUM-14
**Histórias da spec:** 44 a 50, 55 a 58 e 12 (e-mail nunca público)

**O que construir:** na página do café, o usuário logado clica em
"Avaliar", escolhe uma nota inteira de 1 a 5 e, se quiser, escreve um
texto. O review aparece na lista de reviews do café, destacado no topo
para o próprio autor. Depois de avaliar, o botão vira "Editar minha
avaliação". O visitante também vê "Avaliar". Ao clicar, vai para o login
(ou para o cadastro) e volta para a página do café com o formulário
aberto.

- Domínio: a entidade Review, com autor (id do usuário), café (id do
  café), nota, texto opcional, data de criação e marcador de editado
  (falso ao criar). A escala da nota vem de uma única constante do
  domínio (ADR 0001). O texto tem até 1000 caracteres, e um texto só com
  espaços vira "sem texto".
- Ports: repositório de reviews e relógio. O relógio fixo dos fakes deixa
  as datas determinísticas nos testes.
- Caso de uso `CreateReview`: exige que o café exista (senão "não
  encontrado") e que o usuário ainda não tenha avaliado esse café (senão
  conflito, ADR 0002).
- `GetCoffeeDetails` passa a receber, de forma opcional, o id do usuário
  logado. Ele devolve também os reviews do café (do mais recente para o
  mais antigo, com o nome de exibição do autor e o review do usuário
  logado em primeiro) e se esse usuário já avaliou o café.
- Infra: tabela de reviews com data de criação, marcador de editado e
  restrição única sobre (usuário, café), além do relógio real.
- App: formulário de review, botão "Avaliar" / "Editar minha avaliação",
  retorno ao café com um marcador no endereço que abre o formulário, e o
  presenter de datas no formato brasileiro.

**Bloqueado por:** 02 (Página do café), 04 (Login e retorno ao destino).

**Critérios de aceite:**

- [ ] DADO QUE o usuário está logado e ainda não avaliou o café, QUANDO
      envia a nota 4 sem texto, ENTÃO o review é criado e aparece no topo
      da lista com a nota, o nome de exibição dele e a data no formato
      brasileiro.
- [ ] Um texto só com espaços é gravado como "sem texto" e o review conta
      igual a um review com texto.
- [ ] As notas 0 e 6 são recusadas com mensagem de erro no formulário. Um
      texto com 1000 caracteres é aceito, e um com 1001 é recusado com
      mensagem.
- [ ] DADO QUE o usuário já avaliou o café, QUANDO abre a página, ENTÃO
      vê "Editar minha avaliação" no lugar de "Avaliar". Até o ticket 07
      chegar, o botão leva ao review dele no topo da lista.
- [ ] DADO QUE o usuário já avaliou o café, QUANDO reenvia o formulário de
      criação, ENTÃO vê um erro e nenhum segundo review é criado. O fake
      e a restrição única do SQLite garantem isso.
- [ ] Criar um review num café inexistente responde 404.
- [ ] DADO QUE o visitante não está logado, QUANDO clica em "Avaliar",
      ENTÃO vai para o login e, depois de entrar, volta para a página do
      café com o formulário aberto. O mesmo vale para o caminho login →
      "Criar conta" → cadastro.
- [ ] A lista mostra os reviews do mais recente para o mais antigo, com
      nota, nome de exibição, data e texto (quando houver). O review do
      usuário logado aparece destacado em primeiro. O e-mail do autor não
      aparece em lugar nenhum.
- [ ] Testes de `CreateReview` (válido, só nota, texto só com espaços,
      notas 0 e 6, 1000 e 1001 caracteres, café inexistente, segundo
      review no mesmo café) e da lista de reviews do `GetCoffeeDetails`
      (ordem e review próprio em primeiro), citando SCRUM-14, só com
      fakes e relógio fixo.
- [ ] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.

**Fora deste ticket:** nota agregada e histograma (ticket 06), editar e
excluir (ticket 07).
