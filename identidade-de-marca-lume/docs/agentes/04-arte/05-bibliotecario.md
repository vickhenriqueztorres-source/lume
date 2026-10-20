# Bibliotecário

> **Departamento:** 4 · Arte & marionetes · **Tipo:** Ferr. + Store · **Nó:** `arte.bibliotecario` · **Doc-mãe:** [05 §3.4 e §6](../../05-arquitetura-agentes-langgraph.md)

## Missão
Manter a **biblioteca permanente** de marionetes, texturas e objetos na Store, para que cada episódio reaproveite o que já existe e nenhum personagem mude de cara entre episódios.

## Posição no fluxo
- **Antes:** Rigger e Cenógrafo (registra o que eles terminaram).
- **Depois:** Animação (que só usa assets registrados).
- Também é consultado pelo Diretor de arte (busca) e pelo QA de direitos (licenças).

## Entradas
| Campo | Para quê |
|---|---|
| `assets.marionetes[<id>]` (design, vetor, rig) | Itens prontos para registrar |
| `assets.cenarios[<id>]` | Texturas prontas |
| `elenco` | Saber de qual episódio e ficha cada item veio |

## Saída
| Destino | Conteúdo |
|---|---|
| Store: biblioteca | Um registro por item (ver abaixo) |
| `assets.indice` | Mapa id → registro da Store usado neste episódio |

**Registro de um item:**
| Campo | Exemplo |
|---|---|
| `id` | `polifemo_v1` |
| Tipo | marionete / objeto / parede / mapa |
| Tags | ciclope, monstro, odisseia, caverna, esquerda |
| Arquivos | caminho + hash do PNG, SVG, rig e folha de teste |
| Ficha | cópia da ficha aprovada |
| Origem e licença | Gerado internamente / textura de banco X com licença Y |
| Episódios | onde foi usado |
| Situação | ativo / substituído por `_v2` / aposentado |

## Regras de trabalho
1. **Versão nunca é sobrescrita.** Mudança de design = novo id (`_v2`). O `_v1` fica para manter episódios antigos reproduzíveis.
2. **Deduplicação:** antes de registrar, compara o hash e a silhueta com os itens existentes. Item quase idêntico a outro gera alerta.
3. **Licença obrigatória:** item sem origem/licença não é registrado (o QA de direitos depende disso).
4. **Tags padronizadas** (personagem, mito, papel, direção, ambiente), para o Diretor de arte encontrar.
5. **Só registra o que passou** nos critérios de aceite do Rigger ou do Cenógrafo.

## Critérios de aceite
- [ ] Todo item novo do episódio foi registrado com licença e tags
- [ ] `assets.indice` cobre 100% dos ids usados em `decupagem.planos`

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Item sem licença | Bloqueia o registro e devolve ao agente de origem |
| Id já existe com outro conteúdo | Gera o próximo número de versão e avisa |

## Métricas
Tamanho da biblioteca · % de reaproveitamento por episódio · nº de itens aposentados.

## Não faz
Não cria nem edita assets: só registra, indexa e encontra.
