# 04 — Cinematografia: como fazer do Lume um filme, e não um vídeo

> **Objetivo:** superar a referência (doc 02) não com mais efeitos, mas com **gramática de cinema**: luz motivada, direção de tela com significado, escala, ritmo desenhado e som que conduz.
> **Premissa técnica:** o teatro de sombras é feito numa **cena 3D real** (Blender). Uma fonte de luz (a fogueira), marionetes planas entre a luz e a parede, e uma câmera virtual. As sombras são **projetadas de verdade**, não desenhadas. É isso que dá à imagem uma física que a IA de imagem-para-vídeo da referência não tem.

---

## 1. Os dois mundos

O vídeo tem dois planos de realidade, cada um com câmera e luz próprias.

| | **Mundo do Contador** (o "agora") | **Mundo da Parede** (a história) |
|---|---|---|
| O que é | O encapuzado, a fogueira, as ruínas ao redor | As sombras projetadas na pedra |
| Câmera | Lente "longa" (equiv. 85–135 mm), profundidade rasa, câmera na mão sutil (respiração) | Lente "normal" (35–50 mm), câmera em trilho/grua, movimentos limpos |
| Luz | Fogo como única fonte, contraluz no capuz | Fogo de baixo + luzes extras que "não deveriam existir" (deuses) |
| Tempo de tela | ~8–10% do episódio | ~90% |
| Função | Ritual, respiro, comentário, quebra de ritmo | A história |

### Passagens entre os mundos (as transições-assinatura)
1. **Entrar na parede:** push-in no ombro do Contador até a pedra ocupar o quadro, e a sombra começa a se mover.
2. **Faísca:** uma brasa sobe da fogueira em close, a câmera a segue, e ela vira estrela, tocha ou olho na parede (match cut).
3. **Fumaça:** a fumaça cobre a lente e se abre já na cena seguinte.
4. **Mão do Contador:** a mão entra no feixe de luz e **a sombra da mão vira a sombra de um deus**, que pega o barco (Poseidon, Zeus).
5. **Sair da parede:** a chama baixa, a parede escurece e o rack focus volta para o capuz.

> A referência não tem nada disso: é sempre o mesmo plano de realidade. Os dois mundos criam **estrutura de filme**: um narrador e uma história que se comentam.

---

## 2. Luz: o fogo é o diretor de fotografia

### 2.1 Fogo como medidor de tensão
A fogueira é a key light **e** o termômetro emocional. A animação da luz é planejada, não aleatória.

| Nível | Intensidade | Tremulação | Temperatura | Quando |
|---|---|---|---|---|
| 1 · Brasa | 15% | lenta, 0,5 Hz | 1800 K | Mundo dos mortos, luto |
| 2 · Calmo | 40% | suave, 1 Hz | 2200 K | Contador, Ítaca, Calipso |
| 3 · Vivo | 70% | média, 2 Hz | 2600 K | Viagem, diálogo |
| 4 · Alto | 100% | forte, 4 Hz, com picos | 3000 K | Batalha, Polifemo, Lestrigões |
| 5 · Estouro | 160% (clipa a parede) | instantâneo | 5500 K (quase branco) | **Só 2× por episódio**: raio de Zeus e Hélio |

### 2.2 Distância da marionete = tamanho e foco da sombra
É a "lente" do teatro de sombras, uma técnica real que a referência não pode imitar:
- **Marionete perto da parede:** sombra pequena, nítida, borda dura. Use para **humanos, controle, clareza**.
- **Marionete perto do fogo:** sombra **gigante**, borrada, que vibra com a chama. Use para **ameaça, deuses, pesadelo**.
- **Mover a marionete do fogo até a parede** em tempo real é um "zoom" orgânico: o monstro se aproxima e fica mais nítido e mais real.

### 2.3 Luz motivada para o sobrenatural
- **Deuses nunca têm sombra própria.** Eles são uma **segunda fonte de luz** que entra no quadro: Atena = luz fria de cima, Poseidon = luz ondulada (cáustica de água) vinda de baixo, Hélio = sol de meio-dia que apaga o fogo, Zeus = estroboscópio de raio.
- **Duas fontes de luz = duas sombras do mesmo herói.** Quando um deus intervém, Odisseu ganha uma segunda sombra, e a cena literalmente mostra "ele não está sozinho".
- **Monstros:** a luz vaza só pelos furos da marionete (o olho de Polifemo brilha em Brasa).

### 2.4 Contraste e exposição
- Sempre de 1/3 a 2/3 do quadro em Carvão absoluto.
- Ratio de luz alto (contraste 8:1 ou mais). A parede iluminada nunca chega no branco puro, exceto no nível 5.

---

## 3. Câmera: gramática de planos

### 3.1 Vocabulário (o que cada plano significa)

