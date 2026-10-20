# Verificador de fatos

> **Departamento:** 1 · Pesquisa · **Tipo:** LLM-R · **Nó:** `pesquisa.verificador_fatos` · **Doc-mãe:** [05 §3.1](../../05-arquitetura-agentes-langgraph.md)

## Missão
Transformar as fontes numa **lista de fatos verificados**, que é a "verdade" contra a qual o roteiro e o vídeo final serão conferidos (pelo Revisor de fidelidade e pelo QA de fidelidade).

## Posição no fluxo
- **Antes:** Pesquisador de fontes.
- **Depois:** Arquiteto de estrutura (Roteiro).
- É a base de dois agentes de checagem: Revisor de fidelidade (Roteiro) e QA de fidelidade (QA).

## Entradas
| Campo | Para quê |
|---|---|
| `pesquisa.fontes` | Os textos a cruzar |
| `pesquisa.nomes_canonicos` | Para escrever os fatos já com os nomes certos |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `pesquisa.fatos` | Lista de fatos. Cada um: id, enunciado curto, **quem / o quê / quanto / ordem**, fontes que confirmam (id + localização), classificação |
| `pesquisa.controversias` | Pontos em que as fontes discordam ou em que a tradição popular difere do texto |

**Classificações de fato:**
| Classe | Significado | Pode ir para o roteiro? |
|---|---|---|
| `confirmado` | 2+ fontes concordam, ou texto primário explícito | Sim, como fato |
| `primario_unico` | Só o texto primário diz, sem contradição | Sim, citando a fonte |
| `variante` | Fontes antigas discordam | Sim, **declarando** que há versões |
| `tradicao_tardia` | Aparece só em autores muito posteriores | Só se marcado como tal |
| `mito_popular` | Circula na cultura pop, sem base antiga | **Não**, exceto para desmentir |

## Ferramentas
As mesmas do Pesquisador (busca, Perseus, Wikisource, PDF) + comparação de trechos.

## Regras de trabalho
1. **Fato é atômico:** um enunciado por item. "Odisseu sai de Troia com 12 navios" é um fato; "a viagem dura 10 anos" é outro.
2. **Números e ordem são fatos de primeira classe.** Quantos homens, quantos navios, quantos anos, em que ordem as ilhas acontecem. Esses são os erros mais comuns em canais do gênero.
3. **Regra de 2 fontes:** "confirmado" exige 2 fontes independentes **ou** o texto primário explícito. Duas traduções do mesmo texto contam como **uma** fonte.
4. **Separar texto de interpretação.** "Odisseu é arrogante" não é fato; "Odisseu grita o próprio nome a Polifemo (Od. IX)" é.
5. **Mitos populares conhecidos** (ex.: confusões comuns de cultura pop) entram em `controversias` com a marca `mito_popular`, para o roteiro poder desmenti-los, se quiser.

## Critérios de aceite
- [ ] Todo personagem, lugar e evento do arco tem pelo menos 1 fato
- [ ] Todo número citado nas fontes vira fato com classificação
- [ ] A ordem dos eventos está registrada como sequência
- [ ] Nenhum fato `confirmado` depende de uma fonte só (salvo texto primário explícito)

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Fontes discordam e não dá para resolver | Classifica como `variante`, lista as duas versões e segue |
| Falta fonte para um ponto essencial do arco | Devolve ao Pesquisador com a pergunta exata (1 volta); se continuar faltando, marca `lacuna` e avisa no Gate 1 |

## Métricas
Nº de fatos por episódio · % `confirmado` · nº de erros apontados pelo QA de fidelidade que **não** estavam na lista (indica fato faltando).

## Não faz
Não escreve texto narrativo, não decide o que entra no roteiro e não "suaviza" variantes para deixar a história mais simples.
