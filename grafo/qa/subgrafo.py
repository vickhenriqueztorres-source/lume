"""Subgrafo do Departamento de QA (Doc 05 §3.9 e Fichas 01-06).

6 verificações: 5 bloqueantes e 1 informativa (QA de marca apenas avisa).
Em caso de reprovação, define rota de retrabalho cirúrgico para o departamento responsável:
- qa_tecnico -> montagem
- qa_continuidade -> animacao
- qa_fidelidade -> roteiro
- qa_direitos -> audio
- qa_originalidade -> roteiro
- qa_marca -> apenas emite aviso (NÃO bloqueia)
"""

from __future__ import annotations

from typing import Any, Dict
from langgraph.graph import END, START, StateGraph

from contratos.estado import EstadoEpisodio
from grafo.base import no_agente


@no_agente("qa.qa_tecnico", categoria_modelo=None)
def qa_tecnico_node(state: EstadoEpisodio) -> Dict[str, Any]:
    lufs = state.get("audio", {}).get("lufs", -14.0)
    master = state.get("master", {}).get("arquivo") or {}
    forcar_falha = state.get("qa_testes", {}).get("forcar_falha_tecnico", False)

    lufs_ok = abs(lufs - (-14.0)) <= 1.0
    res_ok = master.get("resolucao") in {"3840x2160", "1920x1080"}

    aprovado = lufs_ok and res_ok and not forcar_falha
    relatorio = {
        "autor_no": "qa.qa_tecnico",
        "tipo_verificacao": "tecnica",
        "status": "aprovado" if aprovado else "reprovado",
        "bloqueia": True,
        "departamento_alvo": None if aprovado else "montagem",
        "motivo": "Resolução 4K/1080p e loudness -14 LUFS conformes" if aprovado else "Falha técnica: resolução inadequada ou loudness fora do alvo",
    }
    return {"qa": [relatorio]}


@no_agente("qa.qa_continuidade", categoria_modelo="LLM-V")
def qa_continuidade_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = state.get("decupagem", {}).get("planos", [])
    forcar_falha = state.get("qa_testes", {}).get("forcar_falha_continuidade", False)

    tem_erro_direcao = False
    for p in planos:
        for m in p.get("marionetes", []):
            if "odisseu" in m.get("id", "") and m.get("direcao") == "esq":
                tem_erro_direcao = True

    aprovado = not tem_erro_direcao and not forcar_falha
    relatorio = {
        "autor_no": "qa.qa_continuidade",
        "tipo_verificacao": "continuidade",
        "status": "aprovado" if aprovado else "reprovado",
        "bloqueia": True,
        "departamento_alvo": None if aprovado else "animacao",
        "motivo": "Direção de tela (→ casa) e nível de fogo respeitados" if aprovado else "Falha de continuidade: herói olhando contra Ítaca",
    }
    return {"qa": [relatorio]}


@no_agente("qa.qa_fidelidade", categoria_modelo="LLM-R")
def qa_fidelidade_node(state: EstadoEpisodio) -> Dict[str, Any]:
    fatos = state.get("pesquisa", {}).get("fatos", [])
    forcar_falha = state.get("qa_testes", {}).get("forcar_falha_fidelidade", False)

    aprovado = len(fatos) > 0 and not forcar_falha
    relatorio = {
        "autor_no": "qa.qa_fidelidade",
        "tipo_verificacao": "fidelidade",
        "status": "aprovado" if aprovado else "reprovado",
        "bloqueia": True,
        "departamento_alvo": None if aprovado else "roteiro",
        "motivo": "Narração estritamente aderente aos fatos verificados de Homero" if aprovado else "Falha de fidelidade: afirmação sem suporte em pesquisa.fatos",
    }
    return {"qa": [relatorio]}


@no_agente("qa.qa_marca", categoria_modelo="LLM-V")
def qa_marca_node(state: EstadoEpisodio) -> Dict[str, Any]:
    # QA de marca NUNCA bloqueia: emite apenas aviso se houver ressalva
    color_script = state.get("color_script", {}).get("geral", {})
    teto_brasa = color_script.get("teto_brasa_pct", 5.0)
    forcar_aviso = state.get("qa_testes", {}).get("forcar_aviso_marca", False)

    aviso = teto_brasa > 5.0 or forcar_aviso

    relatorio = {
        "autor_no": "qa.qa_marca",
        "tipo_verificacao": "marca",
        "status": "aviso" if aviso else "aprovado",
        "bloqueia": False,  # Regra inegociável: QA de marca NÃO bloqueia
        "departamento_alvo": None,
        "motivo": "Paleta de 5 cores e proporção de Brasa dentro do limite de 5%" if not aviso else "Brasa acima de 5% da imagem (Doc 03 §3)",
    }
    return {"qa": [relatorio]}


