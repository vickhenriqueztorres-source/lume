# Legendador

> **Departamento:** 7 · Montagem & finalização · **Tipo:** ASR + LLM-R · **Nó:** `montagem.legendador` · **Doc-mãe:** [05 §3.7](../../05-arquitetura-agentes-langgraph.md) · **Tipografia:** [03 §4](../../03-identidade-visual-lume.md)

## Missão
Entregar **legendas** precisas em PT-BR (e opcionalmente ES/EN), sincronizadas com a voz, para acessibilidade e para quem assiste sem som.

## Posição no fluxo
- **Antes:** Finalizador.
- **Depois:** QA.

## Entradas
| Campo | Para quê |
|---|---|
| `master.arquivo` | Áudio final para alinhamento |
| `roteiro.blocos` (versão aprovada) | Texto correto (a transcrição só serve para o tempo) |
| `pesquisa.nomes_canonicos` | Grafia dos nomes |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `master.legendas` | SRT por idioma (caminho + hash), nº de legendas, taxa de leitura média |

## Regras de trabalho
1. **Texto vem do roteiro, tempo vem do áudio.** O ASR é usado para alinhar (alinhamento forçado), não para escrever. Onde a voz diverge do roteiro, vale o que foi **falado**, e a divergência é registrada para o QA de fidelidade.
2. **Máximo de 2 linhas e 38 caracteres por linha** (doc 03 §4).
3. **Quebra por sentido:** não separar artigo do substantivo nem nome e sobrenome.
4. **Taxa de leitura:** até 17 caracteres por segundo; duração mínima de 1 s por legenda.
5. **Silêncios dramáticos ficam sem legenda.** Sons importantes podem ser descritos entre colchetes (ex.: [o fogo apaga]).
6. **Tradução (ES/EN):** feita a partir do roteiro, com os nomes na forma corrente de cada idioma, e revisada contra a tabela de nomes.

## Critérios de aceite
- [ ] Nenhuma linha acima de 38 caracteres
- [ ] Nenhuma legenda com mais de 2 linhas
- [ ] Taxa de leitura ≤ 17 caracteres/s
- [ ] Nomes iguais aos da tabela

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Alinhamento falha num trecho | Realinha só o bloco; se falhar, usa o tempo da narração por bloco |

## Métricas
Correções de legenda feitas no Gate 3 · % de espectadores com legenda ativa (do Analista de desempenho).

## Não faz
Não altera o texto narrado e não decide o que é fato.
