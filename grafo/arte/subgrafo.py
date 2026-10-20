"""Subgrafo do Departamento de Arte e Marionetes (Doc 05 §3.4 e Fichas 01-05).

Processamento de novos ativos e marionetes:
1. arte.designer_silhuetas (IMG + LLM-V)
2. arte.vetorizador (Ferr. potrace)
3. arte.rigger (LLM-V + Ferr.)
4. arte.cenografo (IMG + Ferr.)
5. arte.bibliotecario (Ferr. + Store)
"""

from __future__ import annotations

from typing import Any, Dict
from langgraph.graph import END, START, StateGraph

from contratos.estado import EstadoEpisodio
from grafo.base import no_agente
from grafo.checkpointer import obter_store


@no_agente("arte.designer_silhuetas", categoria_modelo="IMG")
def designer_silhuetas_node(state: EstadoEpisodio) -> Dict[str, Any]:
    marionetes_existentes = state.get("assets", {}).get("marionetes", {})
    marionetes_atualizadas = dict(marionetes_existentes)
    novas = state.get("elenco", {}).get("novas_a_criar", [])

    for item in novas:
        m_id = item.get("id", "marionete_nova")
        marionetes_atualizadas[m_id] = {
            "id": m_id,
            "png_caminho": f"storage_local/marionetes/{m_id}.png",
            "png_hash": f"hash_png_{m_id}",
            "estilo": "figura_negra",
            "furos_luz": item.get("furos_luz", []),
            "status": "desenhada",
        }

    return {
        "assets": {
            "marionetes": marionetes_atualizadas,
        }
    }


@no_agente("arte.vetorizador", categoria_modelo=None)
def vetorizador_node(state: EstadoEpisodio) -> Dict[str, Any]:
    marionetes = dict(state.get("assets", {}).get("marionetes", {}))
    for m_id, dados in marionetes.items():
        dados["svg_caminho"] = f"storage_local/marionetes/{m_id}.svg"
        dados["svg_hash"] = f"hash_svg_{m_id}"
        dados["preto_absoluto"] = True
        dados["status"] = "vetorizada"

    return {
        "assets": {
            "marionetes": marionetes,
        }
    }


@no_agente("arte.rigger", categoria_modelo="LLM-V")
def rigger_node(state: EstadoEpisodio) -> Dict[str, Any]:
    marionetes = dict(state.get("assets", {}).get("marionetes", {}))
    for m_id, dados in marionetes.items():
        dados["rig_caminho"] = f"storage_local/marionetes/{m_id}_rig.json"
        dados["pivos"] = [
            {"junta": "ombro", "x": 0.5, "y": 0.7},
            {"junta": "cotovelo", "x": 0.6, "y": 0.5},
            {"junta": "quadril", "x": 0.5, "y": 0.4},
        ]
        dados["status"] = "riggada"

    return {
        "assets": {
            "marionetes": marionetes,
        }
    }


@no_agente("arte.cenografo", categoria_modelo="IMG")
def cenografo_node(state: EstadoEpisodio) -> Dict[str, Any]:
    cenarios = {
        "caverna_umida": {
            "id": "caverna_umida",
            "textura_caminho": "storage_local/cenarios/caverna_umida.png",
            "textura_hash": "hash_tex_caverna_umida",
            "tipo": "pedra_calcario",
        },
        "ruina_calcario": {
            "id": "ruina_calcario",
            "textura_caminho": "storage_local/cenarios/ruina_calcario.png",
            "textura_hash": "hash_tex_ruina_calcario",
            "tipo": "marmore_penumbra",
        },
    }
    return {
        "assets": {
            "cenarios": cenarios,
        }
    }


@no_agente("arte.bibliotecario", categoria_modelo=None)
def bibliotecario_node(state: EstadoEpisodio) -> Dict[str, Any]:
    store = obter_store()
    marionetes = state.get("assets", {}).get("marionetes", {})

    indice = []
    for m_id, dados in marionetes.items():
        registro = {
            "id": m_id,
            "tipo": "marionete",
            "svg_caminho": dados.get("svg_caminho"),
            "rig_caminho": dados.get("rig_caminho"),
            "tags": ["grego", "homero", "odisseia"],
        }
        indice.append(registro)
        # Salva na Store persistente de assets para reaproveitamento entre episódios
        try:
            store.put(("biblioteca", "marionetes"), m_id, registro)
        except Exception:
            pass

    return {
        "assets": {
            "indice": indice,
        }
    }


def construir_subgrafo_arte() -> StateGraph:
    """Compila o subgrafo de Arte."""
    builder = StateGraph(EstadoEpisodio)

    builder.add_node("arte.designer_silhuetas", designer_silhuetas_node)
    builder.add_node("arte.vetorizador", vetorizador_node)
    builder.add_node("arte.rigger", rigger_node)
    builder.add_node("arte.cenografo", cenografo_node)
    builder.add_node("arte.bibliotecario", bibliotecario_node)

    builder.add_edge(START, "arte.designer_silhuetas")
    builder.add_edge("arte.designer_silhuetas", "arte.vetorizador")
    builder.add_edge("arte.vetorizador", "arte.rigger")
    builder.add_edge("arte.rigger", "arte.cenografo")
    builder.add_edge("arte.cenografo", "arte.bibliotecario")
    builder.add_edge("arte.bibliotecario", END)

    return builder.compile()
