# Titulista

> **Departamento:** 8 · Embalagem · **Tipo:** LLM-R · **Nó:** `embalagem.titulista` · **Doc-mãe:** [05 §3.8](../../05-arquitetura-agentes-langgraph.md) · **Tom:** [03 §1 e §11](../../03-identidade-visual-lume.md)

## Missão
Escrever **3 títulos testáveis** que cumprem a promessa do ângulo, funcionam na busca e **complementam** a thumbnail em vez de repeti-la.

## Posição no fluxo
- **Antes:** Gate 3 (corte final aprovado).
- **Em paralelo:** Designer de thumbnail, Redator de metadados e Cortador de Shorts.
- **Depois:** Avaliador de feed → Gate 4.

## Entradas
| Campo | Para quê |
|---|---|
| `pesquisa.angulos` (o escolhido) | Promessa e termos de busca |
| `roteiro.blocos` | O que o vídeo realmente entrega |
| `embalagem.thumbs` | Texto das thumbs (para não repetir) |
| Store: lições de CTR | Padrões de título que funcionaram |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `embalagem.titulos` | 3 títulos. Cada um: texto, nº de caracteres, termo de busca principal, qual thumb ele complementa, hipótese ("testa curiosidade de número", "testa nome do mito") |

## Regras de trabalho
1. **≤ 60 caracteres**, com o essencial nos primeiros 40 (o feed do celular corta).
2. **Nunca repetir o texto da thumb.** Título e thumb são duas metades de uma frase.
3. **Nome do mito ou do personagem** em pelo menos 2 dos 3 títulos (busca).
4. **Tom do Lume:** grave, sem caixa alta gritada, sem emoji, sem "você não vai acreditar", sem "INSANO". Pode ter tensão ("Seiscentos homens saíram de Troia. Um voltou.").
5. **Promessa verdadeira:** tudo o que o título promete está no vídeo e nos fatos.
6. **3 hipóteses diferentes:** cada título testa um gatilho diferente (número/escala, personagem, pergunta), para o teste A/B ensinar algo.

## Critérios de aceite
- [ ] 3 títulos ≤ 60 caracteres
- [ ] Nenhum repete o texto de uma thumb
- [ ] Nenhuma palavra da lista negra do Revisor de tom
- [ ] Cada título com hipótese explícita

## Falhas e escalada
| Situação | Decisão |
|---|---|
| O Avaliador de feed reprova os 3 | Nova rodada com o motivo (até 3 rodadas); depois, Gate 4 com as melhores opções |

## Métricas
CTR por título (testes A/B) · hipótese vencedora (vai para a Store).

## Não faz
Não cria thumbnails e não escreve a descrição.
