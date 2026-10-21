# Engenheiro de Prompt de Vídeo

> **Departamento:** 5 · Animação & render · **Tipo:** Ferr. + LLM-R · **Nó:** `animacao.engenheiro_prompt_video` · **Doc-mãe:** [05 §3.5](../../05-arquitetura-agentes-langgraph.md) · **Especificação:** [08](../../08-ajustes-engenheiro-prompt-video.md) · **Identidade:** [03](../../03-identidade-visual-lume.md) · **Cinematografia:** [04](../../04-cinematografia.md)

## Missão
Transformar planos do Contador, de VFX e de inserts em pedidos cinemáticos de vídeo para motores de IA (Kling / Firefly), operando exclusivamente sobre elementos aprovados (keyframes / assets 3D), respeitando a identidade visual LUME (rosto 100% oculto, braseiro único, contraste Caravaggio). **Nunca** gera silhuetas ou planos de parede (delegados ao Blender headless).

## Posição no fluxo
- **Antes:** Direção (decupagem e `intencao_visual`) e Arte (keyframe aprovado `contador_v1`).
- **Depois:** Gerente de Render e Revisor de Plano.
- **Não faz:** Planos de parede, criação de aparência, mudança de nível de fogo ou escrita em `decupagem`.

## Entradas
| Campo | Origem | Uso |
|---|---|---|
| `plano.mundo`, `plano.tipo_plano` | Direção | Define se o agente é aplicável e seleciona a bíblia visual |
| `plano.duracao_s` | Direção | Seleciona duração permitida no adaptador de vídeo |
| `plano.camera`, `plano.fogo`, `plano.luz_deus` | Direção / DoP | Traduzidos deterministicamente via tabelas |
| `plano.intencao_visual` | Direção | Orientação dramática para seleção da ação pelo LLM |
| `assets.keyframes` / `aprovacoes` | Arte / Gate | Keyframe aprovado (`contador_v1`) como âncora visual obrigatória |

## Saída
| Subcampo | Conteúdo |
|---|---|
| `assets.planos[<id>].video_ia` | `{aplicavel, adaptador, prompt, negativo, keyframe_ref, seed, biblia_versao, prompt_versao, hash, versao, autor_no}` |
| `qa` (se necessário) | Avisos para o DoP (fogo != 2 no Contador, câmera fixa corrigida) |
| `episodio.fila_humana` (se necessário) | Pendência humana caso o keyframe não esteja aprovado |

## Regras de Trabalho (Doc 08)
1. **Parede é Blender:** Para `mundo == "parede"`, devolve `aplicavel: false`.
2. **Âncora Obrigatória:** Contador exige keyframe de referência aprovado (imagem-para-vídeo). Sem keyframe, encaminha à fila humana.
3. **Contador Sem Rosto:** Rosto 100% invisível em sombra profunda de carvão. Sem instrumentos musicais. Braseiro é a única fonte de luz.
4. **Câmera Orgânica:** Planos do Contador sempre adicionam sutil respiração de mão (`with a subtle handheld breathing motion`). Câmera fixa é convertida para `push_in_lento` com aviso.
5. **Composição em Camadas:** Montagem determinística de camadas (1: Âncora, 2: Bíblia, 3: Ação LLM, 4: Câmera, 5: Fogo, 6: Atmosfera). Se estourar limite, descarta camada 6 inteira sem quebrar frases.
6. **Contrato Limpo:** Nunca altera o dicionário do plano nem grava em `decupagem`.
