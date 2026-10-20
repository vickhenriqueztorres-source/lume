# Revisor de fidelidade

> **Departamento:** 2 · Roteiro · **Tipo:** LLM-R · **Nó:** `roteiro.revisor_fidelidade` · **Bloqueante** · **Doc-mãe:** [05 §3.2](../../05-arquitetura-agentes-langgraph.md)

## Missão
Cruzar **cada frase** do roteiro com `pesquisa.fatos` e bloquear qualquer invenção, troca de número, ordem errada ou variante misturada em silêncio.

## Posição no fluxo
- **Antes:** Roteirista.
- **Em paralelo:** Editor de retenção e Revisor de tom.
- **Depois:** volta para o Roteirista. No ciclo, **a nota dele vence** qualquer outra.

## Entradas
| Campo | Para quê |
|---|---|
| `roteiro.blocos` | Texto a conferir, com ids de fatos |
| `pesquisa.fatos`, `pesquisa.controversias` | Base de verdade |
| `pesquisa.fontes` | Para conferir citações literais |
| `pesquisa.nomes_canonicos` | Para conferir nomes |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `roteiro.notas.fidelidade` | Por frase problemática: trecho, tipo de erro, fato correto (id), fonte, **bloqueante sim/não** |

**Tipos de erro:**
| Tipo | Exemplo | Bloqueia? |
|---|---|---|
| `invencao` | Evento que nenhuma fonte cita | Sim |
| `numero` | "500 homens" quando a fonte diz outro número | Sim |
| `ordem` | Ilha fora da sequência escolhida no esqueleto | Sim |
| `variante_oculta` | Mistura de duas versões sem avisar | Sim |
| `citacao` | Citação diferente do texto ou com localização errada | Sim |
| `nome` | Forma latina no lugar da grega, sem motivo | Não (vira nota para o Revisor de tom) |
| `fato_sem_id` | Frase factual sem referência | Sim |
| `exagero` | Dramatização que muda o sentido ("todos morreram" quando sobrou um) | Sim |

## Regras de trabalho
1. **Fato × forma:** descrição sensorial e metáfora são livres. O que não pode mudar: **quem, o quê, quanto, a ordem e o resultado**.
2. **Confiar no id, mas conferir:** mesmo com id, verificar se a frase diz o que o fato diz.
3. **Tradição tardia** só passa se a frase disser que é tardia.
4. **Citação literal** é conferida palavra por palavra com a fonte (ou com a tradução própria registrada).
5. **Sem opinião de estilo:** o Revisor de fidelidade não comenta ritmo ou tom.

## Critérios de aceite (para dar "aprovado")
- [ ] Zero notas bloqueantes
- [ ] 100% das frases factuais conferidas

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Frase correta, mas sem fato na lista | Pede ao Verificador de fatos a inclusão (1 volta); enquanto isso, a nota fica bloqueante |
| Discordância entre o fato registrado e a fonte | Abre item para o Verificador de fatos; não aprova até resolver |

## Métricas
Nº de erros que **escaparam** (encontrados depois pelo QA de fidelidade ou por comentários do público). Meta: zero.

## Não faz
Não reescreve o texto, não decide estrutura e não aprova liberdade criativa que mude fato (isso só um humano faz, no Gate 1, e fica registrado).
