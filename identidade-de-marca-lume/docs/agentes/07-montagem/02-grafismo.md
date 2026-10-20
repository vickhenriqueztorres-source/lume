# Grafismo

> **Departamento:** 7 · Montagem & finalização · **Tipo:** Ferr. (templates Remotion/AE) · **Nó:** `montagem.grafismo` · **Doc-mãe:** [05 §3.7](../../05-arquitetura-agentes-langgraph.md) · **Sistema gráfico:** [03 §4 e §5](../../03-identidade-visual-lume.md)

## Missão
Inserir o **sistema gráfico do Lume** sobre a timeline: cartelas, lower thirds, mapa, contador de perdas, selos de fonte e marca d'água, sempre a partir dos templates oficiais.

## Posição no fluxo
- **Antes:** Editor.
- **Depois:** Finalizador.

## Entradas
| Campo | Para quê |
|---|---|
| `timeline` | Onde cada elemento entra |
| `roteiro.blocos` | `[CAPÍTULO]`, `[CITAÇÃO]`, primeira aparição de personagens, mortes |
| `pesquisa.nomes_canonicos` | Grafia dos nomes |
| `assets.cenarios` (mapa) | Camadas do mapa de pergaminho |

## Saída
| Campo | Conteúdo |
|---|---|
| `timeline` (camadas de grafismo) | Camadas renderizadas com alfa (caminho + hash), cada uma com tempo de entrada/saída e template usado |

## Elementos (doc 03 §5)
| Elemento | Regra |
|---|---|
| **Cartela de capítulo** | Tela em Carvão, número romano pequeno em Cinzel acima, nome em Cinzel 96 px, friso de figuras vermelhas fino embaixo; ≈ 10 por episódio |
| **Lower third** | Nome em Cinzel 56 px (Pergaminho) + papel em EB Garamond itálico (Brasa); entra como fumaça e sai como cinza; só na primeira aparição |
| **Mapa** | Pergaminho de bordas queimadas; linha que queima a rota; desvio para a esquerda = castigo (doc 04 §4) |
| **Contador de perdas** | Fileira de marionetes pequenas + número em EB Garamond 600; cada morte derruba marionetes |
| **Selo de fonte** | Canto inferior esquerdo, EB Garamond itálico 30 px (ex.: *Odisseia, canto IX, v. 375*) |
| **Nota de pergaminho** | Recorte rasgado de bordas queimadas para citação longa ou frase de marca; no máximo 1 por ato |
| **Marca d'água** | Símbolo U-braseiro em bronze a 40%, canto inferior direito, **exceto nas cenas do Contador** |

## Regras de trabalho
1. **Só duas fontes:** Cinzel e EB Garamond. Nunca Cinzel em parágrafo nem em legenda.
2. **Paleta da marca** apenas; Brasa ≤ 5% da área.
3. **Pergaminho sobre Brasa é proibido para texto** (contraste 2,4:1).
4. **Números do contador de perdas** vêm de `pesquisa.fatos`, nunca estimados.
5. **Área segura:** nada nos 5% das bordas; o canto inferior direito fica livre perto do final (end screen).

## Critérios de aceite
- [ ] Toda cartela bate com um marcador de capítulo
- [ ] Todo selo de fonte bate com uma `[CITAÇÃO]` do roteiro
- [ ] Todo lower third aparece uma vez por personagem
- [ ] Nenhuma fonte ou cor fora da marca

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Template falha | Retry 1×; depois, fila humana para o Engenheiro de motion |
| Nome longo demais para o lower third | Reduz para 48 px; se ainda não couber, usa o nome curto da tabela de nomes |

## Métricas
Avisos do QA de marca por episódio.

## Não faz
Não decide onde há capítulo (é o roteiro) e não cria templates (é o Engenheiro de motion, no Antigravity).
