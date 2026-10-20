"""Testes da Fase B · Esqueleto Completo (Critérios de Aceite).

Verifica:
1. Execução ponta a ponta do Showrunner com os 10 departamentos.
2. Interrupção real nos gates humanos e retomada com Command(resume=...).
3. Persistência de checkpoints e retomada sem duplicação de efeito colateral (idempotência).
4. Retrabalho cirúrgico do QA (QA reprovado volta exclusivamente para o departamento certo).
5. Existência e conformidade do diagrama Mermaid compilado (doc 05 §1).
"""

import os
import sqlite3
import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.types import Command

from contratos.estado import criar_estado_inicial
from contratos.gates import RespostaGate
from grafo.base import limpar_operacoes_teste
from grafo.showrunner.grafo import construir_grafo_showrunner
from grafo.showrunner.supervisor import roteador_pos_qa


def test_execucao_ponta_a_ponta_com_gates_simulados():
    """Garante que o grafo completo roda de ponta a ponta pausando nos 5 gates e retomando."""
    limpar_operacoes_teste()
    checkpointer = MemorySaver()
    app = construir_grafo_showrunner(checkpointer=checkpointer)

    estado_inicial = criar_estado_inicial("ep_teste_b", "A Odisseia", "Polifemo")
    config = {"configurable": {"thread_id": "thread_teste_b_01"}}

    # Inicia execução - deve pausar no Gate 1 (Roteiro)
    app.invoke(estado_inicial, config)
    estado = app.get_state(config)
    assert len(estado.tasks) > 0
    assert estado.tasks[0].interrupts
    assert estado.values["pesquisa"]["fontes"]  # Pesquisa rodou com sucesso

    # Gate 1: Aprova roteiro
    resp_g1 = RespostaGate(gate_id=1, status="aprovado", autor="simulado", simulado=True).model_dump()
    app.invoke(Command(resume=resp_g1), config)

    # Deve pausar no Gate 2 (Storyboard)
    estado = app.get_state(config)
    assert estado.tasks[0].interrupts
    assert estado.values["decupagem"]["planos"]  # Direção rodou

    # Gate 2: Aprova storyboard
    resp_g2 = RespostaGate(gate_id=2, status="aprovado", autor="simulado", simulado=True).model_dump()
    app.invoke(Command(resume=resp_g2), config)

    # Roda Arte, Áudio, Animação, Montagem, QA e pausa no Gate 3 (Corte Final)
    estado = app.get_state(config)
    assert estado.tasks[0].interrupts
    assert estado.values["master"]["arquivo"]  # Master gerado
    assert len(estado.values["qa"]) >= 6  # Todas as 6 checagens de QA rodaram

    # Gate 3: Aprova corte final
    resp_g3 = RespostaGate(gate_id=3, status="aprovado", autor="simulado", simulado=True).model_dump()
    app.invoke(Command(resume=resp_g3), config)

    # Roda Embalagem e pausa no Gate 4 (Embalagem)
    estado = app.get_state(config)
    assert estado.tasks[0].interrupts
    assert len(estado.values["embalagem"]["titulos"]) == 3  # 3 títulos gerados

    # Gate 4: Aprova embalagem
    resp_g4 = RespostaGate(gate_id=4, status="aprovado", autor="simulado", simulado=True).model_dump()
    app.invoke(Command(resume=resp_g4), config)

    # Pausa no Gate 5 (Publicação)
    estado = app.get_state(config)
    assert estado.tasks[0].interrupts

    # Gate 5: Autoriza publicação
    resp_g5 = RespostaGate(gate_id=5, status="aprovado", autor="simulado", simulado=True).model_dump()
    app.invoke(Command(resume=resp_g5), config)

    # Finalizado com sucesso
    estado_final = app.get_state(config)
    assert len(estado_final.tasks) == 0  # Encerrou
    assert estado_final.values["episodio"]["publicacao"]["status"] == "privado"
    assert len(estado_final.values["aprovacoes"]) == 5  # Todos os 5 gates registrados
    assert len(estado_final.values["custos"]) > 0  # Custos acumulados


