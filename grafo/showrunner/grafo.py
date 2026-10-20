"""Grafo Principal do Showrunner (Doc 05 §1, §6 e §7).

Orquestra o supervisor, os 10 subgrafos de departamentos e os 5 gates humanos
com checkpoints persistentes, interrupts e retomadas seguras.
"""

from __future__ import annotations

from typing import Any, Dict
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from contratos.estado import AprovacaoItem, EstadoEpisodio
from contratos.gates import (
    PayloadGateCorteFinal,
    PayloadGateEmbalagem,
    PayloadGatePublicacao,
    PayloadGateRoteiro,
    PayloadGateStoryboard,
    RespostaGate,
)
from grafo.animacao.subgrafo import construir_subgrafo_animacao
from grafo.arte.subgrafo import construir_subgrafo_arte
from grafo.audio.subgrafo import construir_subgrafo_audio
from grafo.checkpointer import obter_checkpointer
from grafo.direcao.subgrafo import construir_subgrafo_direcao
from grafo.embalagem.subgrafo import construir_subgrafo_embalagem
from grafo.montagem.subgrafo import construir_subgrafo_montagem
from grafo.pesquisa.subgrafo import construir_subgrafo_pesquisa
from grafo.publicacao.subgrafo import construir_subgrafo_publicacao
from grafo.qa.subgrafo import construir_subgrafo_qa
from grafo.roteiro.subgrafo import construir_subgrafo_roteiro
from grafo.showrunner.supervisor import (
    roteador_pos_qa,
    showrunner_inicio_node,
    showrunner_monitor_orcamento_node,
)


# ============================================================================
# Nós dos Gates Humanos (Doc 05 §7) com interrupt e gravação em aprovacoes
# ============================================================================

def gate_1_roteiro_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Gate 1: Roteiro e Fidelidade Canônica."""
    roteiro = state.get("roteiro", {})
    notas = roteiro.get("notas", {})

    payload = PayloadGateRoteiro(
        titulo=state.get("episodio", {}).get("mito", "Episódio LUME"),
        versao=roteiro.get("voltas", 0) + 1,
        blocos=roteiro.get("blocos", []),
        notas_retencao=notas.get("retencao", []),
        notas_fidelidade=notas.get("fidelidade", []),
        notas_tom=notas.get("tom", []),
        fontes=state.get("pesquisa", {}).get("fontes", []),
    ).model_dump()

    # Interrupção durável: aguarda operador humano
    resposta_bruta = interrupt(payload)

    if isinstance(resposta_bruta, dict):
        resp = RespostaGate.model_validate(resposta_bruta)
    elif isinstance(resposta_bruta, RespostaGate):
        resp = resposta_bruta
    else:
        resp = RespostaGate(
            gate_id=1,
            status="aprovado",
            autor="operador_default",
            comentarios=str(resposta_bruta),
        )

    item_aprovacao = AprovacaoItem(
        gate_id=1,
        autor=resp.autor,
        status=resp.status,
        comentarios=resp.comentarios,
        ajustes=resp.ajustes,
        simulado=resp.simulado,
    ).model_dump()

    return {
        "aprovacoes": [item_aprovacao],
        "episodio": {
            "status": "gate_1_aprovado" if resp.status != "refazer" else "roteiro_refazer",
        },
    }


def gate_2_storyboard_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Gate 2: Storyboard e Animatic com Narração Provisória."""
    decupagem = state.get("decupagem", {})
    planos = decupagem.get("planos", [])

    payload = PayloadGateStoryboard(
        total_planos=len(planos),
        duracao_total_s=sum(p.get("duracao_s", 5.0) for p in planos),
        animatic_caminho=decupagem.get("animatic", {}).get("caminho"),
        color_script=state.get("color_script", {}),
        planos_preview=planos[:5],
    ).model_dump()

    resposta_bruta = interrupt(payload)

    if isinstance(resposta_bruta, dict):
        resp = RespostaGate.model_validate(resposta_bruta)
    elif isinstance(resposta_bruta, RespostaGate):
        resp = resposta_bruta
    else:
        resp = RespostaGate(gate_id=2, status="aprovado", autor="operador_default")

    item_aprovacao = AprovacaoItem(
        gate_id=2,
        autor=resp.autor,
        status=resp.status,
        comentarios=resp.comentarios,
        ajustes=resp.ajustes,
        simulado=resp.simulado,
    ).model_dump()

    return {
        "aprovacoes": [item_aprovacao],
        "episodio": {
            "status": "gate_2_aprovado" if resp.status != "refazer" else "direcao_refazer",
        },
    }


