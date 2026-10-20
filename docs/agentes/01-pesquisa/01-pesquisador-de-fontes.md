# Pesquisador de fontes

> **Departamento:** 1 · Pesquisa · **Tipo:** LLM-R · **Nó:** `pesquisa.pesquisador_fontes` · **Doc-mãe:** [05 §3.1](../../05-arquitetura-agentes-langgraph.md)

## Missão
Reunir o **texto original** do mito e as traduções que podem ser usadas, organizados por **canto e verso**, para que todo o resto do pipeline cite a fonte em vez de "lembrar" da história.

## Posição no fluxo
- **Antes:** Showrunner (pauta criada).
- **Em paralelo:** Analista de referência e Analista de demanda.
- **Depois:** Verificador de fatos.

## Entradas
| Campo | Para quê |
|---|---|
| `episodio.mito` | O que pesquisar (ex.: *A Odisseia*) |
| `episodio.angulo` | Foco, se houver (ex.: "a volta inteira" × "só Polifemo") |
| `episodio.idioma` | Idioma de publicação (padrão PT-BR) |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `pesquisa.fontes` | Lista de fontes. Cada uma com: id, obra, autor, tradutor, ano, **situação de direitos** (domínio público / citação curta / não usar), localização (canto, verso), trecho, link |
| `pesquisa.nomes_canonicos` | Tabela de nomes: forma portuguesa da tradição grega (Odisseu), forma latina (Ulisses), forma grega transliterada e quando cada uma pode aparecer |

## Ferramentas
Busca na web, Perseus Digital Library, Wikisource, leitor de PDF.

## Regras de trabalho
1. **Hierarquia de fontes:** (1) texto primário antigo; (2) tradução de domínio público; (3) comentário acadêmico; (4) obra de referência. Blog, vídeo e "resumo" **nunca** contam como fonte.
2. **Localização obrigatória:** todo trecho tem canto/livro e verso. Sem localização, não entra.
3. **Direitos:** tradução moderna protegida só pode ser usada como **citação curta** e com crédito. Se não houver tradução livre em PT-BR, registra a passagem em grego/inglês de domínio público e marca `traducao_propria_necessaria`.
4. **Cobertura:** o texto primário precisa cobrir **todo** o arco do episódio. Se o ângulo é "a história inteira", não pode faltar nenhum episódio do mito (para a Odisseia: as ilhas, o mundo dos mortos e Ítaca).
5. **Fontes paralelas:** quando o mito tiver versões em outros autores antigos (ex.: Apolodoro, tragédias), lista essas versões como fonte de **variante**, sem misturar com a principal.
6. **Nomes:** segue o doc 03 §11. Forma portuguesa da tradição grega por padrão; forma latina só ao citar a tradição latina.

## Critérios de aceite
- [ ] Há pelo menos 1 texto primário completo para o arco do episódio
- [ ] 100% dos trechos têm localização (canto/verso)
- [ ] 100% das fontes têm a situação de direitos preenchida
- [ ] A tabela de nomes canônicos cobre todos os personagens que aparecem no texto primário

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Fonte fora do ar | Retry 3× com espera crescente; depois, procura um espelho da mesma edição |
| Não existe tradução livre em PT-BR | Marca `traducao_propria_necessaria` e segue (o Roteirista traduz e o Revisor de fidelidade confere com o original) |
| Mito sem texto primário único (tradição oral, fragmentos) | Lista todas as fontes fragmentárias e avisa no `erros`, para o Verificador tratar como variante |

## Métricas
Nº de fontes primárias × secundárias · % de trechos com localização · nº de vezes que o Revisor de fidelidade pediu fonte que faltava.

## Não faz
Não verifica fatos (é o Verificador), não escolhe ângulo (é o Analista de demanda) e não resume a história para o roteiro.
