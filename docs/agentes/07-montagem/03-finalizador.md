# Finalizador

> **Departamento:** 7 · Montagem & finalização · **Tipo:** Ferr. (ffmpeg / Resolve via script) · **Nó:** `montagem.finalizador` · **Doc-mãe:** [05 §3.7](../../05-arquitetura-agentes-langgraph.md) · **Acabamento:** [04 §8](../../04-cinematografia.md)

## Missão
Dar o **acabamento de filme** e entregar o master: grão, halation, vinheta, gate weave, letterbox e exportação em 4K.

## Posição no fluxo
- **Antes:** Grafismo (e remix do Mixador, se houve).
- **Depois:** Legendador → QA.

## Entradas
| Campo | Para quê |
|---|---|
| `timeline` (com grafismo) | O corte |
| `audio.mix` | Áudio final |
| `decupagem.planos[].proporcao` | Letterbox por trecho |
| `decupagem.planos[].mundo` | Onde aplicar gate weave e 24 × 12 qps |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `master.arquivo` | H.264 de alto bitrate para upload + ProRes de arquivo (caminhos + hashes) |
| `master.capitulos` | Lista de capítulos com timecode (a partir dos marcadores do Editor) |

## Especificação (doc 04 §8)
| Etapa | Valor |
|---|---|
| Halation | Leve brilho vermelho nas bordas mais claras da parede |
| Grão | 35 mm, intensidade constante, inclusive nos mapas e cartelas |
| Vinheta | Sempre ativa, mais forte em fogo baixo |
| Gate weave | 0,3 px, **só no Mundo do Contador** |
| Letterbox | 1,78 / 2,39 / 3,0 conforme o plano; as barras entram e saem em transição suave |
| Taxa de quadros | Parede a 12 qps (com motion blur); Contador e fogo a 24 qps, em master 24p |
| Master | 3840×2160, 24p, Rec.709 |

## Regras de trabalho
1. **Ordem das camadas:** imagem → halation → vinheta → grafismo → grão → letterbox. O grafismo entra **antes** do grão, para receber a mesma textura de película e parecer parte do filme, mas **depois** da halation, porque o texto não pode borrar.
2. **Proibido corrigir cor criativamente** aqui: a cor é do fogo e do DoP. O Finalizador só garante Rec.709 e consistência.
3. **Mesma cadeia em todo episódio** (parâmetros fixos versionados), para a série ter uma cara só.

## Critérios de aceite
- [ ] 3840×2160, 24p, Rec.709
- [ ] Letterbox bate com a proporção de cada plano
- [ ] Gate weave ausente nos planos de parede
- [ ] Áudio do master = `audio.mix` (hash)

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Exportação falha | Retry 2× pelo worker; depois, fila humana |

## Métricas
Tempo de finalização · notas do QA técnico por episódio.

## Não faz
Não altera a montagem, não mexe no mix e não gera legendas.
