# Curador de memória

> **Departamento:** 10 · Publicação & aprendizado · **Tipo:** LLM-R + Store · **Nó:** `publicacao.curador_memoria` · **Doc-mãe:** [05 §3.10 e §6](../../05-arquitetura-agentes-langgraph.md)

## Missão
Transformar os achados do episódio em **lições curtas e acionáveis** na Store, para que o Showrunner as injete nos agentes certos do próximo episódio.

## Posição no fluxo
- **Antes:** Analista de desempenho (relatório de 7 dias).
- **Depois:** fim do episódio (`encerrado`). As lições são lidas pelo Showrunner no **próximo** episódio.
- Também recebe sinais do QA (avisos repetidos) e dos gates (edições humanas recorrentes).

## Entradas
| Fonte | Para quê |
|---|---|
| Relatório do Analista de desempenho | Achados de retenção e CTR |
| `qa` | Falhas e avisos repetidos |
| `aprovacoes` | O que os humanos mudaram em cada gate (o sinal mais forte) |
| `erros` | Falhas recorrentes |
| Store: lições existentes | Evitar duplicar, reforçar ou derrubar lições |

## Saída
| Destino | Conteúdo |
|---|---|
| Store: lições | Uma lição por registro (ver abaixo) |

**Registro de uma lição:**
| Campo | Exemplo |
|---|---|
| Texto | "Fora da caverna e do mundo dos mortos, plano fixo acima de 10 s derruba retenção. Use push-in." |
| Agente(s) alvo | `direcao.diretor`, `animacao.animador` |
| Escopo | Todos os mitos / só Odisseia / só tipo de plano X |
| Evidência | Episódios, timecodes e métricas que sustentam |
| Confiança | baixa (1 episódio) / média (2) / alta (3+ ou decisão humana explícita) |
| Origem | dado de audiência / QA / gate humano |
| Situação | ativa / em observação / aposentada |

## Regras de trabalho
1. **Uma lição = uma regra acionável** para um agente. "O episódio foi bem" não é lição.
2. **Confiança cresce com repetição:** a lição nasce em "baixa" e sobe quando o padrão se repete. O Showrunner trata lições de confiança baixa como observação.
3. **Decisão humana vale mais:** edição recorrente num gate (ex.: o humano sempre corta a mesma expressão) entra direto com confiança alta.
4. **Nunca contradizer os docs 03–05.** Se um dado sugerir quebrar uma regra da marca, a lição vira **proposta de mudança de doc** para o humano, não regra para o agente.
5. **Aposentar:** lição que não se confirma em 3 episódios é aposentada.
6. **Lições viram casos de teste:** cada lição de confiança alta é repassada ao Engenheiro de prompts (Antigravity) como caso de teste do agente alvo.

## Critérios de aceite
- [ ] Todo achado do Analista foi avaliado (virou lição, reforçou uma existente ou foi descartado com motivo)
- [ ] Nenhuma lição duplicada
- [ ] Nenhuma lição contradiz os docs 03–05

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Duas lições se contradizem | Mantém a de maior confiança e coloca a outra em observação |
| Lição sugere mudar a marca | Proposta para o humano, fora da Store |

## Métricas
Nº de lições ativas · % de lições que melhoraram a métrica-alvo no episódio seguinte · lições aposentadas.

## Não faz
Não altera prompts nem docs diretamente e não decide roteamento (é o Showrunner).
