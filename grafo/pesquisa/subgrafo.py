"""Subgrafo do Departamento de Pesquisa (Doc 05 §3.1 e Fichas 01-04).

Agentes:
1. pesquisa.pesquisador_fontes (LLM-R)
2. pesquisa.verificador_fatos (LLM-R)
3. pesquisa.analista_referencia (Ferr. + LLM-V)
4. pesquisa.analista_demanda (LLM-R)
"""

from __future__ import annotations

from typing import Any, Dict
from langgraph.graph import END, START, StateGraph

from contratos.agentes import (
    AnalistaDemandaOutput,
    AnalistaReferenciaOutput,
    PesquisadorFontesOutput,
    VerificadorFatosOutput,
)
from contratos.estado import EstadoEpisodio
from grafo.base import no_agente
from grafo.ferramentas.canal_lume_mcp import injetar_inbox_no_estado
from grafo.ferramentas.modelos import obter_cliente_modelo


@no_agente("pesquisa.pesquisador_fontes", categoria_modelo="LLM-R")
def pesquisador_fontes_node(state: EstadoEpisodio) -> Dict[str, Any]:
    try:
        state_enriquecido = injetar_inbox_no_estado(dict(state))
    except Exception:
        state_enriquecido = state
    episodio_ctx = state_enriquecido.get("episodio")
    cliente = obter_cliente_modelo("LLM-R")
    saida = cliente.gerar_estruturado(
        schema=PesquisadorFontesOutput,
        prompt_sistema="Pesquise fontes canônicas de domínio público para o mito informado.",
        entradas={"episodio": episodio_ctx},
    )
    return {
        "pesquisa": {
            "fontes": [f.model_dump() for f in saida.fontes],
            "nomes_canonicos": saida.nomes_canonicos,
        }
    }


@no_agente("pesquisa.verificador_fatos", categoria_modelo="LLM-R")
def verificador_fatos_node(state: EstadoEpisodio) -> Dict[str, Any]:
    cliente = obter_cliente_modelo("LLM-R")
    saida = cliente.gerar_estruturado(
        schema=VerificadorFatosOutput,
        prompt_sistema="Confirme cada fato em fontes primárias e classifique controvérsias.",
        entradas={"pesquisa": state.get("pesquisa")},
    )
    return {
        "pesquisa": {
            "fatos": [f.model_dump() for f in saida.fatos],
            "controversias": saida.controversias,
        }
    }


@no_agente("pesquisa.analista_referencia", categoria_modelo="LLM-V")
def analista_referencia_node(state: EstadoEpisodio) -> Dict[str, Any]:
    cliente = obter_cliente_modelo("LLM-V")
    saida = cliente.gerar_estruturado(
        schema=AnalistaReferenciaOutput,
        prompt_sistema="Analise ritmo de montagem e lacunas em referências concorrentes.",
        entradas={"pesquisa": state.get("pesquisa")},
    )
    return {
        "pesquisa": {
            "referencia": saida.model_dump(),
        }
    }


@no_agente("pesquisa.analista_demanda", categoria_modelo="LLM-R")
def analista_demanda_node(state: EstadoEpisodio) -> Dict[str, Any]:
    cliente = obter_cliente_modelo("LLM-R")
    saida = cliente.gerar_estruturado(
        schema=AnalistaDemandaOutput,
        prompt_sistema="Mapeie concorrência e ângulos mais fortes para o público de mitologia.",
        entradas={"pesquisa": state.get("pesquisa")},
    )
    return {
        "pesquisa": {
            "angulos": [a.model_dump() for a in saida.angulos_ranqueados],
        }
    }


def construir_subgrafo_pesquisa() -> StateGraph:
    """Compila o subgrafo de Pesquisa com execução sequencial e paralela dos agentes."""
    builder = StateGraph(EstadoEpisodio)
    builder.add_node("pesquisa.pesquisador_fontes", pesquisador_fontes_node)
    builder.add_node("pesquisa.verificador_fatos", verificador_fatos_node)
    builder.add_node("pesquisa.analista_referencia", analista_referencia_node)
    builder.add_node("pesquisa.analista_demanda", analista_demanda_node)

    builder.add_edge(START, "pesquisa.pesquisador_fontes")
    builder.add_edge("pesquisa.pesquisador_fontes", "pesquisa.verificador_fatos")
    builder.add_edge("pesquisa.verificador_fatos", "pesquisa.analista_referencia")
    builder.add_edge("pesquisa.analista_referencia", "pesquisa.analista_demanda")
    builder.add_edge("pesquisa.analista_demanda", END)

    return builder.compile()
