# 08 — Ajustes no agente `animacao.engenheiro_prompt_video`

> **Por que este doc existe:** o take gerado pelo agente (MP4 de ~5 s, 5 quadros amostrados entre 0,2 s e 4,8 s) não é o LUME. É um vídeo bonito de IA, mas é o filme errado.
> **O que este doc faz:** mostra o que está errado no take, liga cada erro a uma causa no agente e define a nova especificação dele (escopo, prompt, âncora visual, revisão automática, contrato e testes).
> **O que não faz:** não traz código. O Engenheiro de grafo (doc 06 §3) implementa a partir daqui.
> **Docs citados:** 02 (referência), 03 (identidade), 04 (cinematografia), 05 (arquitetura), 06 (automação), 07 (super prompt).

---

## 0. Veredito

1. O take mostra **um velho de barba, de rosto inteiro, tocando lira ao lado de uma lareira**. É o "Rapsodo", a identidade que o doc 03 descartou. Não tem capuz, não tem braseiro, a parede não tem sombra e há duas fontes de luz a mais.
2. O problema **não é o motor de vídeo**: o agente manda um prompt genérico, que não sabe em qual mundo o plano está, não leva a bíblia visual, joga a narração crua no prompt e passa parâmetros que o modelo não entende (Hz, "level 4/5").
3. O agente também está **fora da arquitetura**: ele não está entre os 47 agentes do doc 05 e manda planos direto para a IA de vídeo, quando o doc 04 diz que a parede é feita em Blender, com sombra projetada de verdade.
4. A correção tem 3 partes, nesta ordem: **(a)** limitar o que a IA de vídeo pode gerar, **(b)** travar a aparência com uma imagem de referência aprovada, **(c)** só depois disso, reescrever o prompt.

---

## 1. O que o take mostra × o que os docs exigem

Gravidade: **Bloqueante** = o take não pode entrar no corte · **Grave** = quebra a identidade · **Ajuste** = piora a qualidade.

| # | O que aparece no take | Regra | Doc | Gravidade |
|---|---|---|---|---|
| 1 | Rosto inteiro visível: barba branca, olhos fechados, boca se mexendo | O Contador é encapuzado e o **rosto nunca aparece**. Só mãos, braseiro e voz. | 03 §1 | **Bloqueante** |
| 2 | Rosto fotorrealista com acabamento típico de "IA cinematográfica" | Sem rosto humano realista. "Não somos Disney IA." | 03 §1, §8.3, §12 | **Bloqueante** |
| 3 | Lira nas mãos | O Contador não toca nada. A lira existe **só no som** (sonic logo, leitmotiv de Odisseu). | 03 §1, §10 · 04 §7 | **Bloqueante** |
| 4 | Toras empilhadas numa lareira de pedra | É um **braseiro** (cuba de bronze), o mesmo objeto do U do logo | 03 §1, §2.1 | Grave |
| 5 | Lamparina acesa no nicho + uma luz na borda direita | No Mundo do Contador, **o fogo é a única fonte de luz** | 04 §1, §2 | Grave |
| 6 | Parede inteira em âmbar médio, pouco preto de verdade | De 1/3 a 2/3 do quadro em Carvão absoluto, contraste de 8:1 ou mais | 03 §3.2, §12 · 04 §2.4 | Grave |
| 7 | A parede está "vazia": nenhuma sombra, nenhuma ponte para a história | O plano do Contador comenta a história ou passa para ela (push-in no ombro, faísca, mão no feixe) | 04 §1 | Grave |
| 8 | Câmera praticamente parada nos 5 s | Nunca 100% parada. No Contador: câmera na mão sutil (respiração) + push-in de 2–4% | 04 §1, §3.2 | Ajuste |
| 9 | Quadro aberto, lente com cara de ~35 mm, figura de frente para a esquerda | Contador em lente longa (85–135 mm), profundidade rasa, capuz em perfil, mão ao fogo | 04 §1, §3.1 | Ajuste |
| 10 | Brasas subindo em coluna regular, como pontos de bokeh iguais | Partículas com física real, nunca glow digital | 03 §7, §12 | Ajuste |
| 11 | Laranja saturado tomando a parede, com amarelos fora da paleta | 4 cores de marca, Brasa em no máximo 5% da área | 03 §3 | Ajuste |

