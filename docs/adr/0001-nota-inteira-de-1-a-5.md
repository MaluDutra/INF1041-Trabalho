# Nota inteira de 1 a 5

O PBB (SCRUM-14) ainda discute o método de avaliação: estrelas de 0 a 5,
nota de 0 a 10, emojis ou joinha. Decidimos usar uma nota **inteira de 1 a
5**, definida em uma única constante do domínio. O zero foi descartado
porque é ambíguo ("péssimo" ou "não avaliei"). A meia estrela foi descartada
porque dobra as faixas do histograma e complica o formulário sem ganho real
para um catálogo pequeno.

## Consequences

O histograma da nota agregada tem exatamente 5 faixas. Se o PO escolher
outra escala, basta mudar a constante. Reviews já gravados precisariam ser
convertidos.