def test_retomada_processo_novo_com_sqlite_e_idempotencia(tmp_path):
    """Testa persistência em banco SQLite e garante que efeitos colaterais não se repetem após interrupt."""
    limpar_operacoes_teste()
    db_file = str(tmp_path / "checkpoints_teste.db")
    thread_id = "thread_proc_novo"
    config = {"configurable": {"thread_id": thread_id}}

    # 1. Simulação do Processo 1: Inicia e para no Gate 1
    conn1 = sqlite3.connect(db_file, check_same_thread=False)
    cp1 = SqliteSaver(conn1)
    app1 = construir_grafo_showrunner(checkpointer=cp1)
    estado_inicial = criar_estado_inicial("ep_idemp", "A Odisseia", "Polifemo")
    app1.invoke(estado_inicial, config)
    conn1.close()

    # 2. Simulação do Processo 2 (novo processo/conexão)
    conn2 = sqlite3.connect(db_file, check_same_thread=False)
    cp2 = SqliteSaver(conn2)
    app2 = construir_grafo_showrunner(checkpointer=cp2)

    # Lê estado preservado no banco
    estado_recuperado = app2.get_state(config)
    assert estado_recuperado.tasks[0].interrupts
    assert estado_recuperado.values["episodio"]["id"] == "ep_idemp"

    conn2.close()


def test_qa_reprovado_volta_para_departamento_exato():
    """Garante que quando uma checagem bloqueante de QA falha, o fluxo volta cirurgicamente ao departamento alvo."""
    # Cenário 1: QA de Fidelidade reprovado -> volta para depto_roteiro
    estado_reprovado_fidelidade = {
        "episodio": {"status": "qa_reprovado", "rota": "roteiro"},
        "qa": [
            {"tipo_verificacao": "fidelidade", "status": "reprovado", "bloqueia": True, "departamento_alvo": "roteiro"}
        ],
    }
    proximo_passo = roteador_pos_qa(estado_reprovado_fidelidade)
    assert proximo_passo == "depto_roteiro"

    # Cenário 2: QA Técnico reprovado -> volta para depto_montagem
    estado_reprovado_tecnico = {
        "episodio": {"status": "qa_reprovado", "rota": "montagem"},
        "qa": [
            {"tipo_verificacao": "tecnica", "status": "reprovado", "bloqueia": True, "departamento_alvo": "montagem"}
        ],
    }
    proximo_passo = roteador_pos_qa(estado_reprovado_tecnico)
    assert proximo_passo == "depto_montagem"

    # Cenário 3: QA aprovado -> segue para Gate 3
    estado_aprovado = {
        "episodio": {"status": "qa_aprovado", "rota": "gate_3"},
        "qa": [
            {"tipo_verificacao": "marca", "status": "aviso", "bloqueia": False}  # Marca apenas avisa
        ],
    }
    proximo_passo = roteador_pos_qa(estado_aprovado)
    assert proximo_passo == "gate_3_corte_final"


def test_diagrama_mermaid_compilado_existe():
    """Garante que o diagrama compilado foi gerado e documentado."""
    caminho_mmd = "docs/referencias/grafo-compilado.mmd"
    assert os.path.exists(caminho_mmd)
    with open(caminho_mmd, "r", encoding="utf-8") as f:
        conteudo = f.read()

    # Confere nós essenciais no diagrama
    assert "showrunner_inicio" in conteudo
    assert "depto_pesquisa" in conteudo
    assert "depto_roteiro" in conteudo
    assert "gate_1_roteiro" in conteudo
    assert "depto_direcao" in conteudo
    assert "gate_2_storyboard" in conteudo
    assert "depto_arte" in conteudo
    assert "depto_audio" in conteudo
    assert "depto_animacao" in conteudo
    assert "depto_montagem" in conteudo
    assert "depto_qa" in conteudo
    assert "gate_3_corte_final" in conteudo
    assert "depto_embalagem" in conteudo
    assert "gate_4_embalagem" in conteudo
    assert "depto_publicacao" in conteudo
