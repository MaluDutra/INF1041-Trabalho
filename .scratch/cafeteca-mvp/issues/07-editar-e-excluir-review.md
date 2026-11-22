# 07: Editar e excluir o próprio review

**Status:** done

**Jira:** SCRUM-14, SCRUM-19
**Histórias da spec:** 49 (botão de edição), 51 a 54 e 67 (edição e
exclusão)

**O que construir:** na página do café, "Editar minha avaliação" abre o
formulário já preenchido com a nota e o texto do review. Ao salvar, o
review mantém a data original e ganha o selo "editado". O autor também
pode excluir o review, depois de confirmar que a exclusão é definitiva.
Só o autor edita ou exclui. A nota agregada e o histograma refletem a
mudança na hora.

- Domínio: editar um Review troca a nota e o texto (com as mesmas
  validações da criação), mantém a data de criação e liga o marcador de
  editado. Não há histórico de versões.
- Casos de uso `UpdateReview` e `DeleteReview`: o review precisa existir
  (senão "não encontrado") e quem pede precisa ser o autor (senão
  "permissão negada").
- App: formulário de edição, confirmação antes do POST de exclusão,
  selo "editado" no presenter e tradução de "permissão negada" em 403 e
  de "não encontrado" em 404.

**Bloqueado por:** 06 (Nota agregada e histograma).

**Critérios de aceite:**

- [x] DADO QUE o usuário tem um review com nota 3, QUANDO o edita para
      nota 5 com texto novo, ENTÃO a lista mostra a nota 5, o texto novo,
      a data original e o selo "editado".
- [x] A edição recusa nota fora de 1 a 5 e texto com mais de 1000
      caracteres, com a mesma mensagem da criação. Um texto só com
      espaços vira "sem texto".
- [x] DADO QUE o usuário clica em "Excluir", QUANDO confirma, ENTÃO o
      review some da lista e o botão volta a ser "Avaliar". Se cancelar,
      nada muda.
- [x] DADO QUE o review é de outra pessoa, QUANDO alguém tenta editá-lo
      ou excluí-lo (por exemplo, forjando o POST), ENTÃO recebe 403 e o
      review não muda.
- [x] Editar ou excluir um review inexistente responde 404.
- [x] DADO QUE o café tem as notas [5, 3], QUANDO o 3 é editado para 5,
      ENTÃO a nota agregada passa de "4,0" para "5,0". QUANDO um dos
      reviews é excluído, ENTÃO a quantidade cai para 1 e o histograma
      acompanha.
- [x] Testes de `UpdateReview` e `DeleteReview`, citando SCRUM-14, só com
      fakes: edição válida, data mantida, marcador ligado, edição
      inválida, review de outra pessoa (editar e excluir), review
      inexistente e nota agregada recalculada depois de editar e de
      excluir (citando também SCRUM-19).
- [x] `ruff check .`, `ruff format --check .`, `lint-imports` e `pytest`
      passam.
