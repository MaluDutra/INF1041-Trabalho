# 12: Filtro de nota mínima

**Status:** done

**Jira:** SCRUM-13
**Histórias da spec:** 32, 33 e 43 (nota mínima)

**O que construir:** o visitante escolhe uma nota mínima ("4+", "3+",
"2+" ou "Qualquer") e vê só os cafés com nota agregada igual ou maior.
Cafés sem avaliações ficam de fora, porque ainda não têm média. O filtro
combina com o termo, com os outros filtros e com a ordenação.

Este ticket é a prova de OCP citada no README: o filtro entra como uma
estratégia nova, sem alterar o `SearchCoffees`.

- Nova estratégia de filtro que implementa a interface do ticket 11.
- "Qualquer" equivale a não aplicar o filtro, e os cafés sem avaliações
  aparecem.
- A comparação usa a média arredondada, a mesma que o card mostra. Assim
  um café exibido como "4,0 ★" aparece em "4+". **A confirmar com o
  grupo:** a spec não diz se a comparação usa a média exata ou a
  arredondada. Se o grupo preferir a exata, troque este critério e
  registre a decisão no glossário. (Decisão registrada no glossário: média
  arredondada.)

**Bloqueado por:** 11 (Filtros por origem, processo, torra e nota
sensorial).

**Critérios de aceite:**

- [x] Com "4+", um café de média 4,5 aparece e um de média 3,5 não.
- [x] Com "4+", um café de média exata 3,96 (exibida como "4,0") aparece.
- [x] Com "2+", "3+" ou "4+", os cafés sem avaliações não aparecem. Com
      "Qualquer", aparecem.
- [x] A nota mínima combina com o termo, com os outros filtros e com a
      ordenação, e continua marcada na página de resultados.
- [x] O diff deste ticket não altera o corpo do `SearchCoffees`: só
      acrescenta a nova estratégia, a ligação na composition root e a
      interface.
- [x] Testes de `SearchCoffees`, citando SCRUM-13, só com fakes: cada
      opção, exclusão dos cafés sem avaliações, o limite no
      arredondamento e a combinação com os outros filtros.
- [x] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.
