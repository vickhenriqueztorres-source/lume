# QA de originalidade

> **Departamento:** 9 · QA · **Tipo:** Ferr. + LLM-R · **Nó:** `qa.originalidade` · **Bloqueante** · **Doc-mãe:** [05 §3.9 e §7](../../05-arquitetura-agentes-langgraph.md)

## Missão
Provar que o episódio é **obra nova, com direção humana**, e não uma variação em massa de episódios anteriores. Protege o canal de ser tratado como conteúdo repetitivo.

## Posição no fluxo
- **Antes:** Montagem.
- **Em paralelo:** os outros agentes de QA.
- **Depois:** reprovado → departamento responsável; aprovado → Gate 3.

## Entradas
| Campo | Para quê |
|---|---|
| `roteiro.blocos` | Comparar com roteiros anteriores |
| `decupagem.planos` + hashes de render | Comparar com planos anteriores |
| `roteiro.esqueleto` | Comparar estruturas |
| `aprovacoes` | Conferir os registros dos gates humanos |
| Store: episódios anteriores | Base de comparação |

## Saída
| Campo | Conteúdo |
|---|---|
| `qa` (append) | Similaridade por dimensão, itens acima do limite e registros de gate faltando |

## Checagens
| Checagem | Critério (valor inicial, ajustável) |
|---|---|
| Roteiro | Similaridade de texto com qualquer episódio anterior abaixo de 15% (fora das frases rituais) |
| Estrutura | O esqueleto não é cópia de outro com nomes trocados |
| Planos reaproveitados | Render com hash idêntico a outro episódio: no máximo 5% dos planos, e só os rituais (Contador, abertura, end screen) |
| Assets | Reaproveitar marionetes é permitido e desejado; reaproveitar **planos prontos** não |
| Gates humanos | Gates 1 e 2 têm registro em `aprovacoes`, com quem, quando e o que mudou |

## Regras de trabalho
1. **Frases rituais não contam** (bordão de abertura e fechamento).
2. **Marionete ≠ plano:** a biblioteca existe para ser reaproveitada; o que não pode se repetir é o plano renderizado.
3. **Gate sem registro bloqueia:** a evidência de direção humana é obrigatória.

## Critérios de aceite
- [ ] Todas as dimensões abaixo dos limites
- [ ] Registros dos gates anteriores presentes

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Similaridade alta de roteiro | Volta para o Roteiro com os trechos |
| Planos reaproveitados demais | Volta para a Direção para decupar de novo os trechos |
| Gate sem registro | Bloqueia e avisa o Showrunner (pode ser falha de sistema) |

## Métricas
Similaridade média com o episódio mais próximo · % de planos reaproveitados.

## Não faz
Não julga qualidade e não compara com vídeos de outros canais (isso é do Analista de referência, na pesquisa).
