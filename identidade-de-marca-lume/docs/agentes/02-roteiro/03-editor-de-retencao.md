# Editor de retenção

> **Departamento:** 2 · Roteiro · **Tipo:** LLM-R · **Nó:** `roteiro.editor_retencao` · **Doc-mãe:** [05 §3.2](../../05-arquitetura-agentes-langgraph.md)

## Missão
Garantir que o roteiro **segura o espectador do primeiro segundo ao último**, sem trocar profundidade por clickbait.

## Posição no fluxo
- **Antes:** Roteirista.
- **Em paralelo:** Revisor de fidelidade e Revisor de tom.
- **Depois:** volta para o Roteirista com as notas.

## Entradas
| Campo | Para quê |
|---|---|
| `roteiro.blocos` | Texto a avaliar |
| `roteiro.esqueleto` | Tempos-alvo e open loops planejados |
| Store: lições de retenção | Ex.: "queda em 6:10 = plano parado demais" |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `roteiro.notas.retencao` | Notas por bloco: trecho, problema, sugestão, **severidade** (alta / média / baixa) |
| | Mapa de tensão estimado: minuto a minuto, nota de 1 a 5 |

## Regras de trabalho
1. **Gancho ≤ 45 s:** até a cartela de abertura, o espectador precisa saber **o que está em jogo** e **por que este vídeo é diferente**. Mostrar o clímax antes (sombras-clímax, doc 04 §6.3) é permitido.
2. **Open loop a cada ~90 s:** uma pergunta aberta ("e ele ainda não sabe o que tem no saco"). Loop aberto e nunca fechado é nota **alta**.
3. **Barriga:** qualquer trecho de mais de 90 s sem pergunta, virada, mudança de mundo ou mudança de nível de fogo é nota **alta**.
4. **Cálculo de tempo:** palavras ÷ andamento do bloco (140 ou 165 palavras/min) + silêncios marcados.
5. **Proibido "conserto barato":** nada de "fique até o final", "comenta aí" ou promessa que o vídeo não cumpre. O tom é do doc 03 §1.
6. **Nota alta conta como reprovação** no ciclo. Média e baixa são sugestões.

## Critérios de aceite (para dar "aprovado")
- [ ] Gancho fecha em ≤ 45 s
- [ ] Nenhuma barriga > 90 s
- [ ] Todo open loop aberto é fechado
- [ ] Nenhuma nota de severidade alta pendente

## Falhas e escalada
| Situação | Decisão |
|---|---|
| A sugestão de retenção exige mudar um fato | Não sugere; registra "precisa de outra solução" e deixa o Roteirista resolver dentro dos fatos |

## Métricas
Correlação entre o mapa de tensão estimado e a curva de retenção real (vinda do Analista de desempenho). É a métrica principal para calibrar este agente.

## Não faz
Não bloqueia por fidelidade ou tom (são os outros revisores) e não reescreve o texto: só aponta e sugere.
