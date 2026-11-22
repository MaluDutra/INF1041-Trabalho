# Spec: Cafeteca MVP (A2)

Status: ready-for-agent

Histórias do Jira cobertas: SCRUM-11, SCRUM-12, SCRUM-13, SCRUM-14 e
SCRUM-19 (épico SCRUM-7). Decisões vindas do grilling de 22/11/2026
(Q1 a Q21), registradas no `GLOSSARY.md` e nos ADRs 0001 a 0004.

## Problem Statement

Quem gosta de café especial não tem um lugar simples para descobrir cafés,
consultar a ficha técnica de cada um e saber o que outras pessoas acharam
deles. As informações ficam espalhadas entre sites de torrefações,
embalagens e redes sociais. Não há como comparar cafés por origem,
processo, torra ou nota sensorial, nem ver uma nota da comunidade que
resuma as opiniões. Quem prova um café também não tem onde registrar sua
opinião e ajudar outras pessoas a escolher.

## Solution

O Cafeteca é um web-app com um catálogo de cafés. Visitantes navegam
livremente: buscam por termo, combinam filtros, escolhem a ordenação e
abrem a página de cada café, com a ficha técnica, a história, as
recomendações de preparo, a nota agregada, o histograma e os reviews da
comunidade. Quem cria uma conta pode avaliar cada café com uma nota de 1 a
5 e um texto opcional, editar ou excluir o próprio review e ver todos os
seus reviews na página "Minhas avaliações". A nota agregada de cada café é
recalculada a cada review criado, editado ou excluído.

## User Stories

### Conta e login (SCRUM-11)

1. Como visitante, quero criar uma conta com nome de exibição, e-mail e
   senha, para poder avaliar cafés.
2. Como visitante, quero entrar automaticamente logo após o cadastro, para
   não ter que digitar e-mail e senha de novo.
3. Como visitante, quero ver uma mensagem clara quando o e-mail já está
   cadastrado, para saber que devo fazer login em vez de cadastro.
4. Como visitante, quero que "Ana@x.com" e "ana@x.com" sejam tratados como
   o mesmo e-mail, para não acabar com duas contas por engano.
5. Como visitante, quero saber na hora do cadastro que a senha precisa ter
   pelo menos 8 caracteres, com letras e números, para escolher uma senha
   válida já na primeira tentativa.
6. Como visitante, quero saber que o nome de exibição precisa ter de 2 a
   40 caracteres, para escolher um nome aceito.
7. Como visitante, quero poder usar um nome de exibição que outra pessoa
   já usa, porque o nome não precisa ser único.
8. Como usuário, quero fazer login com e-mail e senha, para avaliar cafés
   e gerenciar meus reviews.
9. Como usuário, quero ver uma mensagem genérica quando o e-mail ou a
   senha estiverem errados, sem revelar qual dos dois falhou, para que
   ninguém descubra quais e-mails têm conta.
10. Como usuário, quero sair da minha conta, para proteger meu acesso num
    computador compartilhado.
11. Como usuário, quero que minha senha nunca seja guardada em texto puro,
    para que um vazamento do banco não exponha minha senha.
12. Como usuário, quero que meu e-mail nunca apareça em público, para
    proteger meus dados pessoais (LGPD).

### Página do café (SCRUM-12)

13. Como visitante, quero abrir a página de um café, para ver tudo sobre
    ele num só lugar.
14. Como visitante, quero ver o nome, a torrefação e a origem do café,
    que estão sempre preenchidos.
15. Como visitante, quero ver a ficha técnica (produtor, variedade,
    processo, altitude, torra e notas sensoriais), para entender o perfil
    do café.
16. Como visitante, quero ver "Não informado" em qualquer atributo vazio,
    para distinguir um dado ausente de um erro na página.
17. Como visitante, quero ler a história do café, para conhecer sua
    origem e o produtor.
18. Como visitante, quero ver as recomendações de preparo, cada uma com o
    método e, quando houver, proporção, moagem e temperatura, para
    preparar o café do melhor jeito.
19. Como visitante, quero ver "Não informado" quando o café não tem
    recomendações de preparo ou quando falta proporção, moagem ou
    temperatura numa recomendação.
20. Como visitante, quero ver a foto do café quando houver, para
    reconhecê-lo na prateleira.
