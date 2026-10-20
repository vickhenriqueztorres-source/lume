"""Subgrafo do Departamento de Montagem e Finalização (Doc 05 §3.7 e Fichas 01-04).

Alinhamento da timeline, grafismos, master 4K e legendas:
1. montagem.editor (LLM-R + Ferr. OTIO)
2. montagem.grafismo (Ferr. motion templates)
3. montagem.finalizador (Ferr. ffmpeg master)
4. montagem.legendador (ASR + LLM-R)
"""

from __future__ import annotations

from typing import Any, Dict
from langgraph.graph import END, START, StateGraph

from contratos.estado import EstadoEpisodio
from grafo.base import no_agente


@no_agente("montagem.editor", categoria_modelo="LLM-R")
def editor_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = state.get("decupagem", {}).get("planos", [])
    duracao_total = sum(p.get("duracao_s", 5.0) for p in planos)

    timeline = {
        "otio_json": '{"schema": "OpenTimelineIO", "version": 1, "tracks": ["video", "narracao", "sfx", "musica"]}',
        "versao_corte": 1,
        "total_cortes": len(planos),
        "duracao_total_s": duracao_total,
    }
    return {
        "timeline": timeline,
    }


@no_agente("montagem.grafismo", categoria_modelo=None)
def grafismo_node(state: EstadoEpisodio) -> Dict[str, Any]:
    camadas_motion = [
        {"tipo": "cartela_capitulo", "texto": "I. O Monstro na Penumbra", "timecode_in": "00:00:15"},
        {"tipo": "lower_third_fonte", "texto": "Homero · Odisseia IX, 216", "timecode_in": "00:00:45"},
        {"tipo": "watermark_lume", "posicao": "canto_inferior_esquerdo", "opacidade": 0.4},
    ]
    return {
        "timeline": {
            "camadas_motion": camadas_motion,
        }
    }


@no_agente("montagem.finalizador", categoria_modelo=None)
def finalizador_node(state: EstadoEpisodio) -> Dict[str, Any]:
    arquivo_master = {
        "caminho": "storage_local/master/ep01_master_4k.mp4",
        "hash": "hash_master_4k_ep01",
        "resolucao": "3840x2160",
        "fps": 24,
        "codec": "ProRes_422_HQ_ou_H265",
        "duracao_s": state.get("timeline", {}).get("duracao_total_s", 1440.0),
    }
    capitulos = [
        {"timecode": "00:00", "titulo": "A Fogueira e o Cíclope"},
        {"timecode": "06:00", "titulo": "O Vinho de Ísmaro"},
        {"timecode": "13:00", "titulo": "Ninguém na Caverna"},
        {"timecode": "19:00", "titulo": "A Fuga e a Maldição"},
    ]
    return {
        "master": {
            "arquivo": arquivo_master,
            "capitulos": capitulos,
        }
    }


@no_agente("montagem.legendador", categoria_modelo="LLM-R")
def legendador_node(state: EstadoEpisodio) -> Dict[str, Any]:
    srt_pt = (
        "1\n00:00:01,000 --> 00:00:05,000\nO fogo ainda conta as mesmas histórias.\n\n"
        "2\n00:00:05,500 --> 00:00:10,000\nNa caverna escura, o gigante fecha a rocha.\n"
    )
    return {
        "master": {
            "legendas": {
                "pt-BR": srt_pt,
            }
        }
    }


def construir_subgrafo_montagem() -> StateGraph:
    """Compila o subgrafo de Montagem."""
    builder = StateGraph(EstadoEpisodio)

    builder.add_node("montagem.editor", editor_node)
    builder.add_node("montagem.grafismo", grafismo_node)
    builder.add_node("montagem.finalizador", finalizador_node)
    builder.add_node("montagem.legendador", legendador_node)

    builder.add_edge(START, "montagem.editor")
    builder.add_edge("montagem.editor", "montagem.grafismo")
    builder.add_edge("montagem.grafismo", "montagem.finalizador")
    builder.add_edge("montagem.finalizador", "montagem.legendador")
    builder.add_edge("montagem.legendador", END)

    return builder.compile()
