# Cafeteca

Web-app para amantes de café encontrarem, avaliarem e discutirem cafés com a
comunidade.

## Pessoas

**Visitante**:
Quem navega sem estar logado. Vê todo o conteúdo público, mas não avalia.
_Avoid_: anônimo, convidado

**Usuário** (User):
Pessoa com conta no Cafeteca, identificada pelo e-mail e exibida pelo nome de
exibição.
_Avoid_: membro, conta, cliente

**Nome de exibição**:
O nome público de um usuário, mostrado nos seus reviews. Não precisa ser
único. O e-mail nunca é exibido em público.
_Avoid_: apelido, username, login

## Catálogo

**Catálogo**:
O conjunto de todos os cafés disponíveis para consulta e avaliação.

**Café** (Coffee):
Um produto vendido por uma torrefação, identificado pelo par (nome,
torrefação). O mesmo grão com nome ou torra diferente é outro café. A safra
não distingue cafés.
_Avoid_: produto, grão, lote

**Torrefação**:
Empresa que torra e vende o café. Faz parte da identidade do café.
_Avoid_: marca, torrador

**Produtor**:
Fazenda ou pessoa que cultivou o café. É texto livre e opcional.
_Avoid_: fazenda (como termo separado)

**Origem**:
País onde o café foi cultivado, escolhido em uma lista fechada.
_Avoid_: região, procedência

**Processo**:
Método de pós-colheita do café: Natural, Lavado, Cereja descascado (Honey)
ou Fermentado.
_Avoid_: beneficiamento

**Torra**:
Grau de torra do café: Clara, Média, Média-escura ou Escura.
_Avoid_: ponto de torra

**Nota sensorial**:
Um sabor ou aroma característico do café, escolhido em um conjunto fechado.
Um café pode ter várias.
_Avoid_: sabor, perfil, tag

**Altitude**:
Altura de cultivo do café, em metros. É opcional.
_Avoid_: altura

**Ficha técnica**:
O conjunto de atributos descritivos de um café: origem, produtor, variedade,
processo, altitude, torra e notas sensoriais.

**Recomendação de preparo**:
Uma sugestão de como preparar o café: um método obrigatório (por exemplo,
V60) e, opcionalmente, proporção, moagem e temperatura. Um café pode ter
zero ou mais.
_Avoid_: receita, modo de preparo

**Não informado**:
Como um atributo opcional vazio aparece para quem consulta o café.

## Avaliação

**Review**:
A opinião de um usuário sobre um café: uma nota obrigatória e um texto
opcional. Cada usuário tem no máximo um review por café.
_Avoid_: avaliação (como substantivo no domínio), comentário, resenha

**Nota**:
O número inteiro de 1 a 5 (estrelas) que um usuário dá a um café em seu
review.
_Avoid_: pontuação, score, estrelas (como termo de domínio)

**Nota agregada** (CoffeeRating):
O resumo das notas de um café: média, quantidade de reviews e histograma.
_Avoid_: rating, média (sozinha), score

**Histograma**:
A distribuição das notas de um café: quantos reviews deram cada nota de 1
a 5.

**Sem avaliações**:
Estado de um café que ainda não tem nenhum review e, portanto, não tem nota
agregada.

## Busca

**Busca**:
Consulta ao catálogo por termo, filtros e ordenação. Com o termo vazio,
lista o catálogo inteiro.
_Avoid_: pesquisa (no código), procura

**Termo**:
O texto digitado na busca, comparado com nome, torrefação e produtor sem
diferenciar acentos e maiúsculas.

**Filtro**:
Restrição da busca a valores de origem, processo, torra, nota sensorial ou
nota mínima. Valores do mesmo filtro combinam com OU, e filtros diferentes
combinam com E.

**Nota mínima**:
Filtro que mantém só os cafés cuja média da nota agregada é maior ou igual a
um valor escolhido. Exclui os cafés sem avaliações.

**Ordenação**:
Critério de ordem dos resultados: melhor avaliados, mais avaliados ou mais
recentes.