**O que vale manter:** a textura de pedra, a fumaça subindo e o canto superior esquerdo no escuro. São a direção certa.

---

## 2. Por que o agente gerou isso (causas no agente)

| # | Causa | Onde está no agente | Efeito no take |
|---|---|---|---|
| C1 | **O agente ignora `plano.mundo`.** Para um plano do Contador, a atuação padrão continua sendo *"Subtle living motion of Greek shadow silhouettes"*. | Bloco "Atuação das Silhuetas" | O prompt mistura Contador e sombras. Para resolver a ambiguidade, o modelo usa o clichê mais forte que conhece para "contador grego ao pé do fogo": Homero com a lira. |
| C2 | **Não existe bíblia visual no prompt.** Nada sobre capuz, rosto escondido, braseiro, fonte única de luz, 60% de escuro, figura negra ou pinos. | O prompt inteiro | O que não está escrito, o modelo preenche com o padrão dele. |
| C3 | **A narração entra crua no prompt.** A primeira frase do bloco, em português, cortada em 120 caracteres e rotulada como *"Narrative emotion"*. | Camada "Contexto do Roteiro" | O modelo ilustra literalmente o que lê. A narração foi escrita para o ouvido, não para a câmera. |
| C4 | **Os parâmetros técnicos vão crus:** "2.5 Hz", "level 4/5", "subida intensity". | Camada "Física do Fogo" | Modelos de vídeo não leem Hz nem a escala interna do LUME. O fogo saiu genérico e o nível de fogo não teve efeito nenhum. |
| C5 | **Enum traduzido com `replace('_', ' ')`.** Sai "push in lento", metade em português. A lente fica em 35 mm até para o Contador. | Camada "Câmera" | O movimento pedido não aconteceu (câmera parada) e a lente é a do mundo errado. |
| C6 | **Os negativos estão dentro do prompt positivo:** "no distortion, no morphing". | Fim do prompt | Muitos modelos ignoram negações no texto positivo, e alguns até reforçam o termo citado. |
| C7 | **Corte cego em 1200 caracteres.** | `prompt_sanitizado[:1200]` | Corta o fim do prompt, que é justamente onde estão as restrições de estabilidade. |
| C8 | **Atuação por substring, com sobrescrita.** `if "odisseu" in id`, dentro de um laço: a última marionete vence. Só cobre 2 personagens e ignora `pose_ini`, `pose_fim`, `direcao` e `distancia_fogo`. | Bloco de marionetes | Os campos que formam a linguagem das sombras (doc 04 §2.2 e §4) nunca chegam ao render. |
| C9 | **Não há âncora visual.** O motor recebe só texto (ou uma imagem que ninguém aprovou). | Entrega "direto ao motor de vídeo" | Cada plano reinventa o personagem. É a mesma fraqueza da referência (doc 02 §5) que o LUME prometia resolver. |
| C10 | **Não há revisão entre o render e o aceite.** | Fluxo | Um take com rosto, lira e lamparina chegou até você. O Revisor de plano (doc 05 §3.5) deveria ter reprovado. |
| C11 | **Erros de contrato.** O agente escreve em `decupagem`, que é campo da Direção; devolve `{"decupagem": {"planos": ...}}`, o que pode apagar outras chaves; altera os dicionários do plano no lugar (a cópia é rasa); não grava `versao` nem `autor_no`; o prompt não entra no hash do plano. | Nó `engenheiro_prompt_video_node` | Viola o doc 05 §2 e o doc 07 (regras 3 e 5). Com o prompt fora do hash, o cache pode devolver um take feito com um prompt antigo. |
| C12 | **Declarado como LLM-R, mas é um template fixo.** | Decorator `categoria_modelo="LLM-R"` | O pior dos dois lados: não tem o julgamento de um LLM nem as garantias checadas de uma ferramenta determinística. |