21. Como visitante, quero ver uma página de "café não encontrado" quando
    abro um endereço de café que não existe, em vez de um erro técnico.
22. Como visitante, quero que a página siga a ordem ficha técnica, nota
    agregada com histograma e botão "Avaliar", e por fim os reviews, para
    ler primeiro sobre o café e depois as opiniões.

### Busca e filtros (SCRUM-13)

23. Como visitante, quero que a página inicial mostre o catálogo inteiro,
    para navegar sem precisar digitar nada.
24. Como visitante, quero buscar por um termo que case com o nome, a
    torrefação ou o produtor, para achar um café específico.
25. Como visitante, quero que a busca ignore acentos e maiúsculas, para
    que "sitio" encontre "Sítio da Torre".
26. Como visitante, quero que o termo seja comparado como uma frase
    inteira contida no texto, para ter resultados previsíveis ("sitio da"
    encontra "Sítio da Torre", mas "torre sítio" não encontra nada).
27. Como visitante, quero ver um aviso de mínimo de 2 caracteres quando
    digito só 1 caractere (descontados os espaços), para entender por que
    não houve busca.
28. Como visitante, quero que um termo vazio ou só com espaços mostre o
    catálogo inteiro, sem aviso.
29. Como visitante, quero filtrar por origem, processo, torra e nota
    sensorial, para encontrar cafés com o perfil que procuro.
30. Como visitante, quero marcar vários valores no mesmo filtro (por
    exemplo, Brasil e Etiópia) e ver os cafés que têm qualquer um deles,
    para ampliar a busca dentro de um critério.
31. Como visitante, quero que filtros diferentes se combinem com E (por
    exemplo, (Brasil OU Etiópia) E Natural E (Chocolate OU Frutado)), para
    refinar a busca.
32. Como visitante, quero filtrar por nota mínima ("4+", "3+", "2+" ou
    "Qualquer"), para ver só cafés bem avaliados.
33. Como visitante, quero que o filtro de nota mínima exclua os cafés sem
    avaliações, porque eles ainda não têm média.
34. Como visitante, quero combinar termo, filtros e ordenação na mesma
    busca.
35. Como visitante, quero ordenar por "Melhor avaliados", "Mais avaliados"
    ou "Mais recentes", para ver primeiro o que me interessa.
36. Como visitante, quero que "Melhor avaliados" seja a ordenação padrão,
    tanto na página inicial quanto numa busca com termo.
37. Como visitante, quero que "Melhor avaliados" desempate pela maior
    quantidade de reviews e depois pelo nome, para ter uma ordem estável.
38. Como visitante, quero que "Mais avaliados" desempate pela maior média
    e depois pelo nome.
39. Como visitante, quero que, nas duas ordenações por nota, os cafés sem
    avaliações fiquem no fim, em ordem alfabética.
40. Como visitante, quero que "Mais recentes" mostre primeiro os cafés que
    entraram no catálogo por último, com empate desfeito pelo nome.
41. Como visitante, quero ver em cada card do resultado a média e a
    quantidade de reviews, ou "Sem avaliações", para comparar cafés sem
    abrir cada um.
42. Como visitante, quero ver uma mensagem com dicas para ajustar a busca
    quando nada for encontrado, em vez de uma página vazia.
43. Como visitante, quero que o termo, os filtros e a ordenação continuem
    marcados na página de resultados, para ajustar a busca sem recomeçar.

### Avaliar com nota e review (SCRUM-14)

44. Como usuário, quero dar a um café uma nota inteira de 1 a 5, para
    registrar o quanto gostei dele.
45. Como usuário, quero escrever um texto opcional de até 1000
    caracteres, para explicar minha nota.
46. Como usuário, quero poder publicar só a nota, sem texto, e que ela
    conte na nota agregada do mesmo jeito.
47. Como usuário, quero que um texto feito só de espaços seja tratado como
    "sem texto", para não publicar um review em branco.
48. Como usuário, quero ver uma mensagem de erro quando a nota estiver
    fora de 1 a 5 ou o texto passar de 1000 caracteres.
49. Como usuário, quero ter no máximo um review por café, e que o botão
    "Avaliar" vire "Editar minha avaliação" depois que avaliei, para não
    criar um segundo review por engano.
