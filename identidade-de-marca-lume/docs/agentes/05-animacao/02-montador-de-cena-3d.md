# Montador de cena 3D

> **Departamento:** 5 · Animação & render · **Tipo:** Ferr. (Blender headless) · **Nó:** `animacao.montador_cena` · **Doc-mãe:** [05 §3.5](../../05-arquitetura-agentes-langgraph.md) · **Premissa técnica:** [04, introdução e §8](../../04-cinematografia.md)

## Missão
Aplicar os parâmetros do Animador no **template Blender** do Lume e entregar um arquivo de cena pronto para render, sem nenhuma decisão criativa.

## Posição no fluxo
- **Antes:** Animador de plano.
- **Depois:** Gerente de render. Roda por `Send`, um plano por vez.

## Entradas
| Campo | Para quê |
|---|---|
| `assets.planos[<id>].cena` | Parâmetros do plano |
| `assets.indice` | Caminhos dos rigs e das texturas |
| Template Blender (mantido pelo Técnico de Blender do Antigravity) | A cena-base |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `assets.planos[<id>].blend` | Caminho + hash do `.blend` do plano, versão do template usada, relatório de validação |

## O que o template contém (fixo)
| Elemento | Descrição |
|---|---|
| Fogueira | A única luz-chave, com intensidade e temperatura controladas pela curva do fogo |
| Parede | Plano com material de pedra (recebe a textura do Cenógrafo) |
| Névoa volumétrica | Entre o fogo e a parede, para o feixe de luz ser visível |
| Câmera | Lentes de 35–50 mm (parede) e 85–135 mm (Contador) |
| Slots de luz de deus | Desligados por padrão |
| Slots de marionete | Geometria plana a partir do SVG + rig |
| Saída | 3840×2160, 24p |

## Regras de trabalho
1. **Determinístico:** mesma entrada = mesmo `.blend`. Sem LLM, sem aleatoriedade fora de semente fixa.
2. **Sombras projetadas de verdade:** a marionete fica **entre a luz e a parede**; ninguém desenha sombra.
3. **Validação antes de entregar:**
   - Existe só uma luz-chave (a fogueira), mais as luzes de deus do contrato.
   - Toda marionete está entre o fogo e a parede (distância de 0 a 1).
   - A câmera não enquadra o topo do monstro em planos de tilt.
   - Render de **1 quadro de prévia em baixa resolução** sem erro.
4. **Versão do template** fica gravada; mudar o template invalida o cache dos planos afetados (doc 06, `/rerender`).

## Critérios de aceite
- [ ] Validação passou nos 4 itens
- [ ] Prévia gerada sem erro

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Asset não encontrado no storage | Retry 2×; depois, devolve ao Bibliotecário |
| Validação falha por parâmetro inválido | Devolve ao Animador com o motivo (conta como refação) |
| Erro do Blender | Retry 1×; depois, fila humana para o Técnico de Blender |

## Métricas
Tempo de montagem por plano · taxa de falha de validação.

## Não faz
Não renderiza a versão final e não interpreta o contrato.
