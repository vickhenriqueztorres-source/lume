# Redator de metadados

> **Departamento:** 8 · Embalagem · **Tipo:** LLM-R · **Nó:** `embalagem.redator_metadados` · **Doc-mãe:** [05 §3.8](../../05-arquitetura-agentes-langgraph.md)

## Missão
Escrever **descrição, capítulos, fontes citadas, créditos e tags**, para que o vídeo seja encontrado, navegável e transparente sobre de onde vem cada informação.

## Posição no fluxo
- **Antes:** Gate 3.
- **Em paralelo:** Titulista, Designer de thumbnail e Cortador de Shorts.
- **Depois:** Gate 4 → Publicador.

## Entradas
| Campo | Para quê |
|---|---|
| `master.capitulos` | Timecodes dos capítulos (= cartelas) |
| `pesquisa.fontes` | Fontes a citar |
| `pesquisa.angulos` | Termos de busca |
| `audio.sfx`, `audio.trilha`, `assets.indice` | Créditos e licenças que exigem atribuição |
| `roteiro.blocos` | Resumo fiel |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `embalagem.metadados` | Descrição, lista de capítulos, fontes, créditos, tags, idioma, categoria |

## Estrutura da descrição
| Parte | Conteúdo |
|---|---|
| **2 primeiras linhas** | A promessa do vídeo, no tom do Lume (é o que aparece antes do "mais") |
| Resumo | 2–3 frases sem spoiler do clímax |
| **Capítulos** | `0:00 …` + um por cartela, com o nome da cartela |
| **Fontes** | Obra, autor, tradução, cantos usados |
| **Créditos** | Músicas e sons que exigem atribuição, conforme a licença |
| Tagline | *Mitos ganham vida quando há fogo para contá-los.* |

## Regras de trabalho
1. **Capítulos = cartelas:** mesmos nomes, mesmos tempos, primeiro em 0:00 (o YouTube exige).
2. **Fontes reais e específicas**, com canto/livro; nada de "fontes diversas".
3. **Tags:** nome do mito, personagens principais, termos do ângulo; sem tags enganosas nem nomes de outros canais.
4. **Sem link encurtado** e sem pedidos agressivos de inscrição.
5. **Créditos completos:** toda licença que exige atribuição aparece (o QA de direitos confere).

## Critérios de aceite
- [ ] Capítulos começam em 0:00 e batem com `master.capitulos`
- [ ] Toda fonte usada no roteiro aparece na descrição
- [ ] Todo crédito obrigatório presente

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Descrição passa do limite da plataforma | Corta primeiro o resumo, nunca as fontes nem os créditos |

## Métricas
% de tráfego vindo de busca · cliques em capítulos.

## Não faz
Não escreve título, não cria thumb e não publica.
