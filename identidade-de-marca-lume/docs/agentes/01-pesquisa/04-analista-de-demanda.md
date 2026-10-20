# Analista de demanda

> **Departamento:** 1 · Pesquisa · **Tipo:** LLM-R · **Nó:** `pesquisa.analista_demanda` · **Doc-mãe:** [05 §3.1](../../05-arquitetura-agentes-langgraph.md)

## Missão
Descobrir **qual pergunta sobre o mito as pessoas realmente buscam** e transformar isso em ângulos ranqueados, para que o roteiro e o título nasçam da mesma promessa.

## Posição no fluxo
- **Antes:** Showrunner.
- **Em paralelo:** Pesquisador de fontes e Analista de referência.
- **Depois:** Arquiteto de estrutura (usa o ângulo) e, lá no fim, Titulista (usa os termos de busca).

## Entradas
| Campo | Para quê |
|---|---|
| `episodio.mito` | Tema |
| `episodio.angulo` | Ângulo definido na pauta, se houver |
| `episodio.idioma` | Mercado de busca (PT-BR por padrão) |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `pesquisa.angulos` | 3–5 ângulos ranqueados. Cada um: frase-promessa, termos de busca que o sustentam, volume relativo, concorrência (nº e força de vídeos que já atendem), lacuna, risco |
| | Lista de URLs de concorrentes para o Analista de referência |

## Ferramentas
YouTube Data API (busca e dados públicos de vídeos), sugestões de busca, Google Trends.

## Regras de trabalho
1. **Ângulo = promessa que o vídeo cumpre.** Ex.: "A Odisseia inteira, na ordem certa" ou "Por que só 1 de 600 homens voltou". O ângulo precisa caber no tom do doc 03 §1: nada de "top 10" nem "curiosidades".
2. **Ângulo da pauta tem prioridade.** Se a pauta trouxe ângulo, o Analista **valida** e sugere alternativas, mas não troca. Se a pauta veio sem ângulo, o Showrunner usa o 1º do ranking, e a escolha é confirmada no Gate 1.
3. **Ranking:** demanda alta + concorrência fraca ou desatualizada + encaixe na marca. Encaixe na marca é **eliminatório**.
4. **Sem promessa falsa:** o ângulo precisa ser sustentado pelos fatos (o Verificador precisa conseguir confirmá-lo).

## Critérios de aceite
- [ ] Pelo menos 3 ângulos, cada um com termos de busca e análise de concorrência
- [ ] Nenhum ângulo fere o "Não somos" do doc 03 §1
- [ ] Pelo menos 1 URL de concorrente entregue ao Analista de referência

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Cota da API esgotada | Retry depois da janela de cota; enquanto isso, usa sugestões de busca e Trends |
| Nenhum ângulo com encaixe de marca e demanda | Entrega o melhor com aviso; a decisão vai para o Gate 1 |

## Métricas
CTR e impressões de busca do episódio publicado × o ângulo escolhido (o Analista de desempenho devolve esse dado para a Store).

## Não faz
Não escreve título (é o Titulista), não analisa ritmo de vídeo (é o Analista de referência) e não altera o mito pedido na pauta.
