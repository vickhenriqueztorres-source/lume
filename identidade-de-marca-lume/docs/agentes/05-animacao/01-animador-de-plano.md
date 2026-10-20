# Animador de plano

> **Departamento:** 5 · Animação & render · **Tipo:** LLM-R + Ferr. · **Nó:** `animacao.animador` · **Doc-mãe:** [05 §3.5 e §5](../../05-arquitetura-agentes-langgraph.md) · **Gramática:** [04 §2–§4](../../04-cinematografia.md)

## Missão
Traduzir o contrato de um plano em **parâmetros de cena** exatos: onde cada marionete fica, como ela se move, como o fogo respira e como a câmera anda.

## Posição no fluxo
- **Antes:** Gate 2 + assets do plano registrados pelo Bibliotecário.
- **Depois:** Montador de cena 3D. Roda por `Send`: **um plano por execução**.
- **Loop:** Animador → Montador → Render → Revisor de plano. Até 2 refações automáticas.

## Entradas
| Campo | Para quê |
|---|---|
| Contrato do plano (`decupagem.planos[<id>]`) | Tudo o que o plano precisa ser |
| `assets.indice` | Rig de cada marionete e textura da parede |
| `assets.planos[<id>].revisao` | Motivo da refação, quando é uma nova tentativa |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `assets.planos[<id>].cena` | Arquivo de cena parametrizado (caminho + hash), com: |
| | posição de cada marionete (x, altura, **distância do fogo** de 0 = no fogo a 1 = na parede) no início e no fim |
| | poses-chave por quadro (a partir das poses-base do rig) |
| | curva de intensidade do fogo e tremulação |
| | câmera: lente, posição e alvo nos quadros-chave, tremor (se houver) |
| | luzes de deus (posição, tipo, curva) |

## Regras de trabalho
1. **Distância do fogo = tamanho e nitidez** (doc 04 §2.2). Monstro que "se aproxima" é a marionete indo do fogo para a parede, não um zoom de câmera.
2. **Parede a 12 qps:** as poses mudam em degraus de 2 quadros (24p com pose segurada), e o motion blur fica a cargo do render. Contador e fogo continuam a 24 qps.
3. **Push-in padrão:** 2–4% de escala em 6 s, se o plano não tiver outro movimento.
4. **Tilt para cima:** começa nos pés da sombra e termina com o topo fora do quadro.
5. **Tremor de câmera:** 6–10 quadros, só em impacto.
6. **Curva de fogo:** respeita o nível e a curva do plano (`fogo`). Tremulação na frequência do nível (0,5 / 1 / 2 / 4 Hz) com variação orgânica, nunca senoide perfeita.
7. **Direção de tela:** a marionete anda no sentido do campo `direcao`; dolly lateral no mesmo sentido.
8. **Duas sombras quando um deus intervém:** a luz de deus é posicionada para gerar a segunda sombra do herói na parede.
9. **Refação:** lê o motivo do Revisor e muda **só** o parâmetro apontado (não recomeça do zero).

## Critérios de aceite
- [ ] Duração da cena = `duracao_s`
- [ ] Toda marionete do contrato está presente, com rig válido
- [ ] Movimento de câmera é o do contrato
- [ ] O hash dos campos visuais foi recalculado (se igual ao último render aprovado, o plano pula o render)

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Pose pedida não existe no rig | Usa a pose-base mais próxima e avisa o Rigger (pedido de pose nova para próximos planos) |
| 3ª falha no Revisor | O plano vai para a fila humana; os outros planos seguem |

## Métricas
Taxa de refação por tipo de plano · motivos de refação mais comuns (viram ajuste de prompt).

## Não faz
Não renderiza, não muda o tipo de plano ou a duração e não troca marionetes.