---

## 3. Decisão de escopo (vem antes de mexer no prompt)

**Regra nova:** a IA de vídeo **nunca cria personagem nem sombra da parede**. Ela só anima o que já foi aprovado ou gera elementos sem personagem.

| Tipo de plano | Quem gera | O que este agente faz |
|---|---|---|
| **Parede** (sombras, marionetes, mapa) | Blender headless (doc 04, premissa · doc 05 §3.5) | **Nada.** Devolve `nao_aplicavel` e o plano segue pela rota Blender. Distância do fogo, direção de tela e poses são parâmetros de cena 3D, não texto de prompt. |
| **Contador** | Imagem-para-vídeo a partir de um **keyframe aprovado** (seção 6) | Escreve o prompt de **movimento**. A apar��ncia vem da imagem, não do texto. |
| **Camadas de VFX** (brasas, fumaça, névoa, faísca da passagem) | Vídeo por IA **sem personagem**, sobre fundo preto, para composição | Escreve o prompt do elemento isolado |
| **Insert de objeto** (erva moly, saco de ventos, fio do tear) | Blender, ou imagem aprovada + imagem-para-vídeo | Escreve só o prompt de movimento |

> **Recomendação forte:** como o rosto do Contador nunca aparece, ele é um asset 3D fácil (capuz, manto, mãos, braseiro). Fazer o Contador também em Blender elimina a variação entre planos, e a IA fica só com o fogo e a fumaça. Se a equipe preferir manter o Contador por IA, a seção 6 é obrigatória.

> Se, mesmo assim, alguém decidir gerar a parede por IA, isso é um desvio do doc 04 e precisa ser registrado em `CONFLITOS-DOCS.md` (doc 07). Este doc não dá regras para esse caso, porque a recomendação é não fazer.

**Registro na arquitetura:** o agente passa a existir oficialmente. Crie a ficha `docs/agentes/animacao/engenheiro_prompt_video.md` e acrescente uma linha no doc 05 §3.5, marcada como **[adicionado na construção]**. O total vira 48 agentes + o Showrunner.

| Campo da ficha | Valor |
|---|---|
| Missão | Transformar um plano do Contador, de VFX ou de insert num pedido de vídeo que só anima o que foi aprovado e respeita os docs 03 e 04 |
| Tipo | **Ferr. + LLM-R**: template determinístico para tudo, LLM só para escolher a ação (seção 4.6) |
| Roda | Depois da Direção e da Arte (precisa do keyframe), antes do Gerente de render |
| Não faz | Planos de parede, criação de aparência, mudança de nível de fogo ou de color script, escrita em `decupagem` |

---

## 4. Nova arquitetura do prompt

### 4.1 O que o agente lê

| Campo | Uso |
|---|---|
| `plano.mundo`, `plano.tipo_plano` | Escolhe a bíblia e decide se o agente se aplica |
| `plano.duracao_s` | Escolhe a duração suportada pelo adaptador (arredonda para cima e corta na montagem) |
| `plano.camera`, `plano.fogo`, `plano.luz_deus` | Entram pelas tabelas de tradução (4.5) |
| `plano.transicao_saida` | Define o último quadro quando o adaptador aceita quadro inicial e final |
| `plano.intencao_visual` **(subcampo novo, seção 8)** | Uma frase de intenção visual escrita pela Direção. **Substitui a narração crua.** |
| `assets.keyframes` (Bibliotecário/Store) | A imagem de referência aprovada |
| Store: bíblias e listas negativas, versionadas | Texto fixo do mundo |

**O agente não lê `roteiro.blocos[].texto`.** A narração é para o ouvido. Quem traduz a narração em intenção visual é a Direção.

### 4.2 Camadas em ordem de prioridade

Se o prompt passar do limite do adaptador, o agente **remove camadas inteiras de baixo para cima**, nunca corta no meio de uma camada. As camadas 1 a 4 nunca saem.

