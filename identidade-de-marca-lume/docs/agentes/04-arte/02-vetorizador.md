# Vetorizador

> **Departamento:** 4 · Arte & marionetes · **Tipo:** Ferr. (potrace) · **Nó:** `arte.vetorizador` · **Doc-mãe:** [05 §3.4](../../05-arquitetura-agentes-langgraph.md)

## Missão
Converter o PNG aprovado em **vetor limpo**: preto absoluto + furos, sem nenhum cinza. É esse vetor que vira geometria no Blender e projeta a sombra de verdade.

## Posição no fluxo
- **Antes:** Designer de silhuetas.
- **Depois:** Rigger. Roda por `Send`, um item por vez.

## Entradas
| Campo | Para quê |
|---|---|
| `assets.marionetes[<id>].design` | PNG de alta resolução |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `assets.marionetes[<id>].vetor` | Caminho + hash do SVG, nº de caminhos, nº de furos, área total |
| | PNG de controle renderizado a partir do SVG (para comparação visual) |

## Configuração (sem LLM)
| Passo | Parâmetro padrão |
|---|---|
| Binarização | Limiar fixo em 50%; tudo vira preto (100%) ou transparente |
| Remoção de ruído | Descarta ilhas e furos menores que 0,1% da área da silhueta |
| Suavização de curva | Média: preserva os cantos vivos do estilo figura negra |
| Otimização | Reduz nós sem desviar mais de 0,5 px da borda original |
| Saída | SVG de cor única, furos como subcaminhos (regra par/ímpar) |

## Regras de trabalho
1. **Só dois valores:** preto e transparente. Qualquer pixel cinza no resultado é falha.
2. **Furos são sagrados:** o olho de Polifemo e os furos decorativos dos deuses precisam sobreviver à limpeza de ruído (por isso o limite de 0,1% é relativo e conferido).
3. **Pinos preservados:** o desenho do rebite precisa continuar legível no vetor.

## Critérios de aceite
- [ ] Diferença entre o PNG original e o PNG de controle < 1% de área
- [ ] Nenhum tom intermediário
- [ ] Todos os furos da ficha presentes (contagem conferida)

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Furo obrigatório perdido | Refaz com limpeza de ruído mais branda (1 tentativa) |
| Diferença > 1% | Volta ao Designer de silhuetas com o motivo (traço fino demais, borda borrada) |

## Métricas
Nº de nós por marionete (afeta o tempo de render) · nº de devoluções ao Designer.

## Não faz
Não corrige o design e não separa partes (é o Rigger).
