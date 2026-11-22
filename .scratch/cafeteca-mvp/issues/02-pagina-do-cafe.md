# 02: Página do café com ficha técnica, história e preparo

**Status:** ready-for-agent

**Jira:** SCRUM-12
**Histórias da spec:** 13 a 21, 68 e 70

**O que construir:** o visitante clica num card da página inicial e abre
a página do café, com tudo sobre ele num só lugar: nome, torrefação,
origem, a ficha técnica completa, a foto, a história e as recomendações
de preparo. Atributos vazios aparecem como "Não informado". Um endereço
de café que não existe mostra uma página amigável de "café não
encontrado".

- O Café ganha os atributos opcionais: produtor, variedade e história
  (texto livre), processo e torra (enums), altitude (inteiro positivo em
  metros), notas sensoriais (zero ou mais, sem repetição, de um conjunto
  fechado), foto e a lista de recomendações de preparo.
- Recomendação de preparo é um objeto de valor: método obrigatório e
  proporção, moagem e temperatura opcionais (texto livre).
- Caso de uso `GetCoffeeDetails`: recebe o id do café e devolve o DTO do
  café ou lança "não encontrado". Reviews e nota agregada entram nos
  tickets 05 e 06.
- Persistência das notas sensoriais e das recomendações de preparo em
  tabelas próprias.
- O seed cresce para cerca de 20 cafés. Ele cobre todas as origens,
  processos, torras e notas sensoriais, deixa alguns campos vazios e dá
  a cada café uma data de entrada diferente. A lista fechada de origens
  passa a ter exatamente os países desse seed.
- O presenter formata "Não informado". O domínio não conhece esse texto.

**Bloqueado por:** 01 (Esqueleto: catálogo na página inicial).

**Critérios de aceite:**

- [ ] DADO QUE um café tem todos os atributos, QUANDO o visitante abre a
      página dele, ENTÃO vê nome, torrefação, origem, produtor,
      variedade, processo, altitude, torra, notas sensoriais, foto,
      história e recomendações de preparo.
- [ ] DADO QUE um café não tem produtor, variedade, processo, altitude,
      torra, notas sensoriais ou história, QUANDO a página é aberta,
      ENTÃO cada atributo vazio aparece como "Não informado".
- [ ] Cada recomendação de preparo mostra o método e, quando houver,
      proporção, moagem e temperatura. O que faltar aparece como "Não
      informado". Um café sem recomendações mostra "Não informado" na
      seção de preparo.
- [ ] A foto aparece quando existe. Sem foto, a página continua íntegra.
- [ ] DADO QUE o id não existe, QUANDO o visitante abre o endereço,
      ENTÃO vê a página "café não encontrado" com status 404, e não um
      erro técnico. `GetCoffeeDetails` lança "não encontrado" e a rota
      traduz.
- [ ] O domínio rejeita processo, torra ou nota sensorial fora do
      conjunto fechado, notas sensoriais repetidas, altitude zero ou
      negativa e recomendação sem método.
- [ ] Os cards da página inicial têm link para a página do café.
- [ ] O seed tem cerca de 20 cafés, cobre todos os valores dos enums,
      tem campos vazios em alguns cafés e datas de entrada distintas. Os
      dados passam pelas validações do domínio.
- [ ] Testes de `GetCoffeeDetails` (café encontrado e não encontrado) e
      das invariantes do Café e da Recomendação de preparo, citando
      SCRUM-12, só com fakes.
- [ ] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.

**Fora deste ticket:** nota agregada, histograma, botão "Avaliar" e
lista de reviews (tickets 05 e 06).
