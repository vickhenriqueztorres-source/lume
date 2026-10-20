"""Testes da Fase D · Direção + Storyboard + Gate 2 (Critérios de Aceite).

Verifica:
1. Todo plano gerado cumpre estritamente o contrato do Doc 05 §5.
2. O Supervisor de direção de tela detecta e corrige caso errado plantado no teste (Odisseu olhando para a esquerda).
3. O Diretor de Arte categoriza marionetes em reaproveitadas e novas_a_criar consultando a Store.
4. O Storyboarder gera animatic de baixa resolução com metadados para o Gate 2.
"""

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from contratos.estado import criar_estado_inicial
from contratos.gates import RespostaGate
from contratos.plano import Plano
from grafo.base import limpar_operacoes_teste
from grafo.direcao.subgrafo import construir_subgrafo_direcao, supervisor_direcao_tela_node
from grafo.showrunner.grafo import construir_grafo_showrunner


def test_planos_cumprem_contrato_doc05_paragrafo_5():
    """Garante que todos os planos gerados em decupagem validam contra o modelo canônico Plano."""
    subgrafo = construir_subgrafo_direcao()
    estado = criar_estado_inicial("ep_odisseia", "A Odisseia", "Polifemo")

    resultado = subgrafo.invoke(estado)
    planos = resultado["decupagem"]["planos"]

    assert len(planos) >= 5
    for p in planos:
        plano_obj = Plano.model_validate(p)
        assert plano_obj.id.startswith("ep01_")
        assert plano_obj.duracao_s > 0
        assert plano_obj.tipo_plano in {"friso", "medio", "close", "insert", "escala", "contador"}
        assert plano_obj.proporcao in {"16:9", "2.39", "3:1"}
        assert plano_obj.camera.lente_mm in {35, 50, 85}
        assert 1 <= plano_obj.fogo.nivel <= 5
        assert p.get("storyboard") is not None


def test_supervisor_direcao_tela_corrige_caso_errado_plantado():
    """Garante que o Supervisor de direção de tela corrige caso errado plantado (Odisseu rumo a Ítaca deve ser 'dir')."""
    # Plantando caso intencionalmente errado: Odisseu com direcao='esq'
    plano_errado = {
        "id": "plano_teste_direcao",
        "marionetes": [
            {"id": "odisseu_v1", "distancia_fogo": 0.8, "direcao": "esq"},  # ERRO: herói deve ser 'dir'
            {"id": "polifemo_v1", "distancia_fogo": 0.2, "direcao": "dir"},  # ERRO: monstro deve ser 'esq'
        ],
    }
    estado = {
        "decupagem": {
            "planos": [plano_errado],
            "correcoes_direcao": [],
        }
    }

    resultado = supervisor_direcao_tela_node(estado)
    correcoes = resultado["decupagem"]["correcoes_direcao"]
    plano_corrigido = resultado["decupagem"]["planos"][0]

    # Confere correções registradas
    assert len(correcoes) == 2
    assert any(c["marionete_id"] == "odisseu_v1" and c["direcao_corrigida"] == "dir" for c in correcoes)
    assert any(c["marionete_id"] == "polifemo_v1" and c["direcao_corrigida"] == "esq" for c in correcoes)

    # Confere que o plano foi atualizado no estado
    for m in plano_corrigido["marionetes"]:
        if m["id"] == "odisseu_v1":
            assert m["direcao"] == "dir"
        elif m["id"] == "polifemo_v1":
            assert m["direcao"] == "esq"


def test_elenco_marca_novas_e_reaproveitadas():
    """Garante que o elenco distingue marionetes da biblioteca (reaproveitadas) e novas a criar."""
    limpar_operacoes_teste()
    subgrafo = construir_subgrafo_direcao()
    estado = criar_estado_inicial("ep_odisseia", "A Odisseia", "Polifemo")

    resultado = subgrafo.invoke(estado)
    elenco = resultado["elenco"]

    assert "odisseu_v1" in elenco["reaproveitadas"]
    assert any(m["id"] == "polifemo_v1" for m in elenco["novas_a_criar"])
    # Polifemo deve trazer especificação de estilo e furos de luz (Doc 03 §6.2)
    polifemo = next(m for m in elenco["novas_a_criar"] if m["id"] == "polifemo_v1")
    assert polifemo["estilo"] == "figura_negra"
    assert "olho_central" in polifemo["furos_luz"]


def test_direcao_chega_ao_gate_2_com_animatic():
    """Garante que o Showrunner executa Pesquisa, Roteiro, Gate 1, Direção e pausa no Gate 2 com animatic."""
    limpar_operacoes_teste()
    app = construir_grafo_showrunner(checkpointer=MemorySaver())

    estado_inicial = criar_estado_inicial("ep_teste_d", "A Odisseia", "Polifemo")
    config = {"configurable": {"thread_id": "thread_teste_d_01"}}

    # Executa até Gate 1
    app.invoke(estado_inicial, config)
    # Aprova Gate 1
    resp_g1 = RespostaGate(gate_id=1, status="aprovado", autor="teste_d").model_dump()
    app.invoke(Command(resume=resp_g1), config)

    # Deve pausar no Gate 2
    estado = app.get_state(config)
    assert estado.tasks[0].interrupts
    payload_g2 = estado.tasks[0].interrupts[0].value

    assert payload_g2["total_planos"] >= 5
    assert payload_g2["animatic_caminho"] is not None
    assert "ep01_animatic.mp4" in payload_g2["animatic_caminho"]
    assert payload_g2["color_script"] is not None
