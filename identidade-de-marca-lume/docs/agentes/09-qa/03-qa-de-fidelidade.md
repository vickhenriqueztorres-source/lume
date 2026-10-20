# QA de fidelidade

> **Departamento:** 9 · QA · **Tipo:** ASR + LLM-R · **Nó:** `qa.fidelidade` · **Bloqueante** · **Doc-mãe:** [05 §3.9](../../05-arquitetura-agentes-langgraph.md)

## Missão
Conferir o que **realmente foi dito e mostrado** no master contra `pesquisa.fatos`. O Revisor de fidelidade conferiu o texto; este agente confere o **resultado**, depois de voz, edição e grafismo.

## Posição no fluxo
- **Antes:** Montagem.
- **Em paralelo:** os outros agentes de QA.
- **Depois:** reprovado → departamento responsável; aprovado → Gate 3.

## Entradas
| Campo | Para quê |
|---|---|
| `master.arquivo` | Áudio para transcrição |
| `roteiro.blocos` (versão aprovada) | Texto que deveria ter sido dito |
| `pesquisa.fatos` | Base de verdade |
| Camadas do Grafismo | Textos na tela (números, nomes, selos de fonte) |
| Divergências registradas pelo Legendador | Pontos em que a voz saiu diferente do roteiro |

## Saída
| Campo | Conteúdo |
|---|---|
| `qa` (append) | Por divergência: timecode, o que foi dito/mostrado, o que deveria ser, fato violado, departamento |

## Checagens
| Checagem | Volta para |
|---|---|
| Transcrição do master × roteiro aprovado (palavras trocadas, cortadas, acrescentadas) | Áudio (Narrador) |
| Toda frase factual da transcrição × `pesquisa.fatos` | Roteiro (se o erro já estava no texto) |
| Números e nomes na tela (contador de perdas, lower thirds) | Montagem (Grafismo) |
| Selos de fonte × localização correta | Montagem (Grafismo) |
| Cortes de edição que mudam o sentido (ex.: frase cortada que vira afirmação falsa) | Montagem (Editor) |

## Regras de trabalho
1. **Mesmos tipos de erro do Revisor de fidelidade** (invenção, número, ordem, variante oculta, citação, exagero).
2. **Erro que já estava no roteiro aprovado** também bloqueia, e vira lição para o Revisor de fidelidade (escapou dele).

## Critérios de aceite
- [ ] 100% do áudio transcrito e conferido
- [ ] Zero divergências factuais

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Divergência que foi aprovada por humano no Gate 1 (liberdade criativa registrada) | Não bloqueia; registra a referência em `aprovacoes` |

## Métricas
Divergências por episódio · erros que escaparam (apontados pelo público depois da publicação).

## Não faz
Não reescreve texto e não regrava voz.
