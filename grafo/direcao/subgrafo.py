"""Subgrafo do Departamento de Direção (Doc 05 §3.3 e Fichas 01-05).

Agentes:
1. direcao.diretor_decupagem (LLM-R)
2. direcao.diretor_fotografia (LLM-R)
3. direcao.supervisor_direcao_tela (LLM-R regras)
4. direcao.diretor_arte (LLM-R + Store)
5. direcao.storyboarder (IMG + Ferr.)
"""

from __future__ import annotations

from typing import Any, Dict, List
from langgraph.graph import END, START, StateGraph

from contratos.estado import EstadoEpisodio
from contratos.plano import Plano
from grafo.base import no_agente


@no_agente("direcao.diretor_decupagem", categoria_modelo="LLM-R")
def diretor_decupagem_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = [
        Plano(
            id="ep01_c01_p01",
            bloco_roteiro=1,
            mundo="contador",
            tipo_plano="contador",
            duracao_s=4.0,
            proporcao="16:9",
            camera={"movimento": "push_in_lento", "lente_mm": 85},
            fogo={"nivel": 2, "curva": "estavel", "tremulacao_hz": 1.0},
        ).model_dump(),
        Plano(
            id="ep01_c01_p02",
            bloco_roteiro=1,
            mundo="parede",
            tipo_plano="escala",
            duracao_s=6.0,
            proporcao="2.39",
            marionetes=[
                {"id": "polifemo_v1", "distancia_fogo": 0.2, "direcao": "esq"},
                {"id": "odisseu_v1", "distancia_fogo": 0.8, "direcao": "dir"},
            ],
            camera={"movimento": "tilt_up", "lente_mm": 35},
            fogo={"nivel": 3, "curva": "subida", "tremulacao_hz": 2.0},
            parede="caverna_umida",
        ).model_dump(),
        Plano(
            id="ep01_c01_p03",
            bloco_roteiro=2,
            mundo="parede",
            tipo_plano="close",
            duracao_s=4.5,
            proporcao="2.39",
            marionetes=[
                {"id": "odisseu_v1", "distancia_fogo": 0.7, "direcao": "dir"},
            ],
            camera={"movimento": "push_in_lento", "lente_mm": 50},
            fogo={"nivel": 3, "curva": "estavel", "tremulacao_hz": 2.0},
            parede="caverna_umida",
        ).model_dump(),
        Plano(
            id="ep01_c01_p04",
            bloco_roteiro=3,
            mundo="parede",
            tipo_plano="medio",
            duracao_s=5.0,
            proporcao="2.39",
            marionetes=[
                {"id": "odisseu_v1", "distancia_fogo": 0.6, "direcao": "dir"},
                {"id": "polifemo_v1", "distancia_fogo": 0.3, "direcao": "esq"},
            ],
            camera={"movimento": "dolly_lateral", "lente_mm": 35},
            fogo={"nivel": 4, "curva": "pico", "tremulacao_hz": 4.0},
            parede="caverna_umida",
        ).model_dump(),
        Plano(
            id="ep01_c01_p05",
            bloco_roteiro=3,
            mundo="parede",
            tipo_plano="insert",
            duracao_s=3.5,
            proporcao="2.39",
            camera={"movimento": "push_in_lento", "lente_mm": 50},
            fogo={"nivel": 4, "curva": "estavel", "tremulacao_hz": 3.0},
            parede="caverna_umida",
            sfx=["fogo_crepitando", "rocha_arrastando"],
        ).model_dump(),
    ]
    return {
        "decupagem": {
            "planos": planos,
        }
    }


@no_agente("direcao.diretor_fotografia", categoria_modelo="LLM-R")
def diretor_fotografia_node(state: EstadoEpisodio) -> Dict[str, Any]:
    color_script = {
        "cenas": [
            {
                "cena_id": "c01_abertura",
                "nivel_fogo": 2,
                "temperatura_k": 2200,
                "proporcao": "16:9",
                "textura_parede": "ruina_calcario",
            },
            {
                "cena_id": "c02_caverna_polifemo",
                "nivel_fogo": 4,
                "temperatura_k": 3000,
                "proporcao": "2.39",
                "textura_parede": "caverna_umida",
            },
        ],
        "geral": {"paleta_base": ["#16110D", "#3A2C22", "#F1E6CF", "#E07A2E"], "teto_brasa_pct": 5.0},
    }
    return {
        "color_script": color_script,
    }


@no_agente("direcao.supervisor_direcao_tela", categoria_modelo="LLM-R")
def supervisor_direcao_tela_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = state.get("decupagem", {}).get("planos", [])
    correcoes: List[Dict[str, Any]] = []

    # Valida regra: Odisseu (herói rumo a Ítaca) deve olhar para a direita (dir)
    for p in planos:
        for m in p.get("marionetes", []):
            if m.get("id") == "odisseu_v1" and m.get("direcao") != "dir":
                correcoes.append({
                    "plano_id": p.get("id"),
                    "marionete_id": "odisseu_v1",
                    "direcao_anterior": m.get("direcao"),
                    "direcao_corrigida": "dir",
                    "motivo": "Doc 04 §4: Odisseu rumo a Ítaca deve apontar para a direita",
                })
                m["direcao"] = "dir"

    return {
        "decupagem": {
            "correcoes_direcao": correcoes,
            "planos": planos,
        }
    }


@no_agente("direcao.diretor_arte", categoria_modelo="LLM-R")
def diretor_arte_node(state: EstadoEpisodio) -> Dict[str, Any]:
    elenco = {
        "marionetes_usadas": ["odisseu_v1", "polifemo_v1"],
        "novas_a_criar": [
            {
                "id": "polifemo_v1",
                "nome": "Polifemo",
                "estilo": "figura_negra",
                "furos_luz": ["olho_central"],
                "proporcao_escala": "gigante",
            }
        ],
        "reaproveitadas": ["odisseu_v1"],
    }
    return {
        "elenco": elenco,
    }


@no_agente("direcao.storyboarder", categoria_modelo="IMG")
def storyboarder_node(state: EstadoEpisodio) -> Dict[str, Any]:
    animatic = {
        "caminho": "storage_local/animatic/ep01_animatic.mp4",
        "hash": "hash_animatic_ep01_placeholder",
        "resolucao": "1280x720",
        "duracao_total_s": 23.0,
    }
    planos = state.get("decupagem", {}).get("planos", [])
    for p in planos:
        p["storyboard"] = f"storage_local/storyboard/{p['id']}.png"

    return {
        "decupagem": {
            "animatic": animatic,
            "planos": planos,
        }
    }


def construir_subgrafo_direcao() -> StateGraph:
    """Compila o subgrafo de Direção."""
    builder = StateGraph(EstadoEpisodio)

    builder.add_node("direcao.diretor_decupagem", diretor_decupagem_node)
    builder.add_node("direcao.diretor_fotografia", diretor_fotografia_node)
    builder.add_node("direcao.supervisor_direcao_tela", supervisor_direcao_tela_node)
    builder.add_node("direcao.diretor_arte", diretor_arte_node)
    builder.add_node("direcao.storyboarder", storyboarder_node)

    builder.add_edge(START, "direcao.diretor_decupagem")
    builder.add_edge("direcao.diretor_decupagem", "direcao.diretor_fotografia")
    builder.add_edge("direcao.diretor_fotografia", "direcao.supervisor_direcao_tela")
    builder.add_edge("direcao.supervisor_direcao_tela", "direcao.diretor_arte")
    builder.add_edge("direcao.diretor_arte", "direcao.storyboarder")
    builder.add_edge("direcao.storyboarder", END)

    return builder.compile()
