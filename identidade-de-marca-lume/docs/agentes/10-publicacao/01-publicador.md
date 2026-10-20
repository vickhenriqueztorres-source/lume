# Publicador

> **Departamento:** 10 · Publicação & aprendizado · **Tipo:** Ferr. (YouTube Data API) · **Nó:** `publicacao.publicador` · **Doc-mãe:** [05 §3.10 e §7](../../05-arquitetura-agentes-langgraph.md) · **Segurança:** [06 §9](../../06-automacao-langgraph-antigravity.md)

## Missão
Subir o episódio **como privado**, com tudo o que a embalagem aprovou, e só mudar a visibilidade depois do Gate 5.

## Posição no fluxo
- **Antes:** Gate 4 (título + thumb escolhidos).
- **Depois:** Gate 5 (opcional, publicação) → agendamento → Analista de desempenho (48 h depois).

## Entradas
| Campo | Para quê |
|---|---|
| `master.arquivo`, `master.legendas` | Vídeo e SRTs |
| `embalagem.titulos`, `embalagem.thumbs` | Os escolhidos no Gate 4 |
| `embalagem.metadados` | Descrição, capítulos, tags |
| `embalagem.shorts` | Shorts aprovados |
| `aprovacoes` | Confirmação dos Gates 4 e 5 |

## Saída
| Destino | Conteúdo |
|---|---|
| `episodio` (via Showrunner) | Id do vídeo no YouTube, situação (`privado` / `agendado` / `publico`), data de publicação |
| `custos` e `erros` (append) | Chamadas de API e falhas |

## Passos
1. **Upload como privado** com chave de operação gravada antes (idempotência).
2. Título, descrição, tags, categoria e idioma.
3. Thumbnail escolhida.
4. Legendas (um arquivo por idioma).
5. Capítulos (já vêm na descrição).
6. Shorts como privados, ligados ao episódio.
7. **Para no Gate 5** (se ativo) e espera a conferência do Studio pelo agente de navegador do Antigravity.
8. Depois da aprovação: agenda ou publica.

## Regras de trabalho
1. **Upload sempre privado.** Só o Gate 5 (ou o Gate 4, se o 5 estiver desativado) muda a visibilidade.
2. **Idempotência rígida:** ao ser retomado depois de um `interrupt`, confere a chave de operação e o id do vídeo; **nunca** sobe o vídeo duas vezes.
3. **OAuth só com escopo de upload** (doc 06 §9). Segredos só em variáveis de ambiente.
4. **Shorts depois do longo:** os Shorts são agendados para depois da publicação do episódio.

## Critérios de aceite
- [ ] Vídeo privado com todos os metadados, thumb e legendas
- [ ] Nenhum upload duplicado
- [ ] Visibilidade mudou só depois do gate

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Upload interrompido | Retoma o upload em partes; não recomeça um novo |
| Cota da API esgotada | Espera a janela de cota e avisa o Showrunner |
| Studio aponta problema de direitos | Para; não publica; fila humana |

## Métricas
Tempo de upload · falhas de API · nº de vezes que a idempotência evitou duplicação.

## Não faz
Não escolhe título nem thumb e **nunca** publica sem registro de gate.