| Ordem | Camada | Conteúdo | Pode sair? |
|---|---|---|---|
| 1 | **Âncora** | "Anime a imagem de referência; mantenha figura, roupa, enquadramento e luz" | Nunca |
| 2 | **Bíblia do mundo** | Texto fixo e versionado (4.3 ou 4.4) | Nunca |
| 3 | **Ação** | **Uma** ação principal + no máximo uma secundária (4.6) | Nunca |
| 4 | **Câmera** | Movimento + lente traduzidos (4.5) | Nunca |
| 5 | **Fogo** | Nível + curva traduzidos (4.5) | Só em VFX sem fogo |
| 6 | **Atmosfera** | Brasas, fumaça, névoa | Sim, primeiro a sair |

**Fica fora do prompt:** grão, halation, vinheta, gate weave, letterbox e proporção de tela. É tudo pós-produção (Finalizador, doc 05 §3.7). Pedir isso ao modelo de vídeo dá resultado inconsistente e impede o controle na pós.

**Negativo em campo próprio:** a lista negativa (4.3) vai no campo de negative prompt do adaptador. Se o motor não tiver esse campo, as restrições entram como frases **afirmativas** na camada 2 ("o rosto fica escondido o tempo todo"), nunca como "no X".

**Idioma:** o prompt sai inteiro em inglês, com vocabulário fixo. Nenhum enum, rótulo ou trecho em português chega ao motor.

**Adaptadores:** cada motor tem uma entrada em `config/adaptadores_video.yaml` (limite de caracteres, se aceita negativo, se aceita quadro inicial e final, durações possíveis, se aceita controle de câmera). O nome do modelo fica só nesse arquivo (doc 07, regra 8).

### 4.3 Bíblia do Contador (texto fixo, `biblia_contador_v1`)

**Positivo:**

```text
A hooded storyteller beside a bronze brazier, seen in profile. A deep, heavy wool hood in dark charcoal-brown is pulled far forward; inside the hood there is only darkness, and the face is never visible at any moment. Only two weathered hands are visible, held near the flames. The brazier is the only light source: warm firelight from below and in front. Everything outside its glow falls into near-black. Behind him, a rough limestone wall, mostly in deep shadow.
```

**Negativo (`negativo_contador_v1`):**

```text
face, visible eyes, nose, mouth, lips moving, beard, facial skin, portrait, looking at camera, musical instrument, lyre, harp, string instrument, lantern, oil lamp, candle, torch, window, daylight, second light source, rim light from behind, fireplace, chimney, stacked logs, campfire on the floor, modern objects, text, logo, glowing particles in a regular pattern, bokeh orbs, lens flare, digital glow, morphing, warping hands, extra fingers, cartoon, anime, 3D render look
```

### 4.4 Bíblia de VFX (texto fixo, `biblia_vfx_v1`)

**Positivo:**

```text
Isolated practical element on a pure black background, for compositing. No people, no objects, no environment. Real physical behavior, filmed look.
```

**Negativo:** `people, figure, face, hands, wall, floor, environment, text, logo, regular particle pattern, digital glow, lens flare`

### 4.5 Tabelas de tradução

**Fogo: nível → texto** (nunca enviar Hz, Kelvin ou "level")

| Nível (doc 04 §2.1) | Texto para o motor |
|---|---|
| 1 · Brasa | `only glowing embers, almost no flame, a very slow breathing glow, deep red-orange; the scene is almost entirely dark` |
| 2 · Calmo | `low, steady flames with a gentle, slow flicker; soft warm amber light` |
| 3 · Vivo | `lively medium flames with a moderate flicker; the light visibly dances on the wall` |
| 4 · Alto | `tall roaring flames with a strong, irregular flicker and sudden flares; hard moving shadows` |
| 5 · Estouro | `the fire flares into a near-white blinding burst that floods the frame for an instant` |

**Fogo: curva → texto**

| Curva | Texto |
|---|---|
| `estavel` | `the fire stays at the same strength for the whole shot` |
| `subida` | `the fire slowly grows stronger over the shot` |
| `descida` | `the fire slowly dies down over the shot` |
| `pico` | `one sudden flare midway through the shot, then it settles back` |

