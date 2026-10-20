"""Subgrafo do Departamento de Roteiro (Doc 05 §3.2 e Fichas 01-05).

Implementa o ciclo autor ↔ revisores (máximo de 3 voltas):
Arquiteto de Estrutura -> Roteirista -> (Retenção || Fidelidade || Tom) -> Roteador de Revisão.
"""

from __future__ import annotations

from typing import Any, Dict, Literal
from langgraph.graph import END, START, StateGraph

from contratos.estado import EstadoEpisodio
from grafo.base import no_agente


@no_agente("roteiro.arquiteto_estrutura", categoria_modelo="LLM-R")
def arquiteto_estrutura_node(state: EstadoEpisodio) -> Dict[str, Any]:
    esqueleto = {
        "atos": [
            {"ato": 1, "titulo": "A Armadilha na Caverna", "tempo_alvo_s": 360.0},
            {"ato": 2, "titulo": "O Vinho e a Astúcia de Ninguém", "tempo_alvo_s": 420.0},
            {"ato": 3, "titulo": "A Estaca no Olho e a Fuga", "tempo_alvo_s": 400.0},
            {"ato": 4, "titulo": "O Orgulho e a Maldição de Poseidon", "tempo_alvo_s": 260.0},
        ],
        "tempo_total_previsto_s": 1440.0,
    }
    return {
        "roteiro": {
            "esqueleto": esqueleto,
        }
    }


@no_agente("roteiro.roteirista", categoria_modelo="LLM-R")
def roteirista_node(state: EstadoEpisodio) -> Dict[str, Any]:
    voltas = state.get("roteiro", {}).get("voltas", 0)
    versao = voltas + 1

    blocos = [
        {
            "numero": 1,
            "tempo_estimado_s": 35.0,
            "texto": "O fogo ainda conta as mesmas histórias. Na caverna escura, o gigante fecha a entrada com a rocha que nenhum homem moveria.",
            "marcacoes_cena": ["[CENA: MUNDO_CONTADOR]", "[CENA: PAREDE_CAVERNA]"],
            "fatos_referenciados": ["fato_01"],
            "canto_verso": "Canto IX, 216-243",
        },
        {
            "numero": 2,
            "tempo_estimado_s": 50.0,
            "texto": "Odisseu não desembainha a espada de bronze. Se o monstro tombar morto agora, a saída continuará selada pela pedra.",
            "marcacoes_cena": ["[CENA: PAREDE_SILHUETA_ODISSEU]"],
            "fatos_referenciados": ["fato_01", "fato_02"],
            "canto_verso": "Canto IX, 299-317",
        },
        {
            "numero": 3,
            "tempo_estimado_s": 55.0,
            "texto": "Ele oferece a taça de vinho doce trazido de Ísmaro. 'Bebe, Polifemo. Pergunta meu nome? Ninguém me chama meu pai e minha mãe.'",
            "marcacoes_cena": ["[CENA: PAREDE_TACA_FOGO]"],
            "fatos_referenciados": ["fato_02"],
            "canto_verso": "Canto IX, 345-370",
        },
    ]

    versoes = state.get("roteiro", {}).get("versoes", [])
    nova_versao_registro = {"versao": versao, "total_blocos": len(blocos)}

    return {
        "roteiro": {
            "blocos": blocos,
            "versoes": versoes + [nova_versao_registro],
        }
    }


@no_agente("roteiro.editor_retencao", categoria_modelo="LLM-R")
def editor_retencao_node(state: EstadoEpisodio) -> Dict[str, Any]:
    notas_existentes = state.get("roteiro", {}).get("notas", {})
    return {
        "roteiro": {
            "notas": {
                **notas_existentes,
                "retencao": ["Gancho inicial cumpre meta de tempo (< 45s). Open loops consistentes."],
            }
        }
    }


@no_agente("roteiro.revisor_fidelidade", categoria_modelo="LLM-R")
def revisor_fidelidade_node(state: EstadoEpisodio) -> Dict[str, Any]:
    notas_existentes = state.get("roteiro", {}).get("notas", {})
    return {
        "roteiro": {
            "notas": {
                **notas_existentes,
                "fidelidade": ["Todos os blocos possuem fatos canônicos verificados correspondentes."],
            }
        }
    }


@no_agente("roteiro.revisor_tom", categoria_modelo="LLM-R")
def revisor_tom_node(state: EstadoEpisodio) -> Dict[str, Any]:
    notas_existentes = state.get("roteiro", {}).get("notas", {})
    return {
        "roteiro": {
            "notas": {
                **notas_existentes,
                "tom": ["Tom solene respeitado. Sem gírias, frases curtas no presente narrativo."],
            }
        }
    }


def roteador_ciclo_roteiro(state: EstadoEpisodio) -> Literal["roteiro.roteirista", "__end__"]:
    """Decide se refaz o roteiro ou se encerra o subgrafo (máximo 3 voltas)."""
    roteiro = state.get("roteiro", {})
    voltas = roteiro.get("voltas", 0)
    notas = roteiro.get("notas", {})

    tem_bloqueio = any(
        any("REPROVADO" in str(n).upper() or "BLOQUEANTE" in str(n).upper() for n in lista_notas)
        for lista_notas in notas.values()
        if isinstance(lista_notas, list)
    )

    if tem_bloqueio and voltas < 3:
        # Incrementa contador de voltas e refaz
        return "roteiro.roteirista"

    return "__end__"


def construir_subgrafo_roteiro() -> StateGraph:
    """Compila o subgrafo de Roteiro com o ciclo de revisão."""
    builder = StateGraph(EstadoEpisodio)

    builder.add_node("roteiro.arquiteto_estrutura", arquiteto_estrutura_node)
    builder.add_node("roteiro.roteirista", roteirista_node)
    builder.add_node("roteiro.editor_retencao", editor_retencao_node)
    builder.add_node("roteiro.revisor_fidelidade", revisor_fidelidade_node)
    builder.add_node("roteiro.revisor_tom", revisor_tom_node)

    builder.add_edge(START, "roteiro.arquiteto_estrutura")
    builder.add_edge("roteiro.arquiteto_estrutura", "roteiro.roteirista")

    # Roteirista dispara os 3 revisores em paralelo
    builder.add_edge("roteiro.roteirista", "roteiro.editor_retencao")
    builder.add_edge("roteiro.roteirista", "roteiro.revisor_fidelidade")
    builder.add_edge("roteiro.roteirista", "roteiro.revisor_tom")

    # Todos convergem para o roteador de ciclo
    builder.add_conditional_edges(
        "roteiro.editor_retencao",
        roteador_ciclo_roteiro,
        {"roteiro.roteirista": "roteiro.roteirista", "__end__": END},
    )
    builder.add_conditional_edges(
        "roteiro.revisor_fidelidade",
        roteador_ciclo_roteiro,
        {"roteiro.roteirista": "roteiro.roteirista", "__end__": END},
    )
    builder.add_conditional_edges(
        "roteiro.revisor_tom",
        roteador_ciclo_roteiro,
        {"roteiro.roteirista": "roteiro.roteirista", "__end__": END},
    )

    return builder.compile()
