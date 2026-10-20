# Narrador

> **Departamento:** 6 · Áudio · **Tipo:** TTS / Ferr. · **Nó:** `audio.narrador` · **Doc-mãe:** [05 §3.6](../../05-arquitetura-agentes-langgraph.md) · **Voz:** [03 §10](../../03-identidade-visual-lume.md)

## Missão
Produzir **a voz do Contador** bloco a bloco, por um de dois caminhos: voz própria clonada (TTS) **ou** importação da gravação de um locutor humano.

## Posição no fluxo
- **Antes:** Diretor de voz.
- **Depois:** Mixador (e Editor, que alinha os planos à narração). Roda por `Send`: **um bloco por execução**.

## Entradas
| Campo | Para quê |
|---|---|
| `audio.roteiro_anotado` | Texto + pausas + ênfases + andamento + pronúncia |
| Configuração do episódio | Modo: `tts_voz_propria` ou `locutor_humano` |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `audio.narracao[<bloco>]` | WAV 48 kHz / 24 bits (caminho + hash), duração, palavras/min medidas, resultado da checagem de transcrição, modo usado |

## Os dois modos
| | **TTS com voz própria** | **Locutor humano** |
|---|---|---|
| Origem | Voz clonada **a partir de gravações autorizadas** do dono da voz | Arquivos entregues pelo locutor |
| O que o agente faz | Gera o áudio com as marcações do Diretor de voz | Corta por bloco, limpa ruído, normaliza e confere |
| Quando usar | Escala, revisões rápidas | Episódios-âncora e quando a voz humana for a escolha criativa |

## Regras de trabalho
1. **Voz grave e próxima** (efeito de proximidade), com ar no áudio. Sem música por baixo: isso é do Mixador.
2. **Consentimento:** a voz clonada só pode ser de quem autorizou, por escrito, o uso da voz. Nunca imitar voz de terceiro.
3. **Checagem de transcrição:** transcreve o áudio gerado (ASR) e compara com o texto. Diferença acima de 2% das palavras = refaz o bloco.
4. **Andamento medido** precisa ficar a ±8% do alvo do bloco.
5. **Nomes próprios** conferidos pela transcrição + guia de pronúncia.
6. **Sem cortes no meio de palavra** nem respirações cortadas no início/fim do arquivo (sobra de 150 ms em cada ponta).

## Critérios de aceite
- [ ] Todo bloco tem WAV
- [ ] Diferença de transcrição ≤ 2%
- [ ] Andamento dentro de ±8% do alvo
- [ ] Sem clipping (pico abaixo de −1 dBFS)

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Diferença de transcrição > 2% | Refaz o bloco (até 2×); depois, fila humana |
| Nome pronunciado errado de forma recorrente | Ajusta o guia de pronúncia (soletração fonética) e refaz |
| Locutor humano: arquivo faltando | Fila humana com a lista de blocos pendentes |

## Métricas
Diferença de transcrição média · nº de refações por bloco · correções de voz pedidas no Gate 3.

## Não faz
Não altera o texto, não mixa e não escolhe efeitos.
