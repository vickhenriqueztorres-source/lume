# Supervisor musical

> **Departamento:** 6 · Áudio · **Tipo:** LLM-R + Ferr. · **Nó:** `audio.supervisor_musical` · **Doc-mãe:** [05 §3.6](../../05-arquitetura-agentes-langgraph.md) · **Música:** [04 §7](../../04-cinematografia.md) e [03 §10](../../03-identidade-visual-lume.md)

## Missão
Montar a **trilha do episódio** com leitmotivs, a partir de biblioteca licenciada, de forma que a música conte quem está em cena mesmo sem imagem.

## Posição no fluxo
- **Antes:** Gate 2.
- **Em paralelo:** Diretor de voz, Narrador e Sound designer.
- **Depois:** Mixador.

## Entradas
| Campo | Para quê |
|---|---|
| `roteiro.esqueleto` | Atos, viradas e clímax |
| `decupagem.planos` | Personagens em cena e duração |
| `color_script` | Nível de fogo (intensidade da música) |
| Biblioteca musical licenciada | Fonte |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `audio.trilha` | Por cena: faixa/stems (caminho + hash), início, fim, leitmotiv usado, intensidade, **licença** |
| | Mapa de leitmotivs do episódio |

## Leitmotivs (doc 04 §7)
| Personagem/situação | Motivo |
|---|---|
| Odisseu | Lira de 3 notas (as mesmas do sonic logo) |
| Poseidon | Drone grave com água |
| Penélope | Tear rítmico |
| Mortos | Coro sem palavras |

## Regras de trabalho
1. **Instrumentação** (doc 03 §10): percussão de pele, drones graves, sopros antigos (aulos), coro masculino só nos clímax. Nada de orquestra épica genérica, sintetizador moderno ou batida eletrônica.
2. **Sem música no Mundo do Contador:** lá é só fogo e vento.
3. **Intensidade segue o fogo:** nível 1–2 = drone ou nada; 3 = percussão leve; 4 = percussão cheia; 5 = coro + corte para silêncio.
4. **Silêncio dramático vence a música:** antes das revelações, a música sai junto com o fogo.
5. **Leitmotiv na primeira aparição** de cada personagem e nas viradas ligadas a ele.
6. **Stems separados** (percussão, drone, melodia, coro) para o Mixador conseguir abaixar só uma parte embaixo da voz.
7. **Licença obrigatória**, com escopo que cubra monetização no YouTube.

## Critérios de aceite
- [ ] Todo personagem principal tem o leitmotiv na primeira aparição
- [ ] Nenhuma música nos planos do Contador
- [ ] Todo trecho com licença e stems

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Leitmotiv inexistente na biblioteca | Usa a peça mais próxima e marca para encomenda de composição (fila humana) |
| Licença sem cobertura de monetização | Descarta a faixa |

## Métricas
Reivindicações de Content ID depois da publicação (meta: zero) · notas de música no Gate 3.

## Não faz
Não mixa, não escolhe SFX e não gera música com IA a partir de obras de terceiros.
