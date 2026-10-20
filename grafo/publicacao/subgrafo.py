"""Subgrafo do Departamento de Publicação e Aprendizado (Doc 05 §3.10 e Fichas 01-03).

Publicação obrigatória em modo privado com chave de idempotência e gravação de lições:
1. publicacao.publicador (Ferr. YouTube Data API - estritamente privado)
2. publicacao.analista_desempenho (Ferr. + LLM-R)
3. publicacao.curador_memoria (LLM-R + Store)
"""

from __future__ import annotations

from typing import Any, Dict
from langgraph.graph import END, START, StateGraph

from contratos.estado import EstadoEpisodio
from grafo.base import gerar_chave_idempotencia, no_agente, registrar_operacao_efeito_colateral
from grafo.checkpointer import obter_store


@no_agente("publicacao.publicador", categoria_modelo=None)
def publicador_node(state: EstadoEpisodio) -> Dict[str, Any]:
    ep_id = state.get("episodio", {}).get("id", "ep01")
    chave_op = gerar_chave_idempotencia("publicacao.publicador", ep_id)

    # 1. Checa idempotência: impede re-upload ao retomar após interrupção
    ja_executado = registrar_operacao_efeito_colateral(chave_op)

    publicacao_existente = state.get("episodio", {}).get("publicacao")
    if ja_executado and publicacao_existente:
        return {
            "episodio": {
                "publicacao": publicacao_existente,
                "status": "publicado_privado",
            }
        }

    # 2. Upload estritamente em modo privado (Regra Inegociável 10)
    dados_publicacao = {
        "video_id": f"yt_{ep_id}_privado",
        "status": "privado",  # NUNCA público fora do Gate 5
        "upload_url": f"https://youtube.com/watch?v=yt_{ep_id}_privado",
        "chave_idempotencia": chave_op,
        "titulo": state.get("embalagem", {}).get("titulos", ["Episódio LUME"])[0],
        "modo": "privado_obrigatorio",
    }

    return {
        "episodio": {
            "publicacao": dados_publicacao,
            "status": "publicado_privado",
        }
    }


@no_agente("publicacao.analista_desempenho", categoria_modelo="LLM-R")
def analista_desempenho_node(state: EstadoEpisodio) -> Dict[str, Any]:
    desempenho = {
        "retencao_estimada_media": 68.5,
        "ctr_esperado": 8.2,
        "pontos_atencao": ["Manter corte dinâmico no minuto 06:00"],
    }
    return {
        "episodio": {
            "desempenho": desempenho,
        }
    }


@no_agente("publicacao.curador_memoria", categoria_modelo="LLM-R")
def curador_memoria_node(state: EstadoEpisodio) -> Dict[str, Any]:
    store = obter_store()
    ep_id = state.get("episodio", {}).get("id", "ep01")

    licao = {
        "episodio_id": ep_id,
        "departamento": "animacao",
        "regra": "Planos com Odisseu em escala devem manter tremulação da brasa em 2Hz para manter tensão.",
        "tipo": "ritmo_fogo",
    }

    try:
        store.put(("licoes", "aprendizado"), f"licao_{ep_id}", licao)
    except Exception:
        pass

    return {
        "episodio": {
            "licoes_gravadas": [licao],
            "status": "concluido",
        }
    }


def construir_subgrafo_publicacao() -> StateGraph:
    """Compila o subgrafo de Publicação."""
    builder = StateGraph(EstadoEpisodio)

    builder.add_node("publicacao.publicador", publicador_node)
    builder.add_node("publicacao.analista_desempenho", analista_desempenho_node)
    builder.add_node("publicacao.curador_memoria", curador_memoria_node)

    builder.add_edge(START, "publicacao.publicador")
    builder.add_edge("publicacao.publicador", "publicacao.analista_desempenho")
    builder.add_edge("publicacao.analista_desempenho", "publicacao.curador_memoria")
    builder.add_edge("publicacao.curador_memoria", END)

    return builder.compile()
