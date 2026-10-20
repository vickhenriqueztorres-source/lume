# VFX

> **Departamento:** 5 · Animação & render · **Tipo:** Ferr. (templates) · **Nó:** `animacao.vfx` · **Doc-mãe:** [05 §3.5](../../05-arquitetura-agentes-langgraph.md) · **Acabamento:** [04 §1 e §8](../../04-cinematografia.md)

## Missão
Produzir as **camadas de primeiro plano** (brasas, fumaça, cinzas) e os **planos do Mundo do Contador**, que dão profundidade e fazem a passagem entre os dois mundos.

## Posição no fluxo
- **Antes:** Revisor de plano (planos de parede aprovados) e Gate 2 (planos do Contador decupados).
- **Depois:** Editor (Montagem). Roda por `Send`, um plano por vez.

## Entradas
| Campo | Para quê |
|---|---|
| Contrato do plano | `mundo`, `transicao_saida`, nível de fogo, câmera |
| `assets.planos[<id>].render` | Para planos de parede, a base onde a camada vai por cima |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `assets.planos[<id>].vfx` | Camadas com alfa (caminho + hash): brasas, fumaça, cinzas |
| | Para `mundo = contador`: o plano completo do Contador |

## Templates
| Template | Uso |
|---|---|
| **Brasas e cinzas** | Partículas cruzando o primeiro plano, em profundidade de campo rasa; densidade sobe com o nível de fogo |
| **Fumaça** | Transição "fumaça cobre a lente" (doc 04 §1, transição 3) e entrada/saída de lower thirds |
| **Faísca** | Transição 2: brasa sobe em close e vira estrela, tocha ou olho (match cut) |
| **Contador** | Encapuzado de perfil ou de costas, mão ao fogo, ruínas ao redor; lente longa, câmera na mão sutil |
| **Mão-deus** | Transição 4: a mão do Contador entra no feixe e a sombra da mão vira deus |
| **Push-in no ombro** | Transição 1: entrar na parede |

## Regras de trabalho
1. **Partículas com física**, nunca "glow" digital nem lens flare genérico (doc 03 §12).
2. **O rosto do Contador nunca aparece:** só capuz, mãos e silhueta.
3. **Contador a 24 qps** com câmera na mão sutil (respiração). O gate weave é do Finalizador, não do VFX.
4. **Cama visual do Contador:** fogo, ruínas e busto de mármore em meia-luz, sem elementos de outras épocas.
5. **No mundo dos mortos**, as brasas ficam em Cinza-alma (doc 03 §3.3).

## Critérios de aceite
- [ ] Toda transição-assinatura pedida no contrato foi gerada
- [ ] Todo plano do Contador está sem rosto visível
- [ ] Camadas com alfa limpo (sem borda escura)

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Template falha no render | Retry 2× pelo Gerente de render; depois, fila humana para o Engenheiro de motion/Técnico de Blender |

## Métricas
Nº de planos do Contador reaproveitados entre episódios · notas de "glow digital" no QA de marca.

## Não faz
Não faz grafismo de texto (cartela, lower third, mapa: é o Grafismo) e não faz grão/halation (é o Finalizador).
