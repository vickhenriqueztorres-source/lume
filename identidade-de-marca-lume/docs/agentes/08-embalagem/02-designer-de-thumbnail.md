# Designer de thumbnail

> **Departamento:** 8 · Embalagem · **Tipo:** IMG + Ferr. (composição) · **Nó:** `embalagem.designer_thumbnail` · **Doc-mãe:** [05 §3.8](../../05-arquitetura-agentes-langgraph.md) · **Thumbnails:** [03 §8](../../03-identidade-visual-lume.md)

## Missão
Compor **3 thumbnails**, uma em cada layout fixo (A, B e C), **a partir dos renders reais** do episódio, para que a thumb prometa exatamente o que o vídeo mostra.

## Posição no fluxo
- **Antes:** Gate 3.
- **Em paralelo:** Titulista, Redator de metadados e Cortador de Shorts.
- **Depois:** Avaliador de feed → Gate 4.

## Entradas
| Campo | Para quê |
|---|---|
| `assets.planos[].render` | Quadros reais (planos de escala, clímax, Contador) |
| `assets.indice` | Marionetes em alta resolução para recompor |
| `pesquisa.angulos` (o escolhido) | Promessa |
| Templates A/B/C (doc 03 §13) | Camadas fixas |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `embalagem.thumbs` | 3 PNGs 1280×720 (caminhos + hashes). Cada um: layout, plano(s) de origem, texto usado, nº de palavras |

## Layouts (doc 03 §8.2)
| Layout | Composição |
|---|---|
| **A · Ameaça** | Monstro gigante no centro/direita, herói minúsculo de pé à direita, embaixo; texto empilhado à esquerda; fogo na base |
| **B · Escolha** | Figura gigante à esquerda apontando para um caminho (ruínas, navio); herói pequeno à direita; texto no centro-esquerda |
| **C · Contador** | A pergunta do Contador: ameaça múltipla no alto, herói pequeno à direita, texto em forma de pergunta (até 3 palavras) |

## Regras de trabalho
1. **Fórmula:** 1 silhueta gigante + 1 silhueta pequena + até 3 palavras + brasa (fogo na base).
2. **Partir do render real.** A geração de imagem só entra para **estender** fundo ou ajustar enquadramento, nunca para criar um personagem diferente do que está no vídeo.
3. **Texto:** Cinzel Bold/Black com textura de pergaminho e sombra em Carvão; **máximo 3 palavras**; artigos e preposições menores que as palavras-chave (doc 03 §4).
4. **Wordmark LUME** pequeno no canto inferior esquerdo. **Canto inferior direito livre** (duração do vídeo).
5. **Proibido:** rosto humano realista, setas vermelhas, círculos amarelos, cores fora da paleta.
6. **Silhuetas das fichas:** Odisseu de píleo, nunca o herói genérico de capa e lança do board (doc 03 §6.2).

## Critérios de aceite
- [ ] 3 thumbs, uma por layout
- [ ] ≤ 3 palavras em cada
- [ ] Canto inferior direito livre
- [ ] Todo personagem bate com a ficha e com o render

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Nenhum plano serve para o layout A (não há monstro) | Substitui por um segundo B ou C e explica |
| O Avaliador de feed reprova por legibilidade | Refaz só a thumb reprovada (até 3 rodadas) |

## Métricas
CTR por layout · layout vencedor por tipo de mito (vai para a Store).

## Não faz
Não escreve títulos e não testa no feed (é o Avaliador).
