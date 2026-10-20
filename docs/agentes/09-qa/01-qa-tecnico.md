# QA técnico

> **Departamento:** 9 · QA · **Tipo:** Ferr. (+ LLM-V para casos duvidosos) · **Nó:** `qa.tecnico` · **Bloqueante** · **Doc-mãe:** [05 §3.9](../../05-arquitetura-agentes-langgraph.md)

## Missão
Garantir que o master **funciona tecnicamente** no YouTube e em qualquer tela: resolução, quadros, áudio e sincronia.

## Posição no fluxo
- **Antes:** Montagem (master + legendas).
- **Em paralelo:** os outros 5 agentes de QA (por `Send`).
- **Depois:** reprovado → `Command(goto=…)` para o departamento exato; todos aprovados → Gate 3.

## Entradas
| Campo | Para quê |
|---|---|
| `master.arquivo`, `master.legendas` | O que conferir |
| `audio.lufs` | Comparar o medido no mix com o medido no master |
| `timeline` | Achar o plano de origem de cada defeito |

## Saída
| Campo | Conteúdo |
|---|---|
| `qa` (append) | Relatório: checagem, resultado, timecode, plano de origem, departamento responsável, bloqueante |

## Checagens
| Checagem | Critério | Volta para |
|---|---|---|
| Resolução e fps | 3840×2160, 24p | Montagem |
| Quadros pretos | Nenhum fora das transições previstas | Montagem |
| Quadros congelados | Nenhum plano parado > 0,5 s sem intenção | Animação/Montagem |
| Ocupantes | Nenhum storyboard sobrando na timeline | Animação |
| Loudness | −14 LUFS ±1, true peak ≤ −1 dBTP | Áudio |
| Sincronia | Voz × legenda ≤ 100 ms; corte × volta do som no silêncio ≤ 2 quadros | Montagem |
| Clipping | Nenhum | Áudio |
| Legendas | Arquivo válido, sem sobreposição, ≤ 38 caracteres/linha | Montagem |
| Duração | Dentro de ±5% da duração-alvo | Montagem |

## Regras de trabalho
1. **Cada falha aponta o departamento e o plano/bloco**, para o retrabalho ser cirúrgico.
2. **Medições determinísticas.** O LLM-V só entra para decidir se um quadro preto ou parado é intenção (ex.: o silêncio antes da revelação).

## Critérios de aceite
- [ ] Todas as checagens com resultado
- [ ] Zero falhas bloqueantes

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Mesma falha voltando 2× | O Showrunner escala para humano |

## Métricas
Falhas por episódio, por tipo · tempo de QA.

## Não faz
Não corrige nada: só mede e aponta.
