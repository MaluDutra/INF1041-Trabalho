# 04: Login com e-mail e senha e retorno ao destino

**Status:** ready-for-agent

**Jira:** SCRUM-11
**Histórias da spec:** 8, 9 e a base das histórias 55, 56 e 61

**O que construir:** o usuário entra com e-mail e senha. Se errar
qualquer um dos dois, vê a mesma mensagem genérica, que não revela qual
deles falhou. O login e o cadastro aceitam um parâmetro `next` e, depois
de entrar, levam o usuário de volta à página de onde ele veio. Esse
mecanismo é a base do "Avaliar" sem login (ticket 05) e de "Minhas
avaliações" (ticket 08).

- Caso de uso `AuthenticateUser`: normaliza o e-mail e devolve o usuário,
  ou lança "credenciais inválidas", com a mesma exceção para e-mail
  inexistente e para senha errada.
- App: formulário de login, sessão com só o id do usuário e uma forma
  reaproveitável de marcar uma rota como "exige login", que redireciona
  para o login com `next` igual ao caminho pedido.
- O `next` só é aceito se for um caminho relativo interno. Qualquer outro
  valor é ignorado e o usuário vai para a página inicial (proteção contra
  redirecionamento aberto).
- O link "Criar conta" da página de login preserva o `next`, e o
  cadastro também redireciona para ele.

**Bloqueado por:** 03 (Cadastro com login automático e logout).

**Critérios de aceite:**

- [ ] DADO QUE o usuário existe, QUANDO ele entra com o e-mail certo
      (mesmo com maiúsculas ou espaços nas pontas) e a senha certa, ENTÃO
      fica logado e o cabeçalho mostra o nome de exibição.
- [ ] DADO QUE o e-mail não existe ou a senha está errada, QUANDO o
      usuário tenta entrar, ENTÃO vê a mesma mensagem genérica nos dois
      casos, e o e-mail digitado continua no formulário.
- [ ] DADO QUE o endereço é `/login?next=<caminho de um café>`, QUANDO o
      login dá certo, ENTÃO o usuário volta para a página desse café.
- [ ] DADO QUE o `next` é uma URL externa (por exemplo,
      `https://exemplo.com` ou `//exemplo.com`), QUANDO o login dá certo,
      ENTÃO o usuário vai para a página inicial.
- [ ] DADO QUE o usuário está no login com um `next`, QUANDO segue o link
      "Criar conta" e se cadastra, ENTÃO volta para o mesmo `next`.
- [ ] Testes de `AuthenticateUser`, citando SCRUM-11, só com fakes: login
      válido, senha errada, e-mail inexistente (a mesma exceção) e e-mail
      com maiúsculas.
- [ ] A validação do `next` foi verificada manualmente (ela fica na
      camada de app, fora do seam dos testes) e o passo a passo está
      registrado em `## Comments`.
- [ ] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.

**Fora deste ticket:** login social e recuperação de senha (ADR 0004).
