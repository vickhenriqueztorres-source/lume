"""Testes da Fase G · Montagem + QA (Critérios de Aceite).

Verifica:
1. Master 4K gerado com capítulos, legendas SRT e duração calculada.
2. Cada um dos 5 QAs bloqueantes reprova um defeito plantado e aponta o retrabalho para o departamento certo:
   - QA Técnico -> Montagem
   - QA Continuidade -> Animação
   - QA Fidelidade -> Roteiro
   - QA Direitos -> Áudio
   - QA Originalidade -> Roteiro
3. O QA de Marca apenas emite aviso (bloqueia=False), sem barrar a aprovação geral do QA.
"""

import pytest
from contratos.estado import criar_estado_inicial
from grafo.montagem.subgrafo import construir_subgrafo_montagem
from grafo.qa.subgrafo import (
    construir_subgrafo_qa,
    qa_continuidade_node,
    qa_direitos_node,
    qa_fidelidade_node,
    qa_marca_node,
    qa_originalidade_node,
    qa_tecnico_node,
)


def test_master_gerado_com_capitulos_e_legendas():
    """Garante que a Montagem produz arquivo master 4K, marcadores de capítulo e legendas SRT."""
    subgrafo = construir_subgrafo_montagem()
    estado = criar_estado_inicial("ep_montagem", "A Odisseia", "Polifemo")
    estado["decupagem"]["planos"] = [
        {"id": "p01", "duracao_s": 5.0},
        {"id": "p02", "duracao_s": 6.5},
    ]

    resultado = subgrafo.invoke(estado)
    master = resultado["master"]

    assert master["arquivo"]["resolucao"] in {"4K", "3840x2160"}
    assert "ep01_master_4k.mp4" in master["arquivo"]["caminho"]
    assert len(master["capitulos"]) >= 4
    assert "pt-BR" in master["legendas"]
    assert "O fogo ainda conta as mesmas histórias" in master["legendas"]["pt-BR"]


def test_cada_qa_bloqueante_reprova_defeito_e_aponta_departamento_certo():
    """Garante que cada um dos 5 QAs bloqueantes reprova e indica cirurgicamente seu departamento alvo."""
    # 1. QA Técnico: falha de loudness ou resolução -> aponta montagem
    estado_tecnico_erro = {
        "audio": {"lufs": -24.0},  # Erro de loudness
        "master": {"arquivo": {"resolucao": "720p"}},  # Erro de resolução
        "qa_testes": {"forcar_falha_tecnico": True},
        "custos": [],
    }
    res_tecnico = qa_tecnico_node(estado_tecnico_erro)["qa"][0]
    assert res_tecnico["status"] == "reprovado"
    assert res_tecnico["bloqueia"] is True
    assert res_tecnico["departamento_alvo"] == "montagem"

    # 2. QA Continuidade: herói olhando para trás (esq) -> aponta animacao
    estado_continuidade_erro = {
        "decupagem": {
            "planos": [
                {"id": "p01", "marionetes": [{"id": "odisseu_v1", "direcao": "esq"}]}
            ]
        },
        "qa_testes": {"forcar_falha_continuidade": True},
        "custos": [],
    }
    res_continuidade = qa_continuidade_node(estado_continuidade_erro)["qa"][0]
    assert res_continuidade["status"] == "reprovado"
    assert res_continuidade["bloqueia"] is True
    assert res_continuidade["departamento_alvo"] == "animacao"

    # 3. QA Fidelidade: afirmação sem fatos -> aponta roteiro
    estado_fidelidade_erro = {
        "pesquisa": {"fatos": []},  # Sem fatos canônicos
        "qa_testes": {"forcar_falha_fidelidade": True},
        "custos": [],
    }
    res_fidelidade = qa_fidelidade_node(estado_fidelidade_erro)["qa"][0]
    assert res_fidelidade["status"] == "reprovado"
    assert res_fidelidade["bloqueia"] is True
    assert res_fidelidade["departamento_alvo"] == "roteiro"

    # 4. QA Direitos: faixa sem licença -> aponta audio
    estado_direitos_erro = {
        "audio": {
            "sfx": [{"id": "sfx_pirata", "licenca": None}],  # Sem licença
            "trilha": {"stems": []},
        },
        "qa_testes": {"forcar_falha_direitos": True},
        "custos": [],
    }
    res_direitos = qa_direitos_node(estado_direitos_erro)["qa"][0]
    assert res_direitos["status"] == "reprovado"
    assert res_direitos["bloqueia"] is True
    assert res_direitos["departamento_alvo"] == "audio"

    # 5. QA Originalidade: sem registros de gates humanos -> aponta roteiro
    estado_originalidade_erro = {
        "aprovacoes": [],  # Sem aprovações humanas registradas
        "qa_testes": {"forcar_falha_originalidade": True},
        "custos": [],
    }
    res_originalidade = qa_originalidade_node(estado_originalidade_erro)["qa"][0]
    assert res_originalidade["status"] == "reprovado"
    assert res_originalidade["bloqueia"] is True
    assert res_originalidade["departamento_alvo"] == "roteiro"


def test_qa_marca_emite_apenas_aviso_sem_bloquear():
    """Garante que violação nas diretrizes de marca emite status 'aviso' com bloqueia=False."""
    estado_marca_aviso = {
        "color_script": {"geral": {"teto_brasa_pct": 12.0}},  # Brasa 12% > 5% do teto
        "qa_testes": {"forcar_aviso_marca": True},
        "custos": [],
    }
    res_marca = qa_marca_node(estado_marca_aviso)["qa"][0]

    assert res_marca["status"] == "aviso"
    assert res_marca["bloqueia"] is False  # Regra inegociável: QA de marca NUNCA bloqueia
    assert res_marca["departamento_alvo"] is None


def test_subgrafo_qa_consolida_aprovacao_quando_apenas_marca_avisa():
    """Garante que quando apenas o QA de marca emite aviso, o QA geral é aprovado para o Gate 3."""
    subgrafo = construir_subgrafo_qa()
    estado = criar_estado_inicial("ep_qa", "A Odisseia", "Polifemo")
    # Configura dados válidos de departamentos anteriores
    estado["aprovacoes"] = [{"gate_id": 1}, {"gate_id": 2}]
    estado["master"]["arquivo"] = {"resolucao": "3840x2160"}
    estado["audio"]["lufs"] = -14.0
    estado["audio"]["sfx"] = [{"id": "sfx_fogo", "licenca": "CC0"}]
    estado["pesquisa"]["fatos"] = [{"id": "fato_01", "descricao": "Odisseu cega Polifemo"}]
    # Provoca aviso exclusivamente no QA de marca
    estado["color_script"]["geral"]["teto_brasa_pct"] = 8.0

    resultado = subgrafo.invoke(estado)
    status_ep = resultado["episodio"]["status"]
    rota = resultado["episodio"]["rota"]

    # Como marca não bloqueia, o QA geral aprova e aponta para o Gate 3
    assert status_ep == "qa_aprovado"
    assert rota == "gate_3"
