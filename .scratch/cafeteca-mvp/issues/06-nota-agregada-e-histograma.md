# 06: Nota agregada e histograma na página do café

**Status:** done

**Jira:** SCRUM-19
**Histórias da spec:** 22 e 62 a 67 (na página do café)

**O que construir:** a página do café mostra a nota agregada no formato
"4,3 ★ · 12 avaliações" (ou "Sem avaliações") e um histograma com 5
barras, de 5★ até 1★, com a quantidade e a porcentagem de cada nota. Os
números mudam assim que alguém publica um review. A página segue a
ordem: ficha técnica, depois a nota agregada com o histograma e o botão
"Avaliar", e por fim os reviews.

- Domínio: o objeto de valor Nota agregada (CoffeeRating), criado a
  partir da coleção de notas de um café. Ele expõe a média exata, a média
  arredondada para 1 casa decimal (meio para cima: 4,25 vira 4,3, sem o
  arredondamento bancário do Python), a quantidade de reviews, o
  histograma (uma faixa por valor da escala) e a porcentagem por nota.
  Uma coleção vazia representa "Sem avaliações": não há média.
- O repositório de reviews passa a oferecer as notas de um café.
- Caso de uso `GetCoffeeRating`. `GetCoffeeDetails` passa a incluir a
  Nota agregada.
- A Nota agregada é calculada a partir dos reviews atuais a cada leitura
  e nunca é gravada.
- Presenter: vírgula decimal, "1 avaliação" ou "N avaliações", "Sem
  avaliações" e as porcentagens do histograma.

**Bloqueado por:** 05 (Avaliar um café e ver os reviews).

**Critérios de aceite:**

- [x] As notas [4, 4, 5, 4] dão média exata 4,25, exibida como "4,3"
      (meio para cima, não o arredondamento bancário).
- [x] DADO QUE o café tem um único review com nota 1, QUANDO a página é
      aberta, ENTÃO mostra "1,0 ★ · 1 avaliação". Não há quantidade
      mínima de reviews.
- [x] DADO QUE o café não tem reviews, QUANDO a página é aberta, ENTÃO
      mostra "Sem avaliações", e o histograma não quebra (todas as faixas
      com 0 e 0%, sem divisão por zero).
- [x] As notas [5, 5, 4, 1] dão o histograma 5★: 2 (50%), 4★: 1 (25%),
      3★: 0 (0%), 2★: 0 (0%) e 1★: 1 (25%), exibido de 5★ até 1★.
- [x] DADO QUE o usuário acabou de criar um review, QUANDO a página do
      café recarrega, ENTÃO a nota agregada e o histograma já incluem
      essa nota.
- [x] A página segue a ordem ficha técnica → nota agregada com histograma
      e botão "Avaliar" → reviews.
- [x] Testes de domínio da Nota agregada (arredondamento meio para cima,
      histograma, porcentagens e "Sem avaliações") e de `GetCoffeeRating`
      (incluindo o recálculo depois de um `CreateReview`), citando
      SCRUM-19, só com fakes.
- [x] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.

**Fora deste ticket:** a nota agregada nos cards da busca (ticket 10) e o
recálculo depois de editar ou excluir (ticket 07).
