# DAG das issues: Cafeteca MVP (A2)

Uma aresta `A --> B` significa que A bloqueia B. Os nós em destaque estão
na fronteira (sem bloqueios em aberto) e podem começar já.

O grafo é acíclico: toda aresta vai de uma issue de número menor para uma
de número maior, e a ordenação topológica foi conferida com
`graphlib.TopologicalSorter` a partir do "Bloqueado por" de cada arquivo.

```mermaid
graph TD
    I01["01 Esqueleto: catálogo na página inicial"]
    I02["02 Página do café"]
    I03["03 Cadastro com login automático"]
    I04["04 Login e retorno ao destino"]
    I05["05 Avaliar café e ver reviews"]
    I06["06 Nota agregada e histograma"]
    I07["07 Editar e excluir review"]
    I08["08 Minhas avaliações"]
    I09["09 Busca por termo"]
    I10["10 Ordenações e nota nos cards"]
    I11["11 Filtros do catálogo"]
    I12["12 Filtro de nota mínima"]
    I13["13 Seed de usuários e reviews"]
    I14["14 README: SOLID e uso de IA"]

    I01 --> I02
    I01 --> I03
    I03 --> I04
    I02 --> I05
    I04 --> I05
    I05 --> I06
    I06 --> I07
    I07 --> I08
    I02 --> I09
    I06 --> I10
    I09 --> I10
    I10 --> I11
    I11 --> I12
    I05 --> I13
    I08 --> I14
    I12 --> I14
    I13 --> I14

    classDef frontier fill:#d1fae5,stroke:#047857,stroke-width:3px,color:#064e3b
    class I01 frontier
```

## Ondas de trabalho (enquanto a fronteira avança)

| Onda | Issues que podem rodar em paralelo |
| --- | --- |
| 1 | 01 |
| 2 | 02, 03 |
| 3 | 04, 09 |
| 4 | 05 |
| 5 | 06, 13 |
| 6 | 07, 10 |
| 7 | 08, 11 |
| 8 | 12 |
| 9 | 14 |
