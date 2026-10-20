"""Subgrafo do Departamento de Embalagem (Doc 05 §3.8 e Fichas 01-05).

Criação e teste de títulos, thumbnails A/B/C, metadados e Shorts:
1. embalagem.titulista (LLM-R)
2. embalagem.designer_thumbnail (IMG + Ferr.)
3. embalagem.avaliador_feed (LLM-V)
4. embalagem.redator_metadados (LLM-R)
5. embalagem.cortador_shorts (LLM-R + Ferr.)
"""

from __future__ import annotations

from typing import Any, Dict
from langgraph.graph import END, START, StateGraph

from contratos.estado import EstadoEpisodio
from grafo.base import no_agente


@no_agente("embalagem.titulista", categoria_modelo="LLM-R")
def titulista_node(state: EstadoEpisodio) -> Dict[str, Any]:
    titulos = [
        "A Armadilha do Cíclope: Por Que Ninguém Venceu",  # 47 chars <= 60
        "O Monstro e o Vinho: O Pior Erro de Polifemo",    # 44 chars <= 60
        "Como Odisseu Escapou do Gigante na Caverna",     # 42 chars <= 60
    ]
    return {
        "embalagem": {
            "titulos": titulos,
        }
    }


@no_agente("embalagem.designer_thumbnail", categoria_modelo="IMG")
def designer_thumbnail_node(state: EstadoEpisodio) -> Dict[str, Any]:
    thumbs = [
        {
            "layout": "A",
            "caminho": "storage_local/thumbs/thumb_layout_a.png",
            "hash": "hash_thumb_a",
            "silhueta_gigante": "polifemo_olho_brasa",
            "silhueta_pequena": "odisseu_arco",
            "texto": "NINGUÉM",
            "posicao_wordmark": "inferior_esquerdo",
            "canto_inferior_direito_livre": True,
        },
        {
            "layout": "B",
            "caminho": "storage_local/thumbs/thumb_layout_b.png",
            "hash": "hash_thumb_b",
            "silhueta_gigante": "rocha_e_fogo",
            "silhueta_pequena": "marinheiros",
            "texto": "A CAVERNA",
            "posicao_wordmark": "inferior_esquerdo",
            "canto_inferior_direito_livre": True,
        },
        {
            "layout": "C",
            "caminho": "storage_local/thumbs/thumb_layout_c.png",
            "hash": "hash_thumb_c",
            "silhueta_gigante": "poseidon_olho",
            "silhueta_pequena": "navio_odisseu",
            "texto": "O ERRO",
            "posicao_wordmark": "inferior_esquerdo",
            "canto_inferior_direito_livre": True,
        },
    ]
    return {
        "embalagem": {
            "thumbs": thumbs,
        }
    }


@no_agente("embalagem.avaliador_feed", categoria_modelo="LLM-V")
def avaliador_feed_node(state: EstadoEpisodio) -> Dict[str, Any]:
    ranking = [
        {"layout": "A", "score_120px": 9.4, "contraste_legivel": True, "vencedor": True},
        {"layout": "B", "score_120px": 8.1, "contraste_legivel": True, "vencedor": False},
        {"layout": "C", "score_120px": 7.5, "contraste_legivel": True, "vencedor": False},
    ]
    return {
        "embalagem": {
            "ranking": ranking,
        }
    }


@no_agente("embalagem.redator_metadados", categoria_modelo="LLM-R")
def redator_metadados_node(state: EstadoEpisodio) -> Dict[str, Any]:
    metadados = {
        "descricao": (
            "Mitos ganham vida quando há fogo para contá-los.\n\n"
            "Neste episódio, acompanhe a chegada de Odisseu à ilha dos Cíclopes...\n\n"
            "FONTES CANÔNICAS:\n"
            "- Homero, Odisseia, Canto IX (tradução domínio público)\n\n"
            "CAPÍTULOS:\n"
            "00:00 A Fogueira e o Cíclope\n"
            "06:00 O Vinho de Ísmaro\n"
            "13:00 Ninguém na Caverna\n"
            "19:00 A Fuga e a Maldição\n\n"
            "LUME. Mitologia, histórias, pessoas, sempre."
        ),
        "tags": ["mitologia grega", "odisseia", "homero", "odisseu", "polifemo", "teatro de sombras", "lume"],
    }
    return {
        "embalagem": {
            "metadados": metadados,
        }
    }


@no_agente("embalagem.cortador_shorts", categoria_modelo="LLM-R")
def cortador_shorts_node(state: EstadoEpisodio) -> Dict[str, Any]:
    shorts = [
        {
            "id": "short_01",
            "titulo": "O Segredo de Ninguém #Shorts",
            "tempo_inicio": "13:10",
            "duracao_s": 42.0,
            "proporcao": "9:16",
            "caminho": "storage_local/shorts/short_01.mp4",
        },
        {
            "id": "short_02",
            "titulo": "O Gigante Que Fechou a Caverna #Shorts",
            "tempo_inicio": "02:15",
            "duracao_s": 38.0,
            "proporcao": "9:16",
            "caminho": "storage_local/shorts/short_02.mp4",
        },
    ]
    return {
        "embalagem": {
            "shorts": shorts,
        }
    }


def construir_subgrafo_embalagem() -> StateGraph:
    """Compila o subgrafo de Embalagem."""
    builder = StateGraph(EstadoEpisodio)

    builder.add_node("embalagem.titulista", titulista_node)
    builder.add_node("embalagem.designer_thumbnail", designer_thumbnail_node)
    builder.add_node("embalagem.avaliador_feed", avaliador_feed_node)
    builder.add_node("embalagem.redator_metadados", redator_metadados_node)
    builder.add_node("embalagem.cortador_shorts", cortador_shorts_node)

    builder.add_edge(START, "embalagem.titulista")
    builder.add_edge("embalagem.titulista", "embalagem.designer_thumbnail")
    builder.add_edge("embalagem.designer_thumbnail", "embalagem.avaliador_feed")
    builder.add_edge("embalagem.avaliador_feed", "embalagem.redator_metadados")
    builder.add_edge("embalagem.redator_metadados", "embalagem.cortador_shorts")
    builder.add_edge("embalagem.cortador_shorts", END)

    return builder.compile()
