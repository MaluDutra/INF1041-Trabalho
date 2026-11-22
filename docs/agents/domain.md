# Documentação de domínio

Como as skills de engenharia devem usar a documentação de domínio deste
repositório ao explorar o código.

Layout: **single-context** (um único `GLOSSARY.md` e `docs/adr/` na raiz).

## Antes de explorar, leia

- **`GLOSSARY.md`** na raiz do repositório.
- **`docs/adr/`**: leia os ADRs que tratam da área em que você vai mexer.

Se algum desses arquivos não existir, **siga em frente sem comentar**. Não
aponte a ausência nem sugira criá-los antecipadamente. A skill
`/domain-modeling` (acionada por `/grill-with-docs`) cria esses arquivos sob
demanda, quando termos ou decisões forem de fato definidos.

## Estrutura de arquivos

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── 0001-sqlite-como-persistencia.md
│   └── 0002-escala-de-nota-1-a-5.md
├── domain/
├── use_cases/
├── infra/
└── app/
```

## Use o vocabulário do glossário

Quando sua saída citar um conceito do domínio (título de issue, proposta de
refatoração, hipótese, nome de teste), use o termo como está definido em
`GLOSSARY.md`. Não troque por sinônimos que o glossário evita.

Se o conceito de que você precisa ainda não está no glossário, isso é um
sinal: ou você está inventando uma linguagem que o projeto não usa
(reconsidere), ou existe uma lacuna real (anote para o `/domain-modeling`).

## Aponte conflitos com ADRs

Se a sua saída contradiz um ADR existente, diga isso explicitamente em vez
de sobrescrever a decisão em silêncio:

> _Contradiz o ADR-0002 (escala de nota de 1 a 5), mas vale reabrir
> porque…_
