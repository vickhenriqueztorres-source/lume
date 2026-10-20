"""Episódio de Fumaça (5 Planos, 60 s de Duração) - Doc 05 §9 e Doc 06 §3.

Executa o fluxo completo do estúdio LUME de ponta a ponta:
Tema: 'A Odisseia: Odisseu e Polifemo'
Pauta -> Pesquisa -> Roteiro -> Gate 1 -> Direção (5 planos) -> Gate 2 ->
Arte & Animação (Blender) // Áudio (-14 LUFS) -> Montagem (Master 4K) -> QA -> Gate 3 ->
Embalagem (3 títulos, 3 thumbs) -> Gate 4 -> Gate 5 -> Publicação Privada -> Memória na Store.
"""

import os
import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from contratos.estado import criar_estado_inicial
from contratos.gates import RespostaGate
from contratos.plano import Plano
from grafo.base import limpar_operacoes_teste
from grafo.showrunner.grafo import construir_grafo_showrunner


def test_episodio_de_fumaca_completo_60s():
    """Roda o episódio de fumaça de 5 planos de ponta a ponta com fakes determinísticos."""
    limpar_operacoes_teste()
    checkpointer = MemorySaver()
    app = construir_grafo_showrunner(checkpointer=checkpointer)

    estado_inicial = criar_estado_inicial(
        id_episodio="ep_fumaca_odisseia_01",
        mito="A Odisseia",
        angulo="A Armadilha do Cíclope e a Astúcia de Ninguém",
        duracao_alvo_s=60.0,  # 60 segundos
        idioma="pt-BR",
    )
    config = {"configurable": {"thread_id": "thread_fumaca_completa_01"}}

    # =========================================================================
    # 1. Início -> Pesquisa -> Roteiro -> Pausa no Gate 1
    # =========================================================================
    app.invoke(estado_inicial, config)
    estado = app.get_state(config)
    assert estado.tasks[0].interrupts
    assert estado.tasks[0].name == "gate_1_roteiro"

    # Confere entregas de Pesquisa e Roteiro
    assert len(estado.values["pesquisa"]["fontes"]) >= 1
    assert "Canto IX" in estado.values["pesquisa"]["fontes"][0]["canto_verso"]
    assert len(estado.values["pesquisa"]["fatos"]) >= 2
    assert len(estado.values["roteiro"]["blocos"]) >= 2

    # Notas dos 3 revisores
    notas = estado.values["roteiro"]["notas"]
    assert "retencao" in notas and "fidelidade" in notas and "tom" in notas

    # =========================================================================
    # 2. Resposta do Gate 1 (Roteiro Aprovado) -> Direção -> Pausa no Gate 2
    # =========================================================================
    resp_g1 = RespostaGate(
        gate_id=1,
        status="aprovado",
        autor="operador_fumaca",
        comentarios="Roteiro canônico aprovado para decupagem.",
        simulado=True,
    ).model_dump()
    app.invoke(Command(resume=resp_g1), config)

    estado = app.get_state(config)
    assert estado.tasks[0].interrupts
    assert estado.tasks[0].name == "gate_2_storyboard"

    # Confere entregas de Direção (5 planos somando ~23s a 60s)
    planos = estado.values["decupagem"]["planos"]
    assert len(planos) == 5
    for p in planos:
        Plano.model_validate(p)  # Valida contrato de cada plano

    # Color script e elenco
    assert estado.values["color_script"]["cenas"]
    assert "odisseu_v1" in estado.values["elenco"]["marionetes_usadas"]

    # =========================================================================
    # 3. Resposta do Gate 2 (Storyboard Aprovado) -> Produção Paralela -> QA -> Pausa no Gate 3
    # =========================================================================
    resp_g2 = RespostaGate(
        gate_id=2,
        status="aprovado",
        autor="operador_fumaca",
        comentarios="Animatic e decupagem aprovados para produção de cena.",
        simulado=True,
    ).model_dump()
    app.invoke(Command(resume=resp_g2), config)

    estado = app.get_state(config)
    assert estado.tasks[0].interrupts
    assert estado.tasks[0].name == "gate_3_corte_final"

    # Confere Arte e Animação
    assert estado.values["assets"]["marionetes"]
    assert estado.values["assets"]["planos"]
    # Confere Áudio
    assert estado.values["audio"]["mix"]
    assert estado.values["audio"]["lufs"] == -14.0
    # Confere Montagem
    assert estado.values["master"]["arquivo"]["resolucao"] in {"4K", "3840x2160"}
    assert len(estado.values["master"]["capitulos"]) >= 4
    # Confere QA
    assert len(estado.values["qa"]) >= 6
    assert estado.values["episodio"]["status"] == "qa_aprovado"

    # =========================================================================
    # 4. Resposta do Gate 3 (Corte Final Aprovado) -> Embalagem -> Pausa no Gate 4
    # =========================================================================
    resp_g3 = RespostaGate(
        gate_id=3,
        status="aprovado",
        autor="operador_fumaca",
        comentarios="Master 4K e mix -14 LUFS aprovados para embalagem.",
        simulado=True,
    ).model_dump()
    app.invoke(Command(resume=resp_g3), config)

    estado = app.get_state(config)
    assert estado.tasks[0].interrupts
    assert estado.tasks[0].name == "gate_4_embalagem"

    # Confere Embalagem
    assert len(estado.values["embalagem"]["titulos"]) == 3
    assert len(estado.values["embalagem"]["thumbs"]) == 3
    assert len(estado.values["embalagem"]["ranking"]) == 3

    # =========================================================================
    # 5. Resposta do Gate 4 (Embalagem Aprovada) -> Pausa no Gate 5 (Publicação)
    # =========================================================================
    resp_g4 = RespostaGate(
        gate_id=4,
        status="aprovado",
        autor="operador_fumaca",
        comentarios="Título e Thumbnail vencedora aprovados.",
        simulado=True,
    ).model_dump()
    app.invoke(Command(resume=resp_g4), config)

    estado = app.get_state(config)
    assert estado.tasks[0].interrupts
    assert estado.tasks[0].name == "gate_5_publicacao"

    # =========================================================================
    # 6. Resposta do Gate 5 (Autorização) -> Publicação Privada -> Conclusão
    # =========================================================================
    resp_g5 = RespostaGate(
        gate_id=5,
        status="aprovado",
        autor="operador_fumaca",
        comentarios="Autorizado agendamento do vídeo em modo privado.",
        simulado=True,
    ).model_dump()
    app.invoke(Command(resume=resp_g5), config)

    # Estado final concluído
    estado_final = app.get_state(config)
    assert len(estado_final.tasks) == 0  # Grafo finalizou normalmente

    # Validações finais de integridade
    pub = estado_final.values["episodio"]["publicacao"]
    assert pub["status"] == "privado"
    assert pub["upload_url"].startswith("https://")
    assert len(estado_final.values["aprovacoes"]) == 5
    assert len(estado_final.values["custos"]) >= 10
    assert len(estado_final.values["episodio"]["licoes_gravadas"]) >= 1