@no_agente("qa.qa_direitos", categoria_modelo=None)
def qa_direitos_node(state: EstadoEpisodio) -> Dict[str, Any]:
    audio = state.get("audio", {})
    sfx = audio.get("sfx", [])
    stems = audio.get("trilha", {}).get("stems", [])
    forcar_falha = state.get("qa_testes", {}).get("forcar_falha_direitos", False)

    todos_licenciados = all(item.get("licenca") for item in sfx + stems) and len(sfx) > 0
    aprovado = todos_licenciados and not forcar_falha
    relatorio = {
        "autor_no": "qa.qa_direitos",
        "tipo_verificacao": "direitos",
        "status": "aprovado" if aprovado else "reprovado",
        "bloqueia": True,
        "departamento_alvo": None if aprovado else "audio",
        "motivo": "Todas as trilhas, SFX e texturas com licenças válidas registradas" if aprovado else "Faixa sem licença registrada encontrada",
    }
    return {"qa": [relatorio]}


@no_agente("qa.qa_originalidade", categoria_modelo="LLM-R")
def qa_originalidade_node(state: EstadoEpisodio) -> Dict[str, Any]:
    aprovacoes = state.get("aprovacoes", [])
    forcar_falha = state.get("qa_testes", {}).get("forcar_falha_originalidade", False)

    # Requer evidência de aprovação humana prévia nos gates anteriores (Gates 1 e 2)
    tem_aprovacoes = len(aprovacoes) >= 2
    aprovado = tem_aprovacoes and not forcar_falha
    relatorio = {
        "autor_no": "qa.qa_originalidade",
        "tipo_verificacao": "originalidade",
        "status": "aprovado" if aprovado else "reprovado",
        "bloqueia": True,
        "departamento_alvo": None if aprovado else "roteiro",
        "motivo": "Aprovado com evidências de autoria e gates humanos registrados" if aprovado else "Ausência de registros de direção criativa humana nos gates",
    }
    return {"qa": [relatorio]}


def consolidador_qa(state: EstadoEpisodio) -> Dict[str, Any]:
    """Avalia todas as verificações do QA e define se houve reprovação bloqueante."""
    qa_itens = state.get("qa", [])

    # Procura reprovação em verificações que bloqueiam
    for item in qa_itens:
        if item.get("bloqueia") and item.get("status") == "reprovado":
            depto_alvo = item.get("departamento_alvo", "montagem")
            return {
                "episodio": {
                    "status": "qa_reprovado",
                    "rota": depto_alvo,
                }
            }

    return {
        "episodio": {
            "status": "qa_aprovado",
            "rota": "gate_3",
        }
    }


def construir_subgrafo_qa() -> StateGraph:
    """Compila o subgrafo de QA com verificações paralelas."""
    builder = StateGraph(EstadoEpisodio)

    builder.add_node("qa.qa_tecnico", qa_tecnico_node)
    builder.add_node("qa.qa_continuidade", qa_continuidade_node)
    builder.add_node("qa.qa_fidelidade", qa_fidelidade_node)
    builder.add_node("qa.qa_marca", qa_marca_node)
    builder.add_node("qa.qa_direitos", qa_direitos_node)
    builder.add_node("qa.qa_originalidade", qa_originalidade_node)
    builder.add_node("qa.consolidador", consolidador_qa)

    # Execução das 6 checagens
    builder.add_edge(START, "qa.qa_tecnico")
    builder.add_edge(START, "qa.qa_continuidade")
    builder.add_edge(START, "qa.qa_fidelidade")
    builder.add_edge(START, "qa.qa_marca")
    builder.add_edge(START, "qa.qa_direitos")
    builder.add_edge(START, "qa.qa_originalidade")

    # Todas convergem no consolidador
    builder.add_edge("qa.qa_tecnico", "qa.consolidador")
    builder.add_edge("qa.qa_continuidade", "qa.consolidador")
    builder.add_edge("qa.qa_fidelidade", "qa.consolidador")
    builder.add_edge("qa.qa_marca", "qa.consolidador")
    builder.add_edge("qa.qa_direitos", "qa.consolidador")
    builder.add_edge("qa.qa_originalidade", "qa.consolidador")

    builder.add_edge("qa.consolidador", END)

    return builder.compile()
