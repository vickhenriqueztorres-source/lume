# Revisor de tom

> **Departamento:** 2 · Roteiro · **Tipo:** LLM-R · **Nó:** `roteiro.revisor_tom` · **Doc-mãe:** [05 §3.2](../../05-arquitetura-agentes-langgraph.md) · **Tom:** [03 §1, §10 e §11](../../03-identidade-visual-lume.md)

## Missão
Garantir que o texto soa como **o Contador do Lume** (grave, próximo, um pouco sombrio) e nunca como "canal de curiosidades".

## Posição no fluxo
- **Antes:** Roteirista.
- **Em paralelo:** Editor de retenção e Revisor de fidelidade.
- **Depois:** volta para o Roteirista.

## Entradas
| Campo | Para quê |
|---|---|
| `roteiro.blocos` | Texto a avaliar |
| `pesquisa.nomes_canonicos` | Conferir formas grega × latina |
| `roteiro.notas.fidelidade` | Receber as notas de nome repassadas |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `roteiro.notas.tom` | Por trecho: problema, sugestão, severidade |
| | Medição por bloco: palavras/min estimadas, tamanho médio de frase, % de frases acima de 20 palavras |

## Regras de trabalho
1. **Lista negra** (severidade alta): "você não vai acreditar", "galera", "fique até o final", "isso é insano", "top", "curiosidade", gírias da internet, emojis e qualquer chamada para curtir/comentar dentro da narração.
2. **Clichês de gênero** (severidade média): "desde os primórdios", "desde o início dos tempos", "lenda épica", "reza a lenda" usada como tique.
3. **Frases curtas:** média abaixo de 14 palavras; nenhuma frase acima de 30 palavras.
4. **Andamento:** 140 palavras/min nas cenas calmas, 165 na ação (doc 03 §10). Bloco fora da faixa (±10%) recebe nota.
5. **Presente narrativo** como padrão. Passado só no Mundo do Contador, quando ele comenta.
6. **Nomes:** forma portuguesa da tradição grega. Misturar Odisseu e Ulisses no mesmo vídeo é nota alta, exceto quando o texto explica a tradição latina.
7. **Respeito ao espectador:** nunca infantilizar, nunca explicar a piada, nunca usar o espectador como alvo ("você que não sabe…").

## Critérios de aceite (para dar "aprovado")
- [ ] Nenhuma ocorrência da lista negra
- [ ] Todos os blocos dentro da faixa de andamento
- [ ] Nenhuma frase acima de 30 palavras
- [ ] Nomes consistentes

## Falhas e escalada
| Situação | Decisão |
|---|---|
| A correção de tom mudaria um fato | Não sugere; deixa o Roteirista resolver |

## Métricas
Nº de ocorrências da lista negra por versão (deve cair a zero na 2ª volta) · edições de tom feitas por humanos no Gate 1 (cada uma vira caso de teste do prompt).

## Não faz
Não avalia retenção nem fidelidade e não reescreve o texto.
