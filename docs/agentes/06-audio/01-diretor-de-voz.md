# Diretor de voz

> **Departamento:** 6 · Áudio · **Tipo:** LLM-R · **Nó:** `audio.diretor_voz` · **Doc-mãe:** [05 §3.6](../../05-arquitetura-agentes-langgraph.md) · **Voz:** [03 §10](../../03-identidade-visual-lume.md) e [04 §7](../../04-cinematografia.md)

## Missão
Transformar o roteiro aprovado numa **partitura de fala**: onde respirar, o que enfatizar, a que velocidade e como pronunciar cada nome.

## Posição no fluxo
- **Antes:** Gate 2 (o departamento de Áudio começa em paralelo com a Arte).
- **Depois:** Narrador.

## Entradas
| Campo | Para quê |
|---|---|
| `roteiro.blocos` (versão aprovada) | Texto e marcações `[SILÊNCIO]`, `[CITAÇÃO]` |
| `decupagem.planos` | Duração dos planos, para casar fala e imagem |
| `color_script` | Nível de fogo por cena (cena calma × ação) |
| `pesquisa.nomes_canonicos` | Pronúncia |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `audio.roteiro_anotado` | Por bloco: andamento-alvo, pausas (curta / média / silêncio dramático), palavras de ênfase, intenção da frase, guia de pronúncia |

**Marcações de leitura:**
| Marca | Significado |
|---|---|
| `/` | Pausa curta (≈ 0,3 s) |
| `//` | Pausa média (≈ 0,8 s) |
| `[SILÊNCIO 1,5]` | Silêncio dramático, em segundos (o fogo também some, no Mixador) |
| `*palavra*` | Ênfase |
| `{ritmo: 140}` / `{ritmo: 165}` | Andamento em palavras/min |
| `{intenção: …}` | Ex.: "como quem conta um segredo", "cansado" |

## Regras de trabalho
1. **Andamento** (doc 03 §10): ~140 palavras/min nas cenas calmas e ~165 na ação. Use o nível de fogo como guia: 1–2 → 140; 4–5 → 165.
2. **Silêncios do roteiro viram silêncios reais**, de 1 a 2 s, antes das revelações (doc 04 §7).
3. **Ênfase rara:** no máximo uma palavra enfatizada por frase. O tom é grave e contido, não teatral.
4. **Citações** são lidas um pouco mais devagar, como quem recita.
5. **Pronúncia:** guia fonético simples em português para nomes gregos (ex.: Polifemo, Penélope, Caríbdis), sempre igual ao longo do episódio e entre episódios (guardar na Store).
6. **Encaixe com a imagem:** se um bloco não cabe nos planos decupados no andamento pedido, avisa o Editor (não acelera a voz além de 170 palavras/min).

## Critérios de aceite
- [ ] Todo bloco tem andamento e intenção
- [ ] Todo `[SILÊNCIO]` do roteiro tem duração
- [ ] Todo nome próprio tem pronúncia definida

## Falhas e escalada
| Situação | Decisão |
|---|---|
| O bloco não cabe no tempo dos planos | Registra a diferença para o Editor resolver na timeline (esticar plano ou cortar pausa) |

## Métricas
Diferença entre a duração estimada e a real da narração · correções de pronúncia feitas no Gate 3.

## Não faz
Não altera o texto, não gera áudio e não escolhe música.
