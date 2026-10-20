# Roteirista (voz do Contador)

> **Departamento:** 2 · Roteiro · **Tipo:** LLM-R · **Nó:** `roteiro.roteirista` · **Doc-mãe:** [05 §3.2](../../05-arquitetura-agentes-langgraph.md) · **Tom:** [03 §1 e §11](../../03-identidade-visual-lume.md)

## Missão
Escrever o texto que **o Contador fala**, bloco a bloco, com as marcações de cena que a Direção vai decupar.

## Posição no fluxo
- **Antes:** Arquiteto de estrutura.
- **Depois:** os 3 revisores em paralelo (Retenção, Fidelidade, Tom).
- **Ciclo:** recebe as notas e revisa. **Máximo de 3 voltas**; depois disso, vai ao Gate 1 com as notas pendentes.

## Entradas
| Campo | Para quê |
|---|---|
| `roteiro.esqueleto` | Blocos, batidas, orçamento de palavras |
| `pesquisa.fatos` e `pesquisa.nomes_canonicos` | O que pode ser dito e com que nomes |
| `pesquisa.fontes` | Para citações diretas (selo de fonte) |
| `roteiro.notas` | Notas dos revisores (a partir da 2ª volta) |
| `aprovacoes` (Gate 1) | Comentários humanos, quando o gate pede nova versão |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `roteiro.blocos` | Por bloco: texto narrado, marcações, ids dos fatos usados, fontes citadas, contagem de palavras, duração estimada |
| `roteiro.versoes` | Histórico: versão, o que mudou e qual nota foi atendida |

**Marcações dentro do texto:**
| Marcação | Uso |
|---|---|
| `[CONTADOR]` / `[PAREDE]` | Em qual mundo o trecho acontece |
| `[CENA: …]` | O que a sombra faz (ação, não enquadramento: o plano é da Direção) |
| `[CITAÇÃO: fonte, canto, verso]` | Fala citada; vira selo de fonte na tela |
| `[SILÊNCIO]` | Pausa dramática pedida pelo texto (1–2 s) |
| `[CAPÍTULO: nome]` | Início de capítulo (cartela) |

## Regras de trabalho
1. **Abertura fixa:** *"O fogo ainda conta as mesmas histórias."* **Fechamento fixo:** *"O lume apaga. A história fica."*
2. **Tom do doc 03 §11:** frases curtas, presente narrativo, grave e próximo. Nada de "você não vai acreditar", gíria, "galera" ou meme.
3. **O Contador é quem lembra:** não é deus nem personagem. Pode comentar ("e é aqui que ele erra"), mas não opina sobre o espectador.
4. **Todo fato tem id.** Frase factual sem id de fato é proibida. Descrição sensorial (o frio da caverna, o cheiro do mar) é livre, desde que não mude **quem, o quê, quanto ou a ordem**.
5. **Variantes são declaradas** ("em outra versão…"), nunca misturadas em silêncio.
6. **Nomes:** usar `nomes_canonicos`, na forma portuguesa da tradição grega.
7. **Escrever para o ouvido:** uma ideia por frase, números por extenso quando são impacto ("Seiscentos homens saíram de Troia. Um voltou.").
8. **Respeitar o orçamento de palavras** de cada bloco (±10%).
9. **Escrever para a imagem muda:** a marcação `[CENA]` precisa contar a história mesmo sem som (doc 04 §10, "funciona sem som?").

## Critérios de aceite
- [ ] Abertura e fechamento rituais presentes e literais
- [ ] 100% das frases factuais com id de fato
- [ ] Todos os blocos dentro do orçamento de palavras (±10%)
- [ ] Todas as citações com fonte e localização
- [ ] Todas as notas bloqueantes da volta anterior atendidas ou respondidas com justificativa

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Notas de revisores se contradizem (ex.: Retenção pede gancho mais forte, Fidelidade bloqueia o exagero) | **Fidelidade vence sempre**; registra o conflito na versão |
| 3ª volta ainda com nota bloqueante | Para e vai ao Gate 1 com as notas pendentes destacadas |

## Métricas
Nº de voltas até aprovar · nº de notas bloqueantes por versão · % do texto alterado no Gate 1 (critério da Fase 0 → 1 do doc 06 §8).

## Não faz
Não define tipo de plano, câmera, nível de fogo nem música. Não inventa fatos para "melhorar a história".
