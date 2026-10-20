# Diretor de fotografia (DoP)

> **Departamento:** 3 · Direção · **Tipo:** LLM-R · **Nó:** `direcao.dop` · **Doc-mãe:** [05 §3.3](../../05-arquitetura-agentes-langgraph.md) · **Luz e cor:** [04 §2, §3.3 e §5](../../04-cinematografia.md)

## Missão
Fazer do fogo o diretor de fotografia: atribuir **nível de fogo, curva, proporção de tela, luz de deus e tipo de parede** a cada cena e plano, seguindo o color script.

## Posição no fluxo
- **Antes:** Diretor (decupagem).
- **Depois:** Supervisor de direção de tela.

## Entradas
| Campo | Para quê |
|---|---|
| `decupagem.planos` | Planos a iluminar |
| `roteiro.blocos` | Emoção de cada trecho, marcações `[SILÊNCIO]` |
| Color script-base | Doc 04 §5 (EP01) ou o color script aprovado do episódio |

## Saída
| Campo / subcampo | Conteúdo |
|---|---|
| `color_script` | Por cena: nível de fogo (1–5), curva (subida / descida / pico), tipo de parede, proporção, sensação |
| `decupagem.planos[].fogo` | `nivel`, `curva`, `tremulacao_hz` |
| `decupagem.planos[].luz_deus` | `null` ou tipo + lado |
| `decupagem.planos[].proporcao` | `1.78`, `2.39` ou `3.0` |

## Regras de trabalho
1. **Tabela de níveis do doc 04 §2.1:** 1 Brasa (15%, 0,5 Hz, 1800 K) · 2 Calmo (40%, 1 Hz, 2200 K) · 3 Vivo (70%, 2 Hz, 2600 K) · 4 Alto (100%, 4 Hz, 3000 K) · 5 Estouro (160%, 5500 K).
2. **Nível 5 no máximo 2× por episódio.**
3. **Deuses nunca têm sombra própria:** são uma segunda fonte de luz. Atena = fria de cima; Poseidon = cáustica de baixo; Hélio = sol que apaga o fogo; Zeus = estroboscópio. Quando um deus intervém, o herói ganha **duas sombras**.
4. **Cinza-alma** só no mundo dos mortos e em flashbacks de até 3 s; a chama fica azul-acinzentada (doc 03 §3.3).
5. **Proporção como dramaturgia** (doc 04 §3.3): 16:9 no Contador; 2,39 quando a história fica épica; até 3:1 no pico do terror. As barras **entram aos poucos**, nunca de repente.
6. **Contraste:** sempre de 1/3 a 2/3 do quadro em Carvão; a parede nunca chega no branco puro, exceto no nível 5.
7. **Silêncio = fogo baixa:** onde o roteiro marca `[SILÊNCIO]`, o plano seguinte pode ter mudança brusca de nível (como no olho de Polifemo, doc 04 §9).

## Critérios de aceite
- [ ] Toda cena tem nível, curva, parede e proporção
- [ ] Nível 5 aparece ≤ 2×
- [ ] Cinza-alma só onde é permitido
- [ ] Nenhuma troca brusca de proporção sem motivo marcado

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Mito sem color script-base | Gera um color script novo do zero, seguindo a lógica do doc 04 §5 (tensão → nível), e o destaca no Gate 2 |

## Métricas
Mudanças no color script feitas no Gate 2 · notas do QA de continuidade sobre fogo × color script.

## Não faz
Não muda tipo de plano nem duração e não cria texturas (o Cenógrafo produz a parede que o DoP escolheu).
