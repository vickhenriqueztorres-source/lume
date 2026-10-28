"""Subetapa 3: Gerador Canônico 1:1 dos 50 Planos Visuais (50 Start Frames IA + 50 Vídeos Firefly).

Mapeia estritamente 1:1 cada um dos 50 blocos de `roteiro_ep01_odisseia_8min.json`
para `p01` a `p50` (10.2s cada = 510.0s), eliminando `roteiro_12_planos_firefly.json`
e validando `validar_paridade_1_para_1_blocos_planos`.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Tuple

from contratos.integridade_assets import validar_paridade_1_para_1_blocos_planos

STYLE_PREFIX = (
    "2D hand-drawn Western graphic novel animation frame (style of Tartakovsky's Primal meets Mike Mignola's Hellboy "
    "and Caravaggio tenebrism), heavy charcoal ink outlines, 75% of frame in deep obsidian shadow (#0A0705), dramatic "
    "firelight in aged bronze (#C89B3C), burning ember orange (#E85D04), and incandescent gold (#FFD166), widescreen 16:9, no text: "
)

# Mapa 1:1 (Bloco 1 a 50) -> (prompt_start_frame, prompt_video Firefly-safe)
PROMPTS_50_BLOCOS: Dict[int, Tuple[str, str]] = {
    1: (
        "Medium close-up of O Contador, an ancient blind Greek storyteller with weathered wrinkles, silver-white beard, and dark hooded cloak seated beside a glowing bronze tripod brazier in a pitch-black stone chamber while Troy's ruined walls smoke in the far background.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Bright orange embers and golden flames dance in the bronze brazier, casting flickering Caravaggio rim-lighting across the blind Greek storyteller's weathered face and silver beard. Slow camera push-in at 24fps.",
    ),
    2: (
        "Epic wide 16:9 shot of twelve ancient Greek black-prowed birreme warships embarking from the smoky coast of Troy at night, six hundred silhouetted warriors in bronze helmets boarding with spears under rising golden embers.",
        "Animate this 2D cel-shaded chiaroscuro graphic novel illustration. Twelve ancient Greek black-prowed warships glide across dark coastal waters as wooden oars move rhythmically and golden embers drift upward into the night sky. Slow tracking camera at 24fps.",
    ),
    3: (
        "Emotional 16:9 chiaroscuro frame on the wooden deck of a Greek warship at night: silhouetted Greek warriors in crested bronze helmets looking back across the dark sea, holding bronze lockets and shields, their faces lit by a single warm shipboard torch.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm orange torchlight flickers across the bronze helmets and cloaks of the Greek sailors on the wooden deck as dark ocean waves roll gently beneath the hull. Slow push-in at 24fps.",
    ),
    4: (
        "Extreme close-up of O Contador's aged hand holding an olive-wood staff over the bronze brazier; within the rising golden smoke and embers, the faint silhouette of a lone Greek ship faces a towering black ocean wave.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Swirling golden smoke and glowing orange sparks rise from the bronze brazier around the storyteller's gnarled hand and olive-wood staff. Slow cinematic push-in at 24fps.",
    ),
    5: (
        "Dramatic 16:9 chiaroscuro scene on the beach of Ismarus (land of the Cicones) at twilight: Greek sailors feasting around beach bonfires with bronze amphoras of wine and treasure chests while dark silhouettes of Cicone horsemen gather on the hills behind them.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Beach bonfire flames and orange sparks dance in the coastal wind illuminating the Greek sailors and bronze amphoras while twilight mist rolls over the hills. Slow camera pan at 24fps.",
    ),
    6: (
        "Haunting 16:9 chiaroscuro coastal scene on the Island of the Lotus-Eaters: three Greek sailors kneeling in a dreamy trance holding glowing golden-amber lotus flowers near their faces while their bronze helmets lie forgotten in the black sand.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Glowing golden pollen and warm amber light drift softly from the lotus blossoms held by the kneeling Greek sailors beside the dark ocean surf. Slow atmospheric push-in at 24fps.",
    ),
    7: (
        "Tense 16:9 chiaroscuro frame aboard Odysseus's warship: Odysseus in his crested Corinthian helmet firmly guiding the weeping lotus-entranced sailors beneath the wooden rowing benches as the ship sails toward a towering jagged island of cliffs.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The wooden Greek warship pitches gently on dark waves as Odysseus stands on the torchlit deck pointing toward the looming rocky island ahead. Slow camera push-in at 24fps.",
    ),
    8: (
        "Atmospheric 16:9 chiaroscuro interior of Polyphemus's vast limestone cavern: Greek sailors holding torches beside giant wicker racks of aged cheeses and pens of goats, urging Odysseus to turn back toward the sunlit cave mouth.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Flickering orange torchlight illuminates the towering limestone cavern walls and the Greek sailors gathered around Odysseus. Slow cinematic push-in at 24fps.",
    ),
    9: (
        "Colossal low-angle 16:9 chiaroscuro frame inside the cave at nightfall: the immense silhouette of the Cyclops Polyphemus heaving a monolithic mountain boulder to seal the cavern entrance, blocking out the last sliver of twilight.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Dust and golden embers swirl in the dark cavern as the colossal silhouetted giant sets the massive stone boulder across the cave entrance. Slow low-angle camera tilt at 24fps.",
    ),
    10: (
        "Terrifying 16:9 chiaroscuro shadow-theater composition: the gigantic black silhouette of the Cyclops looming over the cavern floor as terrified tiny Greek warriors scatter into the deep crevices beside a dying fire pit.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The giant shadow of the Cyclops moves across the rough limestone cavern wall as red-orange embers flicker in the fire pit below. Slow tense camera push-in at 24fps.",
    ),
    11: (
        "Intense 16:9 chiaroscuro close-up of Odysseus in the pitch-black cavern, his hand gripping the bronze hilt of his sword, his eyes lit by a thin bar of orange firelight as he stares at the massive stone boulder sealing the exit.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Flickering warm firelight glints off the bronze sword hilt and Odysseus's determined eyes in the dark cavern as embers float past. Slow close-up push-in at 24fps.",
    ),
    12: (
        "Dramatic 16:9 chiaroscuro frame of Odysseus and his men sharpening a long green olive-wood trunk over a blazing cavern fire pit, its pointed tip glowing incandescent gold and orange amidst flying sparks.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Bright golden sparks and orange flames rise from the cavern fire pit around the glowing tip of the wooden stake held by Odysseus and his men. Slow push-in at 24fps.",
    ),
    13: (
        "Striking 16:9 chiaroscuro composition: Odysseus standing small but fearless before the colossal seated shadow of Polyphemus, holding up a carved wooden bowl overflowing with dark ruby-gold wine of Maron.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm amber firelight reflects on the dark wine in the raised wooden bowl as Odysseus offers it upward toward the giant silhouette in the cavern. Slow camera push-in at 24fps.",
    ),
    14: (
        "Wide 16:9 chiaroscuro frame inside the cavern: the colossal silhouette of Polyphemus tilting back a bronze vessel to drink the ketiga draught of wine while outside the cave entrance dark mountain peaks stand under a stormy sky.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Torchlight flickers across the cavern walls as the giant silhouette tilts the drinking bowl and warm embers drift through the dark air. Slow cinematic pan at 24fps.",
    ),
    15: (
        "Iconic 16:9 chiaroscuro close-up of Odysseus's face half-shrouded in deep obsidian shadow, one finger raised in cunning silence as golden firelight illuminates his profile while speaking the name 'Nobody' (Outis).",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Dancing orange firelight casts sharp Caravaggio shadows across Odysseus's profile as glowing embers drift slowly in the foreground. Slow dramatic push-in at 24fps.",
    ),
    16: (
        "High-tension 16:9 chiaroscuro frame: Odysseus and four silhouetted Greek warriors hoisting the giant olive-wood stake with its white-hot incandescent golden tip poised above the sleeping giant Cyclops in the dark cavern.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. White-hot golden sparks and orange flames radiate from the glowing tip of the wooden stake as the silhouetted warriors heave it forward. Dynamic push-in at 24fps.",
    ),
    17: (
        "Dramatic 16:9 chiaroscuro frame at the cavern entrance: the blinded Cyclops Polyphemus roaring with arms outstretched against the stone walls while smaller silhouetted Cyclopes outside on the mountain ridge turn and walk away into the night fog.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Swirling night mist and glowing orange embers move across the mountain ridge outside the cavern as the giant silhouette stands at the threshold. Slow pull-back at 24fps.",
    ),
    18: (
        "Epic 16:9 chiaroscuro frame on the turbulent sea: Odysseus shouting defiantly from the stern of his departing warship while high on the cliff silhouette Polyphemus raises a mountain boulder to invoke Poseidon's curse.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Foaming dark ocean waves roll around the wooden warship as Odysseus stands on the stern and storm clouds swirl in the amber sky above the cliff. Dynamic ocean motion at 24fps.",
    ),
    19: (
        "Mystical 16:9 chiaroscuro frame on the floating bronze-walled island of Aeolia: King Aeolus handing Odysseus a swollen leather wind-sack tied tightly with a gleaming silver cord under a warm golden sky.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. A gentle golden breeze stirs the cloaks of Aeolus and Odysseus as silver light glints on the cord of the leather wind-sack. Slow cinematic push-in at 24fps.",
    ),
    20: (
        "Poetic 16:9 chiaroscuro frame at dawn: an exhausted Odysseus gripping the wooden steering oar of his flagship after nine sleepless nights, gazing toward the distant rocky coast of Ithaca where warm golden campfires smoke on the horizon.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Gentle golden dawn light shimmers on the dark sea waves as smoke rises from the distant shore of Ithaca and Odysseus holds the helm. Slow push-in at 24fps.",
    ),
    21: (
        "Catastrophic 16:9 chiaroscuro frame on the ship deck at night: while Odysseus sleeps near the stern, two greedy sailors untie the silver cord of the leather sack, unleashing a howling vortex of amber and silver hurricane winds that tear the sails.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. A swirling vortex of glowing amber and silver wind gusts erupts from the leather sack on deck, whipping the sails and rigging as waves rise. Dramatic push-in at 24fps.",
    ),
    22: (
        "Ominous 16:9 chiaroscuro wide shot of the narrow canyon-like fjord of Telepylus: eleven Greek warships rowing into the calm dark water trapped between towering vertical black cliffs, while Odysseus's twelfth ship anchors outside the entrance.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Eleven wooden warships glide into the narrow canyon harbor between towering dark cliffs as mist drifts across the still water. Slow high-angle tracking shot at 24fps.",
    ),
    23: (
        "Apocalyptic 16:9 chiaroscuro wide frame inside the harbor of Telepylus: colossal silhouetted Laestrygonian giants standing atop the high cliffs hurling massive boulders down into the eleven trapped Greek ships below amidst orange firelight and spray.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Giant silhouetted figures on the cliff tops gesture downward as huge splashes of water, mist, and glowing orange embers rise from the canyon harbor below. Slow tilt at 24fps.",
    ),
    24: (
        "Urgent 16:9 chiaroscuro close-action frame: Odysseus on the prow of his lone flagship swinging his gleaming bronze sword to sever the thick mooring rope tied to the cliff rock, his single ship surging out into the open dark sea.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm amber light glints off Odysseus's bronze blade by the ship's prow as the lone wooden vessel surges forward through foaming ocean waves. Fast cinematic push-in at 24fps.",
    ),
    25: (
        "Eerie 16:9 chiaroscuro frame inside the stone palace of Circe on Aeaea: the sorceress Circe holding a golden cup and wand in dramatic torchlight while shadowy silhouettes of Greek sailors transform into wild boars in the courtyard.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Glowing golden mist and flickering torchlight swirl around Circe's wand and golden cup inside the shadowy stone colonnade. Slow atmospheric push-in at 24fps.",
    ),
    26: (
        "Powerful 16:9 chiaroscuro frame: Odysseus holding the glowing white-and-gold sacred Moly flower in one hand and his bronze sword in the other, confronting Circe on her marble steps as warm amber light breaks the darkness.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Incandescent golden light radiates from the sacred Moly flower in Odysseus's hand while torchlight flickers across Circe's flowing robes. Slow camera push-in at 24fps.",
    ),
    27: (
        "Haunting 16:9 chiaroscuro frame transitioning to the realm of 'cinza-alma' (soul-ash grey): Odysseus's lone black-sailed ship sailing into a dense wall of pale silver-grey fog at the edge of the world where no sun shines.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Thick pale silver-grey fog and faint amber mist roll slowly across the dark mirror-like water as the lone black-sailed ship glides forward. Slow push-in at 24fps.",
    ),
    28: (
        "Solemn 16:9 chiaroscuro frame in the Underworld (Hades) in 'cinza-alma' palette: Odysseus kneeling on the cold black rock beside a ritual trench, holding his bronze blade as pale grey mist and dim amber light rise from the earth.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Ethereal silver-grey mist and soft golden motes of light rise around the kneeling Odysseus in the cavernous dark landscape. Slow atmospheric push-in at 24fps.",
    ),
    29: (
        "Prophetic 16:9 chiaroscuro frame in Hades: the blind prophet Tiresias emerging from the grey mist as a luminous translucent spectre with glowing pale-gold eyes and a staff, pointing ominously toward Odysseus.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Translucent silver and pale-gold mist swirls around the robed prophet Tiresias and his staff as he stands before Odysseus. Slow tense camera push-in at 24fps.",
    ),
    30: (
        "Heartbreaking 16:9 chiaroscuro frame in Hades: Odysseus reaching out with open arms in tears as the translucent silver-grey spirit of his mother Anticleia dissolves like smoke through his embrace in the dark fog.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The luminous silver-grey silhouette of Anticleia shimmers and drifts like gentle smoke amidst the dark mist as Odysseus reaches forward. Slow emotional push-in at 24fps.",
    ),
    31: (
        "Majestic 16:9 chiaroscuro frame in Hades: the towering armoured shade of Achilles in a crested Corinthian helmet standing in pale silver-grey light before Odysseus, surrounded by shadowy spears of fallen heroes.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Drifting grey fog and faint golden embers move past the armoured silhouette of Achilles and Odysseus in the quiet twilight of the Underworld. Slow push-in at 24fps.",
    ),
    32: (
        "Eerie 16:9 chiaroscuro maritime frame: Odysseus's lone warship floating on water flat and still as a mirror of dark lead, sails hanging slack under a blazing amber sky as the jagged island of the Sirens looms ahead.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Golden-amber sunlight shimmers across the glass-like dark ocean water around the motionless wooden ship as a faint mist hugs the distant rocks. Slow push-in at 24fps.",
    ),
    33: (
        "Mythological 16:9 chiaroscuro frame faithful to Greek black-figure vases: two winged bird-bodied, human-headed Sirens perched atop jagged black sea rocks surrounded by bleached white ship timbers under an amber sun.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The winged bird-bodied Sirens atop the dark coastal rocks slowly rustle their feathers as amber light and sea mist drift across the water. Slow camera push-in at 24fps.",
    ),
    34: (
        "Tactile 16:9 chiaroscuro close-up on the ship deck: Odysseus warming a golden honeycomb of beeswax in his weathered hands and pressing the glowing amber wax to seal the ears of his seated Greek oarsmen.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm golden sunlight gleams on the amber beeswax in Odysseus's hands as the seated oarsmen grip their wooden oars on deck. Slow close-up push-in at 24fps.",
    ),
    35: (
        "Iconic 16:9 chiaroscuro vertical-tension frame: two Greek sailors wrapping thick hemp ropes tightly around Odysseus's chest and arms, binding him standing upright against the central wooden mast of the warship.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The ship's sails and rigging sway gently against the amber sky as Odysseus stands bound to the central wooden mast and the crew rows below. Slow tilt up at 24fps.",
    ),
    36: (
        "Intense 16:9 chiaroscuro close-up of Odysseus bound to the mast, straining forward with veins taut and mouth open in an agonizing cry as golden acoustic waves of light ripple across the dark air from the Sirens' island.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Shimmering golden light waves and sea spray drift past Odysseus as he leans forward against the taut ropes on the wooden mast. Intense push-in at 24fps.",
    ),
    37: (
        "Stoic 16:9 chiaroscuro frame on the rowing deck: Eurylochus and Perimedes pulling the ropes even tighter around the mast while the wax-eared oarsmen row in synchronized rhythm through the dark water.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Wooden oars dip rhythmically into the dark sea throwing golden-lit spray as the Greek crew rows steadily forward. Smooth tracking motion at 24fps.",
    ),
    38: (
        "Colossal 16:9 chiaroscuro seascape: Odysseus's lone wooden ship skirting the edge of Charybdis, a gigantic boiling black whirlpool that swallows the ocean into a bottomless vortex of foam and amber spray.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. The massive ocean whirlpool of Charybdis spins and churns foaming water and mist as the wooden warship navigates the rim. Dynamic ocean motion at 24fps.",
    ),
    39: (
        "Suspenseful 16:9 chiaroscuro low-angle frame: high up in the pitch-black cavern of the opposite cliff face, six monstrous serpentine necks of Scylla coil in shadow with glowing amber eyes while Odysseus stands armed on the prow below.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Sea fog and golden lightning flashes illuminate the towering dark cliff cavern as the six shadowy serpentine shapes sway above the ship. Slow tilt up at 24fps.",
    ),
    40: (
        "Dramatic 16:9 chiaroscuro action frame: the six serpentine necks of Scylla striking down from the high cliff through storm spray toward the warship deck as Odysseus reaches out in horror from the stern.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Storm waves and golden lightning flashes crash around the wooden warship in the narrow strait beneath the towering dark cliff. Dramatic camera movement at 24fps.",
    ),
    41: (
        "Desolate 16:9 chiaroscuro frame on the rocky shore of Thrinacia: the thirty-nine exhausted, gaunt Greek survivors huddled around a dying campfire on the beach while relentless storm winds lash the dark sea, trapping their beached ship.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Strong coastal wind whips the cloaks of the huddled Greek sailors and scatters red-orange embers from the dying beach campfire. Slow camera pan at 24fps.",
    ),
    42: (
        "Sacrilegious 16:9 chiaroscuro frame on the island of Thrinacia: while Odysseus sleeps in a high mountain alcove in the background, Eurylochus and the starving crew surround the luminous white-and-gold sacred cattle of Helios the Sun God.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. An eerie golden aura glows around the sacred cattle of the Sun on the dark hillside as torch-bearing sailors approach through the mist. Slow push-in at 24fps.",
    ),
    43: (
        "Absolute Dramatic Silence 16:9 chiaroscuro frame (90% deep obsidian black #0A0705): Odysseus's last warship frozen on a pitch-black sea under charcoal storm clouds that blot out the sun, a single tiny ember of light trembling before Zeus's thunderbolt.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Heavy charcoal storm clouds gather silently above the lone wooden ship on the dark still ocean as a faint golden glow pulses in the sky. Ultra-slow push-in at 24fps.",
    ),
    44: (
        "Cataclysmic 16:9 chiaroscuro frame: a blinding bolt of incandescent white-and-gold lightning from Zeus striking the central mast of the last warship, splitting the vessel in a halo of golden sparks over the black waves.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Brilliant beams of incandescent gold and white light from the storm sky illuminate the wooden sailing ship amidst rolling dark ocean waves and glowing sparks. 24fps.",
    ),
    45: (
        "Solitary 16:9 chiaroscuro wide frame: Odysseus alone in the vast obsidian ocean, clinging with both hands to a single broken wooden keel and mast timber amidst rolling dark waves under a starless night sky.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Dark ocean swells rise and fall slowly around the lone castaway clinging to the wooden ship timber under dim amber starlight. Slow pull-back at 24fps.",
    ),
    46: (
        "Poignant 16:9 chiaroscuro dawn frame on the shore of Ithaca: Odysseus, aged twenty years and draped in the tattered grey cloak of a beggar, kneeling on the wet sand and pressing his hands to the soil of his homeland.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Gentle golden dawn surf washes onto the dark sand around the kneeling cloaked traveler on the rocky coast of Ithaca. Slow cinematic push-in at 24fps.",
    ),
    47: (
        "Emotional 16:9 chiaroscuro split-depth frame at the stone threshold of the palace of Ithaca: in the foreground, the ancient faithful hound Argos rests his head on beggar-Odysseus's foot; in the background archway, Penelope sits before her tall loom by torchlight.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm amber torchlight flickers through the stone palace archway illuminating Penelope at her loom and the cloaked traveler beside his faithful hound. Slow push-in at 24fps.",
    ),
    48: (
        "Triumphant 16:9 chiaroscuro frame in the great hall of Ithaca: Odysseus casting off his beggar rags, muscles taut in Caravaggio firelight as he effortlessly bends and strings the massive royal bow of horn and bronze.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Bright golden firelight from the hall braziers gleams along the curved royal bow and bronze arrow held by Odysseus. Dramatic low-angle push-in at 24fps.",
    ),
    49: (
        "Solemn 16:9 chiaroscuro frame in the stone throne room of Ithaca: King Odysseus seated once more upon his carved stone throne embracing Penelope in warm bronze firelight, while the empty hall around them lies in deep contemplative shadow.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. Warm golden brazier light illuminates Odysseus and Penelope embracing beside the stone throne as soft embers drift into the high vaulted shadows. Slow pull-back at 24fps.",
    ),
    50: (
        "Final 16:9 chiaroscuro frame returning to O Contador in the pitch-black stone chamber: the last glowing red-orange ember in the bronze tripod brazier fades into ash, sending a single thin thread of golden smoke upward into total darkness.",
        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. In the quiet dark stone chamber, the last red-orange ember in the bronze brazier glows softly as a thin ribbon of golden smoke curls upward into darkness. Slow fade at 24fps.",
    ),
}


def gerar_roteiro_50_planos_1para1() -> Path:
    roteiro_8m_path = Path(r"d:\LUME\storage_local\roteiro\roteiro_ep01_odisseia_8min.json")
    dados_orig = json.loads(roteiro_8m_path.read_text(encoding="utf-8"))
    blocos_orig = dados_orig["blocos"]
    assert len(blocos_orig) == 50, f"Esperados 50 blocos, encontrados {len(blocos_orig)}"

    # Remove o antigo arquivo de 12 planos agrupados se existir
    old_12_path = Path(
        r"d:\LUME\storage_local\episodios\ep01_odisseia_firefly_novo\roteiro\roteiro_12_planos_firefly.json"
    )
    if old_12_path.exists():
        os.remove(old_12_path)

    planos_50 = []
    for b in blocos_orig:
        num = int(b["plano"])
        pid = f"p{num:02d}"
        prompt_sf_body, prompt_vid = PROMPTS_50_BLOCOS[num]
        jan = b["janela_s"]
        dur_s = round(float(jan[1]) - float(jan[0]), 3)

        plano_entry = {
            "id": pid,
            "ordem": num,
            "bloco_roteiro": num,
            "ato_id": b["ato_id"],
            "ato_titulo": b["ato_titulo"],
            "canto_verso": b["canto_verso"],
            "contador_perdas": b["contador_perdas"],
            "paleta_modo": b.get("paleta_modo", "brasa"),
            "cena_tipo": b["cena_tipo"],
            "janela_s": jan,
            "duracao_s": dur_s,
            "texto_narracao": b["texto_narracao"],
            "palavras": b["palavras"],
            "fala_inicio_s": b.get("fala_inicio_s"),
            "fala_fim_s": b.get("fala_fim_s"),
            "prompt_start_frame": STYLE_PREFIX + prompt_sf_body,
            "prompt_video": prompt_vid,
        }
        if "silencio_dramatico_s" in b:
            plano_entry["silencio_dramatico_s"] = b["silencio_dramatico_s"]
        planos_50.append(plano_entry)

    # Valida paridade estrita 1:1 no contrato raiz
    validar_paridade_1_para_1_blocos_planos(blocos_orig, planos_50, episodio_id="ep01_odisseia_firefly_1para1")

    payload = {
        "episodio_id": "ep01_odisseia_firefly_1para1",
        "titulo": dados_orig["titulo"],
        "thumbnail_words": dados_orig["thumbnail_words"],
        "duracao_total_s": dados_orig["duracao_total_s"],
        "duracao_formatada": dados_orig["duracao_formatada"],
        "total_blocos": 50,
        "total_planos": 50,
        "paridade_1_para_1": True,
        "silencio_dramatico_s": dados_orig["silencio_dramatico_s"],
        "blocos": blocos_orig,
        "planos": planos_50,
        "planos_firefly": planos_50,
    }

    out_main = Path(r"d:\LUME\storage_local\roteiro\roteiro_50_planos_firefly_1para1.json")
    out_main.parent.mkdir(parents=True, exist_ok=True)
    out_main.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    out_ep = Path(
        r"d:\LUME\storage_local\episodios\ep01_odisseia_firefly_novo\roteiro\roteiro_50_planos_firefly_1para1.json"
    )
    out_ep.parent.mkdir(parents=True, exist_ok=True)
    out_ep.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[SUCESSO SUBETAPA 3] {len(planos_50)} planos 1:1 gerados em: {out_main}")
    return out_main


if __name__ == "__main__":
    gerar_roteiro_50_planos_1para1()
