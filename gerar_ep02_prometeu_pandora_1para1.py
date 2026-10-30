# -*- coding: utf-8 -*-
"""Gerador Canônico 1:1 do Episódio 02 — O Mito de Prometeu e o Jarro de Pandora (50 Blocos / 510.0s).

1. Gera `storage_local/roteiro/roteiro_ep02_prometeu_pandora_50_planos_1para1.json` validado por
   `validar_paridade_1_para_1_blocos_planos` (50 blocos = 50 Start Frames IA = 50 vídeos Firefly).
2. Sintetiza os 50 blocos de narração com voz neural barítono ("O Contador"), compõe a ambiência
   diegética (fogo do braseiro, forja de Hefesto, vento do Cáucaso, cerâmica do pithos) + trilha modal grega,
   aplica o Silêncio Dramático Absoluto em [436.9s, 438.4s] e masteriza em -14.0 LUFS (510.0s exatos).
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

from contratos.integridade_assets import (
    criar_diretorios_episodio_isolado,
    validar_paridade_1_para_1_blocos_planos,
)

EPISODIO_ID = "ep02_prometeu_pandora_1para1"
TITULO_EPISODIO = "Zeus Não Criou a Mulher por Amor: A Vingança Oculta por Trás do Fogo de Prometeu"
THUMBNAIL_WORDS = "O PREÇO DO FOGO"

STYLE_PREFIX = (
    "2D hand-drawn Western graphic novel animation frame (style of Tartakovsky's Primal meets Mike Mignola's Hellboy "
    "and Caravaggio tenebrism), heavy charcoal ink outlines, 75% of frame in deep obsidian shadow (#0A0705), dramatic "
    "firelight in aged bronze (#C89B3C), burning ember orange (#E85D04), and incandescent gold (#FFD166), widescreen 16:9, no text: "
)

# 50 Blocos (10.2s cada = 510.0s / 08:30):
# (ato_id, ato_titulo, canto_verso, contador_hud, cena_tipo, texto_narracao, prompt_start_frame, prompt_video)
BLOCOS_50_SPEC: List[Tuple[str, str, str, str, str, str, str, str]] = [
    # PRÓLOGO · A MENTIRA DA CAIXA (Blocos 1 a 4 | 00:00.0 - 00:40.8)
    (
        "PROLOGO",
        "PRÓLOGO · A MENTIRA DA CAIXA",
        "Trabalhos e Dias, v. 42-46",
        "MITO I · O FOGO ROUBADO",
        "contador_braseiro",
        "O fogo ainda conta as mesmas histórias. Você cresceu ouvindo que Pandora abriu uma caixa por curiosidade e que a Esperança salvou a humanidade.",
        "Medium close-up of O Contador, an ancient blind Greek storyteller with weathered wrinkles, silver-white beard, and dark hooded cloak seated beside a glowing bronze tripod brazier in a pitch-black stone chamber.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm golden flames and orange embers dance in the bronze brazier, casting flickering Caravaggio light across the blind storyteller's bearded face. Slow camera push-in at 24fps.",
    ),
    (
        "PROLOGO",
        "PRÓLOGO · A MENTIRA DA CAIXA",
        "Trabalhos e Dias, v. 90-95",
        "PITHOS · O JARRO DE BARRO",
        "pithos_sombra",
        "Mas no poema original de Hesíodo, escrito há dois mil e setecentos anos, nunca existiu caixa nenhuma: era um jarro de barro funerário chamado pithos.",
        "Dramatic 16:9 chiaroscuro composition inside a dark ancient Greek temple chamber: a tall ornate terracotta storage jar (pithos) with archaic geometric bronze bands stands on a stone pedestal, lit by a single warm shaft of amber firelight.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Golden dust motes and warm amber torchlight shimmer around the tall ancient Greek terracotta pithos jar in the dark stone chamber. Slow cinematic push-in at 24fps.",
    ),
    (
        "PROLOGO",
        "PRÓLOGO · A MENTIRA DA CAIXA",
        "Teogonia, v. 570-584",
        "A ARMADILHA DE ZEUS",
        "zeus_trono_sombra",
        "Mais perturbador ainda: a primeira mulher não nasceu de um gesto de amor dos deuses, mas de uma ordem fria de vingança decretada no topo do Olimpo.",
        "Colossal low-angle 16:9 chiaroscuro frame atop Mount Olympus at night: the towering bearded silhouette of Zeus seated on a monolithic black marble throne surrounded by glowing golden clouds and distant amber lightning.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Golden storm clouds and warm amber light pulse slowly behind the monumental silhouette of Zeus on his high marble throne. Slow low-angle push-in at 24fps.",
    ),
    (
        "PROLOGO",
        "PRÓLOGO · A MENTIRA DA CAIXA",
        "Trabalhos e Dias, v. 96-100",
        "ELPIS · DÁDIVA OU PRAGA?",
        "contador_fagulha",
        "E aquilo que ficou trancado lá dentro, que chamamos de Esperança, pode ter sido a última e mais engenhosa maldição deixada para os mortais.",
        "Extreme close-up of O Contador's aged hand holding a gnarled olive-wood staff over the bronze brazier as a single bright golden spark hovers above the red-orange ash in pitch-black darkness.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. A single luminous golden spark and thin amber smoke rise from the bronze brazier past the storyteller's weathered hand. Slow atmospheric push-in at 24fps.",
    ),
    # ATO I · O BANQUETE DE MECONE (Blocos 5 a 11 | 00:40.8 - 01:52.2)
    (
        "ATO_I",
        "ATO I · O TRUQUE DE MECONE",
        "Teogonia, v. 535-537",
        "PLANÍCIE DE MECONE",
        "mecone_assembleia",
        "Tudo começou na planície de Mecone, no tempo em que deuses e homens ainda se sentavam à mesma mesa para decidir a partilha do mundo.",
        "Epic wide 16:9 chiaroscuro landscape of the ancient plain of Mecone at twilight: towering stone altars with burning bronze braziers stand between silhouetted mortal men on the left and luminous towering Olympian figures on the right.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Golden smoke rises from the stone altars on the twilight plain of Mecone as warm firelight flickers across the gathered silhouettes. Slow panoramic pan at 24fps.",
    ),
    (
        "ATO_I",
        "ATO I · O TRUQUE DE MECONE",
        "Teogonia, v. 510-514",
        "PROMETEU · A MENTE QUE VÊ ANTES",
        "prometeu_perfil",
        "Diante do altar estava o titã Prometeu — cujo nome em grego significa Aquele Que Pensa Antes — ao lado de seu irmão impulsivo, Epimeteu, Aquele Que Só Pensa Depois.",
        "Striking 16:9 chiaroscuro dual portrait: in the foreground, the noble bearded Titan Prometheus with piercing golden-lit eyes looking ahead in calculation; behind him in softer shadow, his brother Epimetheus looking backward.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Flickering amber firelight illuminates Prometheus's thoughtful profile and bronze cloak as golden embers drift through the dark air. Slow camera push-in at 24fps.",
    ),
    (
        "ATO_I",
        "ATO I · O TRUQUE DE MECONE",
        "Teogonia, v. 538-541",
        "AS DUAS OFERENDAS",
        "altar_duas_partes",
        "Encarregado de dividir o grande boi sacrificado, Prometeu decidiu proteger os humanos da fome eterna armando um dilema visual para o próprio rei dos deuses.",
        "Dramatic 16:9 chiaroscuro close-up of a carved stone sacrificial table lit by twin bronze torches, where Prometheus's hands arrange two distinct ceremonial offerings wrapped on the stone slab.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Twin bronze torches cast dancing orange light over the stone altar as Prometheus's hands prepare the two ceremonial portions. Slow push-in at 24fps.",
    ),
    (
        "ATO_I",
        "ATO I · O TRUQUE DE MECONE",
        "Teogonia, v. 539-540",
        "PORÇÃO I · RICA MAS FEIA",
        "porcao_escondida",
        "Na primeira porção, escondeu toda a carne nutritiva debaixo de um invólucro feio e repulsivo aos olhos, feito para parecer o resto desprezível.",
        "Tactile 16:9 chiaroscuro close-up on the stone altar: a dark, rough-textured leather bundle resting in deep shadow while a faint warm golden aura glimmers from within its folds.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm amber torchlight flickers across the rough dark bundle on the stone altar as subtle golden light glimmers around its edges. Slow push-in at 24fps.",
    ),
    (
        "ATO_I",
        "ATO I · O TRUQUE DE MECONE",
        "Teogonia, v. 540-541",
        "PORÇÃO II · BELA MAS VAZIA",
        "ossos_gordura_branca",
        "Na segunda porção, arrumou apenas os ossos secos e vazios, mas cobriu tudo com uma camada reluzente de gordura branca que brilhava à luz das tochas.",
        "High-contrast 16:9 chiaroscuro close-up on the stone altar: a gleaming, deceptively rich white-and-gold mound that catches the bright reflection of the temple firelight against the obsidian background.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Bright golden firelight shimmers across the gleaming white offering on the stone slab while shadows dance behind it. Slow camera push-in at 24fps.",
    ),
    (
        "ATO_I",
        "ATO I · O TRUQUE DE MECONE",
        "Teogonia, v. 548-552",
        "A ESCOLHA DE ZEUS",
        "zeus_mao_escolha",
        "Zeus estendeu as duas mãos sobre a parte brilhante. Ao levantar o véu branco e encontrar somente ossos nus, uma cólera silenciosa escureceu o céu.",
        "Dramatic 16:9 chiaroscuro frame: the monumental hand of Zeus lifting the gleaming white cover on the stone altar, revealing bare ivory-white bones beneath as dark storm clouds gather overhead.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Golden light flashes across the stone altar as Zeus's hand lifts the veil and dark storm clouds swirl in the background sky. Slow dramatic push-in at 24fps.",
    ),
    (
        "ATO_I",
        "ATO I · O TRUQUE DE MECONE",
        "Teogonia, v. 556-560",
        "A FETERNA DA FUMAÇA",
        "fumaca_altar_ossos",
        "Desde aquele dia, os homens ficaram com o alimento que sustenta a vida e queimaram apenas os ossos nos altares — mas Zeus jurou cobrar o preço.",
        "Atmospheric 16:9 chiaroscuro wide shot of ancient Greek mortals gathered around a stone altar at night as fragrant white-and-gold smoke spirals high toward the cold dark stars of Olympus.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Swirling columns of golden-amber smoke rise from the stone altar toward the night sky while mortals watch in silhouette. Slow vertical camera tilt at 24fps.",
    ),
    # ATO II · O MUNDO SEM FOGO E O CAULE DE FÉRULA (Blocos 12 a 19 | 01:52.2 - 03:13.8)
    (
        "ATO_II",
        "ATO II · O ROUBO DA CENTELHA",
        "Teogonia, v. 561-564",
        "CASTIGO I · TREVAS E FRIO",
        "aldeia_sem_fogo",
        "A primeira retaliação foi imediata: Zeus negou aos freixos a chama incansável do fogo, mergulhando as aldeias humanas no frio e na escuridão absoluta.",
        "Desolate 16:9 chiaroscuro wide shot of an ancient stone village at night in deep obsidian shadow (#0A0705) and cold ash-grey mist, with stone hearths completely cold and dark under a freezing wind.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Cold silver-grey wind and mist blow through the dark stone village around the unlit hearths under a starless night sky. Slow tracking shot at 24fps.",
    ),
    (
        "ATO_II",
        "ATO II · O ROUBO DA CENTELHA",
        "Prometeu Acorrentado, v. 447-453",
        "HOMENS COMO SOMBRAS",
        "caverna_frio_humanos",
        "Nos versos de Ésquilo, os homens viviam como formas de sonhos no fundo de cavernas sem sol, sem saber forjar o bronze, cozer o pão ou medir as estações.",
        "Haunting 16:9 chiaroscuro interior of a cold pitch-black cavern: cloaked mortal families huddled together in pale ash-grey twilight, shivering beside unlit wood piles.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Pale grey mist drifts through the cold cavern entrance past the huddled cloaked figures in deep Caravaggio shadow. Slow empathetic push-in at 24fps.",
    ),
    (
        "ATO_II",
        "ATO II · O ROUBO DA CENTELHA",
        "Teogonia, v. 565-566",
        "A SUBIDA SILENCIOSA",
        "prometeu_subida_olimpo",
        "Vendo a criação definhar no gelo, Prometeu subiu sozinho na calada da noite até a forja divina de Hefesto, levando apenas o caule seco de uma planta.",
        "Majestic 16:9 chiaroscuro low-angle shot of Prometheus in a dark wind-swept cloak ascending the monumental obsidian stairway of Mount Olympus at night, holding a long hollow fennel stalk (narthex).",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Prometheus's cloak billows in the mountain wind on the dark stone steps while warm orange light glows from the forge at the summit. Slow upward pan at 24fps.",
    ),
    (
        "ATO_II",
        "ATO II · O ROUBO DA CENTELHA",
        "Trabalhos e Dias, v. 50-52",
        "NARTHEX · A FÉRULA OCA",
        "caule_ferula_brasa",
        "Não era uma tocha aberta que o vento apagaria: era o narthex, a férula gigante cujo miolo branco queima devagar como um pavio sem mostrar chama por fora.",
        "Extreme close-up 16:9 chiaroscuro frame inside the dark forge: Prometheus's hand touching the hollow fibrous tip of a giant fennel stalk (narthex) to a glowing golden-orange coal on a bronze anvil.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Incandescent golden-orange light ignites inside the hollow core of the fennel stalk as tiny amber sparks float upward in the dark forge. Slow macro push-in at 24fps.",
    ),
    (
        "ATO_II",
        "ATO II · O ROUBO DA CENTELHA",
        "Prometeu Acorrentado, v. 109-111",
        "A SEMENTE DE TODAS AS ARTES",
        "prometeu_descida_fogo",
        "Com a semente do fogo escondida no caule oco, o titã desceu das nuvens trazendo aos mortais o mestre de todas as artes e o princípio da civilização.",
        "Heroic 16:9 chiaroscuro wide frame: Prometheus descending the rocky mountain path through night fog, the hollow fennel stalk in his hand radiating a warm internal golden-orange glow against the obsidian cliffs.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm golden-amber light pulses from the fennel stalk in Prometheus's hand, illuminating the swirling mountain fog around him. Slow tracking camera at 24fps.",
    ),
    (
        "ATO_II",
        "ATO II · O ROUBO DA CENTELHA",
        "Prometeu Acorrentado, v. 454-506",
        "O DESPERTAR DA TÉCNICA",
        "forja_humana_luz",
        "Daquela única brasa nasceram a metalurgia, a cerâmica, a navegação, a escrita e a astronomia: o barro frio transformou-se em cidade iluminada.",
        "Triumphant 16:9 chiaroscuro montage-composition: ancient Greek artisans gathered around a roaring stone hearth, hammering glowing bronze on an anvil and shaping clay amphoras under warm golden firelight.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Bright golden sparks fly from the bronze anvil and warm orange flames dance in the stone hearth illuminating the artisans. Slow cinematic pan at 24fps.",
    ),
    (
        "ATO_II",
        "ATO II · O ROUBO DA CENTELHA",
        "Teogonia, v. 567-569",
        "MIL FOGUEIRAS NA TERRA",
        "terra_iluminada_noite",
        "Mas quando Zeus olhou para baixo do alto do Olimpo e viu o brilho distante de mil fogueiras acesas na noite dos homens, o trovão tremeu de raiva.",
        "Breathtaking high-angle 16:9 chiaroscuro view from the dark clouds of Olympus looking down at the pitch-black earth below, where hundreds of tiny incandescent golden-orange campfires glow along the coastline.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Hundreds of tiny golden campfires twinkle across the dark coastline far below while storm clouds drift in the foreground. Slow high-angle push-in at 24fps.",
    ),
    (
        "ATO_II",
        "ATO II · O ROUBO DA CENTELHA",
        "Trabalhos e Dias, v. 53-58",
        "O PREÇO DO FOGO",
        "zeus_sentenca_fogo",
        "O rei do céu pronunciou então a sentença: em troca do fogo roubado, enviaria aos homens um mal tão belo que todos abraçariam a própria ruína sorrindo.",
        "Intense 16:9 chiaroscuro close-up of Zeus's bearded face half-lit by golden lightning against deep obsidian shadow, his eyes narrowed in cold calculation as he raises his bronze scepter.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Golden light flickers across Zeus's sculpted beard and bronze scepter against the pitch-black background. Slow tense push-in at 24fps.",
    ),
    # ATO III · A FORJA DE PANDORA: O BELO MAL (Blocos 20 a 27 | 03:13.8 - 04:35.4)
    (
        "ATO_III",
        "ATO III · A FORJA DE PANDORA",
        "Trabalhos e Dias, v. 60-63",
        "A OFICINA DE HEFESTO",
        "hefesto_barro_agua",
        "Zeus convocou Hefesto, o deus artífice do fogo, e ordenou que misturasse terra e água para modelar uma figura com a semblante imortal das deusas.",
        "Atmospheric 16:9 chiaroscuro frame inside Hephaestus's subterranean volcanic forge: the muscular bearded smith-god Hephaestus sculpting a serene life-size figure of wet clay and golden light beside a roaring furnace.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm orange furnace light and golden sparks swirl around Hephaestus as he shapes the luminous clay statue in the dark forge. Slow push-in at 24fps.",
    ),
    (
        "ATO_III",
        "ATO III · A FORJA DE PANDORA",
        "Trabalhos e Dias, v. 63-64",
        "O PRESENTE DE ATENA",
        "atena_veu_prata",
        "Cada divindade do Olimpo trouxe um dom para torná-la irresistível: Atena vestiu-a com uma túnica prateada e ensinou suas mãos a tecer teias complexas.",
        "Luminous 16:9 chiaroscuro frame: the helmeted goddess Athena draping a shimmering silver-and-gold woven veil over the head of Pandora, who stands in serene profile amidst deep temple shadows.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The shimmering silver-and-gold veil flows gently in the warm temple light as Athena drapes it over Pandora's shoulders. Slow graceful push-in at 24fps.",
    ),
    (
        "ATO_III",
        "ATO III · A FORJA DE PANDORA",
        "Trabalhos e Dias, v. 65-66",
        "O ENCANTO DE AFRODITE",
        "afrodite_coroa_ouro",
        "Afrodite derramou sobre sua fronte o encanto dourado e o desejo que consome os membros, enquanto Hefesto pousou em seus cabelos uma coroa de ouro cinzelado.",
        "Radiant 16:9 chiaroscuro close-up of Pandora's face in Caravaggio lighting as a finely sculpted golden diadem of floral reliefs is placed upon her dark curls amidst floating golden dust.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Golden light and delicate amber particles shimmer around the ornate gold crown resting on Pandora's dark hair. Slow close-up push-in at 24fps.",
    ),
    (
        "ATO_III",
        "ATO III · A FORJA DE PANDORA",
        "Trabalhos e Dias, v. 67-80",
        "O DOM SECRETO DE HERMES",
        "hermes_sussurro_pandora",
        "Por último veio Hermes, o mensageiro das encruzilhadas: em seu peito ele soprou a voz articulada, a mente astuta e a inquietação que nunca descansa.",
        "Mysterious 16:9 chiaroscuro composition: Hermes in his winged bronze petasos hat leaning from the deep shadow to whisper a stream of glowing golden light toward Pandora's ear.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. A subtle ribbon of glowing golden light drifts from Hermes's hand as warm rim-lighting outlines Pandora's profile. Slow atmospheric pan at 24fps.",
    ),
    (
        "ATO_III",
        "ATO III · A FORJA DE PANDORA",
        "Trabalhos e Dias, v. 81-82",
        "PANDORA · TODOS OS DONS",
        "pandora_revelada_olimpo",
        "Chamaram-na de Pandora — Aquela que possui todos os dons —, aquilo que Hesíodo definiu com duas palavras brutais: kalon kakon, o belo mal.",
        "Iconic 16:9 chiaroscuro full-shot of Pandora standing at the threshold of Olympus, veiled in silver and crowned in gold, backlit by a blazing amber sun while the foreground floor lies in deep obsidian shadow.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Golden sunlight streams behind Pandora's veiled silhouette as her silver robes stir gently in the mountain breeze. Slow majestic push-in at 24fps.",
    ),
    (
        "ATO_III",
        "ATO III · A FORJA DE PANDORA",
        "Trabalhos e Dias, v. 85-87",
        "O AVISO ESQUECIDO",
        "prometeu_alerta_epimeteu",
        "Antes de ser capturado, Prometeu havia deixado um único mandamento ao irmão Epimeteu: jamais aceitar nenhum presente vindo de Zeus Olímpico, mas devolvê-lo na hora.",
        "Urgent 16:9 chiaroscuro frame in a torchlit stone courtyard: Prometheus gripping Epimetheus's shoulder with intense warning in his eyes, pointing upward toward the dark stormy sky of Olympus.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Torchlight flickers sharply across Prometheus and Epimetheus in the dark stone courtyard as embers drift past. Slow dramatic push-in at 24fps.",
    ),
    (
        "ATO_III",
        "ATO III · A FORJA DE PANDORA",
        "Trabalhos e Dias, v. 83-89",
        "A CHEGADA À CASA DE EPIMETEU",
        "epimeteu_recebe_pandora",
        "Mas quando Hermes conduziu Pandora até a porta de Epimeteu, o encanto apagou a memória do aviso: ele abriu os braços — e só lembrou depois que o mal já estava dentro.",
        "Poignant 16:9 chiaroscuro frame at the open wooden doorway of an ancient Greek house: Epimetheus stepping forward in awe as Pandora and Hermes stand illuminated in warm golden doorway light.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm golden light spills through the open doorway across Epimetheus as Pandora stands veiled on the stone threshold. Slow camera push-in at 24fps.",
    ),
    (
        "ATO_III",
        "ATO III · A FORJA DE PANDORA",
        "Trabalhos e Dias, v. 90-93",
        "A IDADE ANTES DA DOR",
        "humanidade_sem_doenca",
        "Até aquele instante, diz o poema, as tribos dos homens viviam sobre a terra livres das fadigas penosas e das doenças silenciosas que trazem a velhice.",
        "Serene 16:9 chiaroscuro pastoral scene in warm bronze and golden sunset light: ancient Greek families harvesting wheat and resting under olive trees in peaceful harmony before the storm.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm golden sunset light sways across the olive trees and wheat fields as gentle amber breeze moves through the scene. Slow panoramic pan at 24fps.",
    ),
    # ATO IV · O CÁUCASO: A ROCHA E A ÁGUIA (Blocos 28 a 34 | 04:35.4 - 05:46.8)
    (
        "ATO_IV",
        "ATO IV · O ROCHEDO DO CÁUCASO",
        "Prometeu Acorrentado, v. 1-11",
        "CONFINS DA CÍTIA",
        "caucaso_deserto_pedra",
        "Enquanto a armadilha descia à Terra, Hefesto, Kratos e Bia arrastaram Prometeu até os confins desertos da Cítia, no abismo gelado das montanhas do Cáucaso.",
        "Colossal 16:9 chiaroscuro mountain landscape: jagged vertical obsidian peaks of the Caucasus rising into freezing ash-grey clouds above a bottomless dark chasm.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Pale silver-grey mountain mist and snow swirl around the towering black rock peaks of the Caucasus. Slow epic camera tilt at 24fps.",
    ),
    (
        "ATO_IV",
        "ATO IV · O ROCHEDO DO CÁUCASO",
        "Prometeu Acorrentado, v. 12-35",
        "O LAMENTO DE HEFESTO",
        "hefesto_relutante_caucaso",
        "Na tragédia de Ésquilo, até o próprio Hefesto chorou ao cumprir a ordem de prender um deus do mesmo sangue naquela escarpa onde nenhum mortal jamais pisou.",
        "Somber 16:9 chiaroscuro frame on the snowy mountain ledge: the bearded smith-god Hephaestus lowering his bronze hammer in sorrow beside the towering stone cliff face while wind whips his cloak.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Cold mountain wind stirs Hephaestus's dark cloak as warm amber light glints off his lowered bronze hammer. Slow push-in at 24fps.",
    ),
    (
        "ATO_IV",
        "ATO IV · O ROCHEDO DO CÁUCASO",
        "Prometeu Acorrentado, v. 88-92",
        "INVOCAÇÃO AO ÉTER E AO SOL",
        "prometeu_pico_caucaso",
        "Sozinho diante do precipício, Prometeu ergueu o rosto para o vento, para os rios e para o olho do Sol, chamando o universo inteiro como testemunha da injustiça.",
        "Heroic 16:9 chiaroscuro frame atop the jagged peak of Mount Caucasus: Prometheus standing tall against the monolithic black stone cliff, looking up as a single shaft of golden sunlight pierces the storm clouds.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. A dramatic beam of golden sunlight breaks through the dark clouds onto Prometheus atop the rocky peak as wind moves his hair. Slow push-in at 24fps.",
    ),
    (
        "ATO_IV",
        "ATO IV · O ROCHEDO DO CÁUCASO",
        "Teogonia, v. 521-525",
        "A ÁGUIA DE ASAS LONGAS",
        "aguia_sombra_caucaso",
        "Todos os dias uma águia colossal de asas longas descia das nuvens; todas as noites o titã imortal se regenerava no gelo para suportar o amanhecer seguinte.",
        "Majestic and ominous 16:9 chiaroscuro sky composition: the gigantic black silhouette of a long-winged eagle soaring across a blazing amber-and-crimson mountain sky above the jagged peaks of the Caucasus.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The colossal silhouetted eagle glides across the glowing amber mountain sky as clouds and golden mist drift below. Slow tracking shot at 24fps.",
    ),
    (
        "ATO_IV",
        "ATO IV · O ROCHEDO DO CÁUCASO",
        "Prometeu Acorrentado, v. 511-525",
        "O SEGREDO QUE ZEUS TEMIA",
        "prometeu_profecia_moiras",
        "No entanto, Prometeu guardava uma arma que nem o raio podia arrancar: o conhecimento profético de qual casamento futuro derrubaria Zeus do trono do Olimpo.",
        "Intense 16:9 chiaroscuro close-up of Prometheus's weathered face against the black mountain stone, his eyes glowing with unyielding golden fire and ancient prophetic wisdom.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm golden firelight reflects in Prometheus's resolute eyes as cold mountain mist drifts across the foreground. Slow close-up push-in at 24fps.",
    ),
    (
        "ATO_IV",
        "ATO IV · O ROCHEDO DO CÁUCASO",
        "Prometeu Acorrentado, v. 944-996",
        "A RECUSA DIANTE DE HERMES",
        "hermes_caucaso_recusa",
        "Quando Hermes desceu à montanha exigindo que revelasse o segredo em troca da liberdade, Prometeu respondeu que preferia aquela rocha a ser servo da tirania.",
        "Dramatic 16:9 chiaroscuro two-shot on the mountain cliff: Hermes hovering with winged sandals in golden light before the unyielding silhouette of Prometheus standing firm against the obsidian rock.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Storm winds swirl around Hermes and Prometheus on the rocky precipice as golden light flashes in the clouds behind them. Slow push-in at 24fps.",
    ),
    (
        "ATO_IV",
        "ATO IV · O ROCHEDO DO CÁUCASO",
        "Prometeu Acorrentado, v. 1080-1093",
        "A TEMPESTADE DO ABISMO",
        "tempestade_caucaso_raio",
        "O céu e o mar se confundiram num rugido de trovões, e a montanha inteira afundou na tempestade — mas o titã que deu a luz aos homens não dobrou os joelhos.",
        "Cataclysmic 16:9 chiaroscuro landscape: brilliant bolts of incandescent white-and-gold lightning illuminating the towering black peaks of the Caucasus amidst swirling storm clouds and golden sparks.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Golden lightning illuminates the swirling storm clouds around the monumental black mountain peak as mist rises from the chasm. Dramatic camera zoom at 24fps.",
    ),
    # ATO V · O JARRO ABERTO E O SILÊNCIO DO MUNDO (Blocos 35 a 41 | 05:46.8 - 06:58.2)
    (
        "ATO_V",
        "ATO V · A ABERTURA DO PITHOS",
        "Trabalhos e Dias, v. 94",
        "O GRANDE JARRO SELADO",
        "pandora_diante_pithos",
        "De volta ao mundo dos mortais, no canto mais escuro da casa de Epimeteu, repousava o grande pithos de barro cozido, fechado por uma pesada tampa de cerâmica.",
        "Suspenseful 16:9 chiaroscuro interior: Pandora standing alone in a shadowy stone room before the tall ancient Greek terracotta pithos jar, a single oil lamp casting long Caravaggio shadows.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The warm flame of the oil lamp flickers across Pandora's silver veil and the tall terracotta pithos jar in the dark room. Slow push-in at 24fps.",
    ),
    (
        "ATO_V",
        "ATO V · A ABERTURA DO PITHOS",
        "Erasmo de Roterdã, Adagia (1508)",
        "DO PITHOS PARA A PYXIS",
        "pithos_detalhe_tampa",
        "Foi apenas no século dezesseis que Erasmo de Roterdã, ao traduzir Hesíodo para o latim, trocou a palavra grega pithos por pyxis — transformando o jarro numa caixa.",
        "Extreme close-up 16:9 chiaroscuro shot of the heavy circular terracotta lid of the ancient Greek pithos jar, engraved with archaic labyrinthine patterns and sealed with aged bronze.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm amber light glides slowly across the archaic geometric carvings on the heavy terracotta lid of the jar. Slow macro pan at 24fps.",
    ),
    (
        "ATO_V",
        "ATO V · A ABERTURA DO PITHOS",
        "Trabalhos e Dias, v. 94-95",
        "AS MÃOS NA TAMPA",
        "pandora_ergue_tampa",
        "Movida pela mente inquieta que Hermes havia soprado em seu peito, Pandora aproximou-se em silêncio e, com as próprias mãos, ergueu a grande tampa do jarro.",
        "High-tension 16:9 chiaroscuro close-up: Pandora's graceful hands lifting the heavy terracotta lid of the pithos as a blinding crack of incandescent amber-and-gold light escapes from inside.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Intense golden-orange light and swirling dark smoke begin to pour through the opening as Pandora lifts the terracotta lid. Slow push-in at 24fps.",
    ),
    (
        "ATO_V",
        "ATO V · A ABERTURA DO PITHOS",
        "Trabalhos e Dias, v. 95-96",
        "A DISPERSÃO DOS MALES",
        "fumaca_sombras_pithos",
        "Num único sopro, espalharam-se pelo ar todas as dores humanas: a fadiga exaustiva, a discórdia, a fome e as febres que consomem a vida sem fazer barulho.",
        "Dramatic 16:9 chiaroscuro wide shot: a towering vortex of charcoal-black and ember-orange smoke erupting from the open mouth of the terracotta pithos jar, filling the vaulted chamber.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Billowing clouds of dark charcoal smoke and glowing orange embers swirl upward from the open terracotta jar toward the ceiling. Dynamic upward pan at 24fps.",
    ),
    (
        "ATO_V",
        "ATO V · A ABERTURA DO PITHOS",
        "Trabalhos e Dias, v. 101-104",
        "CHEIA ESTÁ A TERRA",
        "sombras_sobre_cidade",
        "Cheia está a terra de males, escreveu Hesíodo, e cheio está o mar: as enfermidades vagam de dia e de noite por conta própria, em silêncio, porque Zeus lhes tirou a voz.",
        "Haunting 16:9 chiaroscuro aerial view of an ancient Greek coastal city at twilight as long translucent tendrils of dark ash-grey mist drift silently over the rooftops and the dark sea.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Silent streams of dark ash-grey mist glide slowly over the torchlit rooftops of the ancient coastal city and out across the sea. Slow pan at 24fps.",
    ),
    (
        "ATO_V",
        "ATO V · A ABERTURA DO PITHOS",
        "Trabalhos e Dias, v. 96-98",
        "A TAMPA SE FECHA",
        "pandora_fecha_pithos",
        "Assustada com a nuvem escura que tomou o mundo, Pandora empurrou a pesada tampa de volta sobre os lábios de barro do vaso antes que a última coisa saísse.",
        "Urgent 16:9 chiaroscuro frame: Pandora pressing the heavy terracotta lid back down onto the rim of the pithos jar while a faint golden glow remains trapped inside the vessel.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Residual amber smoke dissipates around the sealed rim of the terracotta jar as Pandora rests her hands on the closed lid. Slow push-in at 24fps.",
    ),
    (
        "ATO_V",
        "ATO V · A ABERTURA DO PITHOS",
        "Trabalhos e Dias, v. 96",
        "PRISIONEIRA NA BORDA",
        "elpis_presa_no_jarro",
        "Sozinha lá dentro, presa sob a borda inquebrável do jarro pela vontade de Zeus, permaneceu apenas uma entidade que os gregos chamavam de Elpis.",
        "Ethereal 16:9 chiaroscuro cross-section/interior view inside the pitch-black clay jar: a solitary, trembling orb of warm incandescent golden light (Elpis) floating just beneath the sealed terracotta rim.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The single warm orb of incandescent golden light pulses gently inside the dark clay interior just beneath the sealed rim. Slow hypnotic push-in at 24fps.",
    ),
    # ATO VI · O ENIGMA DE ELPIS: SALVAÇÃO OU TORTURA? (Blocos 42 a 46 | 06:58.2 - 07:49.2)
    (
        "ATO_VI",
        "ATO VI · O ENIGMA DE ELPIS",
        "Trabalhos e Dias, v. 96-99",
        "O PARADOXO DE HESÍODO",
        "filosofos_pergaminho_elpis",
        "Aqui mora o maior enigma da literatura grega: se o jarro continha apenas pragas enviadas por Zeus para punir os homens, o que a Esperança fazia lá dentro?",
        "Contemplative 16:9 chiaroscuro frame in a candlelit stone library: an ancient Greek scroll unrolled on a wooden table beside a bronze oil lamp, illuminating archaic Greek letters in warm gold.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The warm flame of the bronze oil lamp flickers over the unrolled ancient parchment scroll in deep Caravaggio shadow. Slow camera pan at 24fps.",
    ),
    (
        "ATO_VI",
        "ATO VI · O ENIGMA DE ELPIS",
        "Prometeu Acorrentado, v. 250",
        "ESPERANÇAS CEGAS",
        "silencio_dramatico_elpis",
        "Em grego arcaico, Elpis não era certeza de vitória: era a expectativa cega do amanhã. Ésquilo conta que Prometeu plantou esperanças cegas nos mortais para que parassem de encarar a própria morte.",
        "Absolute Dramatic Silence 16:9 chiaroscuro frame (90% deep obsidian black #0A0705): a single tiny golden flame trembling alone in vast darkness, reflected in the still pupil of a human eye.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. A single tiny golden flame trembles softly in the vast obsidian darkness, casting a subtle warm reflection. Slow meditative push-in at 24fps.",
    ),
    (
        "ATO_VI",
        "ATO VI · O ENIGMA DE ELPIS",
        "Trabalhos e Dias, v. 97-99",
        "DUAS LEITURAS MILENARES",
        "balanca_fogo_esperanca",
        "Há duas leituras que dividem os filósofos há milênios: na primeira, reter Elpis no jarro guardou para o homem um último abrigo que nenhuma desgraça pode destruir.",
        "Symbolic 16:9 chiaroscuro composition: a solitary Greek traveler in a dark cloak walking forward through a fierce storm, shielding a small glowing golden lantern flame against his chest.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The cloaked traveler walks steadily through swirling dark wind while the warm golden lantern flame glows brightly in his hands. Slow tracking shot at 24fps.",
    ),
    (
        "ATO_VI",
        "ATO VI · O ENIGMA DE ELPIS",
        "Nietzsche, Humano, Demasiado Humano, §71",
        "O MAIS PROLONGADO DOS MALES",
        "homem_arando_pedra",
        "Na segunda, mais sombria, a Esperança era o mal supremo de Zeus: a força que impede o homem exausto de desistir, fazendo-o suportar todas as dores esperando pelo amanhã.",
        "Stark 16:9 chiaroscuro wide shot at dawn: a lone Greek farmer guiding a wooden plow across rocky dark soil under heavy storm clouds while gazing toward a thin golden line on the distant horizon.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Wind moves the dark clouds as the lone farmer pushes the wooden plow toward the thin golden glow on the horizon. Slow cinematic pan at 24fps.",
    ),
    (
        "ATO_VI",
        "ATO VI · O ENIGMA DE ELPIS",
        "Teogonia, v. 526-534",
        "A ALIANÇA ENTRE O FOGO E A ESPERANÇA",
        "fogo_e_jarro_dualidade",
        "Mas juntas, a brasa de Prometeu e a expectativa de Pandora definiram a condição humana: somos seres que sofrem no tempo, mas que usam o fogo da mente para transformar o mundo.",
        "Balanced 16:9 chiaroscuro split composition: on the left, the glowing hollow fennel stalk radiating golden fire; on the right, the sealed terracotta pithos jar glowing softly from within against deep obsidian shadow.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm golden embers rise from the fennel stalk on the left while soft amber light pulses around the terracotta jar on the right. Slow push-in at 24fps.",
    ),
    # EPÍLOGO · A BRASA QUE NUNCA SE APAGA (Blocos 47 a 50 | 07:49.2 - 08:30.0)
    (
        "EPILOGO",
        "EPÍLOGO · A BRASA IMORTAL",
        "Teogonia, v. 526-532",
        "A LIBERTAÇÃO POR HÉRACLES",
        "prometeu_livre_luz",
        "Eras depois, Hesíodo conta que Héracles abatou a águia do Cáucaso com o consentimento de Zeus, libertando finalmente o titã da montanha de pedra.",
        "Majestic 16:9 chiaroscuro dawn frame atop Mount Caucasus: Prometheus standing free on the sunlit mountain crest as broken bronze rings lie on the rock and golden sunrise floods the sky.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Brilliant golden sunrise rays expand across the mountain peaks behind Prometheus as warm wind stirs his cloak. Slow uplifting push-in at 24fps.",
    ),
    (
        "EPILOGO",
        "EPÍLOGO · A BRASA IMORTAL",
        "Trabalhos e Dias, v. 47-52",
        "A HERANÇA DOS MORTAIS",
        "oficina_humana_noite",
        "O preço da nossa consciência foi alto: perdemos o paraíso inconsciente de Mecone, mas ganhamos a centelha que nos impede de viver de joelhos na escuridão.",
        "Poetic 16:9 chiaroscuro frame looking through an ancient stone window at night: inside, a Greek scholar writes on a scroll beside a warm bronze oil lamp while stars shine over the dark sea outside.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm golden lamp light illuminates the scholar and the scroll inside the stone window while night waves shimmer outside. Slow push-in at 24fps.",
    ),
    (
        "EPILOGO",
        "EPÍLOGO · A BRASA IMORTAL",
        "Prometeu Acorrentado, v. 109-111",
        "A CENTELHA PERMANECE",
        "contador_olhar_fogo",
        "Toda vez que acendemos uma luz contra o escuro ou insistimos em construir o amanhã em meio às cinzas, repetimos o gesto de Prometeu diante do Olimpo.",
        "Close-up 16:9 chiaroscuro portrait of O Contador in the dark stone chamber, lifting his head as the golden reflection of the bronze brazier flames dances in his weathered face.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Golden flames in the bronze brazier cast warm dancing Caravaggio reflections across the old storyteller's face and silver beard. Slow push-in at 24fps.",
    ),
    (
        "EPILOGO",
        "EPÍLOGO · A BRASA IMORTAL",
        "Hesíodo · Teogonia & Trabalhos",
        "LUME · FIM DO EPISÓDIO",
        "ultima_brasa_ep02",
        "Porque os deuses trancaram os males no mundo e a esperança no barro — mas o fogo continua nas nossas mãos. E o fogo ainda conta as mesmas histórias.",
        "Final 16:9 chiaroscuro frame in the pitch-black stone chamber: a single glowing red-orange ember in the bronze tripod brazier pulses warmly, sending a thin thread of golden smoke upward into total darkness.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The last glowing red-orange ember pulses softly in the bronze brazier as a delicate thread of golden smoke rises into the dark. Slow fade-out push-in at 24fps.",
    ),
]


def gerar_json_decupagem_ep02() -> Path:
    assert len(BLOCOS_50_SPEC) == 50, f"Esperados 50 blocos, encontrados {len(BLOCOS_50_SPEC)}"
    out_dir = Path(r"d:\LUME\storage_local\roteiro")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "roteiro_ep02_prometeu_pandora_50_planos_1para1.json"

    blocos: List[Dict[str, Any]] = []
    planos: List[Dict[str, Any]] = []

    for idx, (ato_id, ato_titulo, canto_verso, contador_hud, cena_tipo, texto, p_img, p_vid) in enumerate(BLOCOS_50_SPEC, start=1):
        plano_id = f"p{idx:02d}"
        t0 = round((idx - 1) * 10.2, 1)
        t1 = round(idx * 10.2, 1)
        dur = round(t1 - t0, 2)

        bloco_obj: Dict[str, Any] = {
            "plano": idx,
            "id": plano_id,
            "bloco_id": f"bloco_{idx:02d}",
            "ato_id": ato_id,
            "ato_titulo": ato_titulo,
            "janela_s": [t0, t1],
            "duracao_s": dur,
            "canto_verso": canto_verso,
            "contador_perdas": contador_hud,
            "cena_tipo": cena_tipo,
            "texto_narracao": texto,
            "prompt_start_frame": f"{STYLE_PREFIX}{p_img}",
            "prompt_video": p_vid,
        }
        if idx == 43:
            bloco_obj["silencio_dramatico_s"] = [436.9, 438.4]

        blocos.append(bloco_obj)
        planos.append(dict(bloco_obj))

    validar_paridade_1_para_1_blocos_planos(blocos, planos, episodio_id=EPISODIO_ID)

    payload = {
        "episodio_id": EPISODIO_ID,
        "titulo": TITULO_EPISODIO,
        "thumbnail_words": THUMBNAIL_WORDS,
        "duracao_total_s": 510.0,
        "duracao_formatada": "08:30",
        "total_blocos": 50,
        "total_planos": 50,
        "paridade_1_para_1": True,
        "silencio_dramatico_s": [436.9, 438.4],
        "blocos": blocos,
        "planos": planos,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Decupagem 1:1 gerada: {out_path} ({len(planos)} planos)")
    return out_path


async def _sintetizar_blocos_tts(blocos: List[Dict[str, Any]], tts_dir: Path) -> List[Path]:
    import edge_tts

    tts_dir.mkdir(parents=True, exist_ok=True)
    wav_paths: List[Path] = []

    for b in blocos:
        idx = int(b["plano"])
        pid = b["id"]
        texto = b["texto_narracao"]
        raw_mp3 = tts_dir / f"tts_{pid}.mp3"
        blk_wav = tts_dir / f"bloco_{idx:02d}_{pid}_10s2.wav"

        if not blk_wav.is_file() or blk_wav.stat().st_size < 50_000:
            comm = edge_tts.Communicate(texto, voice="pt-BR-AntonioNeural", rate="-5%", pitch="-10Hz")
            await comm.save(str(raw_mp3))

            # Conforma exatamente para 10.20s (48kHz stereo) com pad de silêncio e micro-fade
            # No bloco 43, garante silêncio dramático absoluto nos últimos 1.5s (436.9s a 438.4s)
            if idx == 43:
                af_chain = (
                    "adelay=250|250,"
                    "apad=whole_dur=10.20,"
                    "volume=enable='between(t,8.3,10.20)':volume=0,"
                    "afade=t=in:st=0:d=0.08"
                )
            else:
                af_chain = (
                    "adelay=300|300,"
                    "apad=whole_dur=10.20,"
                    "afade=t=in:st=0:d=0.08,"
                    "afade=t=out:st=9.95:d=0.25"
                )

            subprocess.run(
                [
                    "ffmpeg",
                    "-y",
                    "-i",
                    str(raw_mp3),
                    "-af",
                    af_chain,
                    "-ar",
                    "48000",
                    "-ac",
                    "2",
                    "-t",
                    "10.20",
                    str(blk_wav),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        wav_paths.append(blk_wav)
    return wav_paths


def gerar_master_audio_ep02(blocos: List[Dict[str, Any]]) -> Path:
    dirs = criar_diretorios_episodio_isolado(EPISODIO_ID)
    audio_dir = dirs["audio"]
    tts_dir = audio_dir / "blocos_tts"
    master_wav = audio_dir / "master_audio_8min.wav"

    if master_wav.is_file() and master_wav.stat().st_size > 40_000_000:
        print(f"[OK] Master de áudio já existe: {master_wav}")
        return master_wav

    print("[AUDIO] Sintetizando 50 blocos de narração neural barítono ('O Contador')...")
    wav_paths = asyncio.run(_sintetizar_blocos_tts(blocos, tts_dir))

    concat_txt = tts_dir / "concat_tts_50.txt"
    with open(concat_txt, "w", encoding="utf-8") as f:
        for wp in wav_paths:
            f.write(f"file '{wp.resolve().as_posix()}'\n")

    voz_510s_wav = audio_dir / "voz_narrador_510s.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_txt),
            "-c",
            "copy",
            str(voz_510s_wav),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Compõe cama harmônica modal grega (Dórico/Frígio em D2/A2/F3) + crepitar de braseiro diegético
    # respeitando o Silêncio Dramático Absoluto entre 436.9s e 438.4s e normalizando a -14.0 LUFS
    bgm_sfx_wav = audio_dir / "bgm_sfx_bed_510s.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            "aevalsrc='0.035*sin(2*PI*73.42*t)+0.025*sin(2*PI*110.0*t)+0.015*sin(2*PI*146.83*t)*(0.6+0.4*sin(2*PI*0.12*t))':s=48000:c=stereo:d=510.0",
            "-f",
            "lavfi",
            "-i",
            "anoisesrc=d=510.0:c=brown:r=48000:a=0.018",
            "-filter_complex",
            "[1:a]bandpass=f=420:width_type=h:w=300,tremolo=f=4.5:d=0.65[fire];"
            "[0:a][fire]amix=inputs=2:duration=longest,"
            "volume=enable='between(t,436.9,438.4)':volume=0,"
            "afade=t=in:st=0:d=2.5,afade=t=out:st=506.5:d=3.5[bed]",
            "-map",
            "[bed]",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-t",
            "510.0",
            str(bgm_sfx_wav),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print("[AUDIO] Mixando voz + trilha modal + braseiro e masterizando em -14.0 LUFS...")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(voz_510s_wav),
            "-i",
            str(bgm_sfx_wav),
            "-filter_complex",
            "[0:a]volume=1.35[v];[1:a]volume=0.80[b];"
            "[v][b]amix=inputs=2:duration=first:dropout_transition=0,"
            "volume=enable='between(t,436.9,438.4)':volume=0,"
            "loudnorm=I=-14.0:TP=-1.5:LRA=11.0[out]",
            "-map",
            "[out]",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-t",
            "510.0",
            str(master_wav),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"[OK] Master de Áudio 510.0s (-14.0 LUFS) concluído: {master_wav} ({master_wav.stat().st_size / (1024*1024):.2f} MB)")
    return master_wav


if __name__ == "__main__":
    json_path = gerar_json_decupagem_ep02()
    dados = json.loads(json_path.read_text(encoding="utf-8"))
    gerar_master_audio_ep02(dados["blocos"])
