# 02 — Análise do vídeo de referência (Red History · A Odisseia)

**Vídeo:** youtube.com/watch?v=cdrgh_oPFeY, *"The Odyssey story explained in hindi"*, canal Red History
**Arquivo analisado:** MP4 enviado no chat, com **24:49**, 1280×720, 30 fps
**Método:** detecção automática de cortes (limiar de mudança de cena 0,3) + 186 quadros amostrados a cada 8 s, montados nas folhas de contato em [`referencias/frames/`](./referencias/frames/) (folha `sNN` = do minuto `(NN-1)×2:40` até `NN×2:40`, lida da esquerda para a direita).

> **Limites desta análise**
> - O arquivo **não tem trilha de áudio** (só vídeo). Por isso não analisei voz, música nem SFX. A narração vem da transcrição que você já tinha (28 blocos), e aqui eu cruzo com o que aparece na tela.
> - O bitrate do arquivo é baixíssimo (~90 kb/s), então os blocos de compressão são do download, não necessariamente do original.
> - O detector de cortes **subconta dissolves e morphs**. Os números de ritmo abaixo são um piso, não um valor exato.

---

## 1. Resumo em 6 linhas

1. **Estilo:** 2D pintado "animação de longa clássica" (rostos em cel shading, fundos pintados), muito perto da estética de *O Príncipe do Egito* / Disney anos 90. Quase certamente gerado por IA (imagem → vídeo).
2. **Movimento:** clipes curtos de imagem-para-vídeo (personagens andando, com leves deformações) e, nos planos mais longos, empurrões lentos de câmera e rotação sobre uma imagem.
3. **Ritmo:** 163 planos detectados, com **mediana de 6,6 s** por plano e média de 9,1 s. O ritmo é estável, com **aceleração no bloco Cila → raio de Zeus**.
4. **Cor:** a arma mais forte do vídeo. **Cada ilha tem uma temperatura de cor própria**, e é isso que faz 25 minutos não parecerem repetitivos.
5. **Recursos gráficos:** mapa com rota, telas divididas em painéis, letterbox nos momentos de pavor, flashback em preto e branco e um corte esquemático (a casa construída em volta da oliveira).
6. **Fraquezas:** o rosto de Odisseu oscila, não há persona nem elemento-assinatura, o mapa aparece pouco e não existe contador de perdas visível.

---

## 2. Ritmo de montagem (dados)

| Janela | Cortes detectados | Leitura |
|---|---|---|
| 00–02 min | 15 | Gancho + contexto de Troia, ritmo alto |
| 02–04 | 15 | Ismaro e Lotófagos |
| **04–06** | **8** | **Caverna de Polifemo: o ritmo cai de propósito** (planos de 40 s ou mais) para gerar claustrofobia |
| 06–08 | 12 | Olho, fuga, Poseidon, Éolo |
| 08–10 | 14 | Lestrigões |
| 10–12 | 15 | Destruição da frota + Circe |
| 12–14 | 10 | Um ano com Circe (passagem de tempo) + Ítaca intercalada |
| 14–16 | 9 | Mundo dos mortos, ritmo lento e fúnebre |
| 16–18 | 14 | Sereias |
| **18–20** | **18** | **Pico: Cila, gado de Hélio e raio de Zeus**, o maior número de cortes do vídeo |
| 20–22 | 13 | Calipso + chegada a Ítaca |
| 22–24 | 15 | Arco, revelação e massacre |
| 24–24:49 | 6 | Cama de oliveira + CTA |

**Planos mais longos:** 0:00 (54 s, o gancho feito com dissolves contínuos), 5:50 (44 s, o olho do ciclope), 4:31 (42 s, a espera na caverna), 13:30 (41 s, Penélope e Ítaca), 22:44 (34 s, os machados).

**Padrão:** o vídeo **desacelera no terror e no luto** (caverna, mundo dos mortos) e **acelera na perda em massa** (Lestrigões, Cila/Zeus). A transição dominante é o dissolve/morph suave; corte seco é minoria.

