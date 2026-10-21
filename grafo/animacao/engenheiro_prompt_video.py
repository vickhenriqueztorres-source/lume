"""Agente Especialista: Engenheiro de Prompt de Vídeo (Doc 03, Doc 04, Doc 05 §3.5 e Doc 08).

Converte planos do Contador, de VFX e de inserts em especificações cinemáticas determinísticas
para motores de IA de vídeo (Kling / Firefly), operando exclusivamente sobre elementos visuais
aprovados (keyframes / assets 3D), preservando a identidade visual LUME.

Regra inegociável de escopo (Doc 08 §3):
Planos de parede (sombras, marionetes, mapa) são gerados em Blender headless;
este agente não gera prompts de IA para a parede (retorna aplicavel: False).
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import unicodedata
import yaml

from contratos.estado import EstadoEpisodio
from grafo.base import no_agente

LOGGER = logging.getLogger(__name__)

BIBLIA_VERSAO = "biblia_contador_v1"
PROMPT_VERSAO = "1.0.0"
AUTOR_NO = "animacao.engenheiro_prompt_video"

# 4.3 Bíblia do Contador (texto fixo, versionado)
BIBLIA_CONTADOR_V1 = (
    "A hooded storyteller beside a bronze brazier, seen in profile. "
    "A deep, heavy wool hood in dark charcoal-brown is pulled far forward; inside the hood "
    "there is only darkness, and the face is never visible at any moment. "
    "Only two weathered hands are visible, held near the flames. "
    "The brazier is the only light source: warm firelight from below and in front. "
    "Everything outside its glow falls into near-black. Behind him, a rough limestone wall, "
    "mostly in deep shadow."
)

NEGATIVO_CONTADOR_V1 = (
    "face, visible eyes, nose, mouth, lips moving, beard, facial skin, portrait, looking at camera, "
    "musical instrument, lyre, harp, string instrument, lantern, oil lamp, candle, torch, window, "
    "daylight, second light source, rim light from behind, fireplace, chimney, stacked logs, "
    "campfire on the floor, modern objects, text, logo, glowing particles in a regular pattern, "
    "bokeh orbs, lens flare, digital glow, morphing, warping hands, extra fingers, cartoon, anime, 3D render look"
)

# Frases afirmativas injetadas quando o adaptador NÃO aceita negativo (Doc 08 §4.2 e §9 T12)
# Rigorosamente afirmativas, sem negações ou construções com 'no X'
RESTRICOES_AFIRMATIVAS_CONTADOR = (
    "The hood fully conceals the face, head, and eyes in deep shadow without revealing facial features. "
    "The bronze brazier remains the solitary illumination source throughout. "
    "The hands remain completely empty near the flames."
)

# 4.4 Bíblia de VFX (texto fixo, versionado)
BIBLIA_VFX_V1 = (
    "Isolated practical element on a pure black background, for compositing. "
    "No people, no objects, no environment. Real physical behavior, filmed look."
)

NEGATIVO_VFX_V1 = (
    "people, figure, face, hands, wall, floor, environment, text, logo, "
    "regular particle pattern, digital glow, lens flare"
)

CAMADA_ATMOSFERA_PADRAO = (
    "A few embers rise irregularly and drift with the heat; thin smoke curls upward."
)

# 4.5 Tabelas de Tradução Determinística
TABELA_FOGO_NIVEL: Dict[int, str] = {
    1: "only glowing embers, almost no flame, a very slow breathing glow, deep red-orange; the scene is almost entirely dark",
    2: "low, steady flames with a gentle, slow flicker; soft warm amber light",
    3: "lively medium flames with a moderate flicker; the light visibly dances on the wall",
    4: "tall roaring flames with a strong, irregular flicker and sudden flares; hard moving shadows",
    5: "the fire flares into a near-white blinding burst that floods the frame for an instant",
}

TABELA_FOGO_CURVA: Dict[str, str] = {
    "estavel": "The fire stays at the same strength for the whole shot.",
    "subida": "The fire slowly grows stronger over the shot.",
    "descida": "The fire slowly dies down over the shot.",
    "pico": "One sudden flare midway through the shot, then it settles back.",
}

TABELA_CAMERA_MOVIMENTO: Dict[str, str] = {
    "push_in_lento": "a very slow push-in; the camera drifts forward barely noticeably, about 3% closer over the shot",
    "dolly_lateral_dir": "a slow lateral dolly to the right",
    "dolly_lateral_esq": "a slow lateral dolly to the left",
    "dolly_lateral": "a slow lateral dolly",
    "tilt_up": "a slow tilt up",
    "rack_focus": "focus slowly shifts from the hood in the foreground to the wall behind",
    "tremor": "a brief camera shake lasting under half a second, then still",
    "fixo": "a locked-off, completely still camera",
}

TABELA_LUZ_DEUS: Dict[str, str] = {
    "atena": "cold, pale light falling from above",
    "poseidon": "rippling water caustics projected from below",
    "helio": "harsh midday white light that washes out the warm fire",
    "zeus": "strobing lightning flashes",
}

# 4.6 Ações Permitidas do Contador (Lista Fechada Inegociável)
ACOES_PERMITIDAS: Dict[str, str] = {
    "mao_aproxima_fogo": "his right hand moves toward the flames and stops just above them",
    "mao_afasta_fogo": "his hand pulls back from the flames",
    "mao_no_feixe": "his open hand enters the beam of firelight, casting a large shadow on the wall",
    "joga_po_no_fogo": "he tosses a pinch of dust into the brazier and a burst of sparks rises",
    "capuz_inclina": "the hood tilts down a few degrees",
    "respira": "his shoulders rise and fall with a slow breath",
    "abre_pergaminho": "his hands slowly unroll a scorched parchment",
}

ADVERBIOS_PERMITIDOS: Dict[str, str] = {
    "muito devagar": "very slowly",
    "very slowly": "very slowly",
    "devagar": "slowly",
    "slowly": "slowly",
    "firme": "firmly",
    "firmly": "firmly",
}


def carregar_config_adaptadores() -> Dict[str, Any]:
    """Carrega configuração de adaptadores de vídeo declarados em config/adaptadores_video.yaml."""
    caminho = Path("config/adaptadores_video.yaml")
    if caminho.exists():
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return data.get("adaptadores", {})
        except Exception as e:
            LOGGER.warning("Falha ao carregar config/adaptadores_video.yaml: %s", e)

    # Configuração de fallback resiliente
    return {
        "kling_25_turbo": {
            "modelo_real": "Kling 2.5 Turbo",
            "limite_caracteres": 1000,
            "aceita_negativo": True,
            "aceita_quadro_inicial": True,
            "aceita_quadro_final": False,
            "duracoes_possiveis_s": [5, 10],
            "aceita_controle_camera": False,
        },
        "firefly_video_v1": {
            "modelo_real": "Firefly Video",
            "limite_caracteres": 1200,
            "aceita_negativo": False,
            "aceita_quadro_inicial": True,
            "aceita_quadro_final": False,
            "duracoes_possiveis_s": [5],
            "aceita_controle_camera": True,
        },
        "padrao": "kling_25_turbo",
    }


def obter_config_adaptador(nome_adaptador: Optional[str] = None) -> Dict[str, Any]:
    """Obtém configuração do adaptador ativo."""
    configs = carregar_config_adaptadores()
    nome = nome_adaptador or configs.get("padrao", "kling_25_turbo")
    if nome in configs and isinstance(configs[nome], dict):
        cfg = dict(configs[nome])
        cfg["id"] = nome
        return cfg
    return {
        "id": "kling_25_turbo",
        "modelo_real": "Kling 2.5 Turbo",
        "limite_caracteres": 1000,
        "aceita_negativo": True,
        "aceita_quadro_inicial": True,
        "aceita_quadro_final": False,
        "duracoes_possiveis_s": [5, 10],
    }


def calcular_hash_video_ia(
    prompt: str,
    negativo: Optional[str],
    keyframe_ref: Optional[str],
    biblia_versao: str,
    adaptador: str,
) -> str:
    """Calcula hash determinístico SHA-256 para cache de render de vídeo IA."""
    payload = {
        "prompt": prompt,
        "negativo": negativo or "",
        "keyframe_ref": keyframe_ref or "",
        "biblia_versao": biblia_versao,
        "adaptador": adaptador,
    }
    serializado = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()


def _remover_acentos(texto: str) -> str:
    """Remove marcas diacríticas e acentos para correspondência robusta."""
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def selecionar_acao_contador(intencao_visual: Optional[str]) -> Tuple[str, str]:
    """Seleciona ação da lista fechada permitida do Contador a partir de intencao_visual (Doc 08 §4.6).
    
    Retorna: (action_id, adverbio_en).
    Garante 100% de conformidade com a lista fechada, neutralizando qualquer intenção inválida ou proibida.
    """
    if not intencao_visual or not intencao_visual.strip():
        return "respira", "slowly"

    texto = _remover_acentos(intencao_visual.lower().strip())

    # Detecta advérbio de velocidade
    adverbio_en = "slowly"
    if "muito devagar" in texto or "muito lento" in texto or "very slowly" in texto:
        adverbio_en = "very slowly"
    elif "firme" in texto or "firmly" in texto or "rapido" in texto:
        adverbio_en = "firmly"

    # Mapeamento determinístico estrito para a lista de 7 ações permitidas
    if any(k in texto for k in ["estende a mao", "mao para o fogo", "mao ao fogo", "aproxima a mao", "aponta para o fogo", "revelacao"]):
        return "mao_aproxima_fogo", adverbio_en

    if any(k in texto for k in ["afasta a mao", "recua a mao", "horror", "puxa a mao", "recolhe a mao"]):
        return "mao_afasta_fogo", adverbio_en

    if any(k in texto for k in ["feixe", "mural", "sombra da mao", "mao vira deus", "projeta"]):
        return "mao_no_feixe", adverbio_en

    if any(k in texto for k in ["po", "faisca", "brasa", "joga po", "lanca po", "fagulha"]):
        return "joga_po_no_fogo", adverbio_en if adverbio_en != "slowly" else "firmly"

    if any(k in texto for k in ["capuz", "inclina", "luto", "pesado", "olha para baixo", "abaixa a cabeca", "tristeza", "sorri"]):
        # Note: "sorri" é intenção de direção inválida mapeada para reflexão de capuz sem mostrar o rosto
        return "capuz_inclina", adverbio_en

    if any(k in texto for k in ["pergaminho", "rolo", "selo", "desenrola", "abre"]):
        return "abre_pergaminho", adverbio_en

    # Fallback seguro inegociável
    return "respira", adverbio_en


def construir_prompt_contador(
    plano: Dict[str, Any],
    adaptador_cfg: Dict[str, Any],
) -> Tuple[str, Optional[str], List[Dict[str, Any]]]:
    """Monta deterministicamente o prompt em camadas do Contador (Doc 08 §4.2).
    
    Retorna: (prompt_positivo, negativo_prompt, avisos_qa).
    """
    avisos_qa: List[Dict[str, Any]] = []
    plano_id = plano.get("id", "plano")
    aceita_negativo = adaptador_cfg.get("aceita_negativo", True)
    limite_chars = adaptador_cfg.get("limite_caracteres", 1000)

    # Camada 1: Âncora
    camada_ancora = (
        "Animate the reference image. Keep the hooded figure, costume, framing and lighting exactly as shown."
    )

    # Camada 2: Bíblia do mundo
    if aceita_negativo:
        camada_biblia = BIBLIA_CONTADOR_V1
        negativo_final: Optional[str] = NEGATIVO_CONTADOR_V1
    else:
        # Se o adaptador não aceita negativo, inclui restrições afirmativas na bíblia (sem frases 'no X')
        camada_biblia = f"{BIBLIA_CONTADOR_V1} {RESTRICOES_AFIRMATIVAS_CONTADOR}"
        negativo_final = None

    # Camada 3: Ação (classificada da intencao_visual, nunca de narração)
    intencao = plano.get("intencao_visual")
    action_id, adverbio_en = selecionar_acao_contador(intencao)
    action_desc = ACOES_PERMITIDAS.get(action_id, ACOES_PERMITIDAS["respira"])
    camada_acao = f"Action: {adverbio_en}, {action_desc}."

    # Camada 4: Câmera (movimento + lente + sutil respiração de mão)
    cam = plano.get("camera", {})
    mov_camera = cam.get("movimento", "push_in_lento")
    if mov_camera == "fixo":
        # Doc 04 §3.2 e Doc 08 §4.5: Contador nunca fica parado; troca para push_in_lento
        mov_camera = "push_in_lento"
        avisos_qa.append({
            "plano_id": plano_id,
            "tipo": "camera_fixa_convertida",
            "mensagem": "Plano do Contador com camera fixa convertido para push_in_lento com breathing motion (Doc 04 §3.2)",
        })

    mov_traduzido = TABELA_CAMERA_MOVIMENTO.get(mov_camera, TABELA_CAMERA_MOVIMENTO["push_in_lento"])
    camada_camera = (
        f"Camera: {mov_traduzido}, with a subtle handheld breathing motion. "
        f"Telephoto 100mm look, shallow depth of field, background softly out of focus."
    )

    # Camada 5: Fogo (nível + curva)
    fogo = plano.get("fogo", {})
    nivel_fogo = fogo.get("nivel", 2)
    curva_fogo = fogo.get("curva", "estavel")

    if nivel_fogo != 2:
        # Doc 04 §2.1: Contador fica no nível 2; outro nível gera aviso em QA para o DoP
        avisos_qa.append({
            "plano_id": plano_id,
            "tipo": "fogo_nivel_fora_do_padrao",
            "mensagem": f"Plano do Contador com fogo nivel {nivel_fogo} (padrao e nivel 2, Doc 04 §2.1)",
        })

    fogo_nivel_desc = TABELA_FOGO_NIVEL.get(nivel_fogo, TABELA_FOGO_NIVEL[2])
    fogo_curva_desc = TABELA_FOGO_CURVA.get(curva_fogo, TABELA_FOGO_CURVA["estavel"])
    camada_fogo = f"Fire: {fogo_nivel_desc}. {fogo_curva_desc}"

    # Camada 6: Atmosfera (primeira a ser descartada se exceder limite)
    camada_atmosfera = CAMADA_ATMOSFERA_PADRAO

    # Montagem e controle estrito de tamanho sem cortar sentenças (Doc 08 §4.2)
    camadas_completas = [
        camada_ancora,
        camada_biblia,
        camada_acao,
        camada_camera,
        camada_fogo,
        camada_atmosfera,
    ]
    prompt_completo = "\n".join(camadas_completas)

    if len(prompt_completo) > limite_chars:
        # Descarta camada 6 inteira
        camadas_sem_atmosfera = [
            camada_ancora,
            camada_biblia,
            camada_acao,
            camada_camera,
            camada_fogo,
        ]
        prompt_completo = "\n".join(camadas_sem_atmosfera)

    # As camadas 1 a 4 nunca saem e nunca há corte cego de caracteres no meio da frase
    return prompt_completo, negativo_final, avisos_qa


def construir_prompt_vfx(
    plano: Dict[str, Any],
    adaptador_cfg: Dict[str, Any],
) -> Tuple[str, Optional[str]]:
    """Monta prompt para camadas isoladas de VFX em fundo preto (Doc 08 §4.4)."""
    aceita_negativo = adaptador_cfg.get("aceita_negativo", True)
    luz_deus = plano.get("luz_deus", {})
    tipo_luz = luz_deus.get("tipo", "") if isinstance(luz_deus, dict) else ""

    partes = [BIBLIA_VFX_V1]
    if "atena" in tipo_luz:
        partes.append("Cold, pale light falling from above.")
    elif "poseidon" in tipo_luz:
        partes.append("Rippling water caustics projected from below.")
    elif "helio" in tipo_luz:
        partes.append("Harsh midday white light that washes out the warm fire.")
    elif "zeus" in tipo_luz:
        partes.append("Strobing lightning flashes.")
    else:
        partes.append("A single glowing ember rises slowly from the bottom of the frame, swaying slightly.")

    partes.append("Camera: a locked-off, completely still camera.")
    prompt = " ".join(partes)
    negativo = NEGATIVO_VFX_V1 if aceita_negativo else None
    return prompt, negativo


def revisar_take_video_ia(take_info: Dict[str, Any]) -> Dict[str, Any]:
    """Revisão automática de conformidade contra defeitos de IA de vídeo (Doc 08 §7 e §9 T11)."""
    motivos: List[str] = []

    # 1. Detector de rosto
    if take_info.get("confianca_rosto", 0.0) > 0.5 or take_info.get("rosto_visivel") or take_info.get("rosto_detectado"):
        motivos.append("rosto_visivel")

    # 2. Instrumento musical
    if take_info.get("instrumento") or take_info.get("instrumento_detectado") or take_info.get("lyre_detectada"):
        motivos.append("instrumento")

    # 3. Segunda fonte de luz
    if take_info.get("segunda_fonte_luz") or take_info.get("fontes_luz_detectadas", 1) > 1:
        motivos.append("segunda_fonte_luz")

    # 4. Lareira em vez de braseiro
    if take_info.get("lareira") or take_info.get("tipo_fogo") in ("lareira", "chimney", "fireplace", "fogueira_chao"):
        motivos.append("lareira")

    # 5. Área em Carvão < 33.3%
    area_carvao = take_info.get("area_carvao_pct", 0.5)
    if area_carvao < 0.333 or take_info.get("area_carvao_baixa"):
        motivos.append("area_carvao_baixa")

    # 6. Área em Brasa > 10%
    area_brasa = take_info.get("area_brasa_pct", 0.02)
    if area_brasa > 0.10 or take_info.get("area_brasa_alta"):
        motivos.append("area_brasa_alta")

    aprovado = len(motivos) == 0
    return {
        "aprovado": aprovado,
        "motivos": motivos,
    }


def verificar_aprovacao_contador_v1(state: EstadoEpisodio) -> bool:
    """Verifica se o design/keyframe do Contador foi aprovado (Doc 08 §6)."""
    # 1. Verifica aprovações explícitas de gates
    for a in state.get("aprovacoes", []):
        if a.get("item") in ("contador_v1", "design_contador") and a.get("status") == "aprovado":
            return True

    # 2. Verifica registro na Store de keyframes
    keyframes = state.get("assets", {}).get("keyframes", {})
    if "contador_v1" in keyframes:
        return True

    # 3. Verifica em personagens
    personagens = state.get("assets", {}).get("personagens", {})
    if personagens.get("contador_v1", {}).get("aprovado"):
        return True

    return False


@no_agente("animacao.engenheiro_prompt_video", categoria_modelo="Ferr. + LLM-R")
def engenheiro_prompt_video_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Nó do Engenheiro de Prompt de Vídeo.
    
    Função pura: lê decupagem sem modificá-la e retorna exclusivamente gravações em assets.planos,
    com possíveis avisos em qa e itens em episodio.fila_humana (Doc 08 §8).
    """
    planos = state.get("decupagem", {}).get("planos", [])
    adaptador_id = state.get("config", {}).get("adaptador_video")
    adaptador_cfg = obter_config_adaptador(adaptador_id)

    assets_planos_updates: Dict[str, Any] = {}
    qa_avisos: List[Dict[str, Any]] = []
    fila_humana_itens: List[Dict[str, Any]] = []

    contador_v1_aprovado = verificar_aprovacao_contador_v1(state)

    for p in planos:
        p_id = p.get("id", "plano")
        mundo = p.get("mundo", "parede")
        tipo_plano = p.get("tipo_plano", "medio")
        duracao_s = float(p.get("duracao_s", 5.0))

        # 1. Planos de parede (Doc 08 §3 e T2): Blender headless, não vídeo IA
        if mundo == "parede":
            assets_planos_updates[p_id] = {
                "video_ia": {
                    "aplicavel": False,
                    "motivo": "parede_delegada_ao_blender_headless",
                    "versao": 1,
                    "autor_no": AUTOR_NO,
                }
            }
            continue

        # 2. Planos do Contador (Doc 08 §3, §6 e T8)
        if mundo == "contador" or tipo_plano == "contador":
            if not contador_v1_aprovado:
                fila_humana_itens.append({
                    "tipo": "aprovacao_keyframe",
                    "item": "contador_v1",
                    "plano_id": p_id,
                    "motivo": "Keyframe aprovado contador_v1 ausente para imagem-para-video",
                })
                assets_planos_updates[p_id] = {
                    "video_ia": {
                        "aplicavel": False,
                        "status": "aguardando_aprovacao_keyframe",
                        "motivo": "contador_v1_nao_aprovado",
                        "versao": 1,
                        "autor_no": AUTOR_NO,
                    }
                }
                continue

            # Determina duração suportada pelo adaptador (arredonda para cima)
            duracoes_possiveis = adaptador_cfg.get("duracoes_possiveis_s", [5, 10])
            duracao_pedida = duracoes_possiveis[-1]
            for d in duracoes_possiveis:
                if d >= duracao_s:
                    duracao_pedida = d
                    break

            prompt_pos, prompt_neg, avisos = construir_prompt_contador(p, adaptador_cfg)
            qa_avisos.extend(avisos)

            keyframe_ref = p.get("storyboard") or "contador_v1_perfil_mao"
            hash_video = calcular_hash_video_ia(
                prompt=prompt_pos,
                negativo=prompt_neg,
                keyframe_ref=keyframe_ref,
                biblia_versao=BIBLIA_VERSAO,
                adaptador=adaptador_cfg.get("id", "kling_25_turbo"),
            )

            assets_planos_updates[p_id] = {
                "video_ia": {
                    "aplicavel": True,
                    "adaptador": adaptador_cfg.get("id", "kling_25_turbo"),
                    "prompt": prompt_pos,
                    "negativo": prompt_neg,
                    "keyframe_ref": keyframe_ref,
                    "seed": 42,
                    "biblia_versao": BIBLIA_VERSAO,
                    "prompt_versao": PROMPT_VERSAO,
                    "duracao_pedida_s": duracao_pedida,
                    "hash": hash_video,
                    "versao": 1,
                    "autor_no": AUTOR_NO,
                }
            }
            continue

        # 3. Planos de VFX ou Inserts isolados
        prompt_pos, prompt_neg = construir_prompt_vfx(p, adaptador_cfg)
        hash_video = calcular_hash_video_ia(
            prompt=prompt_pos,
            negativo=prompt_neg,
            keyframe_ref=None,
            biblia_versao="biblia_vfx_v1",
            adaptador=adaptador_cfg.get("id", "kling_25_turbo"),
        )
        assets_planos_updates[p_id] = {
            "video_ia": {
                "aplicavel": True,
                "adaptador": adaptador_cfg.get("id", "kling_25_turbo"),
                "prompt": prompt_pos,
                "negativo": prompt_neg,
                "keyframe_ref": None,
                "seed": 42,
                "biblia_versao": "biblia_vfx_v1",
                "prompt_versao": PROMPT_VERSAO,
                "duracao_pedida_s": int(duracao_s),
                "hash": hash_video,
                "versao": 1,
                "autor_no": AUTOR_NO,
            }
        }

    resultado: Dict[str, Any] = {
        "assets": {
            "planos": assets_planos_updates,
        }
    }
    if qa_avisos:
        resultado["qa"] = qa_avisos
    if fila_humana_itens:
        resultado["episodio"] = {
            "fila_humana": fila_humana_itens,
        }

    return resultado
