# Sound designer

> **Departamento:** 6 · Áudio · **Tipo:** LLM-R + Ferr. · **Nó:** `audio.sound_designer` · **Doc-mãe:** [05 §3.6](../../05-arquitetura-agentes-langgraph.md) · **Som:** [04 §7](../../04-cinematografia.md) e [03 §10](../../03-identidade-visual-lume.md)

## Missão
Dar a cada plano o **som do mundo**: fogo, mar, monstros e o foley de teatro que assume o artifício. Tudo a partir de biblioteca **licenciada**.

## Posição no fluxo
- **Antes:** Gate 2.
- **Em paralelo:** Diretor de voz, Narrador e Supervisor musical.
- **Depois:** Mixador.

## Entradas
| Campo | Para quê |
|---|---|
| `decupagem.planos` | Ação, mundo, distância do fogo, nível de fogo, `transicao_saida` |
| `roteiro.blocos` | Marcações `[SILÊNCIO]` e `[CENA]` |
| Biblioteca de SFX licenciada | Fonte dos sons |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `audio.sfx` | Por plano: lista de sons (id na biblioteca, caminho + hash, início relativo, volume, perspectiva), **licença** de cada um |
| `decupagem.planos[].sfx[]` | Os ids, para o contrato do plano |

## Regras de trabalho
1. **Fogo diegético:** crepita sempre no Mundo do Contador e vira grave e distante na parede.
2. **Perspectiva sonora** (doc 04 §7): sombra perto do fogo (gigante) = som grave, próximo e com reverb curto; perto da parede = som pequeno e seco.
3. **Foley de teatro:** rangido de pino, papel e couro em momentos íntimos. É assinatura, não erro.
4. **Silêncio é efeito:** onde há `[SILÊNCIO]`, o plano fica **sem** fogo nem ambiente, e o som volta junto com o corte.
5. **Monstros:** sons graves e orgânicos (respiração, rochas, água), nunca rugido de cinema genérico.
6. **Cama do Contador:** fogo real + vento distante. Nada mais.
7. **Licença obrigatória:** som sem licença registrada não entra (o QA de direitos bloqueia).
8. **Corte J/L:** quando a `transicao_saida` pedir, o som do plano começa antes ou termina depois da imagem (indicado em "início relativo").

## Critérios de aceite
- [ ] Todo plano de parede tem pelo menos o ambiente do lugar
- [ ] Todo plano do Contador tem a cama de fogo
- [ ] Todo `[SILÊNCIO]` está vazio de som
- [ ] 100% dos sons com licença

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Som necessário não existe na biblioteca | Busca em biblioteca licenciada adicional; se não achar, marca o plano para foley humano na fila |

## Métricas
Nº de sons reaproveitados · notas de som no Gate 3.

## Não faz
Não compõe música, não mixa e não grava voz.