---

## 3. Mapa visual cena a cena

Tempos aproximados (±8 s), vindos das folhas de contato.

| Tempo | O que aparece na tela | Recurso visual |
|---|---|---|
| 0:00–0:40 | Odisseu e Cila, Calipso, os pretendentes, Troia em chamas, **um escriba escrevendo o primeiro verso grego da Odisseia** num rolo | **Flashforward** dos clímax + selo de autoridade (o texto original). Etiqueta fixa "इस वीडियो में…" ("Neste vídeo…") no canto superior direito |
| 0:40–1:12 | Céu de tempestade, exércitos com a legenda queimada "trojan", Helena, Troia queimando, o Cavalo à noite | Palavra-chave em amarelo na tela |
| 1:20–1:44 | Odisseu em tela dividida, partida do navio, figura na praia (família), navio ao pôr do sol | Painel duplo |
| **1:52** | **Mapa: Troia → Ismaro, rota tracejada vermelha, nuvens e chamas** | O único mapa de rota amostrado |
| 2:00–2:56 | Ataque a Ismaro, banquete na praia, tochas no morro (reforços), cavalaria, fuga, tempestade | Noite laranja → azul |
| 3:04–3:52 | Lotófagos: praia tropical, fruto brilhante na mão, olhos dopados, resgate à força, amarração noturna | **Paleta verde-dourada saturada** (o "paraíso" é a ameaça) |
| 4:08–5:12 | Ilha nebulosa, entrada da caverna (com **letterbox**), queijos, Odisseu pensativo, Polifemo, rostos apavorados à luz de tochas | Laranja de fogo + preto, câmera baixa |
| 5:20–6:32 | Estaca sendo afiada, o golpe no olho, **o grito desenhado como anéis concêntricos** | Grafismo sonoro estilizado |
| 6:40–7:28 | Ovelhas na saída, Odisseu gritando o nome no barco, **Poseidon de olhos brilhantes dentro de um vórtice**, Poseidon com tridente | Ciano e branco, água em grafismo |
| 7:36–8:32 | Éolo num templo de nuvens, o saco de ventos com veios luminosos, Ítaca no horizonte, homens abrindo o saco (brilho dourado), explosão de vento | Objeto-símbolo em close |
| 8:40–9:28 | Baía entre penhascos, a frota enfileirada, o navio de Odisseu do lado de fora, palácio, **rei e rainha gigantes no trono** | Escala gigante × humano |
| 9:36–10:32 | Gigantes nos penhascos, pedras caindo, **água vermelha**, Odisseu remando em choque, navios queimando, homem sozinho no barco | Cinza-azulado + vermelho |
| 10:40–11:12 | Navios em chamas, ilha em painéis, fumaça na floresta, homens com tochas | — |
| 11:20–12:00 | Circe no trono (roxo), banquete com **anel de luz verde**, homens com cabeça de porco, porcos | **Paleta roxa** |
| 12:08–12:48 | Corrida pela floresta, **Hermes e a erva moly** (o mesmo plano repetido), jantar tenso, confronto | Verde-floresta luminoso |
| 12:56–13:12 | Odisseu na cama com Circe, palácio branco, jogo de tabuleiro | Montagem de tempo passando |
| 13:20–13:44 | Penélope no tear à noite, pretendentes festejando, palácio de Ítaca, cena em silhueta com letterbox | **Intercalação** com casa |
| 13:52–15:20 | Circe orienta Odisseu, **Tirésias espectral**, fileira de almas, Anticleia viva (flashback com vela), **abraço que atravessa o espírito**, visão do gado do Sol | **Azul-cinza dessaturado**, fantasmas em fita branca |
| 15:28–17:04 | Rochedo das Sereias, cera nos ouvidos, Odisseu amarrado, **o canto como fita ciano** envolvendo a cabeça, alucinação luminosa | Som representado como grafismo |
| 17:04–18:32 | Redemoinho com raio, penhascos, caverna de Cila, Caríbdis em push-in, **Cila em silhueta negra de seis cabeças**, navio passando | Azul-aço de tempestade |
| 18:40 | Odisseu chorando em close | Luto pós-sacrifício |
| 18:48–19:52 | Trinácia ensolarada, homens famintos, abate do gado, **Hélio dourado**, Zeus no Olimpo, **raio no vórtice**, navio partido, Odisseu agarrado a um destroço | Ouro → azul |
| 20:00–20:32 | **Grade de 9 painéis de Calipso** (os 7 anos), Calipso reaproveitada do gancho, visão de Ítaca, a partida | Grade = compressão de tempo |
| 20:40–21:12 | Odisseu na floresta com um porco (Eumeu, o porqueiro), Odisseu velho e furioso, salão do banquete, Penélope cercada | Âmbar de tochas |
| 21:20–21:44 | Penélope no tear, **close das mãos desfazendo o fio**, **mendigo encapuzado** | — |
| 21:52–22:40 | Penélope com o arco, pretendentes tentando, falhas, o mendigo se oferece | — |
| 22:48–23:12 | **Grade dos 12 machados**, trajetória da flecha, revelação | Painéis |
| 23:20–23:36 | Portas trancadas, **Odisseu de armadura retesando o arco** | Plano-herói |
| 23:44 | **Flashback em preto e branco** (o redemoinho) | Memória dessaturada |
| 23:52–24:32 | O casal, **corte esquemático da casa construída ao redor da oliveira**, abraço junto à lareira, varanda ao pôr do sol | Ilustração explicativa |
| 24:40 | **End card**: família + ícones Like / Share / Notifications / Subscribe | CTA só no final |

