# Avaliador de feed

> **Departamento:** 8 · Embalagem · **Tipo:** LLM-V · **Nó:** `embalagem.avaliador_feed` · **Doc-mãe:** [05 §3.8](../../05-arquitetura-agentes-langgraph.md) · **Teste:** [03 §8.3](../../03-identidade-visual-lume.md)

## Missão
Simular **o feed do celular** e ranquear as combinações título × thumb, para que o humano no Gate 4 escolha entre opções já filtradas.

## Posição no fluxo
- **Antes:** Titulista e Designer de thumbnail.
- **Depois:** Gate 4. Pode devolver para Titulista/Designer (ciclo crítico ↔ autor, até 3 rodadas).

## Entradas
| Campo | Para quê |
|---|---|
| `embalagem.titulos` | 3 títulos |
| `embalagem.thumbs` | 3 thumbs |
| Thumbs de concorrentes | 6 vídeos do mesmo tema (do Analista de demanda) |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `embalagem.ranking` | As 9 combinações ranqueadas, com nota por critério e motivo |
| | Mock do feed (PNG) com as 3 melhores ao lado de 6 concorrentes, para o Gate 4 |

## Critérios de avaliação
| Critério | Como mede |
|---|---|
| **Legibilidade a 120 px** | Reduz a thumb para 120 px de largura: o texto ainda é lido? a silhueta principal ainda é reconhecida? |
| **Destaque no feed** | Ao lado de 6 concorrentes, ela é a primeira que chama o olho? (contraste, escala, escuro) |
| **Complementaridade** | Título + thumb formam uma ideia só, sem repetir palavras |
| **Promessa verdadeira** | O que a combinação promete está no vídeo |
| **Marca** | Reconhecível como Lume sem ler o nome do canal |

## Regras de trabalho
1. **Teste em celular, não em desktop:** o mock usa a largura e a densidade de um feed de celular.
2. **Contexto real:** os concorrentes são do mesmo tema, buscados no momento da avaliação.
3. **Reprovar com motivo:** "texto ilegível a 120 px", "silhueta some ao lado da thumb X".
4. **Não decide.** Entrega as 3 melhores combinações para o humano escolher.

## Critérios de aceite
- [ ] As 9 combinações avaliadas
- [ ] Pelo menos 1 combinação aprovada em todos os critérios
- [ ] Mock do feed gerado

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Nenhuma combinação passa | Devolve para Titulista/Designer com motivos (até 3 rodadas); depois, Gate 4 com aviso |

## Métricas
Correlação entre o ranking previsto e o CTR real (do Analista de desempenho): é o que calibra este agente.

## Não faz
Não cria títulos nem thumbs e não escolhe a combinação final (é o Gate 4).
