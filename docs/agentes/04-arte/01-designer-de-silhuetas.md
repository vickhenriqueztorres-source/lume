# Designer de silhuetas

> **Departamento:** 4 · Arte & marionetes · **Tipo:** IMG + LLM-V (auto-checagem) · **Nó:** `arte.designer_silhuetas` · **Doc-mãe:** [05 §3.4](../../05-arquitetura-agentes-langgraph.md) · **Estilo:** [03 §6](../../03-identidade-visual-lume.md)

## Missão
Criar **uma única vez** cada marionete nova, no estilo figura negra dos vasos gregos, reconhecível só pela silhueta em 1 segundo num celular.

## Posição no fluxo
- **Antes:** Gate 2 (o `elenco` aprovado diz o que é novo).
- **Depois:** Vetorizador. Roda por `Send`: **um item novo por execução**.
- Também é chamado pelo workflow `/novo-personagem` (doc 06 §5), fora de um episódio.

## Entradas
| Campo | Para quê |
|---|---|
| `elenco` (itens `novo`, tipo marionete/objeto) | A ficha do item |
| Store: marionetes existentes | Consistência de estilo (proporção, espessura de pino, tipo de furo) |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `assets.marionetes[<id>].design` | Caminho + hash do PNG de alta resolução escolhido, variantes descartadas, notas da auto-checagem |

## Regras de trabalho
1. **Figura negra** (doc 03 §6.3): perfil, olho frontal, ombros de frente. Preto chapado, nada de gradiente.
2. **Fundo transparente** ou branco puro, para o Vetorizador separar com limpeza.
3. **Elemento obrigatório da ficha** bem visível (ex.: o píleo de Odisseu, o olho único de Polifemo, as 6 cabeças de Cila).
4. **Pinos visíveis** em ombro, cotovelo, quadril e joelho, com o desenho de um rebite de teatro. Mostrar o pino é charme.
5. **Furos decorativos** (estilo wayang) só em deuses e monstros.
6. **Gerar 4 variantes**, depois rodar a **auto-checagem com LLM-V** e escolher a melhor:
   - Reduz a silhueta para **64 px de altura** e pergunta "quem é este personagem?" sem dar opções. Acertou = passa.
   - Confere se o elemento obrigatório está lá.
   - Confere se a direção do perfil é a da ficha.
   - Confere se não há tons de cinza.
7. **Nunca rosto humano realista**, nunca estilo "Disney", nunca 3/4: sempre perfil.

## Critérios de aceite
- [ ] Passou no teste dos 64 px
- [ ] Elemento obrigatório presente
- [ ] Direção correta
- [ ] Preto chapado + transparência, sem cinza

## Falhas e escalada
| Situação | Decisão |
|---|---|
| Nenhuma das 4 variantes passa | Gera mais 4 com o motivo da falha no pedido; se falhar de novo, vai para a fila humana com as 8 variantes |
| Passa no teste, mas fica parecido com outra marionete da biblioteca | Reprova (dois personagens com a mesma silhueta quebram a regra de ouro) |

## Métricas
Nº de rodadas até passar · nº de marionetes refeitas depois do Gate 3 por não serem reconhecíveis.

## Não faz
Não vetoriza, não define pivôs e **não redesenha** personagem existente por plano (doc 06 §10).
