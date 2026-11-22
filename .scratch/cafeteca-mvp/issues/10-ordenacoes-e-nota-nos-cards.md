# 10: Nota agregada nos cards e ordenações da busca

**Status:** ready-for-agent

**Jira:** SCRUM-13, SCRUM-19
**Histórias da spec:** 34 (termo e ordenação), 35 a 41, 43
(ordenação), 62 e 64 (nos cards)

**O que construir:** cada card da página inicial e dos resultados da
busca mostra a nota agregada ("4,3 ★ · 12 avaliações") ou "Sem
avaliações". O visitante escolhe a ordenação entre "Melhor avaliados"
(padrão, com ou sem termo), "Mais avaliados" e "Mais recentes". A
ordenação escolhida combina com o termo e continua marcada na página de
resultados.

- O repositório de reviews passa a oferecer as notas de todos os cafés
  de uma vez, para a busca não fazer uma consulta por café.
- `SearchCoffees` devolve cada café com a sua Nota agregada.
- Cada ordenação é uma estratégia que produz a chave de ordenação (OCP).
  `SearchCoffees` recebe a estratégia escolhida e não conhece as classes
  concretas. Uma ordenação nova entra como classe nova.
- Regras:
  - Melhor avaliados: média exata (decrescente), depois quantidade
    (decrescente), depois nome normalizado.
  - Mais avaliados: quantidade (decrescente), depois média exata
    (decrescente), depois nome normalizado.
  - Nas duas ordenações por nota, os cafés sem avaliações vão para o
    fim, em ordem alfabética.
  - Mais recentes: data de entrada no catálogo (decrescente), depois
    nome normalizado.
- A ordenação usa a média exata, não a arredondada.

**Bloqueado por:** 06 (Nota agregada e histograma), 09 (Busca por termo).

**Critérios de aceite:**

- [ ] Cada card mostra "4,3 ★ · 12 avaliações", "1 avaliação" no
      singular, ou "Sem avaliações".
- [ ] Sem escolha explícita, a página inicial e uma busca com termo usam
      "Melhor avaliados".
- [ ] Melhor avaliados: com médias 4,5 e 4,0, o 4,5 vem primeiro. Com
      médias iguais, vem primeiro quem tem mais reviews. Com média e
      quantidade iguais, a ordem é a do nome.
- [ ] Mais avaliados: com 10 e 3 reviews, o de 10 vem primeiro. Com
      quantidades iguais, vem primeiro a maior média e depois o nome.
- [ ] Nas duas ordenações por nota, os cafés sem avaliações ficam no fim,
      em ordem alfabética.
- [ ] Duas médias que arredondam para o mesmo valor ("4,3") mas têm
      médias exatas diferentes (4,26 e 4,34) ficam na ordem da média
      exata.
- [ ] Mais recentes: o café que entrou no catálogo por último vem
      primeiro. Datas iguais são desempatadas pelo nome.
- [ ] A ordenação escolhida combina com o termo e continua marcada na
      página de resultados. Um valor de ordenação desconhecido no
      endereço cai na ordenação padrão.
- [ ] Testes de `SearchCoffees`, citando SCRUM-13, só com fakes: as três
      ordenações, cada desempate, cafés sem avaliações no fim, média
      exata contra arredondada e ordenação junto com termo. As
      estratégias são testadas por meio do `SearchCoffees`, não
      diretamente.
- [ ] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.
