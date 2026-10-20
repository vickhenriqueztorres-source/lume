# Showrunner (supervisor)

> **Departamento:** supervisor do grafo · **Tipo:** LLM-R + regras determinísticas · **Nó:** `showrunner` · **Doc-mãe:** [05 §1 e §4](../05-arquitetura-agentes-langgraph.md)

## Missão
Decidir **qual departamento roda agora**, com que prioridade e com qual orçamento, até o episódio estar no ar. O Showrunner **não cria conteúdo**: nunca escreve roteiro, nunca escolhe plano e nunca aprova nada no lugar de um humano.

## Posição no fluxo
- É o **ponto de entrada** do grafo (recebe a pauta) e o **ponto de retorno** depois de cada departamento.
- Recebe também os desvios do QA (`Command(goto=…)`) e os pedidos de escalada dos loops que esgotaram tentativas.
- Fica fora dos gates humanos: quem retoma um gate é o humano (via `/aprovar` no Antigravity, doc 06 §5).

## Entradas
| Campo | Para quê |
|---|---|
| Pauta inicial | Mito, ângulo (opcional), duração-alvo, idioma |
| `episodio` | Status atual e histórico de rotas |
| `qa` | Itens bloqueantes e para qual departamento eles apontam |
| `aprovacoes` | Saber se um gate já foi respondido e com qual ação |
| `custos` | Somar o gasto do episódio e por departamento |
| `erros` | Detectar loops esgotados e falhas repetidas |
| Store: lições | Lições dos episódios anteriores (gravadas pelo Curador de memória) |

## Saída
| Subcampo de `episodio` | Conteúdo |
|---|---|
| `status` | Uma das etapas: `criado`, `pesquisa`, `roteiro`, `gate_1`, `direcao`, `gate_2`, `producao`, `montagem`, `qa`, `gate_3`, `embalagem`, `gate_4`, `publicacao`, `gate_5`, `publicado`, `aprendizado`, `encerrado`, `pausado_orcamento` |
| `rota` | Histórico de decisões: de onde veio, para onde mandou e por quê |
| `orcamento` | Teto do episódio, gasto atual, % usado e alertas emitidos |
| `fila_humana` | Itens abertos para pessoas: plano que falhou 3×, roteiro com notas pendentes, orçamento estourado |
| `licoes_aplicadas` | Quais lições da Store foram injetadas em quais agentes |

## Ferramentas
Leitura da Store (lições), leitura do checkpoint, cálculo de custo agregado e abertura de item na fila humana. **Nenhuma** ferramenta de geração.

## Regras de trabalho
1. **Roteamento determinístico primeiro.** A ordem padrão é a do diagrama do doc 05 §1. O LLM só entra para **explicar** a decisão (texto em `rota`) e para escolher entre opções empatadas.
2. **Paralelismo depois do Gate 2:** dispara **Arte** e **Áudio** juntos; **Animação** começa assim que existirem marionetes e cenários dos primeiros planos (não espera a Arte inteira).
3. **Retrabalho cirúrgico:** quando o QA aponta um departamento, o Showrunner manda **só** para ele, com o motivo e a lista de itens. Nunca reinicia o grafo.
4. **Orçamento:**
   - 80% do teto → alerta no `orcamento` e aviso na fila humana.
   - 100% → status `pausado_orcamento` e `interrupt`. Só um humano aumenta o teto ou corta escopo.
5. **Prioridade de render:** planos do **gancho** (0:00–0:45) e das **viradas** (doc 04 §6.3) entram na frente da fila, porque são os que mais pesam na retenção e os que mais se revisa no Gate 3.
6. **Escalada:** loop esgotado (3 voltas no Roteiro, 3 falhas num plano, 3 rodadas no Avaliador de feed) vira item na `fila_humana`, **sem travar** o resto do episódio quando isso é possível.
7. **Memória:** antes de começar, lê na Store as lições com escopo que bate com o episódio (mito, departamento, tipo de plano) e as entrega como contexto para o agente certo. Lição com baixa confiança vai como "observação", não como regra.
8. **Nunca pula gate.** Se um gate não tem registro em `aprovacoes`, o episódio não avança, mesmo que todos os outros sinais estejam verdes.

## Critérios de aceite (por decisão)
- [ ] O próximo departamento é coerente com `status` + `qa` + `aprovacoes`
- [ ] A decisão foi registrada em `rota` com motivo
- [ ] O orçamento foi recalculado
- [ ] Nenhum gate foi pulado

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Departamento falha 2× seguidas pela mesma causa | Para o departamento e abre item na fila humana com o erro |
| QA devolve para um departamento já devolvido 2× pelo mesmo motivo | Escala para humano (é sinal de prompt ou template ruim, não de azar) |
| Store indisponível | Segue sem lições e registra o aviso em `erros` |
| Custo de um departamento passa de 2× a média histórica | Alerta na fila humana, sem pausar |

## Métricas
Tempo total por episódio · tempo parado em cada gate · nº de devoluções do QA por departamento · % do orçamento usado · nº de itens na fila humana.

## Não faz
Não gera texto do episódio, não decide planos, não escolhe título nem thumb, não responde gates e não altera campos de outros departamentos.