**Regra do Contador:** pelo doc 04 §2.1, o Contador fica no nível 2. Se o plano do Contador chegar com outro nível, o agente **não corrige sozinho**: gera o prompt com o nível pedido e grava um aviso em `qa` para o DoP. A única exceção prevista é a passagem "sair da parede" (chama baixando, curva `descida`).

**Câmera: movimento → texto**

| Enum | Texto |
|---|---|
| `push_in_lento` | `a very slow push-in; the camera drifts forward barely noticeably, about 3% closer over the shot` |
| `dolly_lateral_dir` / `_esq` | `a slow lateral dolly to the right` / `to the left` |
| `tilt_up` | `a slow tilt up` |
| `rack_focus` | `focus slowly shifts from the hood in the foreground to the wall behind` |
| `tremor` | `a brief camera shake lasting under half a second, then still` |
| `fixo` | `a locked-off, completely still camera` |

**Sempre no Contador**, somado ao movimento do plano: `with a subtle handheld breathing motion` (doc 04 §1). Se o plano do Contador vier como `fixo`, o agente troca por `push_in_lento` e grava um aviso, porque o doc 04 §3.2 só permite plano parado na caverna e no mundo dos mortos.

**Lente → texto**

| Mundo | Texto |
|---|---|
| Contador (85–135 mm) | `telephoto 100mm look, shallow depth of field, background softly out of focus` |
| VFX | Sem lente: o elemento é composto depois |

**Luz de deus** (só em camadas de VFX de luz, nunca com figura)

| Deus | Texto |
|---|---|
| Atena | `cold, pale light falling from above` |
| Poseidon | `rippling water caustics projected from below` |
| Hélio | `harsh midday white light that washes out the warm fire` |
| Zeus | `strobing lightning flashes` |

### 4.6 Ação: uma só, de uma lista fechada

É a única parte que usa LLM. O LLM recebe `intencao_visual` e devolve, em saída estruturada, **um item da lista abaixo + um advérbio de velocidade** (`muito devagar`, `devagar`, `firme`). Ele não escreve texto livre para o motor.

**Ações permitidas do Contador:**

| Id | Texto para o motor | Quando usar |
|---|---|---|
| `mao_aproxima_fogo` | `his right hand moves toward the flames and stops just above them` | Antes de uma revelação |
| `mao_afasta_fogo` | `his hand pulls back from the flames` | Depois do horror (ex.: o olho de Polifemo, doc 04 §9 plano 7) |
| `mao_no_feixe` | `his open hand enters the beam of firelight, casting a large shadow on the wall` | Passagem 4 do doc 04 §1 (a mão vira deus) |
| `joga_po_no_fogo` | `he tosses a pinch of dust into the brazier and a burst of sparks rises` | Passagem "faísca" |
| `capuz_inclina` | `the hood tilts down a few degrees` | Comentário, luto |
| `respira` | `his shoulders rise and fall with a slow breath` | Respiro, sem outra ação |
| `abre_pergaminho` | `his hands slowly unroll a scorched parchment` | Selo do texto original (doc 02 §6) |

**Ações proibidas:** falar ou mexer a boca, tocar qualquer instrumento, olhar para a câmera, levantar-se (exceto no end screen, doc 03 §9), qualquer ação que exija mostrar o rosto.

**Instrução do LLM (texto do prompt em `prompts/animacao/engenheiro_prompt_video.md`):**

> Você recebe a intenção visual de um plano do Contador do LUME. Escolha **exatamente uma** ação da lista permitida e um advérbio de velocidade. Se nenhuma ação servir, devolva `respira`. Nunca invente uma ação fora da lista. Nunca descreva rosto, voz, canto ou instrumento. Devolva só o objeto estruturado.

---

## 5. Antes e depois: o mesmo plano

**Plano:** `ep01_c00_p02` · mundo `contador` · `tipo_plano: contador` · 6 s · `push_in_lento` · fogo nível 2, `estavel` · `intencao_visual`: *"O Contador estende a mão para o fogo antes de começar a história."*

### Antes (reconstrução do que o agente atual monta para esse plano)