50. Como usuário, quero receber um erro se eu tentar criar um segundo
    review para o mesmo café (por exemplo, reenviando o formulário).
51. Como usuário, quero editar a nota e o texto do meu review, para
    atualizar minha opinião depois de provar o café de outro jeito.
52. Como usuário, quero que o review editado mantenha a data original e
    mostre o selo "editado", para que os outros saibam que ele mudou.
53. Como usuário, quero excluir meu review depois de confirmar, sabendo
    que a exclusão é definitiva.
54. Como usuário, quero que só eu possa editar ou excluir meus reviews,
    para que ninguém altere minha opinião.
55. Como visitante, quero ver o botão "Avaliar" mesmo sem login e, ao
    clicar, ser levado ao login e depois voltar para a página do café com
    o formulário aberto.
56. Como visitante sem conta, quero ir do login para o cadastro e, depois
    de me cadastrar, também voltar para a página do café que eu queria
    avaliar.
57. Como visitante, quero ler a lista de reviews de um café, do mais
    recente para o mais antigo, com a nota, o nome de exibição do autor,
    a data e o texto, quando houver.
58. Como usuário, quero ver meu próprio review destacado no topo da lista
    de reviews do café.
59. Como usuário, quero a página "Minhas avaliações", com meus reviews do
    mais recente para o mais antigo, para revisar o que já avaliei.
60. Como usuário, quero que cada item de "Minhas avaliações" mostre o nome
    do café (com link), a nota, o texto, a data e as ações de editar e
    excluir.
61. Como visitante, quero ser levado ao login quando tento abrir "Minhas
    avaliações" sem estar logado.

### Nota agregada (SCRUM-19)

62. Como visitante, quero ver a média de cada café com 1 casa decimal e
    vírgula ("4,3 ★ · 12 avaliações"), para ter uma ideia rápida da
    opinião da comunidade.
63. Como visitante, quero que a média apareça já a partir do primeiro
    review, sem quantidade mínima.
64. Como visitante, quero ver "Sem avaliações" num café que ainda não tem
    review.
65. Como visitante, quero que a média seja arredondada para cima a partir
    de 0,05 (4,25 vira 4,3), do jeito que aprendi na escola.
66. Como visitante, quero ver na página do café um histograma com 5
    barras, de 5★ até 1★, com a quantidade e a porcentagem de cada nota,
    para entender se a opinião é unânime ou dividida.
67. Como visitante, quero que a nota agregada e o histograma mudem assim
    que um review é criado, editado ou excluído, para nunca ver números
    desatualizados.

### Demonstração

68. Como equipe, queremos um seed com cerca de 20 cafés que cubra todas as
    origens, processos, torras e notas sensoriais, com alguns campos
    vazios, para demonstrar filtros e o "Não informado".
69. Como equipe, queremos usuários de demonstração com reviews no seed,
    e pelo menos um café sem avaliações, para demonstrar a nota agregada,
    o histograma, as ordenações e o "Sem avaliações".
70. Como equipe, queremos que cada café do seed tenha uma data diferente
    de entrada no catálogo, para que "Mais recentes" seja demonstrável.

## Implementation Decisions

### Camada de domínio

- **Escala da nota**: inteiro de 1 a 5, definido em uma única constante
  do domínio (ADR 0001). O histograma tem uma faixa por valor da escala.
- **User**: nome de exibição (de 2 a 40 caracteres depois de tirar os
  espaços das pontas, não único), e-mail (único, guardado e comparado em
  minúsculas e sem espaços nas pontas) e hash da senha. A regra da senha
  (mínimo de 8 caracteres, com pelo menos uma letra e um número) é do
  domínio e é validada sobre a senha em texto antes do hash. A senha em
  texto nunca é guardada na entidade.
- **Coffee**: identidade pública por (nome, torrefação), comparada depois
  de normalizar acentos e maiúsculas (ADR 0003). Nome, torrefação e origem
  são obrigatórios. Os opcionais são produtor, variedade, processo,
  altitude, torra, notas sensoriais, foto, história e recomendações de
  preparo. O café também guarda a data em que entrou no catálogo.
