"""Showrunner: Supervisor do Estúdio LUME (Doc 05 §4 e Ficha 00).

Responsável por:
1. Injetar lições da memória (Store) no início do episódio.
2. Monitorar tetos de custo e orçamento acumulado.
3. Roteamento entre departamentos e gestão de retrabalho do QA.
4. Escalada para fila humana quando limites são atingidos.
"""

from __future__ import annotations

from typing import Any, Dict
from contratos.estado import EstadoEpisodio
from grafo.base import no_agente
from grafo.checkpointer import obter_store


@no_agente("showrunner", categoria_modelo="LLM-R")
def showrunner_inicio_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Inicializa o episódio, injeta lições prévias da Store e configura orçamento."""
    store = obter_store()

    # Injeta lições aplicáveis da memória de longo prazo
    licoes_injetadas = []
    try:
        # Busca itens na Store se disponíveis
        itens = store.search(("licoes", "aprendizado"))
        for item in itens:
            if hasattr(item, "value") and isinstance(item.value, dict):
                licoes_injetadas.append(item.value)
    except Exception:
        pass

    if not licoes_injetadas:
        licoes_injetadas.append({
            "departamento": "direcao",
            "regra": "Odisseu rumo a Ítaca sempre se move da esquerda para a direita (→ casa).",
            "origem": "doc04_cinematografia",
        })

    orcamento = state.get("episodio", {}).get("orcamento", {"teto_usd": 150.0, "gasto_atual_usd": 0.0})

    return {
        "episodio": {
            "status": "pesquisa_iniciada",
            "licoes_aplicadas": licoes_injetadas,
            "orcamento": orcamento,
        }
    }


@no_agente("showrunner", categoria_modelo="LLM-R")
def showrunner_monitor_orcamento_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Calcula custo acumulado dos nós e valida conformidade com o teto."""
    custos = state.get("custos", [])
    gasto_total = sum(item.get("custo_estimado_usd", 0.0) for item in custos)
    orcamento = dict(state.get("episodio", {}).get("orcamento", {}))
    orcamento["gasto_atual_usd"] = round(gasto_total, 4)

    teto = orcamento.get("teto_usd", 150.0)
    if gasto_total > teto:
        fila = list(state.get("episodio", {}).get("fila_humana", []))
        fila.append({
            "origem": "showrunner",
            "tipo": "estouro_orcamento",
            "gasto_usd": gasto_total,
            "teto_usd": teto,
        })
        return {
            "episodio": {
                "orcamento": orcamento,
                "fila_humana": fila,
                "status": "pausado_orcamento",
            }
        }

    return {
        "episodio": {
            "orcamento": orcamento,
        }
    }


def roteador_pos_qa(state: EstadoEpisodio) -> str:
    """Decide próximo passo após subgrafo de QA: retrabalho cirúrgico ou Gate 3."""
    status = state.get("episodio", {}).get("status")
    rota = state.get("episodio", {}).get("rota")

    if status == "qa_reprovado" and rota:
        # Retrabalho cirúrgico: volta apenas para o departamento responsável
        if rota == "roteiro":
            return "depto_roteiro"
        elif rota == "animacao":
            return "depto_animacao"
        elif rota == "montagem":
            return "depto_montagem"
        elif rota == "audio":
            return "depto_audio"
        elif rota == "direcao":
            return "depto_direcao"

    return "gate_3_corte_final"
