# Rigger

> **Departamento:** 4 · Arte & marionetes · **Tipo:** LLM-V + Ferr. · **Nó:** `arte.rigger` · **Doc-mãe:** [05 §3.4](../../05-arquitetura-agentes-langgraph.md) · **Construção:** [03 §6.3](../../03-identidade-visual-lume.md)

## Missão
Transformar o vetor numa **marionete articulada** de verdade: partes separadas, pivôs nos pinos e poses-base prontas para o Animador.

## Posição no fluxo
- **Antes:** Vetorizador.
- **Depois:** Bibliotecário. Roda por `Send`, um item por vez.

## Entradas
| Campo | Para quê |
|---|---|
| `assets.marionetes[<id>].vetor` | SVG limpo |
| Ficha do item (`elenco`) | Articulações e poses pedidas |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `assets.marionetes[<id>].rig` | Caminho + hash do arquivo de rig no formato do template Blender |
| | Lista de partes, pivô de cada uma, limites de rotação, poses-base |
| | Folha de teste: a marionete em cada pose-base (PNG) |

## Regras de trabalho
1. **Partes padrão de humanoide:** cabeça, tronco, braço superior, antebraço + mão, coxa, canela + pé (cada membro dos dois lados) + acessórios (remo, arco, lança, cajado) como partes próprias.
2. **Partes extras pela ficha:** mandíbula (monstros que falam ou gritam), pescoços (Cila tem 6, cada um com 2–3 segmentos), asas (Sereias).
3. **Pivô no centro do pino desenhado.** O LLM-V localiza os pinos; a ferramenta corta as partes com **sobreposição** de 3–5% para não abrir buraco quando a junta gira.
4. **Limites de rotação** realistas para teatro de sombras (ex.: cotovelo 0–140°). A marionete pode ser exagerada, mas não pode "quebrar".
5. **Poses-base obrigatórias:** neutra, andar (2 quadros), apontar, cair. As poses extras vêm da ficha (ex.: Polifemo dormindo, erguendo pedra).
6. **A silhueta montada na pose neutra precisa ser idêntica ao vetor original** (é a prova de que o corte não estragou o design).
7. **Animação a 12 qps** (doc 04 §8): as poses-base são pensadas para movimento em degraus, como stop-motion.

## Critérios de aceite
- [ ] Pose neutra × vetor original: diferença < 1% de área
- [ ] Nenhum buraco aparece nas juntas ao girar até os limites
- [ ] Todas as poses da ficha existem
- [ ] A folha de teste mostra o personagem reconhecível em todas as poses

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Pino não detectado | Usa a posição anatômica padrão e marca para revisão humana |
| Buraco na junta | Aumenta a sobreposição (até 8%); se persistir, a junta vai para a fila humana |

## Métricas
Nº de planos refeitos por defeito de rig · tempo médio de rig por marionete.

## Não faz
Não anima planos (é o Animador) e não altera o desenho da silhueta.
