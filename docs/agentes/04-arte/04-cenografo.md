# Cenógrafo

> **Departamento:** 4 · Arte & marionetes · **Tipo:** IMG + Ferr. · **Nó:** `arte.cenografo` · **Doc-mãe:** [05 §3.4](../../05-arquitetura-agentes-langgraph.md) · **Texturas:** [03 §7](../../03-identidade-visual-lume.md) · **Paredes por ato:** [04 §5](../../04-cinematografia.md)

## Missão
Produzir **o palco**: as paredes de pedra onde a sombra cai, o mapa de pergaminho e os desenhos a carvão, como texturas que o Blender usa com luz real.

## Posição no fluxo
- **Antes:** Gate 2 (o `color_script` e o `elenco` dizem quais paredes são necessárias).
- **Em paralelo:** Designer de silhuetas → Vetorizador → Rigger.
- **Depois:** Bibliotecário. Roda por `Send`, uma parede/textura por vez.

## Entradas
| Campo | Para quê |
|---|---|
| `color_script` | Tipo de parede por cena |
| `elenco` (itens tipo parede/mapa) | O que é novo |
| Store: texturas existentes | Reaproveitar |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `assets.cenarios[<id>]` | Por textura: mapa de cor, mapa de relevo (normal/altura), mapa de rugosidade, resolução, se repete sem emenda, caminho + hash |
| | Planos atendidos: preenche `parede` de cada plano com o id da textura |

**Paredes do EP01** (doc 04 §5): pedra seca com fuligem · pedra com musgo dourado · rocha de caverna úmida · pedra do mar com sal · parede com folhagem · parede que some no escuro · pedra molhada com vento · pedra clara · pedra quente e quieta · **a mesma parede do início** (Ítaca).

## Regras de trabalho
1. **A parede é pedra, não pintura:** o relevo precisa reagir à luz da fogueira (a luz rasante de baixo revela a textura). Por isso o mapa de relevo é obrigatório.
2. **Base de cor em Fuligem/Pergaminho:** sem cores novas. A variação vem do material (umidade, sal, musgo), não do matiz.
3. **Nunca branco puro** no mapa de cor. O ponto mais claro é o Pergaminho `#F1E6CF`.
4. **Resolução 4K** e sem emenda visível, para permitir push-in e dolly.
5. **Mapa de pergaminho** com bordas queimadas e desenho a carvão, em camadas (uma por ilha), para o Grafismo animar a rota queimando.
6. **Ítaca reutiliza a parede do Ato I:** é uma regra de narrativa (o retorno), não economia.

## Critérios de aceite
- [ ] Toda cena do color script tem parede atribuída
- [ ] Toda textura tem cor + relevo + rugosidade
- [ ] Teste de luz: render de 1 quadro com a fogueira no nível 3 mostra relevo legível

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Textura gerada com cor fora da paleta | Corrige por ajuste de cor determinístico; se não der, gera de novo |
| Emenda visível | Refaz com ajuste de borda (1 tentativa); depois, fila humana |

## Métricas
% de paredes reaproveitadas · nº de planos com nota "parede chapada" no Revisor de plano.

## Não faz
Não decide qual parede vai em qual cena (é o DoP) e não faz marionetes.
