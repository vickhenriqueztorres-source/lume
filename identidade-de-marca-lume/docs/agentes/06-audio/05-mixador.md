# Mixador

> **Departamento:** 6 · Áudio · **Tipo:** Ferr. (ffmpeg loudnorm) · **Nó:** `audio.mixador` · **Doc-mãe:** [05 §3.6](../../05-arquitetura-agentes-langgraph.md) · **Mixagem:** [04 §7](../../04-cinematografia.md)

## Missão
Juntar narração, SFX e trilha num **mix final** que respeita o padrão do YouTube e as regras de silêncio do Lume.

## Posição no fluxo
- **Antes:** Narrador, Sound designer e Supervisor musical.
- **Depois:** Editor (Montagem).
- **Roda duas vezes:** mix v1 (alinhado à narração) e **remix** depois que o Editor trava a timeline, se os tempos tiverem mudado.

## Entradas
| Campo | Para quê |
|---|---|
| `audio.narracao` | Voz por bloco |
| `audio.sfx`, `audio.trilha` | Efeitos e stems |
| `audio.roteiro_anotado` | Silêncios dramáticos |
| `timeline` | Tempos definitivos (no remix) |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `audio.mix` | Mix final estéreo (caminho + hash) + stems de mix (voz, efeitos, música) |
| `audio.lufs` | Loudness integrado medido, true peak, faixa de loudness |

## Parâmetros
| Item | Valor |
|---|---|
| Loudness integrado | **−14 LUFS** (doc 04 §7) |
| True peak | ≤ −1 dBTP |
| Voz × música | Voz sempre **6–8 dB acima** da música |
| Ducking | A música abaixa quando a voz entra (ataque rápido, soltura lenta) |
| Silêncio dramático | Fogo, ambiente e música a zero durante a duração marcada |
| Formato | WAV 48 kHz / 24 bits |

## Regras de trabalho
1. **A voz manda:** qualquer conflito de frequência é resolvido abaixando música/efeitos, nunca a voz.
2. **Silêncio é silêncio de verdade**, não volume baixo.
3. **Volta do som no corte:** depois do silêncio, o som volta junto com o corte de imagem (o Editor alinha).
4. **Medir depois de mixar:** a medição de loudness é a última etapa e vai para o estado.

## Critérios de aceite
- [ ] −14 LUFS ±1
- [ ] True peak ≤ −1 dBTP
- [ ] Voz 6–8 dB acima da música em todos os trechos com fala
- [ ] Todos os silêncios dramáticos presentes

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Loudness fora da faixa | Ajusta o ganho e mede de novo (até 2×) |
| Voz encoberta mesmo com ducking | Abaixa o stem musical do trecho e registra para o Supervisor musical |

## Métricas
LUFS medido por episódio · notas de "voz baixa" ou "música alta" no Gate 3.

## Não faz
Não escolhe sons ou músicas e não muda tempos da timeline.
