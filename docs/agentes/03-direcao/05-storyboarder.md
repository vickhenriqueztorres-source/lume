# Storyboarder

> **Departamento:** 3 · Direção · **Tipo:** IMG + Ferr. (ffmpeg) · **Nó:** `direcao.storyboarder` · **Doc-mãe:** [05 §3.3 e §7](../../05-arquitetura-agentes-langgraph.md)

## Missão
Produzir um **quadro rápido por plano** e montar o **animatic** com narração provisória, que é o que o humano assiste no Gate 2.

## Posição no fluxo
- **Antes:** Diretor de arte.
- **Depois:** **Gate 2** (storyboard). Roda por `Send` (um quadro por plano), com limite de concorrência.

## Entradas
| Campo | Para quê |
|---|---|
| `decupagem.planos` | Tipo de plano, marionetes, direção, distância do fogo, câmera, proporção, fogo |
| `elenco` | Silhueta aproximada de cada personagem (ou a marionete real, se já existir) |
| `roteiro.blocos` | Texto para a narração provisória |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `decupagem.planos[].storyboard` | Caminho + hash do quadro de baixa resolução |
| `decupagem.animatic` | Caminho + hash do vídeo do animatic, duração total, versão |

## Ferramentas
Geração de imagem rápida (baixa resolução), TTS de rascunho (voz neutra, só para tempo), ffmpeg para montar o animatic.

## Regras de trabalho
1. **Quadro é diagrama, não arte final:** fundo Carvão, parede em Fuligem/Pergaminho, silhuetas em preto. O que importa: **composição, escala, direção e quantidade de escuro**.
2. **Marcar o que não aparece na imagem parada:** seta de movimento de câmera, nível de fogo (1–5) no canto e barras de proporção desenhadas.
3. **Animatic:** cada quadro dura `duracao_s`, com um push-in simples para dar noção de movimento. A narração provisória é **TTS de rascunho**, claramente diferente da voz final.
4. **Marionetes reais quando existirem:** se a biblioteca já tem a marionete, usar a silhueta dela em vez de gerar uma nova. Isso evita aprovar no Gate 2 um design que não é o que vai sair.
5. **Escrever o id do plano** no quadro (canto inferior), para o humano poder comentar "trocar o `ep01_c07_p03`".

## Critérios de aceite
- [ ] Todo plano tem quadro
- [ ] A duração do animatic bate com a soma de `duracao_s`
- [ ] Todo quadro mostra id, nível de fogo e proporção

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Geração de imagem falha | Retry 2×; depois, usa um quadro esquemático (formas simples) e marca como "esquema" |
| Quadro gerado inverte a direção pedida | Espelha horizontalmente (determinístico) em vez de gerar de novo |

## Métricas
Tempo de geração do animatic · nº de comentários no Gate 2 do tipo "não entendi o plano" (indica quadro pouco claro).

## Não faz
Não produz arte final, não decide planos e não grava a narração final.
