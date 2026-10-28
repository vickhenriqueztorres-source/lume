r"""Produção Completa 1:1 de 8m24s (504.0s) do Episódio 02 LUME (MCP: LUME-THM-20261022-5F40D7 + LUME-TIP-20261022-C26221).

Tema MCP: "O Canto das Sereias e a Cera nos Ouvidos" (A Odisseia, Canto XII, v. 39-200)
Dica MCP: "Silêncio de 1.5s antes da revelação" (Cortar o crepitar do fogo por 1.5s antes do clímax em 334.50s-336.00s)
Duração Total: 504.0s (08m24s — mais de 8 minutos)
Política: Zero-Reuso Estrito + Paridade 1:1 (36 Blocos de 14.0s = 36 Planos = 36 Start Frames IA Inéditos = 36 Vídeos Firefly Inéditos).
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from contratos.integridade_assets import (
    criar_diretorios_episodio_isolado,
    validar_paridade_1_para_1_blocos_planos,
)
from grafo.ferramentas.audio import sintetizar_voz_gemini_com_fallback

EPISODIO_ID = "ep02_sereias_firefly_1para1"
DURACAO_BLOCO_S = 14.0
NUM_BLOCOS = 36
DURACAO_TOTAL_S = DURACAO_BLOCO_S * NUM_BLOCOS  # 504.0s (08m24s)
SR = 48000
TOTAL_SAMPLES = int(SR * DURACAO_TOTAL_S)

SILENCIO_INICIO_S = 334.50  # Fim do Bloco 24 (322.0s - 336.0s)
SILENCIO_FIM_S = 336.00     # Exatos 1.50s de corte absoluto antes da Revelação no Bloco 25 (336.0s)

REAL_BGM_DIR = Path(r"D:\LUME\storage_local\trilha\real_2d")
REAL_SFX_DIR = Path(r"D:\LUME\storage_local\sfx\real_2d")


RAW_36_SPECS: List[Dict[str, Any]] = [
    # PRÓLOGO RITUAL (p01 a p03: 00:00 a 00:42)
    {
        "plano": 1,
        "id": "p01",
        "ato": "Abertura Ritual",
        "ato_titulo": "PRÓLOGO · O FOGO DO CONTADOR",
        "canto_verso": "Odisseia, Canto XII, v. 39-46",
        "contador_perdas": "NAVIO DE ÍTACA",
        "gatilho_psicologico": "Prediction Error (Erro de Previsão) + Infinite Loop Completion",
        "texto_narracao": (
            "...todo marinheiro que ouviu essa voz morreu sorrindo nas pedras. Exceto um. "
            "Aproxime-se do fogo, viajante. Hoje o braseiro revela o segredo mais mortal do Canto Doze da Odisseia."
        ),
        "cues_legenda": [
            ("...todo marinheiro que ouviu essa voz", "morreu sorrindo nas pedras. Exceto um."),
            ("Aproxime-se do fogo. Hoje o braseiro", "revela o Canto Doze da Odisseia."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Warm orange brazier flames flicker and glowing amber embers drift upward into the night air "
            "as the hooded storyteller gently tilts the Greek pottery shard. Slow cinematic push-in at 24fps."
        ),
    },
    {
        "plano": 2,
        "id": "p02",
        "ato": "Ato I",
        "ato_titulo": "ATO I · O AVISO DE CIRCE",
        "canto_verso": "Odisseia, Canto XII, v. 37-43",
        "contador_perdas": "ILHA DE EEA",
        "gatilho_psicologico": "Aversão à Perda + Autoridade Profética (Schwartz Nível 4)",
        "texto_narracao": (
            "Na última noite na ilha de Eea, enquanto a tripulação dormia na praia, "
            "a feiticeira Circe tomou Odisseu pela mão e sussurrou um aviso gelado sobre o caminho de volta a Ítaca."
        ),
        "cues_legenda": [
            ("Na última noite na ilha de Eea,", "enquanto a tripulação dormia,"),
            ("a feiticeira Circe deu a Odisseu", "um aviso gelado sobre o retorno."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Golden torchlight flickers across Circe and Odysseus while warm amber dust motes float "
            "through the shadowy hall. Slow cinematic camera push-in at 24fps."
        ),
    },
    {
        "plano": 3,
        "id": "p03",
        "ato": "Ato I",
        "ato_titulo": "ATO I · ÁGUAS SEM RETORNO",
        "canto_verso": "Odisseia, Canto XII, v. 41-43",
        "contador_perdas": "1 NAVIO RESTANTE",
        "gatilho_psicologico": "Irreversibilidade + Custo do Erro",
        "texto_narracao": (
            "Primeiro você chegará às Sereias, disse ela, que encantam todos os homens que delas se aproximam. "
            "Quem por imprudência escuta aquela voz jamais vê a esposa e os filhos pequenos ao voltar para casa."
        ),
        "cues_legenda": [
            ("Primeiro você chegará às Sereias,", "que encantam todos os mortais."),
            ("Quem escuta aquela voz jamais", "volta para abraçar esposa e filhos."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "The Greek wooden ship glides smoothly over the glassy black water while golden amber mist "
            "drifts across the sea and the prow brazier glows warmly. Slow pan at 24fps."
        ),
    },
    # ATO I — A ANATOMIA DO MITO E O PACTO DE CIRCE (p04 a p12: 00:42 a 02:48)
    {
        "plano": 4,
        "id": "p04",
        "ato": "Ato I",
        "ato_titulo": "ATO I · AS AVES DE ROSTO HUMANO",
        "canto_verso": "Odisseia, Canto XII, v. 44-46",
        "contador_perdas": "VASO GREGO §6.2",
        "gatilho_psicologico": "Quebra de Expectativa Visual (Fidelidade Arqueológica Homérica)",
        "texto_narracao": (
            "Esqueça as mulheres com cauda de peixe inventadas séculos depois. Na Grécia de Homero "
            "e nos vasos antigos, as Sereias têm corpo emplumado de ave de rapina e rosto humano sereno."
        ),
        "cues_legenda": [
            ("Esqueça as caudas de peixe modernas.", "Na Grécia de Homero e nos vasos,"),
            ("as Sereias têm corpo de ave escura", "e rosto humano banhado em âmbar."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Feathers ruffle gently in the sea breeze as the winged Greek Sirens pluck golden lyres "
            "under warm amber backlighting. Slow cinematic push-in at 24fps."
        ),
    },
    {
        "plano": 5,
        "id": "p05",
        "ato": "Ato I",
        "ato_titulo": "ATO I · O PRIMEIRO MECANISMO",
        "canto_verso": "Odisseia, Canto XII, v. 47-49",
        "contador_perdas": "1ª ARMA: CERA",
        "gatilho_psicologico": "Mecanismo Único Tangível (Engenharia de Sobrevivência)",
        "texto_narracao": (
            "Nenhuma espada de bronze pode ferir uma melodia. Por isso Circe revelou uma defesa física: "
            "amassar cera doce de abelha como ouro derretido e vedar os ouvidos de cada remador."
        ),
        "cues_legenda": [
            ("Nenhuma espada de bronze pode", "ferir uma melodia no mar."),
            ("A primeira defesa era amassar cera", "de abelha e vedar os remadores."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Warm orange firelight dances across Odysseus's hands as the golden beeswax glistens "
            "and softens in the lantern glow. Slow cinematic push-in at 24fps."
        ),
    },
    {
        "plano": 6,
        "id": "p06",
        "ato": "Ato I",
        "ato_titulo": "ATO I · A BARREIRA DO SILÊNCIO",
        "canto_verso": "Odisseia, Canto XII, v. 48-50",
        "contador_perdas": "TRIPULAÇÃO PROTEGIDA",
        "gatilho_psicologico": "Isolamento Sensorial + Contraste de Destino",
        "texto_narracao": (
            "Com os ouvidos lacrados pela cera espessa, os marinheiros remariam imunes ao feitiço. "
            "Mas Circe conhecia o coração inquieto de Odisseu: ela sabia que ele desejaria escutar o proibido."
        ),
        "cues_legenda": [
            ("Com os ouvidos lacrados pela cera,", "os marinheiros remariam imunes."),
            ("Mas Circe sabia que Odisseu", "desejaria escutar o proibido."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Odysseus carefully seals the oarsman's ear with golden wax while deck torches flicker "
            "and amber light reflects on the dark sea. Slow camera motion at 24fps."
        ),
    },
    {
        "plano": 7,
        "id": "p07",
        "ato": "Ato I",
        "ato_titulo": "ATO I · O CONTRATO DO MASTRO",
        "canto_verso": "Odisseia, Canto XII, v. 50-54",
        "contador_perdas": "2ª ARMA: O MASTRO",
        "gatilho_psicologico": "Pre-Commitment Pact (O Contrato de Ulisses)",
        "texto_narracao": (
            "Se você quiser ouvir, ordenou a deusa, peça que o prendam de pé na base do mastro central. "
            "Assim você ouvirá o canto das Sereias sentindo deleite, sem poder lançar o navio às pedras."
        ),
        "cues_legenda": [
            ("Se quiser ouvir, disse a deusa,", "prenda-se de pé ao mastro central."),
            ("Assim ouvirá o canto com deleite", "sem lançar o navio às pedras."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Odysseus stands resolute at the wooden mast as orange torch flames billow in the night breeze "
            "and golden mist swirls around the ship. Slow heroic push-in at 24fps."
        ),
    },
    {
        "plano": 8,
        "id": "p08",
        "ato": "Ato I",
        "ato_titulo": "ATO I · O CHAMADO ACÚSTICO",
        "canto_verso": "Odisseia, Canto XII, v. 39-45",
        "contador_perdas": "ARMADILHA SONORA",
        "gatilho_psicologico": "Curiosidade Epistêmica (Por que o canto mata?)",
        "texto_narracao": (
            "Mas por que nenhum homem jamais resistiu àquela canção? Os marinheiros não pulavam no mar "
            "por loucura cega: eles simplesmente paravam de remar até morrerem de inanição ouvindo a voz."
        ),
        "cues_legenda": [
            ("Por que nenhum homem jamais", "resistiu àquela canção antiga?"),
            ("Eles paravam de remar hipnotizados", "até morrerem ouvindo a voz."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Shimmering waves of golden amber light particles float gracefully across the dark water "
            "from the coastal cliff toward the Greek ship. Smooth cinematic motion at 24fps."
        ),
    },
    {
        "plano": 9,
        "id": "p09",
        "ato": "Ato I",
        "ato_titulo": "ATO I · A MENTE DE ODISSEU",
        "canto_verso": "Odisseia, Canto XII, v. 50-54",
        "contador_perdas": "RISCO CALCULADO",
        "gatilho_psicologico": "Conflito Interno (Razão Presente vs. Desejo Futuro)",
        "texto_narracao": (
            "Odisseu compreendeu que no instante em que a voz tocasse seus tímpanos, sua mente seria sequestrada. "
            "O Odisseu do presente precisava derrotar o Odisseu do futuro antes que a ilha aparecesse."
        ),
        "cues_legenda": [
            ("Assim que a voz tocasse seus ouvidos,", "sua razão seria sequestrada."),
            ("O Odisseu do presente precisava", "conter o Odisseu do futuro."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Golden amber reflections shimmer in Odysseus's wide spellbound eyes while glowing dust motes "
            "drift slowly in the dark air. Slow intense camera push-in at 24fps."
        ),
    },
    {
        "plano": 10,
        "id": "p10",
        "ato": "Ato I",
        "ato_titulo": "ATO I · A REGRA DE FERRO",
        "canto_verso": "Odisseia, Canto XII, v. 53-54",
        "contador_perdas": "ORDEM IRREVOGÁVEL",
        "gatilho_psicologico": "Inversão de Comando (O Rei Submisso à Própria Lei)",
        "texto_narracao": (
            "A regra era implacável: durante a travessia, o rei perdia o comando. "
            "Quanto mais o capitão suplicasse ou ordenasse para ser solto, mais forte a tripulação deveria remar."
        ),
        "cues_legenda": [
            ("A regra era implacável no convés:", "durante o canto, o rei não manda."),
            ("Quanto mais ele implorasse soltura,", "mais forte deveriam remar."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "The Greek oarsmen row rhythmically in unison as golden torchlight flares on the wooden deck "
            "and ocean spray glints in amber light. Dynamic camera motion at 24fps."
        ),
    },
    {
        "plano": 11,
        "id": "p11",
        "ato": "Ato I",
        "ato_titulo": "ATO I · RUMO AO DESCONHECIDO",
        "canto_verso": "Odisseia, Canto XII, v. 142-147",
        "contador_perdas": "AURORA DOURADA",
        "gatilho_psicologico": "Antecipação Dramática + Cruzamento do Limiar",
        "texto_narracao": (
            "Quando a Aurora de dedos róseos iluminou o horizonte, Circe retornou ao interior da ilha "
            "e Odisseu subiu na nau negra, convocando os companheiros a ocuparem os bancos de remo."
        ),
        "cues_legenda": [
            ("Quando a Aurora tocou o horizonte,", "Circe recolheu-se à sua morada."),
            ("Odisseu subiu na nau negra", "e convocou os homens aos remos."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "The Greek ship sails forward across gentle night waves while warm amber lantern light "
            "reflects on the water and stars glimmer above. Smooth camera pan at 24fps."
        ),
    },
    {
        "plano": 12,
        "id": "p12",
        "ato": "Ato I",
        "ato_titulo": "ATO I · A BRASA DA MEMÓRIA",
        "canto_verso": "Odisseia, Canto XII, v. 148-152",
        "contador_perdas": "CONTADOR NO FOGO",
        "gatilho_psicologico": "Ancoragem no Narrador (O Contador) + Micro-Payoff do Ato I",
        "texto_narracao": (
            "Observe as fagulhas subindo deste braseiro, viajante. A preparação estava traçada na mente de Odisseu, "
            "mas o mar estava prestes a mostrar que o perigo real supera qualquer profecia."
        ),
        "cues_legenda": [
            ("Observe as fagulhas no braseiro.", "O plano estava traçado na mente,"),
            ("mas o mar mostraria que o perigo", "supera qualquer profecia."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Glowing orange and amber embers swirl upward from the bronze brazier as the hooded storyteller "
            "sits in solemn silhouette. Slow atmospheric push-in at 24fps."
        ),
    },
    # ATO II — A CALMARIA SOBRENATURAL E A CERA NOS OUVIDOS (p13 a p21: 02:48 a 04:54)
    {
        "plano": 13,
        "id": "p13",
        "ato": "Ato II",
        "ato_titulo": "ATO II · A PARTIDA DE EEA",
        "canto_verso": "Odisseia, Canto XII, v. 148-151",
        "contador_perdas": "COSTA DE EEA",
        "gatilho_psicologico": "Imersão Sensorial Homérica",
        "texto_narracao": (
            "Em fila nos bancos, os marinheiros feriram o mar cinzento com os remos de abeto. "
            "De trás da proa azul-escura, Circe enviou um vento favorável, bom companheiro que enchia as velas."
        ),
        "cues_legenda": [
            ("Em fila nos bancos, os marinheiros", "feriram o mar com os remos."),
            ("Circe enviou um vento favorável", "que enchia as velas da nau."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Golden dawn mist rises over the dark sea as the Greek wooden ship departs the rocky shore "
            "and the bronze brazier on the headland flickers warmly. Slow wide pan at 24fps."
        ),
    },
    {
        "plano": 14,
        "id": "p14",
        "ato": "Ato II",
        "ato_titulo": "ATO II · VENTO NAS VELAS",
        "canto_verso": "Odisseia, Canto XII, v. 151-153",
        "contador_perdas": "VELAS CHEIAS",
        "gatilho_psicologico": "Contraste Dinâmico (Movimento Rápido antes da Paralisia)",
        "texto_narracao": (
            "Arrumadas todas as cordas pelo navio, eles se sentaram enquanto o vento e o piloto "
            "conduziam a embarcação. Mas no peito de Odisseu, o coração pesava com o segredo que carregava sozinho."
        ),
        "cues_legenda": [
            ("O vento e o piloto conduziam", "a embarcação sobre as ondas."),
            ("Mas no peito de Odisseu, o coração", "pesava com o segredo de Circe."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "The woven linen sail billows with golden amber wind as foaming dark waves part around "
            "the bronze prow of the Greek warship. Dynamic tracking motion at 24fps."
        ),
    },
    {
        "plano": 15,
        "id": "p15",
        "ato": "Ato II",
        "ato_titulo": "ATO II · O VENTO MORRE",
        "canto_verso": "Odisseia, Canto XII, v. 166-169",
        "contador_perdas": "VENTO: 0 NÓS",
        "gatilho_psicologico": "Suspensão Atmosférica Súbita (Presságio Sobrenatural)",
        "texto_narracao": (
            "De repente, ao se aproximarem da ilha das Sereias, o vento cessou por completo. "
            "Fez-se uma calmaria sem sopro de ar: uma divindade invisível havia adormecido todas as ondas."
        ),
        "cues_legenda": [
            ("De repente, perto da ilha,", "o vento cessou por completo."),
            ("Uma divindade invisível havia", "adormecido todas as ondas."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "The slack linen sail sways gently above the Greek sailors as eerie amber mist drifts "
            "across the mirror-still black ocean water. Slow tense push-in at 24fps."
        ),
    },
    {
        "plano": 16,
        "id": "p16",
        "ato": "Ato II",
        "ato_titulo": "ATO II · VELAS RECOLHIDAS",
        "canto_verso": "Odisseia, Canto XII, v. 170-172",
        "contador_perdas": "APENAS REMOS",
        "gatilho_psicologico": "Urgência Operacional + Ponto Sem Retorno",
        "texto_narracao": (
            "Sem vento para empurrar o casco, a sobrevivência agora dependia apenas do músculo humano. "
            "Os companheiros se levantaram, enrolaram a grande vela, guardaram-na no fundo do navio e voltaram aos remos."
        ),
        "cues_legenda": [
            ("Sem vento para empurrar o casco,", "tudo dependia da força humana."),
            ("Eles enrolaram a grande vela", "e assumiram os remos de abeto."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Greek sailors gather the heavy linen sail on the wooden deck while orange brazier light "
            "casts warm amber highlights across their shoulders. Smooth camera motion at 24fps."
        ),
    },
    {
        "plano": 17,
        "id": "p17",
        "ato": "Ato II",
        "ato_titulo": "ATO II · A CONFISSÃO NO CONVÉS",
        "canto_verso": "Odisseia, Canto XII, v. 154-164",
        "contador_perdas": "PACTO COLETIVO",
        "gatilho_psicologico": "Liderança Transparente (Compromisso Público)",
        "texto_narracao": (
            "Odisseu reuniu os homens e falou: Amigos, não convém que apenas um ou dois conheçam "
            "as profecias de Circe. Eu lhes direi tudo, para que saibamos como escapar da morte e do destino!"
        ),
        "cues_legenda": [
            ("Amigos, disse Odisseu no convés,", "todos devem saber a profecia."),
            ("Direi tudo para que saibamos", "escapar da morte e do destino!"),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Odysseus gestures earnestly before his gathered crew on the torchlit wooden deck "
            "as glowing orange embers rise from the ship brazier. Slow push-in at 24fps."
        ),
    },
    {
        "plano": 18,
        "id": "p18",
        "ato": "Ato II",
        "ato_titulo": "ATO II · A RODA DE CERA E HÉLIOS",
        "canto_verso": "Odisseia, Canto XII, v. 173-176",
        "contador_perdas": "CERA AQUECIDA",
        "gatilho_psicologico": "Detalhe Sensorial Homérico (A Força e o Sol)",
        "texto_narracao": (
            "Então Odisseu tomou uma grande roda de cera de abelha, cortou-a em pedaços pequenos "
            "e os espremeu com suas mãos vigorosas. Logo a cera aqueceu, vencida pela força e pelo brilho de Hélios."
        ),
        "cues_legenda": [
            ("Odisseu cortou uma grande roda", "de cera dourada de abelha."),
            ("Logo a cera amoleceu sob a força", "das mãos e o calor de Hélios."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Golden amber light shimmers across the translucent honeycomb beeswax wheel resting on "
            "the bronze tray beside the deck lantern. Slow macro push-in at 24fps."
        ),
    },
    {
        "plano": 19,
        "id": "p19",
        "ato": "Ato II",
        "ato_titulo": "ATO II · LACRANDO OS OUVIDOS",
        "canto_verso": "Odisseia, Canto XII, v. 177",
        "contador_perdas": "EURÍLOCO SELADO",
        "gatilho_psicologico": "Ritual de Blindagem (Silêncio Protetor)",
        "texto_narracao": (
            "Seguindo em ordem pelo convés, Odisseu tapou os ouvidos de todos os companheiros. "
            "De Euríloco ao mais jovem remador, o mundo ao redor deles mergulhou em um silêncio absoluto e seguro."
        ),
        "cues_legenda": [
            ("Seguindo em ordem pelo convés,", "ele tapou os ouvidos de todos."),
            ("O mundo para a tripulação mergulhou", "em um silêncio absoluto e seguro."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Warm golden beeswax glows softly as Odysseus seals the bearded lieutenant's ear "
            "under flickering orange torchlight on the wooden deck. Slow push-in at 24fps."
        ),
    },
    {
        "plano": 20,
        "id": "p20",
        "ato": "Ato II",
        "ato_titulo": "ATO II · OS REMADORES SURDOS",
        "canto_verso": "Odisseia, Canto XII, v. 177-180",
        "contador_perdas": "CADÊNCIA CEGA",
        "gatilho_psicologico": "Tensão Mecânica (O Navio que Não Pode Parar)",
        "texto_narracao": (
            "Agora nenhum marinheiro ouviria trovão, grito ou melodia. Seus olhos estavam cravados na madeira "
            "dos remos, programados para uma única missão: atravessar a zona da morte sem olhar para o lado."
        ),
        "cues_legenda": [
            ("Nenhum marinheiro ouviria agora", "trovão, grito ou melodia."),
            ("Estavam prontos para atravessar", "a zona da morte sem parar."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Two rows of muscular Greek oarsmen lean forward in silent cadence along the torchlit deck "
            "as amber reflections dance on the wooden oars. Slow center-aisle push-in at 24fps."
        ),
    },
    {
        "plano": 21,
        "id": "p21",
        "ato": "Ato II",
        "ato_titulo": "ATO II · PRESO AO MASTRO CENTRAL",
        "canto_verso": "Odisseia, Canto XII, v. 178-180",
        "contador_perdas": "AMARRE-ME AO MASTRO",
        "gatilho_psicologico": "Thumbnail Payoff ('AMARRE-ME AO MASTRO') + Vulnerabilidade Voluntária",
        "texto_narracao": (
            "Por fim, Perimedes e Euríloco prenderam Odisseu no navio, de pé na base do mastro, "
            "pelas mãos e pelos pés. O único homem com os ouvidos abertos no Mediterrâneo estava pronto."
        ),
        "cues_legenda": [
            ("Perimedes e Euríloco prenderam", "Odisseu de pé junto ao mastro."),
            ("O único homem de ouvidos abertos", "no mar estava pronto para ouvir."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Odysseus stands tall against the central wooden mast while his two companions secure "
            "golden woven linen sashes around his waist under warm torchlight. Slow push-in at 24fps."
        ),
    },
    # ATO III — O CANTO PROIBIDO, O SILÊNCIO DE 1.5s E A REVELAÇÃO (p22 a p28: 04:54 a 06:32)
    {
        "plano": 22,
        "id": "p22",
        "ato": "Ato III",
        "ato_titulo": "ATO III · O PRADO E OS ROCHEDOS",
        "canto_verso": "Odisseia, Canto XII, v. 45-46, 181",
        "contador_perdas": "DISTÂNCIA DE UM GRITO",
        "gatilho_psicologico": "Contraste Macabro (Beleza Dourada vs. Ruína)",
        "texto_narracao": (
            "Quando estavam à distância em que se ouve um homem gritar, correndo velozmente sobre a água negra, "
            "surgiu o prado florido da ilha. A rápida embarcação não passou despercebida às Sereias."
        ),
        "cues_legenda": [
            ("À distância de um grito humano,", "surgiu o prado florido da ilha."),
            ("A rápida embarcação grega não", "passou despercebida às Sereias."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Golden amber mist and glowing pollen drift over the coastal meadow and dark slate cliffs "
            "as gentle black waves lap against the rocks. Slow atmospheric pan at 24fps."
        ),
    },
    {
        "plano": 23,
        "id": "p23",
        "ato": "Ato III",
        "ato_titulo": "ATO III · A VOZ HARMONIOSA",
        "canto_verso": "Odisseia, Canto XII, v. 182-183",
        "contador_perdas": "ONDA SONORA ATIVA",
        "gatilho_psicologico": "Hipnose Acústica + Escalada Límbica",
        "texto_narracao": (
            "Pousadas na rocha escura, as criaturas aladas ergueram o rosto humano e entoaram seu canto harmonioso. "
            "O ar noturno vibrou como cordas de ouro, atravessando o peito de Odisseu."
        ),
        "cues_legenda": [
            ("Pousadas na rocha, as criaturas", "aladas entoaram o canto doce."),
            ("O ar noturno vibrou como ouro,", "atravessando o peito de Odisseu."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Rings of shimmering golden-amber light ripple outward through the night air as the winged "
            "Greek Sirens sing in profile on the cliff. Slow hypnotic push-in at 24fps."
        ),
    },
    {
        "plano": 24,
        "id": "p24",
        "ato": "Ato III",
        "ato_titulo": "ATO III · ANTES DA REVELAÇÃO",
        "canto_verso": "Odisseia, Canto XII, v. 184",
        "contador_perdas": "SILÊNCIO 1.5s",
        "gatilho_psicologico": "Open Loop Máximo + Silêncio Dramático de 1.5s (LUME-TIP-20261022-C26221)",
        "silencio_dramatico_s": [334.50, 336.00],
        "texto_narracao": (
            "Elas não cantaram sobre amor ou riquezas. Escute com atenção, viajante: "
            "sabe quais foram as palavras exatas que as Sereias cantaram para destruir Odisseu?"
        ),
        "cues_legenda": [
            ("Elas não cantaram sobre amor", "ou ouro comum aos marinheiros."),
            ("Sabe quais foram as palavras exatas", "que cantaram para Odisseu?"),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "A thin wisp of golden amber smoke and a solitary orange spark rise slowly from the bronze "
            "brazier into pitch-black shadow. Slow dramatic push-in at 24fps."
        ),
    },
    {
        "plano": 25,
        "id": "p25",
        "ato": "Ato III",
        "ato_titulo": "ATO III · A GLÓRIA DE TROIA",
        "canto_verso": "Odisseia, Canto XII, v. 184-188",
        "contador_perdas": "CLÍMAX · ONISCIÊNCIA",
        "gatilho_psicologico": "Catarse de Revelação (O Canto Literal de Homero)",
        "texto_narracao": (
            "Vem cá, famoso Odisseu, grande glória dos Aqueus! Para o navio para escutares nossa voz! "
            "Aquele que aqui passa parte encantado e sabendo muito mais do que sabia antes!"
        ),
        "cues_legenda": [
            ("Vem cá, famoso Odisseu, grande", "glória dos Aqueus! Para o navio!"),
            ("Quem nos ouve parte encantado", "e sabendo mais do que antes!"),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Swirling golden-amber clouds and glowing embers form the shimmering silhouette of ancient Troy "
            "and the Trojan Horse in the night sky above the dark sea. Epic slow push-in at 24fps."
        ),
    },
    {
        "plano": 26,
        "id": "p26",
        "ato": "Ato III",
        "ato_titulo": "ATO III · TUDO NA TERRA FECUNDA",
        "canto_verso": "Odisseia, Canto XII, v. 189-191",
        "contador_perdas": "TENTAÇÃO DO SABER",
        "gatilho_psicologico": "Insight Psicológico Profundo (A Armadilha do Ego e da Memória)",
        "texto_narracao": (
            "Pois nós sabemos tudo o que argivos e troianos sofreram na vasta Troia pela vontade dos deuses, "
            "e sabemos tudo o que acontece sobre a terra fecunda! Elas ofereciam a ele a própria onisciência."
        ),
        "cues_legenda": [
            ("Sabemos tudo o que sofreram", "em Troia pela vontade dos deuses,"),
            ("e tudo o que acontece na Terra!", "Elas ofereciam a onisciência."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Warm golden-amber light shimmers across Odysseus's emotional face and eyes at the wooden mast "
            "as glowing sparks drift through the dark air. Slow close-up push-in at 24fps."
        ),
    },
    {
        "plano": 27,
        "id": "p27",
        "ato": "Ato III",
        "ato_titulo": "ATO III · A SÚPLICA SILENCIOSA",
        "canto_verso": "Odisseia, Canto XII, v. 192-194",
        "contador_perdas": "ORDEM RECUSADA",
        "gatilho_psicologico": "Colapso da Vontade Humana sob Hipnose",
        "texto_narracao": (
            "Assim disseram, enviando sua bela voz. E o coração de Odisseu quis ouvir mais! "
            "Francamente vencido pelo encanto, ele ordenou aos companheiros que o soltassem, acenando com as sobrancelhas."
        ),
        "cues_legenda": [
            ("O coração de Odisseu quis ouvir!", "Vencido pelo encanto daquela voz,"),
            ("ele ordenou que o soltassem,", "acenando com as sobrancelhas."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Odysseus leans forward from the wooden mast gesturing urgently with his brow while orange "
            "brazier flames flare brightly in the foreground. Dynamic camera push-in at 24fps."
        ),
    },
    {
        "plano": 28,
        "id": "p28",
        "ato": "Ato III",
        "ato_titulo": "ATO III · LAÇOS REFORÇADOS",
        "canto_verso": "Odisseia, Canto XII, v. 195-196",
        "contador_perdas": "PACTO CUMPRIDO",
        "gatilho_psicologico": "Prova do Mecanismo em Ação (Perimedes e Euríloco)",
        "texto_narracao": (
            "Mas os marinheiros surdos curvaram-se para a frente e remaram ainda mais forte! "
            "E levantando-se imediatamente, Perimedes e Euríloco envolveram o mastro com novos laços e o apertaram mais."
        ),
        "cues_legenda": [
            ("Os marinheiros surdos curvaram-se", "e remaram ainda mais forte!"),
            ("Perimedes e Euríloco levantaram-se", "e apertaram os laços em dobro."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "The two loyal Greek companions wrap an additional golden linen sash around the central wooden "
            "mast under dramatic Caravaggio torchlight. Slow resolute push-in at 24fps."
        ),
    },
    # ATO IV — A TRAVESSIA, A LIBERTAÇÃO E O FECHAMENTO RITUAL (p29 a p36: 06:32 a 08:24)
    {
        "plano": 29,
        "id": "p29",
        "ato": "Ato IV",
        "ato_titulo": "ATO IV · CORTANDO A ESPUMA",
        "canto_verso": "Odisseia, Canto XII, v. 194-197",
        "contador_perdas": "FORÇA NOS REMOS",
        "gatilho_psicologico": "Impulso Físico de Fuga",
        "texto_narracao": (
            "Os remos de abeto rasgavam a água negra levantando espuma dourada sob as lanternas da proa. "
            "Braçada após braçada, o navio vencia o campo gravitacional daquela melodia antiga."
        ),
        "cues_legenda": [
            ("Os remos de abeto rasgavam a água", "levantando espuma dourada."),
            ("Braçada após braçada, o navio", "vencia o alcance da melodia."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Long wooden Greek oars strike the dark ocean water in unison, sending up glowing amber "
            "and orange backlit water spray. Dynamic low-angle motion at 24fps."
        ),
    },
    {
        "plano": 30,
        "id": "p30",
        "ato": "Ato IV",
        "ato_titulo": "ATO IV · O CANTO SE APAGA",
        "canto_verso": "Odisseia, Canto XII, v. 197-198",
        "contador_perdas": "FORA DE ALCANCE",
        "gatilho_psicologico": "Alívio Acústico + Distanciamento do Perigo",
        "texto_narracao": (
            "Para trás, nos rochedos sombrios, as figuras aladas ficaram imóveis vendo a presa escapar. "
            "A voz divina foi se tornando um sussurro distante até não se ouvir mais nem palavra nem canto."
        ),
        "cues_legenda": [
            ("Para trás, nos rochedos sombrios,", "as Sereias viram a nau escapar."),
            ("A voz divina tornou-se um sussurro", "até desaparecer na distância."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "The rocky island and silhouetted winged Sirens recede into the dark night mist as the "
            "Greek ship sails toward the amber horizon. Slow pull-back at 24fps."
        ),
    },
    {
        "plano": 31,
        "id": "p31",
        "ato": "Ato IV",
        "ato_titulo": "ATO IV · O SOM RETORNA",
        "canto_verso": "Odisseia, Canto XII, v. 199",
        "contador_perdas": "CERA REMOVIDA",
        "gatilho_psicologico": "Descompressão Sensorial",
        "texto_narracao": (
            "Quando já tinham passado pelas Sereias e o perigo ficara para trás, "
            "os fiéis companheiros tiraram dos ouvidos a cera de abelha que Odisseu lhes havia colocado."
        ),
        "cues_legenda": [
            ("Quando já tinham passado a ilha", "e o perigo ficara para trás,"),
            ("os companheiros tiraram dos ouvidos", "a cera dourada de abelha."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Bearded Greek oarsmen smile in relief on the wooden deck as warm golden lantern light "
            "illuminates the beeswax in their hands. Smooth camera pan at 24fps."
        ),
    },
    {
        "plano": 32,
        "id": "p32",
        "ato": "Ato IV",
        "ato_titulo": "ATO IV · O REI LIBERTO",
        "canto_verso": "Odisseia, Canto XII, v. 200",
        "contador_perdas": "ODISSEU LIVRE",
        "gatilho_psicologico": "Catarse de Sobrevivência + Reconhecimento Mútuo",
        "texto_narracao": (
            "Em seguida, desataram seu capitão do mastro central. Odisseu deu um passo à frente no convés: "
            "ele havia provado o fruto proibido do conhecimento divino e continuava vivo entre seus homens."
        ),
        "cues_legenda": [
            ("Em seguida, desataram o capitão", "do grande mastro central."),
            ("Ele ouvira o canto proibido", "e continuava vivo no convés."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Odysseus steps forward freely from the wooden mast and places a hand on his companion's "
            "shoulder under warm amber firelight. Slow heroic push-in at 24fps."
        ),
    },
    {
        "plano": 33,
        "id": "p33",
        "ato": "Ato IV",
        "ato_titulo": "ATO IV · FUMAÇA NO ESTREITO",
        "canto_verso": "Odisseia, Canto XII, v. 201-205",
        "contador_perdas": "PRÓXIMO DESAFIO",
        "gatilho_psicologico": "Gancho Epódico Homérico (Cila e Caríbdis à Frente)",
        "texto_narracao": (
            "Mas na Odisseia, uma vitória apenas abre a porta para a provação seguinte. "
            "Logo após deixarem a ilha, eles avistaram fumaça ardente, grandes ondas e um estrondo no estreito adiante."
        ),
        "cues_legenda": [
            ("Mas na Odisseia, uma vitória abre", "a porta para a provação seguinte."),
            ("Adiante no mar surgiram fumaça,", "grandes ondas e um estrondo."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Towering dark sea crags ahead of the Greek warship are wreathed in swirling golden-orange "
            "mist and ocean spray. Slow epic push-in at 24fps."
        ),
    },
    {
        "plano": 34,
        "id": "p34",
        "ato": "Fechamento Ritual",
        "ato_titulo": "EPÍLOGO · O LEGADO NO BARRO",
        "canto_verso": "Odisseia, Canto XII, v. 39-200",
        "contador_perdas": "3.000 ANOS DE HISTÓRIA",
        "gatilho_psicologico": "Prova Histórica + Sabedoria Atemporal",
        "texto_narracao": (
            "Por quase três mil anos, pintores gregos gravaram essa cena no barro e no bronze. "
            "Porque Homero nos ensinou que a força de vontade sozinha sempre falha diante de uma tentação perfeita."
        ),
        "cues_legenda": [
            ("Por três mil anos, a Grécia gravou", "essa cena no barro e no bronze."),
            ("Pois a vontade sozinha falha", "diante da tentação perfeita."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Warm firelight glides across the painted surface of the ancient Greek amphora depicting "
            "Odysseus at the mast and the winged Sirens. Slow museum-grade pan at 24fps."
        ),
    },
    {
        "plano": 35,
        "id": "p35",
        "ato": "Fechamento Ritual",
        "ato_titulo": "EPÍLOGO · A LIÇÃO DE ULISSES",
        "canto_verso": "Odisseia, Canto XII, v. 178-183",
        "contador_perdas": "PRÉ-COMPROMISSO",
        "gatilho_psicologico": "Auto-Projeção Filosófica (Aplicação na Vida do Espectador)",
        "texto_narracao": (
            "Quem confia apenas na própria resistência no calor do abismo acaba naufragado nas rochas. "
            "O sábio constrói suas amarras e sela os ouvidos enquanto o mar ainda está calmo."
        ),
        "cues_legenda": [
            ("Quem confia só na própria força", "acaba naufragado nas rochas."),
            ("O sábio constrói suas amarras", "enquanto o mar ainda está calmo."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "The hooded Greek storyteller stirs the glowing orange coals of the bronze brazier with a "
            "rod, sending a cascade of golden amber sparks upward. Slow push-in at 24fps."
        ),
    },
    {
        "plano": 36,
        "id": "p36",
        "ato": "Fechamento Ritual",
        "ato_titulo": "EPÍLOGO · O LAÇO ETERNO",
        "canto_verso": "Odisseia, Canto XII, v. 200",
        "contador_perdas": "O ÚNICO SOBREVIVENTE",
        "gatilho_psicologico": "Ponte de Laço Infinito (503.9s -> 00.0s)",
        "texto_narracao": (
            "O fogo baixa, mas a canção continua ecoando nas águas escuras da memória humana. "
            "Porque desde o princípio dos tempos..."
        ),
        "cues_legenda": [
            ("O fogo baixa, mas a canção ecoa", "nas águas escuras da memória."),
            ("Porque desde o princípio", "dos tempos..."),
        ],
        "prompt_video": (
            "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
            "Warm amber embers rise into the dark night air beside the hooded storyteller in profile "
            "holding the ancient Siren pottery shard. Slow atmospheric push-in at 24fps."
        ),
    },
]

# Preenche automaticamente janela_s de 14.0s para cada um dos 36 blocos (36 * 14.0s = 504.0s = 08m24s)
BLOCOS_E_PLANOS_36: List[Dict[str, Any]] = []
for _idx, _spec in enumerate(RAW_36_SPECS):
    _item = dict(_spec)
    _w0 = round(_idx * DURACAO_BLOCO_S, 2)
    _w1 = round((_idx + 1) * DURACAO_BLOCO_S, 2)
    _item["janela_s"] = [_w0, _w1]
    _item["prompt_start_frame"] = _item["prompt_video"]
    BLOCOS_E_PLANOS_36.append(_item)


def sintetizar_bloco_vocal_resiliente(blocos_voz_dir: Path, plano_num: int, texto: str) -> Path:
    blocos_voz_dir.mkdir(parents=True, exist_ok=True)
    mp3_path = blocos_voz_dir / f"voz_p{plano_num:02d}_8m.mp3"
    if mp3_path.exists() and mp3_path.stat().st_size > 12_000:
        return mp3_path

    texto_limpo = texto.lstrip(". ").strip()

    # Tenta primeiro Gemini TTS (Chave #2 ativa -> Chave #1)
    try:
        sintetizar_voz_gemini_com_fallback(
            texto=texto_limpo,
            output_path=mp3_path,
            voice_name="Charon",
            chaves=[
                "ENV_GEMINI_API_KEY_2",
                "ENV_GEMINI_API_KEY_1",
            ],
        )
        if mp3_path.exists() and mp3_path.stat().st_size > 8_000:
            print(f"  + [TTS GEMINI CHARON] P{plano_num:02d} sintetizado ({mp3_path.stat().st_size} bytes)")
            time.sleep(1.2)
            return mp3_path
    except Exception as exc:
        print(f"  ! [TTS GEMINI] P{plano_num:02d} cota atingida ({exc}). Usando fallback neural Antonio Barítono...")

    # Fallback Neural Barítono via edge-tts (pt-BR-AntonioNeural com pitch grave -10Hz e rate -5%)
    import edge_tts

    async def _run_edge() -> None:
        comm = edge_tts.Communicate(texto_limpo, voice="pt-BR-AntonioNeural", rate="-5%", pitch="-10Hz")
        await comm.save(str(mp3_path))

    asyncio.run(_run_edge())
    print(f"  + [TTS NEURAL ANTONIO] P{plano_num:02d} sintetizado ({mp3_path.stat().st_size} bytes)")
    return mp3_path


def processar_bloco_vocal(blocos_voz_dir: Path, mp3_path: Path, max_dur_s: float) -> np.ndarray:
    tmp_trim = blocos_voz_dir / f"_trim_{mp3_path.stem}.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(mp3_path),
            "-af", (
                "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-42dB:"
                "stop_periods=-1:stop_duration=0.18:stop_threshold=-45dB,"
                "highpass=f=75,"
                "equalizer=f=150:t=q:w=1.1:g=2.4,"
                "equalizer=f=3200:t=q:w=1.3:g=2.2"
            ),
            "-ar", str(SR),
            "-ac", "1",
            "-c:a", "pcm_s16le",
            str(tmp_trim),
        ],
        check=True,
    )
    with wave.open(str(tmp_trim), "rb") as wf:
        samples = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    dur_s = len(samples) / float(SR)

    if dur_s > max_dur_s:
        ratio = min(1.50, max(1.02, (dur_s / max_dur_s) * 1.03))
        tmp_tempo = blocos_voz_dir / f"_tempo_{mp3_path.stem}.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(tmp_trim),
                "-af", f"atempo={ratio:.4f}",
                "-ar", str(SR),
                "-ac", "1",
                "-c:a", "pcm_s16le",
                str(tmp_tempo),
            ],
            check=True,
        )
        with wave.open(str(tmp_tempo), "rb") as wf:
            samples = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        tmp_tempo.unlink(missing_ok=True)

    tmp_trim.unlink(missing_ok=True)

    n = len(samples)
    fi = min(n, int(0.025 * SR))
    fo = min(n, int(0.035 * SR))
    if fi > 0:
        samples[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 0:
        samples[n - fo :] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)

    rms = float(np.sqrt(np.mean(samples**2)) + 1e-9)
    target_rms = 10.0 ** (-18.0 / 20.0)
    samples = np.clip(samples * (target_rms / rms), -0.88, 0.88)
    return samples


def carregar_wav_stereo_loop(wav_path: Path, dur_samples: int) -> np.ndarray:
    tmp_s = wav_path.parent / f"_tmp_st_{wav_path.stem}_{dur_samples}.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-stream_loop", "-1",
            "-i", str(wav_path),
            "-t", f"{dur_samples / float(SR):.3f}",
            "-ar", str(SR),
            "-ac", "2",
            "-c:a", "pcm_s16le",
            str(tmp_s),
        ],
        check=True,
    )
    with wave.open(str(tmp_s), "rb") as wf:
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    tmp_s.unlink(missing_ok=True)
    arr = raw.reshape(-1, 2)
    if len(arr) < dur_samples:
        pad = np.zeros((dur_samples - len(arr), 2), dtype=np.float32)
        arr = np.vstack((arr, pad))
    return arr[:dur_samples]


def carregar_sfx_curto(wav_path: Path, max_dur_s: float = 4.0) -> np.ndarray:
    tmp_s = wav_path.parent / f"_tmp_sfx_{wav_path.stem}.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(wav_path),
            "-t", f"{max_dur_s:.3f}",
            "-ar", str(SR),
            "-ac", "2",
            "-c:a", "pcm_s16le",
            str(tmp_s),
        ],
        check=True,
    )
    with wave.open(str(tmp_s), "rb") as wf:
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    tmp_s.unlink(missing_ok=True)
    arr = raw.reshape(-1, 2)
    fo = min(len(arr), int(0.15 * SR))
    if fo > 0:
        arr[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    return arr


def fmt_srt_time(segundos: float) -> str:
    ms_total = int(round(segundos * 1000))
    hh = ms_total // 3_600_000
    rem = ms_total % 3_600_000
    mm = rem // 60_000
    rem = rem % 60_000
    ss = rem // 1000
    ms = rem % 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def construir_roteiro_voz_audio_legendas() -> Dict[str, Any]:
    dirs = criar_diretorios_episodio_isolado(EPISODIO_ID)
    roteiro_dir = dirs["roteiro"]
    audio_dir = dirs["audio"]
    blocos_voz_dir = dirs["blocos_voz"]
    legendas_dir = dirs["legendas"]
    master_dir = dirs["master"]

    # Limpa blocos_1para1_conformados antigos de 10s para que sejam reconformados em 14.0s (504.0s = 8m24s)
    cap_dir = master_dir / "blocos_1para1_conformados"
    if cap_dir.exists():
        shutil.rmtree(cap_dir, ignore_errors=True)

    print("=" * 80)
    print(f"[EPISÓDIO 02 — 08m24s (504.0s)] ROTEIRO 36 BLOCOS 1:1, VOZ NEURAL, MIXAGEM -14 LUFS E LEGENDAS")
    print("=" * 80)

    voice_mono = np.zeros(TOTAL_SAMPLES, dtype=np.float32)
    janelas_fala: Dict[int, Tuple[float, float]] = {}

    for b in BLOCOS_E_PLANOS_36:
        p = int(b["plano"])
        w0, w1 = float(b["janela_s"][0]), float(b["janela_s"][1])
        mp3_p = sintetizar_bloco_vocal_resiliente(blocos_voz_dir, p, b["texto_narracao"])

        if p == 1:
            t_in = w0 + 0.25
            max_d = 13.00
        elif p == 24:
            # Respeita rigorosamente o Silêncio Dramático de 1.5s (334.50s a 336.00s) da Dica MCP LUME-TIP-20261022-C26221!
            t_in = w0 + 0.35
            max_d = 11.75  # Termina até <= 334.10s!
        elif p == 25:
            # Começa imediatamente após o Silêncio Dramático de 1.5s (336.05s) para máximo impacto de revelação!
            t_in = 336.05
            max_d = 13.20
        elif p == 36:
            t_in = w0 + 0.35
            max_d = 13.30  # Termina próximo a 503.65s para colar no Loop Infinito em 0.25s!
        else:
            t_in = w0 + 0.40
            max_d = 12.90

        seg = processar_bloco_vocal(blocos_voz_dir, mp3_p, max_dur_s=max_d)
        i0 = int(t_in * SR)
        i1 = min(TOTAL_SAMPLES, i0 + len(seg))
        voice_mono[i0:i1] = seg[: i1 - i0]
        t_out = i1 / float(SR)
        janelas_fala[p] = (round(t_in, 3), round(t_out, 3))
        b["fala_inicio_s"] = janelas_fala[p][0]
        b["fala_fim_s"] = janelas_fala[p][1]
        print(f"  -> Plano P{p:02d} ({w0:5.1f}s..{w1:5.1f}s): Voz em {t_in:6.2f}s .. {t_out:6.2f}s (dur={t_out - t_in:4.2f}s)")

    # Zera absolutamente a janela do Silêncio Dramático de 1.5s (334.50s a 336.00s)
    sil_i0 = int(SILENCIO_INICIO_S * SR)
    sil_i1 = int(SILENCIO_FIM_S * SR)
    voice_mono[sil_i0:sil_i1] = 0.0

    # Constrói cama BGM em 5 movimentos cobrindo os 504.0s (08m24s)
    bgm_1 = carregar_wav_stereo_loop(REAL_BGM_DIR / "bgm_01_lira_abertura_fechamento.wav", int(168.0 * SR))  # p01..p12
    bgm_2 = carregar_wav_stereo_loop(REAL_BGM_DIR / "bgm_02_drone_aulos_caverna.wav", int(126.0 * SR))       # p13..p21
    bgm_3 = carregar_wav_stereo_loop(REAL_BGM_DIR / "bgm_03_percussao_tensao_astucia.wav", int(42.0 * SR))   # p22..p24
    bgm_4 = carregar_wav_stereo_loop(REAL_BGM_DIR / "bgm_04_coro_climax_epico.wav", int(84.0 * SR))          # p25..p30
    bgm_5 = carregar_wav_stereo_loop(REAL_BGM_DIR / "bgm_01_lira_abertura_fechamento.wav", int(84.0 * SR))   # p31..p36
    bgm_bed = np.vstack((bgm_1, bgm_2, bgm_3, bgm_4, bgm_5))[:TOTAL_SAMPLES] * 0.26

    fogo_bed = carregar_wav_stereo_loop(REAL_SFX_DIR / "sfx_01_braseiro_fogo_intimo.wav", TOTAL_SAMPLES) * 0.22
    mar_bed = carregar_wav_stereo_loop(REAL_SFX_DIR / "sfx_04_ambiencia_caverna_gotas.wav", TOTAL_SAMPLES) * 0.14

    sfx_timeline = fogo_bed + mar_bed

    sfx_whoosh = carregar_sfx_curto(REAL_SFX_DIR / "sfx_09_eco_sussurro_caverna.wav", 2.2) * 0.32
    sfx_boom = carregar_sfx_curto(REAL_SFX_DIR / "sfx_03_rocha_selando_caverna.wav", 3.2) * 0.38
    sfx_chamas = carregar_sfx_curto(REAL_SFX_DIR / "sfx_11_estaca_chamas_ataque.wav", 3.5) * 0.30

    for p_idx in range(1, NUM_BLOCOS):
        t_trans = max(0.0, p_idx * DURACAO_BLOCO_S - 0.35)
        if not (SILENCIO_INICIO_S - 0.20 <= t_trans <= SILENCIO_FIM_S + 0.10):
            idx0 = int(t_trans * SR)
            idx1 = min(TOTAL_SAMPLES, idx0 + len(sfx_whoosh))
            sfx_timeline[idx0:idx1] += sfx_whoosh[: idx1 - idx0]

    # Impacto dramático exatamente em 336.02s (fim do Silêncio de 1.5s e entrada da Revelação do Clímax!)
    idx_rev0 = int((SILENCIO_FIM_S + 0.02) * SR)
    idx_rev1 = min(TOTAL_SAMPLES, idx_rev0 + len(sfx_boom))
    sfx_timeline[idx_rev0:idx_rev1] += sfx_boom[: idx_rev1 - idx_rev0]

    idx_ch0 = int((SILENCIO_FIM_S + 0.20) * SR)
    idx_ch1 = min(TOTAL_SAMPLES, idx_ch0 + len(sfx_chamas))
    sfx_timeline[idx_ch0:idx_ch1] += sfx_chamas[: idx_ch1 - idx_ch0]

    voice_stereo = np.column_stack((voice_mono, voice_mono))
    delay_samples = int(0.014 * SR)
    voice_stereo[delay_samples:, 0] += 0.05 * voice_mono[:-delay_samples]
    voice_stereo[: TOTAL_SAMPLES - delay_samples, 1] += 0.05 * voice_mono[delay_samples:]

    env_win = int(0.08 * SR)
    voice_abs = np.abs(voice_mono)
    kernel = np.ones(env_win, dtype=np.float32) / float(env_win)
    voice_env = np.convolve(voice_abs, kernel, mode="same")
    duck_gain = np.clip(1.0 - 0.58 * np.clip(voice_env / 0.12, 0.0, 1.0), 0.38, 1.0)[:, None]

    mix_raw = voice_stereo + (bgm_bed + sfx_timeline) * duck_gain

    # Aplica o CORTE TOTAL DE 1.5s ANTES DA REVELAÇÃO (Dica MCP LUME-TIP-20261022-C26221: 334.50s a 336.00s)
    fade_pre = int(0.04 * SR)
    if sil_i0 - fade_pre > 0:
        mix_raw[sil_i0 - fade_pre : sil_i0] *= np.linspace(1.0, 0.0, fade_pre, dtype=np.float32)[:, None]
    mix_raw[sil_i0:sil_i1] = 0.0

    tmp_pre_wav = audio_dir / "_tmp_pre_master_sereias_8m.wav"
    master_wav = audio_dir / "master_audio_sereias.wav"
    with wave.open(str(tmp_pre_wav), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        pcm16 = np.clip(mix_raw * 32767.0, -32767, 32767).astype(np.int16)
        wf.writeframes(pcm16.tobytes())

    p1 = subprocess.run(
        [
            "ffmpeg", "-nostats", "-i", str(tmp_pre_wav),
            "-filter_complex", "ebur128=peak=true", "-f", "null", "-",
        ],
        capture_output=True, text=True, check=True,
    )
    measured_i = float(re.findall(r"I:\s*([-\d\.]+)\s*LUFS", p1.stderr)[-1])
    gain_db = -14.0 - measured_i

    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(tmp_pre_wav),
            "-af", f"volume={gain_db:.3f}dB,alimiter=limit=-1.2dB:level=false",
            "-ar", str(SR),
            "-ac", "2",
            "-c:a", "pcm_s16le",
            str(tmp_pre_wav.with_name("_tmp_norm16_8m.wav")),
        ],
        check=True,
    )
    with wave.open(str(tmp_pre_wav.with_name("_tmp_norm16_8m.wav")), "rb") as wf:
        norm_arr = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).reshape(-1, 2).copy()
    norm_arr[sil_i0:sil_i1] = 0
    with wave.open(str(tmp_pre_wav.with_name("_tmp_norm16_sil_8m.wav")), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        wf.writeframes(norm_arr.tobytes())

    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(tmp_pre_wav.with_name("_tmp_norm16_sil_8m.wav")),
            "-ar", str(SR),
            "-ac", "2",
            "-c:a", "pcm_s24le",
            str(master_wav),
        ],
        check=True,
    )
    for f_tmp in [
        tmp_pre_wav,
        tmp_pre_wav.with_name("_tmp_norm16_8m.wav"),
        tmp_pre_wav.with_name("_tmp_norm16_sil_8m.wav"),
    ]:
        f_tmp.unlink(missing_ok=True)

    p2 = subprocess.run(
        [
            "ffmpeg", "-nostats", "-i", str(master_wav),
            "-filter_complex", "ebur128=peak=true", "-f", "null", "-",
        ],
        capture_output=True, text=True, check=True,
    )
    final_lufs = float(re.findall(r"I:\s*([-\d\.]+)\s*LUFS", p2.stderr)[-1])
    final_tp = float(re.findall(r"Peak:\s*([-\d\.]+)\s*dBFS", p2.stderr)[-1])
    print(f"  [MASTER AUDIO 08m24s VALIDADO] {master_wav} | Loudness = {final_lufs:.1f} LUFS | True Peak = {final_tp:.2f} dBTP")

    cues: List[Dict[str, Any]] = []
    cue_id = 1
    for b in BLOCOS_E_PLANOS_36:
        p = int(b["plano"])
        t_in = float(b["fala_inicio_s"])
        t_out = float(b["fala_fim_s"])
        t_mid = round(t_in + (t_out - t_in) * 0.50, 3)
        c1_lines, c2_lines = b["cues_legenda"]
        for ln in list(c1_lines) + list(c2_lines):
            assert len(ln) <= 38, f"Linha excedeu 38 chars no plano {p}: '{ln}' ({len(ln)})"
        cues.append({"id": cue_id, "plano": p, "start": t_in, "end": round(t_mid - 0.04, 3), "lines": list(c1_lines)})
        cue_id += 1
        cues.append({"id": cue_id, "plano": p, "start": round(t_mid + 0.02, 3), "end": t_out, "lines": list(c2_lines)})
        cue_id += 1

    srt_path = legendas_dir / "ep02_sereias_pt.srt"
    vtt_path = legendas_dir / "ep02_sereias_pt.vtt"
    srt_text = "\n\n".join(
        f"{c['id']}\n{fmt_srt_time(c['start'])} --> {fmt_srt_time(c['end'])}\n" + "\n".join(c["lines"])
        for c in cues
    ) + "\n"
    vtt_text = "WEBVTT\n\n" + "\n\n".join(
        f"{c['id']}\n{fmt_srt_time(c['start']).replace(',', '.')} --> {fmt_srt_time(c['end']).replace(',', '.')}\n"
        + "\n".join(c["lines"])
        for c in cues
    ) + "\n"
    srt_path.write_text(srt_text, encoding="utf-8")
    vtt_path.write_text(vtt_text, encoding="utf-8")
    print(f"  [LEGENDAS GERADAS] {srt_path} ({len(cues)} cues <= 38 chars/linha)")

    roteiro_doc = {
        "episodio_id": EPISODIO_ID,
        "mcp_theme_id": "LUME-THM-20261022-5F40D7",
        "mcp_tip_id": "LUME-TIP-20261022-C26221",
        "titulo": "O Canto das Sereias e a Cera nos Ouvidos",
        "mito": "A Odisseia (Homero)",
        "referencia_primaria": "Odisseia, Canto XII, v. 39-200",
        "big_idea": "O único homem que ouviu a promessa mortal das Sereias amarrado ao mastro e sobreviveu.",
        "thumbnail_concept": "B · Escolha — AMARRE-ME AO MASTRO",
        "schwartz_awareness_level": 4,
        "duracao_total_s": DURACAO_TOTAL_S,
        "silencio_dramatico_s": [SILENCIO_INICIO_S, SILENCIO_FIM_S],
        "blocos": BLOCOS_E_PLANOS_36,
        "planos": BLOCOS_E_PLANOS_36,
    }
    validar_paridade_1_para_1_blocos_planos(roteiro_doc["blocos"], roteiro_doc["planos"], episodio_id=EPISODIO_ID)
    roteiro_json_path = roteiro_dir / "roteiro_sereias_1para1.json"
    roteiro_json_path.write_text(json.dumps(roteiro_doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  [ROTEIRO 1:1 VALIDADO] {roteiro_json_path} (36 blocos == 36 planos | 504.0s = 08m24s)")
    return roteiro_doc


if __name__ == "__main__":
    construir_roteiro_voz_audio_legendas()
