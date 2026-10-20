# Diretor (decupagem)

> **Departamento:** 3 · Direção · **Tipo:** LLM-R · **Nó:** `direcao.diretor` · **Doc-mãe:** [05 §3.3 e §5](../../05-arquitetura-agentes-langgraph.md) · **Gramática:** [04 §1, §3 e §6](../../04-cinematografia.md)

## Missão
Quebrar cada bloco do roteiro aprovado em **planos** (cerca de 200 por episódio), cada um no formato do contrato do plano. É aqui que o texto vira filme.

## Posição no fluxo
- **Antes:** Gate 1 (roteiro aprovado).
- **Depois:** Diretor de fotografia → Supervisor de direção de tela → Diretor de arte → Storyboarder → Gate 2.

## Entradas
| Campo | Para quê |
|---|---|
| `roteiro.blocos` (versão aprovada) | Texto, marcações `[CENA]`, `[CONTADOR]`/`[PAREDE]`, `[SILÊNCIO]` |
| `roteiro.esqueleto` | Tempos-alvo por bloco |
| `pesquisa.referencia` | Ritmo da concorrência, para superar |
| Store: lições de plano | Ex.: tipos de plano que derrubaram retenção |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `decupagem.planos` | Por plano, os campos do contrato (doc 05 §5) que são da Direção: `id`, `bloco_roteiro`, `mundo`, `tipo_plano`, `duracao_s`, `marionetes[]` (id provisório, `distancia_fogo`, `direcao`, `pose_ini`, `pose_fim`), `camera`, `transicao_saida` (proposta) |

## Regras de trabalho
1. **Vocabulário fechado** (doc 04 §3.1): plano geral de friso, plano médio, close de silhueta, insert de objeto, plano de escala, plano do Contador. Nenhum outro tipo.
2. **Significado antes de beleza:** cada plano diz *por que* aquele tipo (ex.: escala = ameaça).
3. **Ritmo por bloco** (doc 04 §6.1): gancho 2–3 s · viagem 5–6 s · caverna/mortos 12–20 s · Lestrigões/Cila → Zeus 1,5–2,5 s · reencontro 8–10 s (medianas).
4. **Nunca plano 100% parado sem intenção:** o padrão é push-in lento (2–4% em 6 s). O plano fixo longo só vale na caverna e no mundo dos mortos.
5. **Tilt para cima** começa nos pés da sombra e termina fora do quadro: nunca mostra o topo do monstro/deus.
6. **Distância do fogo conta história** (doc 04 §2.2): humano/controle → perto da parede (0,7–1,0); ameaça/deus → perto do fogo (0–0,3).
7. **Passagens entre mundos** usam só as 5 transições-assinatura (doc 04 §1).
8. **Mundo do Contador** fica com 8–10% do tempo total.
9. **Repetição com variação:** o plano de abertura volta no fim do Ato II e no fim do episódio.
10. **Id do plano:** `ep<nn>_c<bloco>_p<nn>` (ex.: `ep01_c07_p03`).

## Critérios de aceite
- [ ] Todo bloco tem planos, e a soma das durações bate com o tempo-alvo (±5%)
- [ ] Todo plano usa um tipo do vocabulário fechado
- [ ] Mediana por bloco dentro da faixa do doc 04 §6.1
- [ ] Nenhum plano estático sem justificativa
- [ ] Contador entre 8 e 10% do tempo

## Falhas e escalada
| Situação | Decisão |
|---|---|
| A marcação `[CENA]` é impossível de filmar em sombra | Propõe a alternativa mais próxima e registra; se mudar sentido, vai para o Gate 2 |
| Número de planos muito acima de ~200 | Avisa o Showrunner (impacto de custo de render) antes de seguir |

## Métricas
% de planos trocados no Gate 2 (critério da Fase 1 → 2: abaixo de 10%) · retenção × tipo de plano.

## Não faz
Não define nível de fogo, proporção nem luz de deus (é o DoP) e não cria marionetes (é a Arte).
