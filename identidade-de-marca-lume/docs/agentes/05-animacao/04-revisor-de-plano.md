# Revisor de plano

> **Departamento:** 5 · Animação & render · **Tipo:** LLM-V · **Nó:** `animacao.revisor_plano` · **Doc-mãe:** [05 §3.5](../../05-arquitetura-agentes-langgraph.md) · **Checklist:** [04 §10](../../04-cinematografia.md)

## Missão
Olhar o render de cada plano e decidir **aprovado** ou **refazer, com motivo exato**, antes que o plano chegue à montagem.

## Posição no fluxo
- **Antes:** Gerente de render.
- **Depois:** aprovado → VFX/Montagem; reprovado → volta ao Animador.
- **Limite:** 2 refações automáticas. Na 3ª reprovação, o plano vai para a fila humana sem travar os outros.

## Entradas
| Campo | Para quê |
|---|---|
| `assets.planos[<id>].render` | O vídeo do plano |
| Contrato do plano | O que deveria ser |
| `decupagem.planos[<id>].storyboard` | O que foi aprovado no Gate 2 |
| Fichas das marionetes do plano | Silhueta esperada |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `assets.planos[<id>].revisao` | `status` (aprovado / refazer / humano), checagens com resultado, motivo, parâmetro sugerido para mudar |

## O que ele olha
Extrai **3 quadros** (início, meio, fim) e confere:

| Checagem | Critério |
|---|---|
| Composição × storyboard | Mesmo tipo de plano, posição e escala relativas |
| Silhueta reconhecível | Cada personagem identificável pela forma; elemento obrigatório visível |
| Direção de tela | Bate com o contrato |
| Tamanho/foco da sombra | Coerente com a distância do fogo (perto do fogo = grande e borrada) |
| Escuro | De 1/3 a 2/3 do quadro em Carvão |
| Branco | A parede não chega no branco puro (exceto nível 5) |
| Luz de deus | Presente quando pedida; segunda sombra visível |
| Topo do monstro | Fora do quadro nos planos de tilt |
| Artefatos | Buraco em junta, marionete atravessando outra, cintilação |

## Regras de trabalho
1. **Motivo acionável:** "sombra de Polifemo nítida demais; aumentar a distância do fogo de 0,6 para 0,2" em vez de "não ficou bom".
2. **Só reprovar por regra.** Gosto pessoal não é motivo; dúvida estética vai como observação para o Gate 3.
3. **Storyboard é referência, não molde:** pequenas diferenças de posição são aceitas se o sentido do plano se mantém.

## Critérios de aceite
- [ ] Todas as checagens com resultado
- [ ] Toda reprovação com parâmetro sugerido

## Falhas e escalada
| Situação | Decisão |
|---|---|
| 3ª reprovação | Status `humano` + item na fila com os 3 renders e motivos |
| O defeito vem do rig ou da textura, não do plano | Aponta para o Rigger/Cenógrafo, em vez de pedir refação de animação |

## Métricas
Taxa de refação · % de planos aprovados no Revisor e depois reprovados no Gate 3 (falso positivo) · critério da Fase 2 → 3: menos de 15% de refação manual.

## Não faz
Não altera a cena e não aprova o episódio (é o QA + Gate 3).
