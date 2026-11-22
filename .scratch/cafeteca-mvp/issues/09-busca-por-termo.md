# 09: Busca por termo

**Status:** done

**Jira:** SCRUM-13
**Histórias da spec:** 24 a 28, 42 e 43 (termo)

**O que construir:** a página inicial ganha um campo de busca. O
visitante digita um termo e vê os cafés cujo nome, torrefação ou
produtor contém esse termo como uma frase inteira, sem diferenciar
acentos e maiúsculas. Um termo com só 1 caractere útil mostra um aviso
de mínimo de 2 caracteres. Um termo vazio mostra o catálogo inteiro.
Quando nada é encontrado, a página mostra dicas para ajustar a busca. O
termo continua no campo na página de resultados.

- `SearchCoffees` passa a receber o termo. O casamento é feito no caso de
  uso, em memória, com a normalização de texto do domínio, e não com
  `LIKE` no banco. Assim todas as regras podem ser testadas sem banco.
- Um termo com exatamente 1 caractere útil (descontados os espaços) é
  rejeitado com um erro de validação, que a rota mostra como aviso.

**Bloqueado por:** 02 (Página do café, que traz o produtor e o seed
completo).

**Critérios de aceite:**

- [x] "sitio" encontra "Sítio da Torre", e "SITIO DA" também.
- [x] "torre sítio" não encontra "Sítio da Torre": o termo é comparado
      como uma frase inteira contida no texto, não palavra por palavra.
- [x] O termo casa com a torrefação e com o produtor, além do nome.
- [x] "a" e " a " mostram o aviso de mínimo de 2 caracteres e não fazem a
      busca.
- [x] Um termo vazio ou "   " mostra o catálogo inteiro, sem aviso.
- [x] DADO QUE nenhum café casa com o termo, QUANDO a busca é feita,
      ENTÃO a página mostra uma mensagem com dicas (conferir a grafia,
      usar um termo mais curto, remover filtros), e não uma lista vazia.
- [x] O termo digitado continua no campo de busca na página de
      resultados.
- [x] Testes de `SearchCoffees`, citando SCRUM-13, só com fakes: termo no
      nome, na torrefação e no produtor, termo com acentos e maiúsculas,
      frase fora de ordem, termo com 1 caractere, termo vazio, termo só
      com espaços e nenhum resultado.
- [x] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.

**Fora deste ticket:** ordenações e nota agregada nos cards (ticket 10)
e filtros (tickets 11 e 12).
