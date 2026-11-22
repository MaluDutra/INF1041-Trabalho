# 14: README com arquitetura, SOLID e uso de IA

**Status:** ready-for-agent

**Jira:** épico SCRUM-7 (entrega do A2)
**Histórias da spec:** nenhuma diretamente. Cobre os critérios de
avaliação de Clean Architecture, SOLID e o bônus de uso de IA.

**O que construir:** um README que permite ao professor rodar, testar e
avaliar o trabalho sem perguntar nada ao grupo. Ele mostra onde estão as
camadas, onde cada princípio SOLID aparece no código e como a IA foi
usada.

- Como rodar: ambiente virtual, dependências, inicialização do banco com
  seed, subir a aplicação, rodar os testes com cobertura e os linters.
- Credenciais dos usuários de demonstração.
- Arquitetura: as quatro camadas, a regra de dependência e os contratos
  do import-linter que a garantem.
- Mapeamento das histórias do Jira (SCRUM-11, 12, 13, 14 e 19) para os
  casos de uso.
- SOLID com exemplos concretos do código:
  - SRP: um caso de uso por classe.
  - OCP: as estratégias de filtro e de ordenação, com o filtro de nota
    mínima como exemplo de extensão sem alterar o `SearchCoffees`.
  - LSP: fakes em memória e repositórios SQLite substituíveis.
  - ISP: ports pequenos (hasher de senha e relógio separados dos
    repositórios).
  - DIP: casos de uso dependem dos ports, e a composition root faz a
    ligação.
- Uso de IA (bônus): onde e como o Claude foi usado (grilling da spec,
  ADRs e glossário, quebra em tickets, TDD a partir dos critérios de
  aceite) e a estratégia de revisão humana.

**Bloqueado por:** 08 ("Minhas avaliações"), 12 (Filtro de nota mínima),
13 (Usuários e reviews de demonstração).

**Critérios de aceite:**

- [ ] Uma pessoa sem contexto consegue, seguindo só o README, instalar,
      inicializar o banco, subir a aplicação e entrar com um usuário de
      demonstração.
- [ ] Cada princípio SOLID cita pelo menos uma classe ou módulo real do
      código e explica em uma ou duas frases por que ele aplica o
      princípio.
- [ ] A seção de arquitetura explica a regra de dependência e diz como o
      `lint-imports` a verifica.
- [ ] A seção de uso de IA descreve as etapas em que o Claude foi usado e
      como o grupo revisou o resultado.
- [ ] `pytest --cov` mostra cobertura de pelo menos 70% em `domain` e
      `use_cases`, e o número está registrado no README.
- [ ] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.
