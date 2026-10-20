"""Bateria de Testes Robustos: Integração Firefly & Start Frames no Subgrafo de Animação (Subetapa 4).

Cobre:
1. Teste Unitário: Execução do subgrafo de animação orquestrando StartFrameGenerator e FireflyEngine.
2. Teste de Estresse: Cache Hit determinístico na reexecução sem re-renderizar arquivos existentes.
3. Teste de Segurança: Integridade e isolamento dos caminhos de renderização em storage_local/renders.
4. Teste de Caos: 3ª falha simulada é escalada para fila humana sem travar os demais planos do lote.
"""

import os
from pathlib import Path
import pytest
from contratos.estado import criar_estado_inicial
from contratos.plano import Plano
from grafo.animacao.subgrafo import construir_subgrafo_animacao, _RENDER_CACHE
from grafo.base import limpar_operacoes_teste


@pytest.fixture(autouse=True)
def setup_subetapa4():
    limpar_operacoes_teste()
    _RENDER_CACHE.clear()
    yield
    _RENDER_CACHE.clear()


def test_unit_subgrafo_animacao_with_firefly():
    """1. Teste Unitário: O subgrafo de animação gera start frames e vídeos MP4 via FireflyEngine."""
    subgrafo = construir_subgrafo_animacao()
    estado = criar_estado_inicial("ep_teste_firefly", "Mito Teste", "Angulo Teste")

    # Adiciona 3 planos decupados com movimento e proporção distintos
    planos = [
        Plano(
            id=f"ep_test_p0{i}",
            bloco_roteiro=1,
            mundo="parede",
            duracao_s=3.0 + float(i),
            camera={"movimento": f"movimento_cam_{i}", "lente_mm": 50},
        ).model_dump()
        for i in range(1, 4)
    ]
    estado["decupagem"]["planos"] = planos

    res = subgrafo.invoke(estado)
    assets_planos = res["assets"]["planos"]

    assert len(assets_planos) == 3
    for i in range(1, 4):
        p_id = f"ep_test_p0{i}"
        render_info = assets_planos[p_id]["render"]
        assert render_info["status"] == "concluido"
        assert render_info["cache_hit"] is False
        assert Path(render_info["caminho"]).exists()
        assert Path(render_info["caminho"]).stat().st_size > 100
        assert assets_planos[p_id]["revisao"]["aprovado"] is True


def test_stress_cache_hit_on_subsequent_runs():
    """2. Teste de Estresse: Segunda execução do subgrafo de animação reaproveita cache_hit=True."""
    subgrafo = construir_subgrafo_animacao()
    estado = criar_estado_inicial("ep_cache_stress", "Mito Teste", "Angulo Teste")

    planos = [
        Plano(
            id=f"ep_cache_p0{i}",
            bloco_roteiro=1,
            mundo="parede",
            duracao_s=3.0 + float(i),
        ).model_dump()
        for i in range(1, 4)
    ]
    estado["decupagem"]["planos"] = planos

    # Primeira execução: gera e armazena no cache
    res1 = subgrafo.invoke(estado)
    for p_id in [f"ep_cache_p0{i}" for i in range(1, 4)]:
        assert res1["assets"]["planos"][p_id]["render"]["cache_hit"] is False

    # Segunda execução: planos idênticos devem obter cache_hit=True
    res2 = subgrafo.invoke(estado)
    for p_id in [f"ep_cache_p0{i}" for i in range(1, 4)]:
        assert res2["assets"]["planos"][p_id]["render"]["cache_hit"] is True


def test_security_rendered_paths_containment():
    """3. Teste de Segurança: Garante que os caminhos gerados estão contidos em storage_local."""
    subgrafo = construir_subgrafo_animacao()
    estado = criar_estado_inicial("ep_sec", "Mito Teste", "Angulo Teste")
    estado["decupagem"]["planos"] = [
        Plano(id="ep_sec_p01", bloco_roteiro=1, mundo="parede").model_dump()
    ]

    res = subgrafo.invoke(estado)
    caminho = res["assets"]["planos"]["ep_sec_p01"]["render"]["caminho"]

    assert ".." not in caminho
    assert "storage_local" in caminho


def test_chaos_third_failure_escalation_isolated():
    """4. Teste de Caos: 3ª falha em um plano é escalada sem afetar planos sadios."""
    subgrafo = construir_subgrafo_animacao()

    p1 = Plano(id="plano_bom_1", bloco_roteiro=1).model_dump()
    p2_falha = Plano(id="plano_falha_2", bloco_roteiro=1).model_dump()

    estado = {
        "decupagem": {"planos": [p1, p2_falha]},
        "assets": {
            "planos": {
                "plano_falha_2": {
                    "render": {
                        "tentativas": 2,
                        "forcar_falha": True,
                    }
                }
            }
        },
        "episodio": {"id": "ep_caos", "fila_humana": []},
        "custos": [],
        "erros": [],
    }

    res = subgrafo.invoke(estado)
    assets = res["assets"]["planos"]

    # Plano bom é aprovado
    assert assets["plano_bom_1"]["revisao"]["aprovado"] is True

    # Plano com erro acumulado na 3ª falha é reprovado e escalado
    assert assets["plano_falha_2"]["revisao"]["aprovado"] is False
    assert any(
        e.get("autor_no") == "animacao.revisor_plano" and e.get("decisao") == "escalar"
        for e in res.get("erros", [])
    )
