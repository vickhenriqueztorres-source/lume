# Gerente de render

> **Departamento:** 5 · Animação & render · **Tipo:** Ferr. · **Nó:** `animacao.gerente_render` · **Doc-mãe:** [05 §3.5 e §6](../../05-arquitetura-agentes-langgraph.md) · **Implantação:** [06 §2](../../06-automacao-langgraph-antigravity.md)

## Missão
Levar cada `.blend` até um vídeo pronto: enviar para a fila de GPU, priorizar, aproveitar o cache, reenviar em falha e **retomar o grafo** quando terminar, sem deixar nenhum worker parado esperando.

## Posição no fluxo
- **Antes:** Montador de cena 3D.
- **Depois:** Revisor de plano (quando o webhook do worker retoma o grafo).

## Entradas
| Campo | Para quê |
|---|---|
| `assets.planos[<id>].blend` | O que renderizar |
| Hash dos campos visuais do plano | Cache |
| `episodio.rota` / prioridade do Showrunner | Ordem da fila |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `assets.planos[<id>].render` | `caminho`, `hash`, `status` (`na_fila` / `renderizando` / `pronto` / `falhou` / `cache`), `tentativas`, segundos de GPU |
| `custos` (append) | Segundos de GPU e custo por plano |

## Regras de trabalho
1. **Jobs longos fora do grafo** (doc 05 §6): o nó envia o job, grava a chave de operação e **encerra**. O worker chama o webhook ao terminar, e o grafo é retomado com `resume`.
2. **Cache por hash:** se o hash do plano é igual ao de um render aprovado, marca `cache` e não renderiza.
3. **Prioridade:** gancho e viradas primeiro (decisão do Showrunner); depois, ordem cronológica.
4. **Limite de concorrência** configurável, para respeitar o teto de custo e o número de GPUs.
5. **Retry automático** em falha de infraestrutura (worker caiu, timeout): até 3×, com espera crescente. Falha de conteúdo (erro na cena) não é retry: volta para o Montador.
6. **Idempotência:** ao ser retomado, confere a chave de operação para não mandar o mesmo job duas vezes.
7. **Saída do render:** vídeo do plano em formato intermediário de alta qualidade, com alfa quando o plano tem camadas.

## Critérios de aceite
- [ ] Todo plano termina em `pronto` ou `cache`, ou em `falhou` com motivo
- [ ] Nenhum job duplicado
- [ ] Custo registrado por plano

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Webhook nunca chega | Timeout configurável → consulta o status do job; se estiver perdido, reenvia |
| Fila parada (todos os workers fora) | Alerta ao Showrunner e à fila humana |
| Custo projetado passa do teto | Avisa o Showrunner antes de enviar mais jobs |

## Métricas
Tempo de fila · segundos de GPU por plano · % de acerto do cache · taxa de falha de infraestrutura.

## Não faz
Não julga a qualidade do render (é o Revisor) e não edita a cena.