---

## 4. O que a referência faz bem (copiar o princípio, não a estética)

### 4.1 Uma cor por lugar
É o maior achado da análise. O espectador sabe "onde está" só pela cor:

| Lugar | Temperatura |
|---|---|
| Troia / Ismaro | Laranja de incêndio |
| Lotófagos | Verde-ouro tropical |
| Polifemo | Laranja de fogo + preto |
| Poseidon / Éolo | Ciano e branco |
| Lestrigões | Cinza-teal + vermelho |
| Circe | Roxo + tocha |
| Mundo dos mortos | Azul-cinza dessaturado |
| Trinácia | Amarelo-verde saturado |
| Sereias / Cila | Azul-aço |
| Calipso | Tropical claro |
| Ítaca | Âmbar de tocha |

### 4.2 Gancho que entrega os clímax antes do contexto
Os primeiros 40 s mostram as cenas mais fortes do vídeo (Cila, Calipso, pretendentes) **e** o escriba com o verso grego, que funciona como selo de "isso é o texto original".

### 4.3 O ritmo respira
Ele não corta rápido o tempo todo: segura a caverna e o mundo dos mortos e acelera a carnificina. É uma curva de tensão desenhada, não um ritmo constante.

### 4.4 Som virando imagem
O grito do ciclope vira anéis, o canto das sereias vira fita ciano e os fantasmas viram fitas brancas. Isso garante que o vídeo funcione **sem som**, o que importa muito no celular.

### 4.5 Ilustração explicativa no momento certo
O corte esquemático da casa com a oliveira resolve em 3 s algo que levaria 30 s de narração.

### 4.6 Grade de painéis para passar o tempo
Calipso (7 anos) e os machados usam grades. É barato de produzir e comunica "muito tempo" ou "muitas tentativas".

### 4.7 CTA só no fim
Não há pedido de inscrição no meio da história, o que preserva a retenção.

---

## 5. Onde a referência é fraca (onde o Lume ganha)

