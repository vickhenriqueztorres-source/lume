# QA de marca

> **Departamento:** 9 · QA · **Tipo:** Ferr. + LLM-V · **Nó:** `qa.marca` · **Não bloqueia (aviso)** · **Doc-mãe:** [05 §3.9](../../05-arquitetura-agentes-langgraph.md) · **Identidade:** [03](../../03-identidade-visual-lume.md)

## Missão
Avisar onde o episódio **se afasta da identidade do Lume**: paleta, fontes, marca d'água, end screen e os "não faça" do doc 03.

## Posição no fluxo
- **Antes:** Montagem.
- **Em paralelo:** os outros agentes de QA.
- **Depois:** os avisos vão junto para o Gate 3; não devolvem trabalho automaticamente.

## Entradas
| Campo | Para quê |
|---|---|
| `master.arquivo` | Quadros amostrados |
| Camadas do Grafismo | Fontes, cores e posições |
| `timeline` | Onde ficam o Contador e o end screen |

## Saída
| Campo | Conteúdo |
|---|---|
| `qa` (append) | Avisos com timecode, regra do doc 03 e sugestão |

## Checagens
| Checagem | Critério (doc 03) |
|---|---|
| Paleta | Até 5 cores (Carvão, Fuligem, Pergaminho, Brasa, Cinza-alma); proporção próxima de 60/25/10/5 |
| Brasa | ≤ 5% da área por quadro amostrado |
| Fontes | Só Cinzel e EB Garamond; Cinzel nunca em parágrafo nem em legenda de vídeo longo |
| Logo | Wordmark sem filete nem círculo; chama só dentro do U; letras sem afastamento |
| Contraste | Nenhum texto Pergaminho sobre Brasa |
| Marca d'água | Presente fora do Contador; ausente nas cenas do Contador |
| End screen | 20 s, Contador se levanta, fala final *"O lume apaga. A história fica."* |
| Abertura | Sting LUME na 0:45 |
| "Não faça" | Glow digital, lens flare, rosto realista, parede iluminada por igual, cores novas |

## Regras de trabalho
1. **Aviso, não bloqueio:** a marca é importante, mas uma exceção pode ser decisão criativa. O humano decide no Gate 3.
2. **Medição de cor determinística** (histograma por quadro); o LLM-V só entra para os "não faça" visuais.

## Critérios de aceite
- [ ] Todas as checagens com resultado

## Falhas e escalada
| Situação | Decisão |
|---|---|
| O mesmo aviso aparece em 3 episódios seguidos | Vira lição para o departamento de origem (via Curador de memória) |

## Métricas
Avisos por episódio (devem cair com o tempo).

## Não faz
Não bloqueia e não corrige.
