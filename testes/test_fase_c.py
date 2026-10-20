"""Testes da Fase C · Pesquisa + Roteiro + Gate 1 (Critérios de Aceite).

Verifica:
1. Roteiro chega ao Gate 1 com fontes por bloco (canto/verso).
2. Notas dos 3 revisores (retenção, fidelidade, tom) registradas no estado.
3. Nenhuma frase sem fato correspondente verificado em pesquisa.fatos.
4. Caso de reprovação de gíria detectado pelo Revisor de Tom.
5. Caso de reprovação de fato inventado detectado pelo Revisor de Fidelidade.
6. Caso de reprovação de gancho > 45s detectado pelo Editor de Retenção.
7. O ciclo de revisão executa refações respeitando o limite máximo de 3 voltas.
"""

import pytest
from langgraph.checkpoint.memory import MemorySaver

from contratos.estado import criar_estado_inicial
from grafo.base import limpar_operacoes_teste
from grafo.pesquisa.subgrafo import construir_subgrafo_pesquisa
from grafo.roteiro.subgrafo import (
    construir_subgrafo_roteiro,
    editor_retencao_node,
    revisor_fidelidade_node,
    revisor_tom_node,
)
from grafo.showrunner.grafo import construir_grafo_showrunner


def test_pesquisa_e_roteiro_chegam_ao_gate_1_com_fontes_e_fatos():
    """Garante que 'A Odisseia' gera fontes, fatos e chega ao Gate 1 com canto/verso por bloco."""
    limpar_operacoes_teste()
    app = construir_grafo_showrunner(checkpointer=MemorySaver())

    estado_inicial = criar_estado_inicial("ep_odisseia_c", "A Odisseia", "Polifemo")
    config = {"configurable": {"thread_id": "thread_fase_c_01"}}

    # Inicia até o Gate 1
    app.invoke(estado_inicial, config)
    estado = app.get_state(config)

    # 1. Parou no Gate 1
    assert estado.tasks[0].interrupts
    payload_gate_1 = estado.tasks[0].interrupts[0].value
    assert payload_gate_1["titulo"] == "A Odisseia"

    # 2. Fontes por bloco com canto/verso
    blocos = estado.values["roteiro"]["blocos"]
    assert len(blocos) > 0
    for b in blocos:
        assert "canto_verso" in b
        assert "Canto IX" in b["canto_verso"]
        assert len(b["fatos_referenciados"]) > 0

    # 3. Notas dos 3 revisores presentes no estado
    notas = estado.values["roteiro"]["notas"]
    assert "retencao" in notas and len(notas["retencao"]) > 0
    assert "fidelidade" in notas and len(notas["fidelidade"]) > 0
    assert "tom" in notas and len(notas["tom"]) > 0

    # 4. Todos os revisores aprovaram a versão canônica (sem bloqueios)
    for tipo, lista in notas.items():
        assert not any("[BLOQUEANTE]" in str(nota) for nota in lista)


def test_revisor_tom_reprova_giria():
    """Garante que gíria ('aí galera', 'mano', 'doidão') é reprovada com bloqueio."""
    estado = {
        "roteiro": {
            "blocos": [
                {
                    "numero": 1,
                    "texto": "E aí galera, mano, Polifemo ficou doidão na caverna.",
                    "tempo_estimado_s": 25.0,
                    "fatos_referenciados": ["fato_01"],
                }
            ],
            "notas": {},
        }
    }
    resultado = revisor_tom_node(estado)
    notas_tom = resultado["roteiro"]["notas"]["tom"]
    assert any("[BLOQUEANTE]" in n and "gíria proibida" in n for n in notas_tom)


def test_revisor_fidelidade_reprova_fato_inventado():
    """Garante que fato sem correspondência em pesquisa.fatos é reprovado com bloqueio."""
    estado = {
        "pesquisa": {
            "fatos": [{"id": "fato_01", "descricao": "Odisseu oferece vinho"}]
        },
        "roteiro": {
            "blocos": [
                {
                    "numero": 1,
                    "texto": "Odisseu usou uma bazuca mágica.",
                    "tempo_estimado_s": 30.0,
                    "fatos_referenciados": ["fato_inexistente_bazuca"],
                }
            ],
            "notas": {},
        }
    }
    resultado = revisor_fidelidade_node(estado)
    notas_fidelidade = resultado["roteiro"]["notas"]["fidelidade"]
    assert any("[BLOQUEANTE]" in n and "fato inventado" in n for n in notas_fidelidade)


def test_editor_retencao_reprova_gancho_maior_que_45s():
    """Garante que gancho inicial acima de 45 segundos é reprovado com bloqueio."""
    estado = {
        "roteiro": {
            "blocos": [
                {
                    "numero": 1,
                    "texto": "Uma longa e interminável introdução sem conflito...",
                    "tempo_estimado_s": 65.0,  # 65s > 45s
                    "fatos_referenciados": ["fato_01"],
                }
            ],
            "notas": {},
        }
    }
    resultado = editor_retencao_node(estado)
    notas_retencao = resultado["roteiro"]["notas"]["retencao"]
    assert any("[BLOQUEANTE]" in n and "Gancho inicial excede 45 segundos" in n for n in notas_retencao)


def test_ciclo_revisao_refaz_roteiro_e_limita_3_voltas():
    """Garante que quando há bloqueio, o ciclo refaz e converge sem loop infinito."""
    subgrafo = construir_subgrafo_roteiro()
    estado_com_falha = {
        "pesquisa": {"fontes": [{"canto_verso": "Canto IX, 105"}], "fatos": [{"id": "fato_01"}]},
        "roteiro": {
            "_forcar_caso_teste": "giria",  # Primeira rodada força gíria para testar refação
            "voltas": 0,
            "notas": {},
        },
        "episodio": {"id": "ep01"},
        "custos": [],
    }

    resultado_final = subgrafo.invoke(estado_com_falha)
    assert resultado_final["roteiro"]["voltas"] <= 3
    # Após a refação, a versão limpa é aprovada
    notas = resultado_final["roteiro"]["notas"]
    assert not any("[BLOQUEANTE]" in str(n) for n in notas.get("tom", []))
