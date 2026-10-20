# Editor

> **Departamento:** 7 · Montagem & finalização · **Tipo:** LLM-R + Ferr. (OTIO) · **Nó:** `montagem.editor` · **Doc-mãe:** [05 §3.7](../../05-arquitetura-agentes-langgraph.md) · **Montagem:** [04 §6](../../04-cinematografia.md)

## Missão
Montar a **linha do tempo** do episódio: alinhar os planos à narração e aplicar o ritmo desenhado, os cortes J/L e os match cuts do doc 04.

## Posição no fluxo
- **Antes:** Animação (planos aprovados + VFX) e Áudio (narração + mix v1).
- **Depois:** Grafismo → Finalizador → Legendador → QA.
- **Retorno:** recebe ajustes por timecode do Gate 3 e devoluções do QA.

## Entradas
| Campo | Para quê |
|---|---|
| `decupagem.planos` | Ordem, duração planejada, `transicao_saida` |
| `assets.planos[].render` e `.vfx` | Vídeos e camadas |
| `audio.narracao`, `audio.mix` | A narração é a espinha da timeline |
| `roteiro.esqueleto` | Capítulos e viradas |
| Notas do Diretor de voz | Blocos que não cabem no tempo |

## Saída
| Campo | Conteúdo |
|---|---|
| `timeline` | Linha do tempo em formato OTIO/EDL (caminho + hash), versão do corte, duração total, marcadores de capítulo, lista de diferenças de duração × decupagem |

## Regras de trabalho
1. **A narração dita o tempo.** Os planos são ajustados à voz, não o contrário (exceto silêncios, que são da imagem).
2. **Medianas do doc 04 §6.1** por bloco. Ajustar a duração do plano em até ±20%; acima disso, avisa a Direção.
3. **Match cuts** previstos na decupagem: fogueira → olho, brasa → estrela, fumaça → canto das sereias, fio do tear → corda do arco.
4. **Corte J/L:** a voz do bloco seguinte entra antes da imagem (J); o som do monstro continua sobre o Contador (L).
5. **Corte no silêncio:** a imagem corta junto com a volta do som.
6. **Montagem por friso** nas passagens de tempo (dolly lateral sobre várias sombras).
7. **Repetição com variação:** o plano de abertura volta no fim do Ato II e no fim do episódio, com o fogo cada vez mais baixo.
8. **Capítulos:** marcador no início de cada cartela; o primeiro capítulo em 0:00.
9. **Pede remix** ao Mixador se os tempos mudarem depois do mix v1.

## Critérios de aceite
- [ ] Duração total dentro de ±5% da duração-alvo
- [ ] Nenhum plano faltando ou repetido sem intenção
- [ ] Todos os match cuts e cortes J/L da decupagem aplicados
- [ ] Capítulos marcados

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Plano ainda na fila humana | Usa o storyboard como ocupante (marcado em vermelho) e segue; o QA técnico bloqueia até ser trocado |
| Bloco longo demais para os planos | Estica planos dentro dos ±20%; acima disso, pede plano extra à Direção |

## Métricas
Ajustes por timecode no Gate 3 · retenção por bloco × mediana de duração dos planos.

## Não faz
Não cria grafismo, não aplica grão/cor e não gera legendas.
