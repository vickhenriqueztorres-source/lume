# QA de continuidade

> **Departamento:** 9 · QA · **Tipo:** LLM-V + regras · **Nó:** `qa.continuidade` · **Bloqueante** · **Doc-mãe:** [05 §3.9](../../05-arquitetura-agentes-langgraph.md)

## Missão
Conferir, no **episódio montado**, que as silhuetas, a direção de tela e o fogo são consistentes do primeiro ao último plano. É a visão de conjunto que o Revisor de plano (um plano por vez) não tem.

## Posição no fluxo
- **Antes:** Montagem.
- **Em paralelo:** os outros agentes de QA.
- **Depois:** reprovado → departamento responsável; aprovado → Gate 3.

## Entradas
| Campo | Para quê |
|---|---|
| `master.arquivo` + `timeline` | O episódio e o plano de cada trecho |
| `decupagem.planos` e `color_script` | O que foi planejado |
| Fichas das marionetes (`assets.indice`) | A silhueta correta |

## Saída
| Campo | Conteúdo |
|---|---|
| `qa` (append) | Relatório por checagem, com timecode, plano e departamento |

## Checagens
| Checagem | Critério | Volta para |
|---|---|---|
| Silhueta × ficha | Cada personagem igual à ficha em todos os planos (mesma versão de marionete) | Arte/Animação |
| Direção de tela | → casa / ← contra respeitado; exceções só onde a decupagem marcou | Direção/Animação |
| Fogo × color script | Nível de fogo do plano coerente com a cena (tolerância de 1 nível em transição) | Animação |
| Nível 5 | ≤ 2× no episódio | Direção |
| Cinza-alma | Só no mundo dos mortos e em flashbacks ≤ 3 s | Animação |
| Proporção | Letterbox de acordo com o plano | Montagem |
| Contador de perdas | Número na tela = número nos fatos | Montagem |
| Eixo entre cortes | Personagem não "pula" de lado entre planos consecutivos sem motivo | Direção |

## Regras de trabalho
1. **Amostragem por plano:** 1 quadro por plano + 3 em planos-chave (gancho, viradas, clímax).
2. **Comparação com a ficha, não com o plano anterior:** se dois planos estão iguais mas errados, os dois falham.

## Critérios de aceite
- [ ] 100% dos planos amostrados
- [ ] Zero falhas bloqueantes

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Erro sistemático (ex.: marionete `_v1` em vez de `_v2` em 30 planos) | Uma devolução só, com a lista, e sugestão de `/rerender` com filtro |

## Métricas
Falhas de continuidade por episódio · falhas que escaparam e foram apontadas no Gate 3.

## Não faz
Não avalia qualidade estética e não corrige planos.