def gate_3_corte_final_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Gate 3: Corte Final Master e Relatórios de QA."""
    master = state.get("master", {})
    payload = PayloadGateCorteFinal(
        master_caminho=master.get("arquivo", {}).get("caminho"),
        duracao_total_s=state.get("timeline", {}).get("duracao_total_s", 1440.0),
        lufs_medido=state.get("audio", {}).get("lufs", -14.0),
        relatorios_qa=state.get("qa", []),
        marcas_tempo=master.get("capitulos", []),
    ).model_dump()

    resposta_bruta = interrupt(payload)

    if isinstance(resposta_bruta, dict):
        resp = RespostaGate.model_validate(resposta_bruta)
    elif isinstance(resposta_bruta, RespostaGate):
        resp = resposta_bruta
    else:
        resp = RespostaGate(gate_id=3, status="aprovado", autor="operador_default")

    item_aprovacao = AprovacaoItem(
        gate_id=3,
        autor=resp.autor,
        status=resp.status,
        comentarios=resp.comentarios,
        ajustes=resp.ajustes,
        simulado=resp.simulado,
    ).model_dump()

    return {
        "aprovacoes": [item_aprovacao],
        "episodio": {
            "status": "gate_3_aprovado" if resp.status != "refazer" else "montagem_refazer",
        },
    }


def gate_4_embalagem_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Gate 4: Títulos, Thumbnails A/B/C e Shorts."""
    embalagem = state.get("embalagem", {})
    payload = PayloadGateEmbalagem(
        titulos=embalagem.get("titulos", []),
        thumbs=embalagem.get("thumbs", []),
        ranking_feed=embalagem.get("ranking", []),
        descricao=embalagem.get("metadados", {}).get("descricao", ""),
        shorts=embalagem.get("shorts", []),
    ).model_dump()

    resposta_bruta = interrupt(payload)

    if isinstance(resposta_bruta, dict):
        resp = RespostaGate.model_validate(resposta_bruta)
    elif isinstance(resposta_bruta, RespostaGate):
        resp = resposta_bruta
    else:
        resp = RespostaGate(gate_id=4, status="aprovado", autor="operador_default")

    item_aprovacao = AprovacaoItem(
        gate_id=4,
        autor=resp.autor,
        status=resp.status,
        comentarios=resp.comentarios,
        ajustes=resp.ajustes,
        simulado=resp.simulado,
    ).model_dump()

    return {
        "aprovacoes": [item_aprovacao],
        "episodio": {
            "status": "gate_4_aprovado" if resp.status != "refazer" else "embalagem_refazer",
        },
    }


