# Supervisor de direção de tela

> **Departamento:** 3 · Direção · **Tipo:** LLM-R (regras) · **Nó:** `direcao.supervisor_direcao_tela` · **Doc-mãe:** [05 §3.3](../../05-arquitetura-agentes-langgraph.md) · **Regra:** [04 §4](../../04-cinematografia.md) · **Fichas:** [03 §6.2](../../03-identidade-visual-lume.md)

## Missão
Garantir que **a direção de cada sombra na tela significa algo**: → é casa, ← é contra. É a regra que, segundo o doc 04, "transforma tudo".

## Posição no fluxo
- **Antes:** Diretor de fotografia.
- **Depois:** Diretor de arte.

## Entradas
| Campo | Para quê |
|---|---|
| `decupagem.planos` | Direção de cada marionete e movimento de câmera |
| `roteiro.blocos` | Saber quando o herói erra (a exceção da regra) |
| Fichas de silhueta | Direção padrão de cada personagem (doc 03 §6.2) |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `decupagem.correcoes_direcao` | Por plano corrigido: campo, valor antigo, valor novo, regra aplicada |
| | Os planos corrigidos recebem a nova `direcao` diretamente em `decupagem.planos` |

## Regras de trabalho
**A parte determinística (sem LLM) confere:**
1. Odisseu e aliados → **direita**; deuses contrários e monstros → **esquerda** (tabela do doc 03 §6.2).
2. Dolly lateral sempre no sentido da direção de tela do personagem principal do plano.
3. A rota no mapa respeita a regra: desvio para a esquerda = castigo.
4. Consistência entre planos consecutivos (sem inverter um personagem de um corte para o outro sem motivo).

**A parte com LLM decide as exceções:**
5. Odisseu olha para a **esquerda** só quando **erra** (ex.: grita o próprio nome para Polifemo; os homens abrem o saco de ventos). O LLM lê o roteiro e confirma se o plano é um desses momentos.
6. **Frontalidade** só no reencontro final com Penélope (doc 04 §4).

## Critérios de aceite
- [ ] 100% dos planos obedecem à regra ou têm exceção justificada pelo roteiro
- [ ] Toda exceção cita o trecho do roteiro que a justifica
- [ ] Frontalidade do herói aparece só uma vez

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Personagem novo sem direção na ficha | Pede ao Diretor de arte para definir na ficha (aliado → direita, contrário → esquerda, neutro → de frente para o objeto) |
| Exceção ambígua | Mantém a regra padrão e marca o plano para o Gate 2 |

## Métricas
Nº de correções por episódio (deve cair com o tempo, porque o Diretor aprende pelas lições) · falhas de direção encontradas depois no QA de continuidade.

## Não faz
Não muda tipo de plano, duração ou luz. Só a direção.
