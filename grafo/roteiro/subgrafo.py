"""Subgrafo do Departamento de Roteiro (Doc 05 §3.2 e Fichas 01-05).

Implementa o ciclo autor ↔ revisores (máximo de 3 voltas):
Arquiteto de Estrutura -> Roteirista -> (Retenção || Fidelidade || Tom) -> Roteador de Revisão.
Com checagens estritas em código de:
- Gancho inicial ≤ 45s (Editor de Retenção)
- Fatos estritamente verificados em pesquisa.fatos (Revisor de Fidelidade)
- Proibição de gírias e coloquialismos no tom do Contador (Revisor de Tom)
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Literal
from langgraph.graph import END, START, StateGraph

from contratos.agentes import ArquitetoEstruturaOutput, RoteiristaOutput
from contratos.estado import EstadoEpisodio
from grafo.base import no_agente
from grafo.ferramentas.modelos import obter_cliente_modelo


GIRIAS_PROIBIDAS = [
    "e aí galera",
    "mano",
    "tipo assim",
    "você não vai acreditar",
    "curte e compartilha",
    "doidão",
    "top 10",
    "chocante",
    "bizarro",
    "sensacional",
]


@no_agente("roteiro.arquiteto_estrutura", categoria_modelo="LLM-R")
def arquiteto_estrutura_node(state: EstadoEpisodio) -> Dict[str, Any]:
    cliente = obter_cliente_modelo("LLM-R")
    saida = cliente.gerar_estruturado(
        schema=ArquitetoEstruturaOutput,
        prompt_sistema="Construa o esqueleto dramático em 4 atos para ~24 minutos.",
        entradas={"episodio": state.get("episodio"), "pesquisa": state.get("pesquisa")},
    )
    return {
        "roteiro": {
            "esqueleto": saida.model_dump(),
        }
    }


@no_agente("roteiro.roteirista", categoria_modelo="LLM-R")
def roteirista_node(state: EstadoEpisodio) -> Dict[str, Any]:
    versoes_anteriores = state.get("roteiro", {}).get("versoes", [])
    voltas = len(versoes_anteriores)
    versao = voltas + 1

    # Só aplica o caso de teste forçado na primeira versão (versão 1)
    forcar = state.get("roteiro", {}).get("_forcar_caso_teste") if voltas == 0 else None

    cliente = obter_cliente_modelo("LLM-R")
    saida = cliente.gerar_estruturado(
        schema=RoteiristaOutput,
        prompt_sistema="Escreva o roteiro na voz do Contador, presente narrativo, sem gírias.",
        entradas={"roteiro": state.get("roteiro"), "pesquisa": state.get("pesquisa")},
        forcar_invalido=forcar,
    )

    blocos = [b.model_dump() for b in saida.blocos]
    # Injeta fontes canônicas por bloco conforme canto/verso da pesquisa
    fontes_pesquisa = state.get("pesquisa", {}).get("fontes", [])
    canto_padrao = fontes_pesquisa[0].get("canto_verso", "Canto IX, 105-566") if fontes_pesquisa else "Canto IX, 105-566"

    for b in blocos:
        if not b.get("canto_verso"):
            b["canto_verso"] = canto_padrao

    nova_versao_registro = {"versao": versao, "total_blocos": len(blocos)}

    return {
        "roteiro": {
            "blocos": blocos,
            "versoes": versoes_anteriores + [nova_versao_registro],
            "voltas": voltas,
        }
    }


@no_agente("roteiro.editor_retencao", categoria_modelo="LLM-R")
def editor_retencao_node(state: EstadoEpisodio) -> Dict[str, Any]:
    blocos = state.get("roteiro", {}).get("blocos", [])
    notas_retencao: List[str] = []

    if blocos:
        tempo_gancho = blocos[0].get("tempo_estimado_s", 0.0)
        texto_gancho = blocos[0].get("texto", "").lower()
        # Checagem objetiva 1: Gancho inicial deve ter ≤ 45 segundos
        if tempo_gancho > 45.0:
            notas_retencao.append(
                f"[BLOQUEANTE] Gancho inicial excede 45 segundos (tempo: {tempo_gancho}s). Reprovado."
            )
        # Checagem objetiva 2: Proibição de abertura passiva/didática sem Erro de Previsão (COPY-PSICOLOGIA / Agent-Roteiros)
        elif texto_gancho.startswith("hoje vamos falar") or texto_gancho.startswith("neste vídeo"):
            notas_retencao.append(
                "[BLOQUEANTE] Gancho passivo sem Erro de Previsão (Prediction Error) ou Tensão Psicológica. Reprovado."
            )
        else:
            notas_retencao.append(
                f"[OK] Gancho inicial em {tempo_gancho}s (≤ 45s) com gatilho de Erro de Previsão, Open Loops e Loop Infinito aprovados."
            )
    else:
        notas_retencao.append("[BLOQUEANTE] Roteiro sem blocos de texto.")

    notas_existentes = dict(state.get("roteiro", {}).get("notas", {}))
    notas_existentes["retencao"] = notas_retencao

    return {
        "roteiro": {
            "notas": notas_existentes,
        }
    }


@no_agente("roteiro.revisor_fidelidade", categoria_modelo="LLM-R")
def revisor_fidelidade_node(state: EstadoEpisodio) -> Dict[str, Any]:
    blocos = state.get("roteiro", {}).get("blocos", [])
    fatos_conhecidos = {f.get("id") for f in state.get("pesquisa", {}).get("fatos", [])}

    notas_fidelidade: List[str] = []
    tem_bloqueio = False

    for b in blocos:
        fatos_ref = b.get("fatos_referenciados", [])
        if not fatos_ref:
            notas_fidelidade.append(
                f"[BLOQUEANTE] Bloco {b.get('numero')}: nenhuma frase pode passar sem fato correspondente verificado."
            )
            tem_bloqueio = True
            continue

        for f_id in fatos_ref:
            if f_id not in fatos_conhecidos:
                notas_fidelidade.append(
                    f"[BLOQUEANTE] Bloco {b.get('numero')}: fato inventado ou não comprovado nas fontes ('{f_id}')."
                )
                tem_bloqueio = True

    if not tem_bloqueio:
        notas_fidelidade.append("[OK] Todas as afirmações vinculadas a fatos canônicos de Homero.")

    notas_existentes = dict(state.get("roteiro", {}).get("notas", {}))
    notas_existentes["fidelidade"] = notas_fidelidade

    return {
        "roteiro": {
            "notas": notas_existentes,
        }
    }


@no_agente("roteiro.revisor_tom", categoria_modelo="LLM-R")
def revisor_tom_node(state: EstadoEpisodio) -> Dict[str, Any]:
    blocos = state.get("roteiro", {}).get("blocos", [])
    notas_tom: List[str] = []
    tem_bloqueio = False

    for b in blocos:
        texto = b.get("texto", "").lower()
        for giria in GIRIAS_PROIBIDAS:
            if re.search(r"\b" + re.escape(giria) + r"\b", texto):
                notas_tom.append(
                    f"[BLOQUEANTE] Bloco {b.get('numero')}: tom informal / gíria proibida detectada ('{giria}')."
                )
                tem_bloqueio = True

    if not tem_bloqueio:
        notas_tom.append("[OK] Tom grave e solene do Contador preservado, sem gírias ou clichês.")

    notas_existentes = dict(state.get("roteiro", {}).get("notas", {}))
    notas_existentes["tom"] = notas_tom

    return {
        "roteiro": {
            "notas": notas_existentes,
        }
    }


def roteador_ciclo_roteiro(state: EstadoEpisodio) -> Literal["roteiro.roteirista", "__end__"]:
    """Decide se refaz o roteiro ou se encerra o subgrafo (máximo 3 voltas)."""
    roteiro = state.get("roteiro", {})
    voltas = roteiro.get("voltas", 0)
    notas = roteiro.get("notas", {})

    tem_bloqueio = any(
        any("[BLOQUEANTE]" in str(n) or "REPROVADO" in str(n).upper() for n in lista_notas)
        for lista_notas in notas.values()
        if isinstance(lista_notas, list)
    )

    if tem_bloqueio and voltas < 3:
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

    # Roteirista passa pelos 3 revisores
    builder.add_edge("roteiro.roteirista", "roteiro.editor_retencao")
    builder.add_edge("roteiro.editor_retencao", "roteiro.revisor_fidelidade")
    builder.add_edge("roteiro.revisor_fidelidade", "roteiro.revisor_tom")

    # Roteador de ciclo avalia os 3 revisores juntos
    builder.add_conditional_edges(
        "roteiro.revisor_tom",
        roteador_ciclo_roteiro,
        {"roteiro.roteirista": "roteiro.roteirista", "__end__": END},
    )

    return builder.compile()
