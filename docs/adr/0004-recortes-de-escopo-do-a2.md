# Recortes de escopo do A2

O A2 implementa SCRUM-11, 12, 13, 14 e 19. Para caber no prazo e manter o
foco na arquitetura, cortamos de propósito alguns itens que constam nessas
histórias no Jira. Este ADR existe para que ninguém "corrija" essas
ausências achando que foram esquecidas.

- **SCRUM-15 (amizades) e SCRUM-17 (comentar reviews): fora.** Cinco
  histórias já passam do mínimo de 4 exigido. Se sobrar tempo, o SCRUM-17 é
  o candidato natural.
- **SCRUM-11**: sem confirmação de e-mail, recuperação de senha, login
  social, aceite dos Termos de Uso, "Manter conectado" e "Excluir conta".
  Como não há confirmação de e-mail, o usuário **entra automaticamente logo
  após o cadastro**.
- **SCRUM-12**: sem página de administração (o catálogo vem só do seed), sem
  selo "Verificado" (depende do RoastDB) e sem URL amigável com
  pré-visualização.
- **SCRUM-14**: o review não aparece num perfil (SCRUM-16 está fora). Em
  vez disso, o usuário logado tem a página "Minhas avaliações".
