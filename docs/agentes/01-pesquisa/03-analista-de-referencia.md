# Analista de referência

> **Departamento:** 1 · Pesquisa · **Tipo:** Ferr. + LLM-V · **Nó:** `pesquisa.analista_referencia` · **Doc-mãe:** [05 §3.1](../../05-arquitetura-agentes-langgraph.md) · **Método:** [doc 02](../../02-analise-video-referencia.md)

## Missão
Medir como os concorrentes contaram **o mesmo mito**: ritmo de corte, cenas, cor por lugar, forças e lacunas. Assim o Lume sabe exatamente **onde superar**, em vez de copiar.

## Posição no fluxo
- **Antes:** Showrunner.
- **Em paralelo:** Pesquisador de fontes e Analista de demanda.
- **Depois:** os dados alimentam o Arquiteto de estrutura, o Editor de retenção e o Diretor (decupagem).

## Entradas
| Campo | Para quê |
|---|---|
| `episodio.mito` | Que vídeos procurar |
| URLs de referência | Fornecidas na pauta ou encontradas pelo Analista de demanda (até 5 vídeos) |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `pesquisa.referencia` | Por vídeo: duração, nº de planos, **mediana de duração por plano** por bloco, curva de ritmo, cenas cobertas/puladas, cor dominante por lugar, caminho das folhas de contato |
| | Síntese: o que todos fazem (o mínimo esperado), o que ninguém faz (a lacuna) e erros factuais visíveis |

## Ferramentas
ffmpeg (detecção de cena por diferença de quadro), gerador de folhas de contato (1 quadro por plano), LLM-V para descrever cenas e cor.

## Regras de trabalho
1. **Seguir o método do doc 02**, para que os números sejam comparáveis entre episódios e com a referência original.
2. **Detecção de cena:** limiar padrão de mudança de quadro, revisado pelo LLM-V nos trechos de transição suave (fumaça e fades enganam o detector).
3. **Mediana, não média:** a média distorce por causa de planos muito longos.
4. **Medir por bloco** (gancho, viagem, clímax, final), porque é assim que o doc 04 §6.1 define os alvos.
5. **Só análise.** O vídeo de referência nunca é usado como material (nem quadros, nem áudio) no episódio. As folhas de contato ficam só para estudo interno.

## Critérios de aceite
- [ ] Cada vídeo tem nº de planos, mediana por bloco e mapa de cenas
- [ ] A síntese lista pelo menos 3 lacunas concretas
- [ ] As folhas de contato estão no storage, com caminho + hash no estado

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Vídeo indisponível ou bloqueado | Pula e registra; o mínimo é 1 referência |
| Detecção de cena claramente errada (ex.: 2 planos em 20 min) | Refaz com outro limiar; se continuar, marca o vídeo como "não medível" |

## Métricas
Diferença entre o ritmo planejado do Lume e o da referência · nº de lacunas que viraram cenas no roteiro.

## Não faz
Não define o ritmo do Lume (isso é o doc 04 + Diretor), não baixa material para reutilizar e não avalia título/thumb (é a Embalagem).