```text
Cinematic video animation: Smooth cinematic camera push in lento with 35mm lens perspective. Subtle living motion of Greek shadow silhouettes, slight breathing and joint articulation. Brazier fire flame flickering naturally at 1 Hz (estavel intensity, level 2/5), organic embers drifting upwards with delicate smoke curl. Narrative emotion: 'O fogo ainda conta as mesmas histórias'. Ultra-consistent 24fps motion, high quality shadow puppet theater physics, constant lighting geometry, perfect temporal stability, no distortion, no morphing
```

O que está errado: não diz quem está no quadro, não esconde o rosto, menciona silhuetas num plano sem silhuetas, mistura português, passa Hz e "level", usa a narração como emoção, coloca os negativos no texto positivo e usa a lente do outro mundo.

### Depois

**Imagem de referência:** `contador_v1_perfil_mao` (seção 6).

**Positivo:**

```text
Animate the reference image. Keep the hooded figure, costume, framing and lighting exactly as shown.
A hooded storyteller beside a bronze brazier, seen in profile. A deep, heavy wool hood in dark charcoal-brown is pulled far forward; inside the hood there is only darkness, and the face is never visible at any moment. Only two weathered hands are visible, held near the flames. The brazier is the only light source: warm firelight from below and in front. Everything outside its glow falls into near-black. Behind him, a rough limestone wall, mostly in deep shadow.
Action: slowly, his right hand moves toward the flames and stops just above them.
Camera: a very slow push-in; the camera drifts forward barely noticeably, about 3% closer over the shot, with a subtle handheld breathing motion. Telephoto 100mm look, shallow depth of field, background softly out of focus.
Fire: low, steady flames with a gentle, slow flicker; soft warm amber light. The fire stays at the same strength for the whole shot.
A few embers rise irregularly and drift with the heat; thin smoke curls upward.
```

**Negativo:** `negativo_contador_v1` (seção 4.3).
**Duração pedida:** a duração do adaptador mais próxima acima de 6 s. A sobra é cortada na montagem.

### Exemplo de VFX: passagem "faísca" (doc 04 §1, passagem 2)

```text
Isolated practical element on a pure black background, for compositing. No people, no objects, no environment. Real physical behavior, filmed look.
A single glowing ember rises slowly from the bottom of the frame, swaying slightly with the heat, leaving a faint trail, and gets brighter as it reaches the upper third.
Camera: a locked-off, completely still camera.
```

---

## 6. Âncora visual do Contador (obrigatória se ele for feito por IA)

| Item | Regra |
|---|---|
| **Design único** | O Contador é desenhado **uma vez** (capuz, manto, mãos, braseiro), aprovado por um humano e registrado na Store pelo Bibliotecário como `contador_v1`. É o mesmo princípio das marionetes (doc 06 §10). |
| **Gate de personagem** | A aprovação do design fica em `aprovacoes`, como os outros gates (doc 05 §7). Sem `contador_v1` aprovado, nenhum plano do Contador vai para render. |
| **Keyframes por enquadramento** | Um still aprovado para cada enquadramento usado: `perfil_mao` (100 mm), `costas_parede` (abertura e repetições, doc 04 §6.2), `ombro_push` (entrada na parede), `close_maos`. |
| **Sempre imagem-para-vídeo** | Todo plano do Contador parte de um desses keyframes. Texto-para-vídeo é proibido para o Contador. |
| **Quadro final** | Nas passagens entre mundos, se o adaptador aceitar quadro inicial e final, o quadro final também é um keyframe aprovado (ex.: a pedra enchendo o quadro). |
| **Seed** | A seed de cada take aprovado é gravada. Uma refação muda a seed de propósito. |

---

## 7. Revisor automático (entre o render e o aceite)

O take só é aceito depois de passar por estas checagens. Isso pode ficar no próprio Revisor de plano (doc 05 §3.5) com um perfil "vídeo IA". São analisados 1 quadro por segundo, mais o primeiro e o último.

### 7.1 Checagens determinísticas (Ferr.)

