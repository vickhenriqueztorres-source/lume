# Analista de desempenho

> **Departamento:** 10 · Publicação & aprendizado · **Tipo:** Ferr. (YouTube Analytics API) + LLM-R · **Nó:** `publicacao.analista_desempenho` · **Doc-mãe:** [05 §3.10 e §8](../../05-arquitetura-agentes-langgraph.md)

## Missão
Ler como o episódio se saiu e **ligar cada queda ou pico a uma decisão de produção** (plano, bloco, título, thumb), para que o próximo episódio seja melhor.

## Posição no fluxo
- **Antes:** Publicador (episódio público).
- **Roda duas vezes:** **48 h** e **7 dias** depois da publicação (o grafo fica em espera durável entre uma e outra).
- **Depois:** Curador de memória.

## Entradas
| Campo | Para quê |
|---|---|
| Id do vídeo (`episodio`) | Consulta à API |
| `timeline` | Mapear cada segundo da curva de retenção para um plano |
| `decupagem.planos` | Tipo de plano, nível de fogo, mundo, duração |
| `roteiro.esqueleto` | Blocos e viradas |
| `embalagem.titulos`, `embalagem.thumbs`, `embalagem.ranking` | O que foi testado e o que foi previsto |
| `roteiro.notas.retencao` | Mapa de tensão previsto |

## Saída
| Destino | Conteúdo |
|---|---|
| Relatório (anexo ao `episodio`) | Retenção média, curva por segundo, CTR, impressões, origem de tráfego, título/thumb vencedores, desempenho dos Shorts |
| | **Achados:** cada queda ou pico relevante com o timecode, o plano, o tipo de plano e uma hipótese |
| | Comparação: previsto (Editor de retenção, Avaliador de feed) × real |

## Regras de trabalho
1. **Queda relevante:** perda de retenção acima do normal do próprio canal naquele trecho do vídeo (não comparar com vídeos de outros tamanhos).
2. **Hipótese, não certeza:** um achado é "a queda em 6:10 coincide com um plano fixo de 18 s fora da caverna". O Curador decide se vira lição.
3. **Primeiros 45 s à parte:** a retenção do gancho é analisada separadamente.
4. **Calibração dos agentes:** compara o mapa de tensão previsto com a curva real e o ranking do Avaliador de feed com o CTR real.
5. **Só dados agregados** da API; nada de dados pessoais de espectadores.

## Critérios de aceite
- [ ] Relatório de 48 h e de 7 dias gerados
- [ ] Toda queda relevante ligada a um plano
- [ ] Comparação previsto × real feita

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Dados ainda não disponíveis | Tenta de novo em 6 h (até 4×) |

## Métricas
Nº de achados que viraram lição e melhoraram o episódio seguinte.

## Não faz
Não grava lições na Store (é o Curador) e não muda episódios publicados.
