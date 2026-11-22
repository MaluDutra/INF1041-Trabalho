# 03: Cadastro com login automático e logout

**Status:** ready-for-agent

**Jira:** SCRUM-11
**Histórias da spec:** 1 a 7, 10, 11 e 12

**O que construir:** o visitante cria uma conta com nome de exibição,
e-mail e senha e já entra logado. O cabeçalho passa a mostrar o nome de
exibição e o botão "Sair", que encerra a sessão. Erros de cadastro
aparecem como mensagens claras em português no próprio formulário.

- Domínio: a entidade Usuário. O nome de exibição tem de 2 a 40
  caracteres depois de tirar os espaços das pontas e não precisa ser
  único. O e-mail é único e é guardado e comparado em minúsculas, sem
  espaços nas pontas. A regra da senha (mínimo de 8 caracteres, com pelo
  menos uma letra e um número) é do domínio e é validada sobre a senha em
  texto antes do hash. A entidade guarda só o hash.
- Ports separados (ISP): repositório de usuários e hasher de senha. Os
  dois ganham fakes em memória (o hasher falso é determinístico).
- Caso de uso `RegisterUser`: valida, rejeita e-mail duplicado com erro
  de conflito, gera o hash, grava e devolve o usuário criado.
- Infra: tabela de usuários com e-mail único já normalizado, repositório
  SQLite e hasher com `werkzeug.security`.
- App: formulário de cadastro, sessão do Flask com só o id do usuário,
  login automático com o resultado do `RegisterUser` e logout.

**Bloqueado por:** 01 (Esqueleto: catálogo na página inicial).

**Critérios de aceite:**

- [ ] DADO QUE os dados são válidos, QUANDO o visitante se cadastra,
      ENTÃO a conta é criada e ele já está logado: o cabeçalho mostra o
      nome de exibição e "Sair".
- [ ] DADO QUE "ana@x.com" já está cadastrado, QUANDO alguém se cadastra
      com " Ana@X.com ", ENTÃO vê a mensagem de que o e-mail já está
      cadastrado, com um link para o login, e nenhuma conta nova é
      criada.
- [ ] "abc1234" (7 caracteres), "abcdefgh" (sem número) e "12345678" (sem
      letra) são recusadas com uma mensagem que explica a regra.
      "abcd1234" é aceita.
- [ ] Um nome de exibição com 1 caractere ou com 41 caracteres (depois de
      tirar os espaços das pontas) é recusado com mensagem. "  Ana  " é
      gravado como "Ana".
- [ ] Dois usuários podem ter o mesmo nome de exibição.
- [ ] O banco guarda só o hash da senha. Nenhum caminho do código grava a
      senha em texto.
- [ ] Depois de um erro, o formulário mantém o nome e o e-mail
      preenchidos, nunca a senha.
- [ ] O e-mail não aparece em nenhuma página pública. O cabeçalho mostra
      só o nome de exibição.
- [ ] "Sair" limpa a sessão e volta para a página inicial.
- [ ] Testes de `RegisterUser` e das invariantes do Usuário, citando
      SCRUM-11, só com fakes: cadastro válido, e-mail duplicado, e-mail
      com maiúsculas, cada regra da senha e os limites do nome.
- [ ] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.

**Fora deste ticket:** login com e-mail e senha e o parâmetro `next`
(ticket 04). Confirmação de e-mail, recuperação de senha, "Manter
conectado" e "Excluir conta" estão fora do escopo (ADR 0004).