| Checagem | Limite | Resultado se falhar |
|---|---|---|
| Detector de rosto | Qualquer rosto com confiança > 0,5 | **Bloqueia** |
| Área em Carvão (luminância muito baixa) | < 1/3 do quadro | **Bloqueia**; entre 1/3 e 50% gera aviso |
| Área em Brasa (faixa de tom e saturação de `#E07A2E`) | > 5% | Aviso; acima de 10% **bloqueia** |
| Cor fora da paleta (distância de cor às 4 cores de marca) | > 10% dos pixels | Aviso |
| Pontos de luz separados do braseiro (manchas de alta luminância longe da fonte) | 1 ou mais | **Bloqueia** no Contador |
| Movimento (fluxo óptico médio) | Abaixo do mínimo = parado; acima do máximo = deformação | Refazer |
| Fidelidade ao keyframe (similaridade do 1º quadro) | Abaixo do limiar | Refazer |

### 7.2 Checagens com LLM-V (sim/não, com o quadro como evidência)

1. Aparece rosto, olho, boca ou barba?
2. Aparece instrumento ou algum objeto que não está no keyframe?
3. Há fonte de luz além do braseiro?
4. O fogo está num braseiro, ou virou lareira, toras ou fogueira no chão?
5. As brasas sobem em padrão regular, com cara de efeito digital?
6. A ação pedida aconteceu?

### 7.3 Refação

- Cada reprovação vira um motivo específico (ex.: `rosto_visivel`). A refação troca a seed e reforça **só** o trecho da bíblia e do negativo ligado àquele motivo.
- No máximo **2 refações automáticas** (doc 05 §3.5). Na terceira falha, o plano vai para a fila humana sem travar os outros.

**Teste de regressão obrigatório:** o take atual (o do velho com a lira) entra nos testes como caso que **precisa ser reprovado**, pelos motivos `rosto_visivel`, `instrumento`, `segunda_fonte_luz`, `lareira` e `area_carvao_baixa`.

---

## 8. Correções de contrato e estado

| Item | Hoje | Correção | Base |
|---|---|---|---|
| Onde grava | `decupagem.planos[].prompt_video` (campo da Direção) | `assets.planos[<id>].video_ia` = `{aplicavel, adaptador, prompt, negativo, keyframe_ref, seed, biblia_versao, prompt_versao, hash, versao, autor_no}` | doc 05 §2 · doc 07 regras 3 e 5 |
| Formato do retorno | `{"decupagem": {"planos": [...]}}` (pode apagar outras chaves) | Devolve só o subcampo dele em `assets`, sem tocar em `decupagem` | doc 05 §2 |
| Mutação | Altera os dicionários do plano no lugar (cópia rasa) | Função pura: lê o plano e devolve um objeto novo | doc 07, receita item 3 |
| Narração | Lida de `roteiro.blocos` | **Subcampo novo** `decupagem.planos[].intencao_visual` (texto curto, opcional, escrito pela Direção), marcado **[adicionado na construção]** no doc 05 §5 | doc 07, decisão 3 |
| Hash do plano | O prompt não entra | O hash passa a incluir `prompt`, `negativo`, `keyframe_ref`, `biblia_versao` e `adaptador`. Mudou a bíblia? O plano é refeito. | doc 05 §5 |
| Tipo | `LLM-R` | `Ferr. + LLM-R` | doc 05 §3 (legenda) |
| Nome do modelo | Citado no comentário e no fluxo (Kling/Firefly) | Só em `config/adaptadores_video.yaml` | doc 07 regra 8 |
| Prompts | Dentro do código | `prompts/animacao/engenheiro_prompt_video.md`, com versão, casos de teste e critério de reprovação; bíblias e negativos versionados na Store | doc 06 §4 (`prompts.md`) |
| Planos de parede | Iam para o motor de vídeo | `aplicavel: false`, sem job enviado | Seção 3 deste doc |
| Sem keyframe aprovado | Gerava mesmo assim | Não envia o job; abre item em `episodio.fila_humana` | Seção 6 deste doc |

---

## 9. Casos de teste