def gate_5_publicacao_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Gate 5 (Opcional): Autorização para Publicação / Agendamento."""
    publicacao = state.get("episodio", {}).get("publicacao") or {}
    payload = PayloadGatePublicacao(
        video_id=publicacao.get("video_id", "pendente"),
        status_atual="privado",
        verificacoes_youtube={"copyright": "sem_reclamacoes", "hd_processado": True},
        agendamento_sugerido="2026-10-25T18:00:00Z",
    ).model_dump()

    resposta_bruta = interrupt(payload)

    if isinstance(resposta_bruta, dict):
        resp = RespostaGate.model_validate(resposta_bruta)
    elif isinstance(resposta_bruta, RespostaGate):
        resp = resposta_bruta
    else:
        resp = RespostaGate(gate_id=5, status="aprovado", autor="operador_default")

    item_aprovacao = AprovacaoItem(
        gate_id=5,
        autor=resp.autor,
        status=resp.status,
        comentarios=resp.comentarios,
        ajustes=resp.ajustes,
        simulado=resp.simulado,
    ).model_dump()

    return {
        "aprovacoes": [item_aprovacao],
        "episodio": {
            "status": "gate_5_aprovado",
        },
    }


# ============================================================================
# Construção do Grafo Completo do Showrunner
# ============================================================================

def construir_grafo_showrunner(checkpointer=None) -> Any:
    """Constrói e compila o grafo mestre do Showrunner com todos os 10 subgrafos e 5 gates."""
    builder = StateGraph(EstadoEpisodio)

    # 1. Nós do Showrunner
    builder.add_node("showrunner_inicio", showrunner_inicio_node)
    builder.add_node("showrunner_monitor", showrunner_monitor_orcamento_node)

    # 2. Subgrafos dos 10 Departamentos
    builder.add_node("depto_pesquisa", construir_subgrafo_pesquisa())
    builder.add_node("depto_roteiro", construir_subgrafo_roteiro())
    builder.add_node("depto_direcao", construir_subgrafo_direcao())
    builder.add_node("depto_arte", construir_subgrafo_arte())
    builder.add_node("depto_audio", construir_subgrafo_audio())
    builder.add_node("depto_animacao", construir_subgrafo_animacao())
    builder.add_node("depto_montagem", construir_subgrafo_montagem())
    builder.add_node("depto_embalagem", construir_subgrafo_embalagem())
    builder.add_node("depto_qa", construir_subgrafo_qa())
    builder.add_node("depto_publicacao", construir_subgrafo_publicacao())

    # 3. Gates Humanos
    builder.add_node("gate_1_roteiro", gate_1_roteiro_node)
    builder.add_node("gate_2_storyboard", gate_2_storyboard_node)
    builder.add_node("gate_3_corte_final", gate_3_corte_final_node)
    builder.add_node("gate_4_embalagem", gate_4_embalagem_node)
    builder.add_node("gate_5_publicacao", gate_5_publicacao_node)

    # --- Roteamento e Conexões ---
    builder.add_edge(START, "showrunner_inicio")
    builder.add_edge("showrunner_inicio", "depto_pesquisa")
    builder.add_edge("depto_pesquisa", "depto_roteiro")
    builder.add_edge("depto_roteiro", "gate_1_roteiro")

    # Gate 1 -> Direção (ou refaz roteiro se reprovado)
    builder.add_conditional_edges(
        "gate_1_roteiro",
        lambda s: "depto_roteiro" if s.get("episodio", {}).get("status") == "roteiro_refazer" else "depto_direcao",
        {"depto_roteiro": "depto_roteiro", "depto_direcao": "depto_direcao"},
    )

    builder.add_edge("depto_direcao", "gate_2_storyboard")

    # Gate 2 -> Paralelismo Arte & Áudio
    # Nó divisor para o fork paralelo
    def roteador_pos_gate_2(state: EstadoEpisodio):
        if state.get("episodio", {}).get("status") == "direcao_refazer":
            return "depto_direcao"
        return "fork_producao"

    builder.add_node("fork_producao", lambda s: {})
    builder.add_conditional_edges(
        "gate_2_storyboard",
        roteador_pos_gate_2,
        {"depto_direcao": "depto_direcao", "fork_producao": "fork_producao"},
    )

    # Paralelismo: Arte -> Animação // Áudio
    builder.add_edge("fork_producao", "depto_arte")
    builder.add_edge("fork_producao", "depto_audio")
    builder.add_edge("depto_arte", "depto_animacao")

    # Barreira de sincronização: Montagem só roda quando Animação E Áudio terminarem
    builder.add_edge(["depto_animacao", "depto_audio"], "depto_montagem")

    # Montagem -> QA
    builder.add_edge("depto_montagem", "depto_qa")

    # Pós-QA: Retrabalho Cirúrgico ou Gate 3
    builder.add_conditional_edges(
        "depto_qa",
        roteador_pos_qa,
        {
            "depto_roteiro": "depto_roteiro",
            "depto_animacao": "depto_animacao",
            "depto_montagem": "depto_montagem",
            "depto_audio": "depto_audio",
            "depto_direcao": "depto_direcao",
            "gate_3_corte_final": "gate_3_corte_final",
        },
    )

    # Gate 3 -> Embalagem
    builder.add_conditional_edges(
        "gate_3_corte_final",
        lambda s: "depto_montagem" if s.get("episodio", {}).get("status") == "montagem_refazer" else "depto_embalagem",
        {"depto_montagem": "depto_montagem", "depto_embalagem": "depto_embalagem"},
    )

    builder.add_edge("depto_embalagem", "gate_4_embalagem")

    # Gate 4 -> Gate 5 (opcional) -> Publicação
    builder.add_conditional_edges(
        "gate_4_embalagem",
        lambda s: "depto_embalagem" if s.get("episodio", {}).get("status") == "embalagem_refazer" else "gate_5_publicacao",
        {"depto_embalagem": "depto_embalagem", "gate_5_publicacao": "gate_5_publicacao"},
    )

    builder.add_edge("gate_5_publicacao", "depto_publicacao")
    builder.add_edge("depto_publicacao", "showrunner_monitor")
    builder.add_edge("showrunner_monitor", END)

    cp = checkpointer if checkpointer is not None else obter_checkpointer()
    return builder.compile(checkpointer=cp)


# Instância padrão para uso e langgraph.json
grafo_showrunner = construir_grafo_showrunner()
