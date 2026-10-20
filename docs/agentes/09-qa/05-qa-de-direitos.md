# QA de direitos

> **Departamento:** 9 · QA · **Tipo:** Ferr. (+ LLM-R para ler licenças) · **Nó:** `qa.direitos` · **Bloqueante** · **Doc-mãe:** [05 §3.9](../../05-arquitetura-agentes-langgraph.md)

## Missão
Garantir que **todo** material de terceiros no episódio (música, SFX, textura, tradução, fonte tipográfica) tem licença registrada e compatível com monetização no YouTube.

## Posição no fluxo
- **Antes:** Montagem.
- **Em paralelo:** os outros agentes de QA.
- **Depois:** reprovado → departamento que trouxe o material; aprovado → Gate 3.

## Entradas
| Campo | Para quê |
|---|---|
| `timeline` | Lista de tudo o que está no corte |
| `audio.sfx`, `audio.trilha` | Licenças de som |
| `assets.indice` (Store) | Origem e licença de marionetes e texturas |
| `pesquisa.fontes` | Situação de direitos das traduções citadas |
| `embalagem.metadados` | Créditos obrigatórios na descrição |

## Saída
| Campo | Conteúdo |
|---|---|
| `qa` (append) | Por item: id, tipo, licença, escopo, resultado, departamento responsável |

## Checagens
| Checagem | Critério |
|---|---|
| Cobertura | 100% dos itens da timeline têm licença registrada |
| Escopo | A licença cobre uso comercial/monetização e o território |
| Atribuição | Toda licença que exige crédito aparece na descrição |
| Traduções | Citação de tradução protegida dentro do limite de citação curta e com crédito |
| Fontes tipográficas | Licença permite uso em vídeo |
| Material de referência | Nenhum quadro ou áudio de vídeos concorrentes (Analista de referência) |

## Regras de trabalho
1. **Sem licença = bloqueia.** Não existe "provavelmente é livre".
2. **Licença lida, não suposta:** o LLM-R lê o texto da licença registrada e confirma o escopo.

## Critérios de aceite
- [ ] 100% dos itens com licença válida
- [ ] Todos os créditos obrigatórios na descrição

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Item sem licença | Volta para o departamento de origem para trocar o item |
| Licença ambígua | Fila humana |

## Métricas
Reivindicações de Content ID depois da publicação (meta: zero) · itens bloqueados por episódio.

## Não faz
Não procura material substituto e não negocia licenças.
