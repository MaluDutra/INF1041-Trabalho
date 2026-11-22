# 13: Usuários e reviews de demonstração no seed

**Status:** ready-for-agent

**Jira:** SCRUM-14, SCRUM-19 (demonstração)
**Histórias da spec:** 69

**O que construir:** depois de rodar o comando de inicialização num
banco vazio, a aplicação já abre com usuários de demonstração e reviews
espalhados pelo catálogo. Isso basta para demonstrar a nota agregada, o
histograma, as ordenações (com desempates), o filtro de nota mínima e o
estado "Sem avaliações", sem precisar cadastrar nada à mão.

- O seed cria alguns usuários de demonstração. As senhas passam pelo
  mesmo hasher da aplicação, e as credenciais ficam documentadas no
  README.
- Os reviews passam pelas validações do domínio e respeitam um review por
  usuário por café. Eles têm datas distintas, com e sem texto, e pelo
  menos um review editado.
- A distribuição das notas foi pensada para a demonstração: médias
  variadas, um histograma dividido, dois cafés com a mesma média e
  quantidades diferentes e pelo menos um café sem avaliações.

**Bloqueado por:** 05 (Avaliar um café e ver os reviews).

**Critérios de aceite:**

- [ ] Num banco vazio, o comando de inicialização cria o catálogo, os
      usuários de demonstração e os reviews, sem erro.
- [ ] Pelo menos um café fica sem avaliações e mostra "Sem avaliações".
- [ ] Pelo menos um café tem um histograma com três ou mais notas
      diferentes.
- [ ] Há pelo menos um par de cafés com a mesma média e quantidades
      diferentes, para demonstrar o desempate de "Melhor avaliados".
- [ ] Há reviews com e sem texto e pelo menos um com o selo "editado".
- [ ] É possível entrar com as credenciais de demonstração do README e
      ver os reviews desse usuário.
- [ ] Nenhuma senha de demonstração fica gravada em texto no banco.
- [ ] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.
