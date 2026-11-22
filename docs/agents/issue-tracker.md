# Issue tracker: Markdown local

As specs e as issues deste repositório ficam em arquivos markdown dentro de
`.scratch/`. **Não** use o GitHub Issues nem o `gh`, mesmo que o `git remote`
aponte para o GitHub.

## Convenções

- Uma feature por diretório: `.scratch/<feature-slug>/`
- A spec fica em `.scratch/<feature-slug>/spec.md`
- Cada issue de implementação é um arquivo próprio em
  `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numerado a partir de `01`.
  Nunca junte várias issues em um único arquivo.
- O estado da issue fica em uma linha `Status:` perto do topo do arquivo:
  - `ready-for-agent`: issue especificada e pronta para implementar (é o
    valor que `/to-spec` e `/to-tickets` gravam ao criar a issue);
  - `done`: issue concluída (veja "Como fechar uma issue").
- Comentários e histórico de conversa vão no fim do arquivo, sob o título
  `## Comments`.

## Quando uma skill disser "publique no issue tracker"

Crie um arquivo novo em `.scratch/<feature-slug>/`, criando o diretório se
ele ainda não existir.

## Quando uma skill disser "busque a issue"

Leia o arquivo no caminho indicado. Normalmente o usuário passa o caminho ou
o número da issue diretamente.

## Como fechar uma issue

Ao concluir uma issue:

1. Marque todos os critérios de aceite com `[x]` (troque `- [ ]` por
   `- [x]`).
2. Troque a linha `Status:` para `done`.
