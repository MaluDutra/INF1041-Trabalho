# 11: Filtros por origem, processo, torra e nota sensorial

**Status:** done

**Jira:** SCRUM-13
**Histórias da spec:** 29 a 31, 34 (termo, filtros e ordenação) e 43
(filtros)

**O que construir:** ao lado da busca, o visitante marca valores de
origem, processo, torra e nota sensorial. Vários valores no mesmo filtro
combinam com OU (Brasil ou Etiópia). Filtros diferentes combinam com E.
Os filtros combinam com o termo e com a ordenação, e os valores marcados
continuam marcados na página de resultados.

- Cada filtro é uma estratégia que implementa uma interface comum: "este
  café, com esta nota agregada, passa?". Recebe a Nota agregada desde já,
  para o filtro de nota mínima (ticket 12) entrar sem mudar a interface.
- Dentro de um filtro, os valores combinam com OU. `SearchCoffees`
  combina os filtros recebidos com E, sem conhecer as classes concretas
  (OCP).
- Nota sensorial: o café passa se tiver qualquer uma das notas marcadas.
- As opções de cada filtro vêm dos conjuntos fechados do domínio.

**Bloqueado por:** 10 (Nota agregada nos cards e ordenações).

**Critérios de aceite:**

- [x] Marcar Brasil e Etiópia mostra os cafés de qualquer um dos dois
      países.
- [x] (Brasil OU Etiópia) E Natural E (Chocolate OU Frutado) mostra só
      os cafés que atendem aos três critérios.
- [x] Um café sem processo, torra ou notas sensoriais não passa num
      filtro desse atributo.
- [x] Os filtros combinam com o termo e com a ordenação na mesma busca.
- [x] Os valores marcados continuam marcados na página de resultados.
      Valores desconhecidos no endereço são ignorados.
- [x] Uma combinação sem resultados mostra a mensagem com dicas do
      ticket 09.
- [x] Testes de `SearchCoffees`, citando SCRUM-13, só com fakes: cada
      filtro sozinho, vários valores no mesmo filtro (OU), filtros
      diferentes (E), filtros com termo e ordenação, café com atributo
      vazio e nenhum resultado.
- [x] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.

**Fora deste ticket:** filtro de nota mínima (ticket 12).