- **Valores controlados** (conjuntos fechados do domínio, em enums):
  - Origem: os países produtores presentes no seed.
  - Processo: Natural, Lavado, Cereja descascado (Honey), Fermentado.
  - Torra: Clara, Média, Média-escura, Escura.
  - Nota sensorial: Chocolate, Caramelo, Castanhas, Frutado, Cítrico,
    Floral, Frutas vermelhas, Especiado, Mel, Herbal. Um café pode ter
    zero ou mais, sem repetição.
- **Altitude**: inteiro positivo em metros, opcional (o "altura" da Q5 é
  a altitude de cultivo).
- **Texto livre**: produtor, variedade e história.
- **Recomendação de preparo**: objeto de valor dentro do café, com método
  obrigatório e proporção, moagem e temperatura opcionais (texto livre).
  O café tem uma lista de zero ou mais recomendações. Isso substitui o
  "texto livre" para preparo previsto na Q5 (decisão da Q17).
- **Review**: autor (id do usuário), café (id do café), nota, texto
  opcional (até 1000 caracteres, e texto só com espaços vira "sem
  texto"), data de criação e marcador de editado. Editar altera nota e
  texto, mantém a data de criação e liga o marcador. Não há histórico de
  versões.
- **CoffeeRating** (objeto de valor): criado a partir da coleção de notas
  de um café. Expõe a média, a média arredondada para 1 casa decimal (meio
  para cima, ou seja, 4,25 vira 4,3, sem o arredondamento bancário do
  Python), a quantidade de reviews, o histograma (quantidade por nota) e a
  porcentagem por nota. Uma coleção vazia representa "Sem avaliações": não
  há média, e as ordenações e o filtro de nota mínima tratam esse estado
  de forma explícita.
- **Normalização de texto** (sem acentos, em minúsculas e sem espaços nas
  pontas): uma função pura do domínio, usada pela identidade do café e
  pela busca.
- **Exceções do domínio**: um erro base com especializações para
  validação, recurso não encontrado, conflito (e-mail já cadastrado,
  segundo review no mesmo café), credenciais inválidas e permissão negada
  (editar ou excluir o review de outra pessoa). As rotas traduzem cada uma
  em resposta HTTP.

### Camada de casos de uso (módulo de regras)

- Cada caso de uso é uma classe com um único `execute()`. As dependências
  entram pelo construtor, tipadas pelos ports. A entrada e a saída usam
  DTOs imutáveis, sem objetos do Flask.
- **Ports**: repositório de usuários, repositório de cafés, repositório de
  reviews, hasher de senha e relógio. O relógio permite datas
  determinísticas nos testes. Os ports são pequenos e separados (ISP).
- **Casos de uso**:
  - `RegisterUser`: valida os dados, rejeita e-mail duplicado, gera o hash
    e devolve o usuário criado. A rota usa o resultado para o login
    automático.
  - `AuthenticateUser`: devolve o usuário ou lança "credenciais
    inválidas", com a mesma exceção para e-mail inexistente e para senha
    errada.
  - `GetCoffeeDetails`: recebe o id do café e, opcionalmente, o id do
    usuário logado. Devolve o café, o CoffeeRating, os reviews (do mais
    recente para o mais antigo, com o nome de exibição do autor e o review
    do usuário logado em primeiro) e se esse usuário já avaliou o café
    (para decidir entre "Avaliar" e "Editar minha avaliação").
  - `SearchCoffees`: recebe o termo, os filtros e a ordenação. Rejeita um
    termo com exatamente 1 caractere útil. Com o termo vazio, considera o
    catálogo inteiro. Devolve cada café com seu CoffeeRating. O casamento
    do termo, os filtros e a ordenação são feitos no caso de uso, em
    memória, porque o catálogo é pequeno e não há paginação. Assim todas
    as regras da busca podem ser testadas sem banco.
  - `CreateReview`, `UpdateReview`, `DeleteReview`: criar exige que o café
    exista e que o usuário ainda não tenha avaliado esse café. Editar e
    excluir exigem que quem pede seja o autor.
  - `GetCoffeeRating`: devolve o CoffeeRating de um café.
  - `ListUserReviews`: os reviews de um usuário, do mais recente para o
    mais antigo, com o nome de cada café, para a página "Minhas
    avaliações".
- **Busca extensível (OCP)**:
  - Cada filtro é uma estratégia que implementa uma interface comum
    ("este café com esta nota agregada passa?"): origem, processo, torra,
    nota sensorial e nota mínima. Dentro de um filtro, os valores combinam
    com OU. `SearchCoffees` combina os filtros recebidos com E.
  - Cada ordenação é uma estratégia que produz a chave de ordenação:
    "Melhor avaliados" (padrão), "Mais avaliados" e "Mais recentes".
  - Um novo filtro ou uma nova ordenação entra como nova classe, sem
    alterar `SearchCoffees`. O filtro de nota mínima é o exemplo usado no
    README.
- **Regras de ordenação**:
  - Melhor avaliados: média (decrescente), depois quantidade (decrescente),
    depois nome normalizado. Cafés sem avaliações vão para o fim, em ordem
    alfabética.
  - Mais avaliados: quantidade (decrescente), depois média (decrescente),
    depois nome normalizado. Cafés sem avaliações vão para o fim, em ordem
    alfabética.
  - Mais recentes: data de entrada no catálogo (decrescente), depois nome
    normalizado.
  - A ordenação por média usa a média exata, não a arredondada.
- **Nota agregada sempre atual**: o CoffeeRating é calculado a partir dos
  reviews atuais a cada leitura e nunca é gravado. Assim ele reflete
  automaticamente a criação, a edição e a exclusão, sem risco de ficar
  dessincronizado. O repositório de reviews oferece as notas de um café e
  as notas de todos os cafés de uma vez, que a busca usa.

### Infra (frameworks e drivers)

- **Schema SQLite**:
  - `users`: e-mail único já normalizado.
  - `coffees`: inclui a data de entrada no catálogo e uma restrição de
    unicidade sobre o par (nome, torrefação) normalizado.
  - Uma tabela para as notas sensoriais do café e outra para as
    recomendações de preparo.
  - `reviews`: inclui a data de criação, o marcador de editado e uma
    restrição única sobre (usuário, café), que repete no banco a regra do
    ADR 0002.
- Os repositórios SQLite implementam os mesmos ports dos fakes (LSP).
- O hasher de senha usa `werkzeug.security`.
- O seed cria o catálogo de demonstração (cerca de 20 cafés com datas de
  entrada distintas e campos vazios em alguns), os usuários de
  demonstração e os reviews, deixando pelo menos um café sem avaliações.
  Ele roda sobre um banco vazio.

### App (adaptadores e Flask)

- A composition root monta os repositórios SQLite, o hasher, o relógio e
  os casos de uso. As rotas recebem os casos de uso prontos.
- A sessão do Flask guarda só o id do usuário logado. Não há "Manter
  conectado".
- **Fluxo de login**:
  - As ações que exigem login redirecionam para o login com um parâmetro
    `next`. Depois do login ou do cadastro, o usuário volta para o `next`.
  - O `next` só é aceito se for um caminho relativo interno, para evitar
    redirecionamento aberto.
  - Voltar para a página do café com o formulário aberto é feito com um
    marcador no endereço.
- **Rotas** (HTML renderizado no servidor, formulários POST para
  mutações): página inicial/busca, página do café, cadastro, login,
  logout, criar review, editar review, excluir review e "Minhas
  avaliações".
- **Erros e mensagens**: a exclusão pede confirmação antes do POST. As
  exceções do domínio viram mensagens em português no formulário, ou
  respostas 404 ou 403.
- **Presenters**: formatam a saída dos casos de uso para os templates:
  - média com vírgula decimal ("4,3");
  - "Sem avaliações" e "Não informado";
  - selo "editado";
  - datas no formato brasileiro;
  - porcentagens do histograma.
  - Nenhuma regra de negócio fica nos presenters, só formatação.
- Sem paginação, nem na busca nem na lista de reviews.

## Testing Decisions

- **Seam único: o módulo de regras**, ou seja, os casos de uso das camadas
  `use_cases` + `domain`, exercitados pelo `execute()` com fakes em
  memória dos ports. Nenhum teste usa Flask, HTTP ou SQLite.
- Os testes de **domínio** (entidades e CoffeeRating) ficam no mesmo
  seam: são o núcleo puro desse módulo. Eles cobrem o que é mais claro
  testar diretamente:
  - a validação das invariantes;
  - o arredondamento meio para cima;
  - o histograma e as porcentagens;
  - o estado "Sem avaliações".
- Um bom teste verifica comportamento externo: dada uma entrada no
  `execute()` e um estado nos fakes, confere a saída (DTO) ou a exceção
  lançada. Ele não verifica chamadas internas, a ordem das chamadas aos
  repositórios nem as classes de estratégia diretamente. As estratégias de
  filtro e de ordenação são testadas por `SearchCoffees`.
- Os testes nascem dos critérios de aceitação (DADO QUE / QUANDO / ENTÃO)
  e citam a issue no nome ou na docstring, por exemplo
  `test_create_review_rejects_second_review_same_coffee  # SCRUM-14`.
- **Módulos testados**:
  - `RegisterUser` e `AuthenticateUser` (SCRUM-11).
  - `GetCoffeeDetails` (SCRUM-12).
  - `SearchCoffees` com todos os filtros, as combinações E/OU, os casos de
    borda do termo e as três ordenações com desempates (SCRUM-13).
  - `CreateReview`, `UpdateReview`, `DeleteReview` e `ListUserReviews`
    (SCRUM-14).
  - `GetCoffeeRating` e CoffeeRating (SCRUM-19).
- **Casos de borda obrigatórios**:
  - termo com 1 caractere, termo vazio, termo só com espaços e termo com
    acentos;
  - nenhum resultado;
  - filtro de nota mínima excluindo os cafés sem avaliações;
  - empates em cada ordenação;
  - texto só com espaços e texto com 1000 e com 1001 caracteres;
  - nota 0 e nota 6;
  - e-mail com maiúsculas;
  - editar e excluir o review de outra pessoa;
  - a nota agregada recalculada depois de criar, editar e excluir.
- **Fakes**: um fake em memória por port (incluindo um hasher falso e um
  relógio fixo), substituíveis pelos repositórios SQLite (LSP). Eles ficam
  na pasta de fakes de teste e são reaproveitados por todos os testes de
  casos de uso.
- **Prior art**: ainda não há código nem testes no repositório. Esta spec
  define o padrão: os fakes e os primeiros testes de casos de uso servem
  de referência para os seguintes.
- Meta: cobertura de pelo menos 70% em `domain` e `use_cases`, que são as
  fontes configuradas no coverage.

## Out of Scope

- SCRUM-15 (amizades) e SCRUM-17 (comentar reviews). O SCRUM-17 é o
  candidato se sobrar tempo (ADR 0004).
- SCRUM-16 (perfil), SCRUM-18 (cadastro de café pelo usuário e
  moderação) e os épicos SCRUM-8, 9 e 10.
- Do SCRUM-11: confirmação de e-mail, recuperação de senha, login social,
  aceite dos Termos de Uso, "Manter conectado" e "Excluir conta".
- Do SCRUM-12: página de administração (o catálogo vem só do seed), selo
  "Verificado" (RoastDB) e URL amigável com pré-visualização.
- Do SCRUM-14: exibir o review no perfil (substituído por "Minhas
  avaliações").
- Meia estrela, nota de 0 a 10, mais de um review por usuário por café e
  histórico de versões de reviews.
- Paginação, busca palavra por palavra, busca por relevância e safra como
  atributo do café.
- Importação do RoastDB, HTTPS e CI/CD de homologação.
- Detalhes cosméticos (cores, tipografia, layout fino).

## Further Notes

- Vocabulário: o domínio usa **Review**, **Nota**, **Nota agregada**,
  **Altitude** e **Origem**, conforme o `GLOSSARY.md`. "Avaliação" e
  "avaliar" aparecem só nos textos da interface ("Avaliar", "12
  avaliações", "Sem avaliações", "Minhas avaliações").
- ADRs que regem esta spec: 0001 (nota inteira de 1 a 5), 0002 (um review
  por usuário por café), 0003 (identidade do café) e 0004 (recortes de
  escopo).
- O README deve citar onde cada princípio SOLID aparece. As estratégias de
  busca (OCP), os ports separados (ISP/DIP) e os fakes contra os
  repositórios SQLite (LSP) são os exemplos principais.
- A lista de países de origem é definida junto com o seed: entram só os
  países que aparecem no catálogo de demonstração.
