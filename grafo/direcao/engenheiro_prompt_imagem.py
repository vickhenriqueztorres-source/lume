"""Agente Especialista: Engenheiro de Prompt de Imagem (Doc 03, Doc 04 e Doc 05).

Responsável por sintetizar decupagem, roteiro, semiótica e color script em prompts
cinematográficos ultra-consistentes, garantindo estética de cinema (teatro de sombras,
chiaroscuro, braseiro quente e silhuetas nítidas) entre todos os planos do episódio.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List
from contratos.estado import EstadoEpisodio
from grafo.base import no_agente

LOGGER = logging.getLogger(__name__)


def construir_prompt_cinematografico(plano: Dict[str, Any], color_script: Dict[str, Any] | None = None) -> str:
    """Gera prompt cinematográfico em inglês com vocabulário de direção de fotografia LUME."""
    mundo = plano.get("mundo", "parede")
    tipo_plano = plano.get("tipo_plano", "medio")
    proporcao = plano.get("proporcao", "2.39")
    parede = plano.get("parede", "pedra_calcario")
    fogo = plano.get("fogo", {})
    nivel_fogo = fogo.get("nivel", 2)
    camera = plano.get("camera", {})
    lente = camera.get("lente_mm", 35)
    movimento = camera.get("movimento", "push_in_lento")
    marionetes = plano.get("marionetes", [])

    # Paleta canônica LUME
    paleta_tokens = (
        "color palette strictly charcoal black silhouette #16110D, incandescent brazier ember orange #E85D04, "
        "divine soft amber light #FDF0D5, warm slate cave stone background #2B2621"
    )

    if mundo == "contador":
        cena_desc = (
            f"Ancient Greek mythical storyteller illuminated by low flickering hearth fire, close cinematic shot, "
            f"{lente}mm portrait lens, deep shadows, atmospheric chiaroscuro, warm embers in the air, 16:9 frame"
        )
    else:
        # Mundo da parede: teatro de sombras arcaico
        char_desc_list = []
        for m in marionetes:
            m_id = m.get("id", "figura")
            direcao = m.get("direcao", "dir")
            dir_str = "facing right towards home" if direcao == "dir" else "facing left in towering confrontation"
            if "odisseu" in m_id:
                char_desc_list.append(f"heroic Greek warrior silhouette Odysseus with pointed helm {dir_str}")
            elif "polifemo" in m_id:
                char_desc_list.append(f"colossal Cyclops monster silhouette with central piercing light aperture {dir_str}")
            else:
                char_desc_list.append(f"shadow figure {m_id} {dir_str}")

        chars_str = ", ".join(char_desc_list) if char_desc_list else "mythic Greek shadow puppets"

        cena_desc = (
            f"Cinematic ancient Greek shadow puppet play on rough {parede} wall. "
            f"Figures: {chars_str}. Shot type: {tipo_plano}, framing: {proporcao}:1 anamorphic aspect ratio. "
            f"Lit from below by flickering brazier fire level {nivel_fogo}/5, rising sparks and delicate embers. "
            f"Shot on {lente}mm anamorphic cinema lens, {movimento} camera motion, atmospheric theatrical smoke haze"
        )

    # Prompt final unificado com diretrizes cinematográficas
    prompt_completo = (
        f"Masterpiece cinematic frame, {cena_desc}, {paleta_tokens}, "
        f"high contrast chiaroscuro, sharp silhouette outlines, organic rock texture, 35mm film grain, "
        f"dramatic theatrical lighting, clean composition, 8k resolution, photorealistic shadow textures"
    )

    # Sanitização: remove caracteres nulos ou sequências inválidas
    prompt_sanitizado = prompt_completo.replace("\x00", "").strip()
    return prompt_sanitizado[:1500]


@no_agente("direcao.engenheiro_prompt_imagem", categoria_modelo="LLM-R")
def engenheiro_prompt_imagem_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Nó do Agente Engenheiro de Prompt de Imagem."""
    planos = list(state.get("decupagem", {}).get("planos", []))
    color_script = state.get("color_script")

    for p in planos:
        p["prompt_imagem"] = construir_prompt_cinematografico(p, color_script=color_script)

    return {
        "decupagem": {
            "planos": planos,
        }
    }
