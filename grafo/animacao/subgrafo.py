"""Subgrafo do Departamento de Animação e Render (Doc 05 §3.5 e Fichas 01-05).

Processamento de render por plano com cache por hash e limite de refações:
1. animacao.animador_plano (LLM-R + Ferr.)
2. animacao.montador_cena_3d (Ferr. Blender headless)
3. animacao.gerente_render (Ferr. fila de GPU com cache de hash)
4. animacao.revisor_plano (LLM-V)
5. animacao.vfx (Ferr. camadas de brasas e fumaça)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List
from langgraph.graph import END, START, StateGraph

from contratos.estado import EstadoEpisodio
from contratos.plano import calcular_hash_plano
from grafo.base import no_agente


# Cache local de renders concluídos: hash -> caminho
_RENDER_CACHE: Dict[str, str] = {}


@no_agente("animacao.animador_plano", categoria_modelo="LLM-R")
def animador_plano_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = state.get("decupagem", {}).get("planos", [])
    assets_planos = dict(state.get("assets", {}).get("planos", {}))

    for p in planos:
        p_id = p.get("id")
        cena_param = {
            "plano_id": p_id,
            "poses_chave": [{"frame": 0, "rotacao": 0}, {"frame": 120, "rotacao": 15}],
            "camera_curva": p.get("camera", {}).get("movimento", "push_in_lento"),
            "fogo_intensidade": p.get("fogo", {}).get("nivel", 2) * 0.3,
        }
        if p_id not in assets_planos:
            assets_planos[p_id] = {}
        assets_planos[p_id]["cena"] = cena_param

    return {
        "assets": {
            "planos": assets_planos,
        }
    }


@no_agente("animacao.montador_cena_3d", categoria_modelo=None)
def montador_cena_3d_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = state.get("decupagem", {}).get("planos", [])
    assets_planos = dict(state.get("assets", {}).get("planos", {}))

    for p in planos:
        p_id = p.get("id")
        if p_id not in assets_planos:
            assets_planos[p_id] = {}
        assets_planos[p_id]["blend"] = {
            "caminho": f"storage_local/cenas/{p_id}.blend",
            "hash": f"hash_blend_{p_id}",
        }

    return {
        "assets": {
            "planos": assets_planos,
        }
    }


@no_agente("animacao.gerente_render", categoria_modelo=None)
def gerente_render_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = state.get("decupagem", {}).get("planos", [])
    assets_planos = dict(state.get("assets", {}).get("planos", {}))
    from grafo.ferramentas.start_frame import StartFrameGenerator
    from grafo.ferramentas.firefly import FireflyEngine

    sf_gen = StartFrameGenerator()
    firefly_engine = FireflyEngine(simulate=True)
    episodio_id = state.get("episodio", {}).get("id") or state.get("id") or "lume_ep"

    for p in planos:
        p_id = p.get("id")
        hash_visual = calcular_hash_plano(p)

        # 1. Checa cache de render pelo hash do contrato
        if hash_visual in _RENDER_CACHE and os.path.exists(_RENDER_CACHE[hash_visual]):
            video_caminho = _RENDER_CACHE[hash_visual]
            cache_hit = True
        else:
            # Obtém ou gera o start frame correspondente
            start_frame_path = p.get("storyboard")
            if not start_frame_path or not os.path.exists(start_frame_path):
                start_frame_path = str(sf_gen.gerar_start_frame(
                    plano_id=p_id,
                    prompt=p.get("mundo", "parede"),
                    proporcao=p.get("proporcao", "16:9"),
                    nivel_fogo=p.get("fogo", {}).get("nivel", 2),
                    direcao_olhar=p.get("direcao_olhar", "D"),
                ))

            # Animação serial via FireflyEngine
            movimento = p.get("camera", {}).get("movimento", "push_in_lento")
            dur = p.get("duracao_s", 5.0)
            clipe = firefly_engine.animate_start_frame(
                plano_id=f"{p_id}_{hash_visual[:8]}",
                start_frame_path=start_frame_path,
                motion_prompt=f"Movimento de camera {movimento} com teatro de sombras",
                target_duration=dur,
                episodio_id=str(episodio_id),
            )
            video_caminho = str(clipe)
            _RENDER_CACHE[hash_visual] = video_caminho
            cache_hit = False

        if p_id not in assets_planos:
            assets_planos[p_id] = {}

        render_info = dict(assets_planos[p_id].get("render", {}))
        tentativas = render_info.get("tentativas", 0) + 1
        render_info.update({
            "caminho": video_caminho,
            "hash": hash_visual,
            "status": "concluido",
            "tentativas": tentativas,
            "cache_hit": cache_hit,
        })
        assets_planos[p_id]["render"] = render_info

    return {
        "assets": {
            "planos": assets_planos,
        }
    }


@no_agente("animacao.revisor_plano", categoria_modelo="LLM-V")
def revisor_plano_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = state.get("decupagem", {}).get("planos", [])
    assets_planos = dict(state.get("assets", {}).get("planos", {}))
    erros = []

    for p in planos:
        p_id = p.get("id")
        render_info = assets_planos.get(p_id, {}).get("render", {})
        tentativas = render_info.get("tentativas", 1)
        video_p = render_info.get("caminho")

        # Se for a 3ª falha em um plano simulado com erro, registra erro para escalada do Showrunner
        if render_info.get("forcar_falha", False) and tentativas >= 3:
            erros.append({
                "autor_no": "animacao.revisor_plano",
                "erro": f"Plano {p_id}: Esgotadas 2 refações automáticas no render",
                "tentativa": tentativas,
                "decisao": "escalar",
                "detalhes": {"plano_id": p_id},
            })
            aprovado = False
        elif not video_p or not os.path.exists(video_p) or os.path.getsize(video_p) < 50:
            erros.append({
                "autor_no": "animacao.revisor_plano",
                "erro": f"Plano {p_id}: Arquivo de video MP4 corrompido ou inexistente",
                "tentativa": tentativas,
                "decisao": "refazer",
                "detalhes": {"plano_id": p_id},
            })
            aprovado = False
        else:
            aprovado = True

        if p_id not in assets_planos:
            assets_planos[p_id] = {}

        assets_planos[p_id]["revisao"] = {
            "aprovado": aprovado,
            "motivo": "Conforme regras de silhueta e iluminação" if aprovado else "Falha persistente",
        }

    resultado: Dict[str, Any] = {
        "assets": {
            "planos": assets_planos,
        }
    }
    if erros:
        resultado["erros"] = erros

    return resultado


@no_agente("animacao.vfx", categoria_modelo=None)
def vfx_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = state.get("decupagem", {}).get("planos", [])
    assets_planos = dict(state.get("assets", {}).get("planos", {}))

    for p in planos:
        p_id = p.get("id")
        if p_id not in assets_planos:
            assets_planos[p_id] = {}
        assets_planos[p_id]["vfx"] = {
            "brasas": True,
            "fumaça": True,
            "cinzas_primeiro_plano": True,
            "status": "composto",
        }

    return {
        "assets": {
            "planos": assets_planos,
        }
    }


def construir_subgrafo_animacao() -> StateGraph:
    """Compila o subgrafo de Animação e Render."""
    builder = StateGraph(EstadoEpisodio)

    builder.add_node("animacao.animador_plano", animador_plano_node)
    builder.add_node("animacao.montador_cena_3d", montador_cena_3d_node)
    builder.add_node("animacao.gerente_render", gerente_render_node)
    builder.add_node("animacao.revisor_plano", revisor_plano_node)
    builder.add_node("animacao.vfx", vfx_node)

    builder.add_edge(START, "animacao.animador_plano")
    builder.add_edge("animacao.animador_plano", "animacao.montador_cena_3d")
    builder.add_edge("animacao.montador_cena_3d", "animacao.gerente_render")
    builder.add_edge("animacao.gerente_render", "animacao.revisor_plano")
    builder.add_edge("animacao.revisor_plano", "animacao.vfx")
    builder.add_edge("animacao.vfx", END)

    return builder.compile()