| Plano | Na parede | Significado |
|---|---|---|
| **Plano geral de friso** | Parede inteira, várias sombras lado a lado | Tempo, multidão, viagem |
| **Plano médio** | Uma ou duas marionetes | Diálogo, ação |
| **Close de silhueta** | Cabeça/mão de perfil, borda nítida | Decisão, emoção |
| **Insert de objeto** | Saco de ventos, erva moly, arco, fio do tear | O objeto que muda a história |
| **Plano de escala** | Sombra gigante enchendo o quadro + humano minúsculo no canto | Ameaça (assinatura do canal) |
| **Plano do Contador** | Capuz em perfil, mão ao fogo | Comentário, ritual |

### 3.2 Movimentos

| Movimento | Uso | Regra |
|---|---|---|
| **Push-in lento** (2–4% de escala em 6 s) | Tensão crescente | Padrão para cenas paradas; nunca deixar um plano 100% estático |
| **Dolly lateral** acompanhando a sombra | Viagem, perseguição | Sempre no sentido da direção de tela do personagem |
| **Tilt para cima** | Revelar a altura de um monstro/deus | Começar nos pés da sombra, terminar fora do quadro (nunca mostrar o topo) |
| **Rack focus** entre o capuz (primeiro plano) e a parede | Passagem entre mundos | Só nas passagens |
| **Câmera tremendo** | Impacto (pedra, raio) | 6–10 quadros, nunca contínuo |
| **Plano fixo e longo** | Caverna de Polifemo, mundo dos mortos | O único lugar onde a câmera para de propósito |

### 3.3 Proporção de tela como dramaturgia
- **16:9** no Mundo do Contador.
- **2,39:1** (barras pretas que entram lentamente) quando a história fica épica: chegada a uma ilha, monstro, batalha.
- **Barras fechando até 3:1** no pico do terror (caverna, Cila): a imagem literalmente esmaga.
- A referência usa letterbox de forma esporádica. Aqui é uma regra com significado.

---

## 4. Direção de tela (a regra que transforma tudo)

Na tradição do teatro de sombras e nos vasos gregos, **o perfil é tudo**. Vamos usar isso como linguagem:

| Direção | Significado |
|---|---|
| **→ Esquerda para direita** | Rumo a Ítaca, para casa, o desejo de Odisseu |
| **← Direita para esquerda** | Para longe de casa: deuses contra, tempestades, monstros |
| **Odisseu olhando para a esquerda** | Só quando ele **erra** (gritar o nome para Polifemo, os homens abrindo o saco de ventos) |
| **Virada final** | No reencontro com Penélope, os dois se viram de frente (o único momento de frontalidade do herói no episódio) |

**Mapa:** a rota no pergaminho também respeita isso. Cada desvio para a esquerda é um castigo, e o espectador sente isso sem perceber.

---

## 5. Cor: o color script do EP01

A paleta da marca não muda (doc 03). A variação vem da **temperatura e da intensidade do fogo** (seção 2.1) e da **textura da parede**.

| Ato | Ilhas | Nível de fogo | Parede | Sensação |
|---|---|---|---|---|
| **I · Saída** | Troia, Ismaro | 4 | Pedra seca, fuligem | Glória → arrogância |
| | Lotófagos | 2 | Pedra com musgo dourado | Torpor bonito |
| **II · Descida** | Polifemo | 4 → 1 → 4 | Rocha de caverna, úmida | Claustrofobia |
| | Éolo, Lestrigões | 3 → 4 | Pedra do mar, sal | Esperança → massacre |
| | Circe | 3 | Parede com folhagem em sombra | Sedução |
| **III · Fundo** | Mundo dos mortos | **1 + Cinza-alma** | Parede que some no escuro | Luto |
| | Sereias, Cila, Caríbdis | 4 | Pedra molhada, vento | Pavor |
| | Trinácia | 3 → **5** | Pedra clara, sol | Pecado → castigo |
| **IV · Volta** | Calipso | 2 | Pedra quente, quieta | Prisão doce |
| | Ítaca | 2 → 4 → 2 | A mesma parede do início | Retorno, vingança, paz |

---

## 6. Montagem: ritmo desenhado

### 6.1 Curva de tensão do episódio
Baseada nos dados da referência (doc 02), mas mais extrema nos dois sentidos:

| Bloco | Mediana por plano | Referência |
|---|---|---|
| Gancho | 2–3 s | ~4 s |
| Viagem/transição | 5–6 s | ~6,6 s |
| Caverna / mundo dos mortos | **12–20 s** | ~10 s |
| Lestrigões / Cila → Zeus | **1,5–2,5 s** | ~3–4 s |
| Reencontro final | 8–10 s | ~8 s |

### 6.2 Técnicas de corte
- **Match cut de forma:** fogueira → olho do ciclope; brasa → estrela; fumaça → canto das sereias; fio do tear → corda do arco.
- **Corte J e L:** a voz do próximo bloco entra antes da imagem (J); o som do monstro continua sobre o Contador (L). Isso costura os dois mundos.
- **Corte no silêncio:** antes de cada revelação, 1–2 s sem fogo no áudio, e a imagem corta junto com a volta do som.
- **Montagem por friso:** passagens de tempo (o ano com Circe, os 7 anos com Calipso) como várias sombras lado a lado, com a câmera passando em dolly lateral. Substitui a grade de painéis da referência.
- **Repetição com variação:** o plano de abertura (Contador de costas, fogueira, parede) volta no fim do Ato II e no fim do episódio, cada vez com o fogo mais baixo.

