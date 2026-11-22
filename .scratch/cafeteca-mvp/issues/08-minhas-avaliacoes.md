# 08: Página "Minhas avaliações"

**Status:** ready-for-agent

**Jira:** SCRUM-14
**Histórias da spec:** 59 a 61

**O que construir:** o usuário logado abre "Minhas avaliações" pelo
cabeçalho e vê todos os seus reviews, do mais recente para o mais
antigo. Cada item mostra o nome do café (com link para a página dele), a
nota, o texto, a data, o selo "editado" quando for o caso e as ações de
editar e excluir. O visitante que tenta abrir a página é levado ao login
e volta para ela depois de entrar.

- Caso de uso `ListUserReviews`: devolve os reviews de um usuário, do
  mais recente para o mais antigo, com o id e o nome de cada café.
- App: rota marcada como "exige login" (mecanismo do ticket 04), link no
  cabeçalho para usuários logados e reaproveitamento dos fluxos de editar
  e excluir do ticket 07, voltando para "Minhas avaliações" depois da
  ação.

**Bloqueado por:** 07 (Editar e excluir o próprio review).

**Critérios de aceite:**

- [ ] DADO QUE o usuário avaliou três cafés em datas diferentes, QUANDO
      abre "Minhas avaliações", ENTÃO vê os três, do mais recente para o
      mais antigo, cada um com nome do café (com link), nota, texto
      (quando houver), data e ações de editar e excluir.
- [ ] A página mostra só os reviews do usuário logado, nunca os de outras
      pessoas.
- [ ] DADO QUE o usuário ainda não avaliou nenhum café, QUANDO abre a
      página, ENTÃO vê uma mensagem que convida a explorar o catálogo,
      com link para a página inicial.
- [ ] DADO QUE o visitante não está logado, QUANDO abre "Minhas
      avaliações", ENTÃO vai para o login e, depois de entrar, volta para
      "Minhas avaliações".
- [ ] Editar ou excluir a partir desta página leva de volta a "Minhas
      avaliações", já com a mudança.
- [ ] Testes de `ListUserReviews`, citando SCRUM-14, só com fakes e
      relógio fixo: ordem, só os reviews do usuário, nome do café em cada
      item e lista vazia.
- [ ] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.
