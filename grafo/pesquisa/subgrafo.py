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

from contratos.estado import EstadoEpisodio
from grafo.base import no_agente


@no_agente("pesquisa.pesquisador_fontes", categoria_modelo="LLM-R")
def pesquisador_fontes_node(state: EstadoEpisodio) -> Dict[str, Any]:
    mito = state.get("episodio", {}).get("mito", "A Odisseia")
    fontes = [
        {
            "canto_verso": "Canto IX, 105-566",
            "obra": "Odisseia",
            "autor": "Homero",
            "texto_original": "Cíclope Polifemo e a fuga sob os carneiros.",
            "traducao_pt": "Odisseu cega o Cíclope Polifemo com a estaca aquecida no fogo.",
            "dominio_publico": True,
            "url_ou_referencia": "Perseus Digital Library: Hom. Od. 9.105",
        },
        {
            "canto_verso": "Canto XI, 1-640",
            "obra": "Odisseia",
            "autor": "Homero",
            "texto_original": "Nekuia: invocação das sombras no Hades.",
            "traducao_pt": "Odisseu consulta Tirésias e encontra as almas dos mortos.",
            "dominio_publico": True,
            "url_ou_referencia": "Perseus Digital Library: Hom. Od. 11.1",
        },
    ]
    nomes_canonicos = {
        "Ulisses": "Odisseu",
        "Ciclope": "Polifemo",
        "Minerva": "Atena",
        "Netuno": "Poseidon",
    }
    return {
        "pesquisa": {
            "fontes": fontes,
            "nomes_canonicos": nomes_canonicos,
        }
    }


@no_agente("pesquisa.verificador_fatos", categoria_modelo="LLM-R")
def verificador_fatos_node(state: EstadoEpisodio) -> Dict[str, Any]:
    fatos = [
        {
            "id": "fato_01",
            "descricao": "Odisseu oferece vinho puro a Polifemo antes de atacá-lo.",
            "fontes_confirmadas": ["Canto IX, 105-566"],
            "variante_ou_tardia": False,
            "grau_certeza": "canonica",
        },
        {
            "id": "fato_02",
            "descricao": "Odisseu diz chamar-se Ninguém (Outis).",
            "fontes_confirmadas": ["Canto IX, 105-566"],
            "variante_ou_tardia": False,
            "grau_certeza": "canonica",
        },
        {
            "id": "fato_03",
            "descricao": "A fuga ocorre amarrando os marinheiros sob os ventres dos carneiros.",
            "fontes_confirmadas": ["Canto IX, 105-566"],
            "variante_ou_tardia": False,
            "grau_certeza": "canonica",
        },
    ]
    return {
        "pesquisa": {
            "fatos": fatos,
            "controversias": [],
        }
    }


@no_agente("pesquisa.analista_referencia", categoria_modelo="LLM-V")
def analista_referencia_node(state: EstadoEpisodio) -> Dict[str, Any]:
    referencia = {
        "metricas_ritmo": {"media_duracao_plano_s": 5.2, "cortes_por_minuto": 11.5},
        "densidade_cortes_ppm": 11.5,
        "lacunas_identificadas": ["Ausência de física real de sombras nos concorrentes"],
    }
    return {
        "pesquisa": {
            "referencia": referencia,
        }
    }


@no_agente("pesquisa.analista_demanda", categoria_modelo="LLM-R")
def analista_demanda_node(state: EstadoEpisodio) -> Dict[str, Any]:
    angulos = [
        {"angulo": "O Erro Fatal de Polifemo: Por Que a Força Bruta Perdeu", "score": 9.2},
        {"angulo": "A Maldição de Poseidon e a Solidão no Mar", "score": 8.7},
    ]
    return {
        "pesquisa": {
            "angulos": angulos,
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