### 6.3 Estrutura de 4 atos com pontos de virada

| Minuto (alvo) | Batida |
|---|---|
| 0:00–0:45 | **Gancho**: faíscas → sombras-clímax → Contador → bordão |
| 0:45 | Cartela de abertura (sting LUME) |
| ~6:00 | **Virada I:** Odisseu grita o próprio nome (vira para a esquerda) |
| ~10:00 | **Virada II:** a frota é destruída (fileira de marionetes cai) |
| ~14:00 | **Ponto médio:** mundo dos mortos, o único Cinza-alma |
| ~19:00 | **Virada III:** raio de Zeus, nível de fogo 5, o último tripulante cai |
| ~23:00 | **Clímax:** o arco (fio do tear → corda) |
| ~24:00 | **Resolução:** a cama de oliveira, os dois de frente |
| final | Contador: *"O lume apaga. A história fica."* + end screen |

---

## 7. Som: metade do filme

> A referência veio sem áudio (doc 02, pendência). Estas são as regras do Lume, independentes dela.

| Técnica | Aplicação |
|---|---|
| **Diegese da fogueira** | O fogo crepita sempre no Mundo do Contador e vira grave e distante na parede |
| **Perspectiva sonora** | Sombra perto do fogo (gigante) = som grave, próximo e com reverb curto; perto da parede = som pequeno e seco |
| **Foley de teatro** | Rangido de pino de marionete, papel e couro em momentos íntimos. Assume o artifício, como os pinos visíveis. |
| **Leitmotivs** | Odisseu = lira de 3 notas (as mesmas do sonic logo); Poseidon = drone grave com água; Penélope = tear rítmico; mortos = coro sem palavras |
| **Silêncio dramático** | Antes da revelação do mendigo e antes do raio de Zeus |
| **Voz do Contador** | Microfone próximo (efeito de proximidade), ar no áudio, sem música por baixo |
| **Mixagem** | −14 LUFS integrado (padrão do YouTube); diálogo sempre 6–8 dB acima da música |

---

## 8. Pós-produção (acabamento de filme)

| Etapa | Especificação |
|---|---|
| Halation | Leve brilho vermelho em volta das bordas mais claras da parede (efeito de película) |
| Grão | 35 mm, intensidade constante, inclusive nos mapas |
| Vinheta | Sempre ativa, mais forte em fogo baixo |
| Gate weave | Micro-oscilação do quadro (0,3 px) só no Mundo do Contador, como se fosse filmado |
| Partículas | Brasas e cinzas cruzando o primeiro plano, em profundidade de campo rasa |
| Névoa volumétrica | Fumaça entre o fogo e a parede, que torna o **feixe de luz visível** |
| Taxa de quadros | Parede a **12 qps com motion blur** (efeito stop-motion artesanal); Contador e fogo a 24 qps. A mistura deixa claro que são dois mundos. |
| Master | 3840×2160, 24p, Rec.709, entregue em H.264 alto bitrate + ProRes de arquivo |

---

## 9. Plano a plano: como fica uma cena (exemplo: o olho de Polifemo)

| # | Plano | Duração | Câmera | Fogo | Som |
|---|---|---|---|---|---|
| 1 | Close: a estaca na brasa, ponta incandescente | 4 s | Push-in | 3 | Crepitar crescente |
| 2 | Sombra dos 4 homens levantando a estaca (perto da parede, nítidos) | 3 s | Fixo | 3 | Respiração |
| 3 | Sombra de Polifemo dormindo (perto do fogo, gigante, borrada) | 5 s | Tilt lento para cima | 3 | Ronco grave |
| 4 | **Silêncio**: o fogo some do áudio | 1,5 s | Fixo | 2 | Nada |
| 5 | A estaca entra, **o furo-olho da marionete apaga** | 0,5 s | Tremor | **4** | Grito |
| 6 | A chama inteira se curva para trás (o grito "sopra" o fogo) | 2 s | Fixo | 4 → 2 | Grito em reverb |
| 7 | Contador: a mão se afasta do fogo | 2 s | Rack focus | 2 | Fogo volta |

**Diferença para a referência:** lá, o grito é um anel desenhado. Aqui, **o grito age sobre a luz da cena**, e o espectador sente isso fisicamente.

---

## 10. Checklist de "filme, não vídeo" (para cada cena)

- [ ] A luz tem uma fonte que dá para apontar?
- [ ] A direção de tela respeita → casa / ← contra?
- [ ] O tamanho da sombra (distância do fogo) está contando algo?
- [ ] Há um plano 100% parado sem intenção? (corrigir com push-in)
- [ ] A proporção de tela está certa para a emoção?
- [ ] O nível de fogo segue o color script?
- [ ] Há pelo menos um corte motivado por som ou forma?
- [ ] Funciona sem som (no celular, mudo)?
- [ ] O personagem é reconhecível só pela silhueta?