| Fraqueza observada | Evidência | Nossa resposta (identidade do Lume) |
|---|---|---|
| **Rosto do protagonista oscila** | Odisseu de cabelo escuro (4:00), grisalho a partir das Sereias (16:00) e com traços diferentes de plano para plano | Silhuetas de teatro de sombras têm **forma fixa**: a consistência sai de graça |
| **Sem persona** | Narrador invisível, nenhum ritual de abertura ou fechamento | **O Contador** na fogueira abre e fecha cada episódio |
| **Sem elemento-assinatura** | Nada se repete de episódio para episódio além do estilo | A fogueira + marionetes que caem (contador de perdas) |
| **Mapa subutilizado** | 1 mapa de rota amostrado em 25 min | Mapa desenhado no pergaminho, **voltando a cada ilha**, com a rota queimando |
| **Perdas não contabilizadas** | 600 homens → 1 homem é dito, não mostrado | Fileira de marionetes na base da parede; cada perda derruba algumas |
| **Artefatos de IA** | Deformação no andar do ciclope (5:30), plano de Hermes repetido (12:16/12:24) | Recorte articulado (cut-out) não deforma; a IA gera só texturas e fundos |
| **Estética genérica de IA "Disney"** | Indistinguível de dezenas de canais | Sombra + pergaminho + brasa é reconhecível num thumbnail de 120 px |

---

## 6. Tradução para o nosso estilo (sombras + fogo)

A paleta do board tem 4 cores e **não muda**. A variação por lugar (item 4.1) entra só pela **luz do fogo e pela textura da parede**:

| Lugar | Como fazemos "uma cor por lugar" sem quebrar a paleta |
|---|---|
| Cenas de guerra / Polifemo | Fogo alto, Brasa saturada, sombras duras |
| Lotófagos / Calipso (paraísos-armadilha) | Fogo baixo e quieto, Pergaminho dominante, sombras macias e borradas |
| Poseidon / tempestades | Parede molhada, a chama se dobra pelo vento, mais Fuligem |
| Mundo dos mortos | Fogo quase apagado: só brasa, a parede some no Carvão, sombras translúcidas |
| Trinácia (Sol) | A única cena em que a chama "estoura" de brilho, quase branca |
| Ítaca | Volta ao fogo calmo do início, fechando o círculo |

Os outros recursos da referência ficam assim:

- **Gancho em flashforward:** mantido, mas como **faíscas** que sobem da fogueira e viram, cada uma, uma sombra-clímax na parede.
- **Selo do texto original:** em vez do escriba, o Contador abre um pergaminho com o verso grego (*Ἄνδρα μοι ἔννεπε, Μοῦσα…*), que é lido em português.
- **Som virando imagem:** o canto das sereias vira fumaça que se enrola na sombra de Odisseu; o grito do ciclope faz a chama tremer.
- **Grade de painéis:** vira **várias sombras lado a lado na parede**, como quadros de um friso.
- **Corte esquemático:** vira **desenho a carvão sobre o pergaminho** (oliveira, rota, estreito de Cila e Caríbdis).
- **Flashback:** a chama fica azul-acinzentada por 2 s (o único momento fora da paleta, como regra de exceção).

---

## 7. Métricas-alvo para o nosso EP01 (derivadas da referência)

| Item | Referência | Nosso alvo |
|---|---|---|
| Duração | 24:49 | 22–25 min |
| Mediana por plano | ~6,6 s | 5–7 s |
| Bloco mais lento | Caverna, ~8 cortes em 2 min | Manter a desaceleração na caverna e no mundo dos mortos |
| Bloco mais rápido | Cila → Zeus, 18 cortes em 2 min | 20+ cortes, com as marionetes caindo no ritmo |
| Mapas de rota | ~1 | 1 por ilha (≈ 10) |
| Momentos de "som virando imagem" | 4–5 | 6 ou mais |
| CTA no meio | 0 | 0 (só a fala do Contador no fechamento) |
| Gancho | 40–48 s | ≤ 45 s |

---

## 8. Pendências

- [ ] **Áudio:** conseguir um arquivo **com som** para analisar voz (andamento, pausas), música e SFX. O MP4 enviado é só vídeo.
- [ ] Cruzar os tempos desta tabela com os 28 blocos da transcrição, para gerar o roteiro do EP01 já com as marcações de cena.
- [ ] Testar uma thumbnail da referência ao lado de 3 thumbnails do Lume num print do feed.