| # | Entrada | Esperado |
|---|---|---|
| T1 | Plano do Contador, nível 2, `push_in_lento`, keyframe aprovado | O prompt tem âncora + bíblia + ação + câmera + fogo; o negativo tem `face`, `lyre`, `lantern`; não aparece "Hz", "level" nem palavra em português |
| T2 | Plano de parede | `aplicavel: false`; nenhum job enviado ao motor de vídeo |
| T3 | `intencao_visual` vazia e narração que fala em "canto" e "lira" | Ação `respira`; o prompt não contém `sing`, `song`, `lyre` nem `instrument` |
| T4 | `intencao_visual` pedindo "o Contador sorri" | O LLM devolve uma ação da lista (nunca "sorrir"); o teste confere se o id existe na lista |
| T5 | Plano do Contador com fogo nível 4 | Prompt gerado com nível 4 + aviso em `qa` para o DoP |
| T6 | Plano do Contador com câmera `fixo` | Troca para `push_in_lento` + aviso |
| T7 | Prompt acima do limite do adaptador | Sai a camada 6 inteira; as camadas 1 a 4 ficam intactas; nenhuma frase cortada no meio |
| T8 | Sem `contador_v1` aprovado | Nenhum job; item na fila humana |
| T9 | Mesma entrada duas vezes | Mesmo prompt e mesmo hash (idempotência) |
| T10 | Qualquer plano | O estado depois do nó não tem nenhuma mudança em `decupagem` |
| T11 | Take atual (velho com lira) no Revisor | Reprovado com `rosto_visivel`, `instrumento`, `segunda_fonte_luz`, `lareira` e `area_carvao_baixa` |
| T12 | Adaptador sem campo de negativo | As restrições aparecem como frases afirmativas na bíblia; nenhuma frase "no X" no texto positivo |

---

## 10. Critérios de aceite do agente corrigido

- [ ] Nenhum plano de parede passa pelo motor de vídeo.
- [ ] Em 10 takes seguidos do Contador: **0** com rosto, **0** com instrumento e **0** com segunda fonte de luz.
- [ ] Pelo menos 8 de 10 aprovados na 1ª ou 2ª tentativa.
- [ ] O Contador é reconhecidamente o mesmo nos 10 takes (similaridade com o keyframe acima do limiar).
- [ ] Os testes T1 a T12 passam.
- [ ] O episódio de fumaça de 60 s (`/fumaca`, doc 06 §5) passa com pelo menos 1 plano do Contador e 1 camada de VFX.

---

## 11. Ordem das correções

| # | Correção | Por que nesta ordem |
|---|---|---|
| 1 | **Rota por mundo:** parede vai para o Blender, e o agente só atende Contador, VFX e inserts | Elimina a maior fonte de erro sem escrever uma linha de prompt |
| 2 | **Âncora do Contador:** design aprovado, keyframes e imagem-para-vídeo obrigatória (ou Contador em Blender) | A aparência deixa de depender de texto |
| 3 | **Bíblias, negativo separado e tabelas de tradução** (seções 4.3 a 4.5) | O prompt passa a falar a língua do motor |
| 4 | **Revisor automático** (seção 7) | Nenhum take como o atual chega a você |
| 5 | **Contrato** (seção 8) | Para de sujar o campo da Direção e o cache passa a funcionar |
| 6 | **LLM só para a ação** (seção 4.6) | Por último, porque é a parte de menor risco |

---

## 12. Checklist rápido para cada take (operador)

- [ ] O rosto aparece em algum quadro? → refazer.
- [ ] Há algo nas mãos que não seja fogo, pó ou pergaminho? → refazer.
- [ ] Dá para apontar uma única fonte de luz, e ela é o braseiro?
- [ ] Pelo menos 1/3 do quadro está em preto de verdade?
- [ ] A câmera se move, mesmo que pouco?
- [ ] O Contador é o mesmo do keyframe?
- [ ] O take funciona como ponte para a parede ou como comentário? Se não serve a nenhum dos dois, o plano não deveria existir.


otimiza o agente eng de prompt de video