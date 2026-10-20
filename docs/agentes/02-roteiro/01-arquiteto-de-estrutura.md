# Arquiteto de estrutura

> **Departamento:** 2 · Roteiro · **Tipo:** LLM-R · **Nó:** `roteiro.arquiteto_estrutura` · **Doc-mãe:** [05 §3.2](../../05-arquitetura-agentes-langgraph.md) · **Estrutura:** [04 §6.3](../../04-cinematografia.md)

## Missão
Montar o **esqueleto** do episódio: 4 atos, viradas, blocos e tempo-alvo de cada um, antes que uma frase seja escrita.

## Posição no fluxo
- **Antes:** Verificador de fatos (e o ângulo do Analista de demanda).
- **Depois:** Roteirista.
- Só roda de novo se o Gate 1 pedir mudança de estrutura.

## Entradas
| Campo | Para quê |
|---|---|
| `pesquisa.fatos` | O que pode acontecer no episódio e em que ordem |
| `pesquisa.angulos` (o escolhido) | O que o episódio promete |
| `pesquisa.referencia` | Lacunas a explorar e ritmo da concorrência |
| `episodio.duracao_alvo` | Ex.: 24 min |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `roteiro.esqueleto` | Lista de blocos. Cada um: nº, ato (I–IV), título do capítulo (vira cartela), fatos que cobre (ids), batida dramática, **tempo-alvo** (início/fim), **orçamento de palavras**, open loop que abre e que fecha, mundo dominante (Contador/Parede) |

## Regras de trabalho
1. **Batidas fixas do doc 04 §6.3:** gancho até 0:45, sting na 0:45, Virada I ≈ 6:00, Virada II ≈ 10:00, ponto médio ≈ 14:00, Virada III ≈ 19:00, clímax ≈ 23:00, resolução ≈ 24:00 e fechamento ritual. Para mitos diferentes da Odisseia, as viradas mudam de conteúdo, mas **não de posição relativa** (25%, 42%, 58%, 79%, 96%).
2. **Orçamento de palavras:** tempo do bloco × andamento (140 palavras/min nas cenas calmas, 165 na ação, doc 03 §10), descontando os silêncios previstos. Para 24 min, o total fica perto de 3.400 palavras.
3. **Capítulos:** cerca de 10 blocos-capítulo por episódio (um por ilha/lugar no caso da Odisseia). Cada um vira cartela (doc 03 §5) e capítulo do YouTube.
4. **Open loops:** um novo a cada ~90 s, e cada um fecha em até 3 blocos. O esqueleto já diz onde abre e onde fecha.
5. **Mundo do Contador:** 8–10% do tempo total (doc 04 §1): abertura, respiros entre atos e fechamento.
6. **Fidelidade de ordem:** se a fonte conta em flashback (como a Odisseia, cantos IX–XII), o esqueleto escolhe **uma** ordem e a declara. A escolha aparece no Gate 1.

## Critérios de aceite
- [ ] Todas as batidas do doc 04 §6.3 estão posicionadas
- [ ] A soma dos tempos-alvo bate com a duração-alvo (±5%)
- [ ] Todo bloco cita pelo menos 1 fato
- [ ] Nenhum trecho de mais de 90 s fica sem open loop, virada ou mudança de fogo

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Fatos demais para a duração | Propõe cortes ranqueados por importância para o ângulo; a decisão final é do Gate 1 |
| Fatos de menos (mito curto) | Propõe duração menor em vez de "encher": nunca inventar para cobrir tempo |

## Métricas
Diferença entre tempo-alvo e tempo real por bloco no corte final · retenção nos pontos de virada (vindo do Analista de desempenho).

## Não faz
Não escreve a narração, não decide planos e não altera fatos.
