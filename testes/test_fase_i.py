"""Testes da Fase I · Memória e Aprendizado (Critérios de Aceite).

Verifica:
1. Gravação de lição de aprendizado na Store pelo Curador de Memória no término de um episódio.
2. Injeção automática da lição aprendida no contexto do episódio subsequente pelo Showrunner.
3. Registro formal em `episodio.licoes_aplicadas` confirmando a retenção de aprendizado inter-episódios.
"""

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from contratos.estado import criar_estado_inicial
from contratos.gates import RespostaGate
from grafo.base import limpar_operacoes_teste
from grafo.checkpointer import obter_store
from grafo.publicacao.subgrafo import curador_memoria_node
from grafo.showrunner.grafo import construir_grafo_showrunner
from grafo.showrunner.supervisor import showrunner_inicio_node


def test_licao_gravada_em_episodio_aparece_no_proximo_episodio():
    """Garante que uma lição gravada num episódio é recuperada pelo Showrunner no episódio seguinte."""
    limpar_operacoes_teste()
    store = obter_store()

    # 1. Simula gravação de lição de retenção no Episódio 1 pelo Curador de Memória
    estado_ep1 = criar_estado_inicial("ep01_odisseia", "A Odisseia", "Polifemo")
    resultado_ep1 = curador_memoria_node(estado_ep1)

    licao_gravada = resultado_ep1["episodio"]["licoes_gravadas"][0]
    assert licao_gravada["episodio_id"] == "ep01_odisseia"
    assert "animacao" in licao_gravada["departamento"]

    # 2. Inicializa o Episódio 2 (ex.: O Mito de Prometeu)
    estado_ep2 = criar_estado_inicial("ep02_prometeu", "Prometeu Acorrentado", "O Fogo Roubado")

    # Showrunner inicializa o episódio 2 e busca a memória persistente
    resultado_inicio_ep2 = showrunner_inicio_node(estado_ep2)
    licoes_ep2 = resultado_inicio_ep2["episodio"]["licoes_aplicadas"]

    # 3. Confere que a lição do episódio 1 foi recuperada e injetada no episódio 2
    assert len(licoes_ep2) >= 1
    textos_licoes = [l.get("regra", "") for l in licoes_ep2]
    assert any("tremulação da brasa em 2Hz" in r for r in textos_licoes)


def test_fluxo_completo_injecao_memoria_fim_a_fim():
    """Executa episódio completo provando que licoes_aplicadas é alimentado e mantido no estado."""
    limpar_operacoes_teste()
    checkpointer = MemorySaver()
    app = construir_grafo_showrunner(checkpointer=checkpointer)

    estado_inicial = criar_estado_inicial("ep_memoria_teste", "A Odisseia", "Polifemo")
    config = {"configurable": {"thread_id": "thread_memoria_01"}}

    # Inicia
    app.invoke(estado_inicial, config)
    estado = app.get_state(config)

    # Confere que o Showrunner já iniciou com as lições aplicadas ativas
    assert len(estado.values["episodio"]["licoes_aplicadas"]) > 0
    primeira_licao = estado.values["episodio"]["licoes_aplicadas"][0]
    assert "regra" in primeira_licao
    assert "departamento" in primeira_licao
