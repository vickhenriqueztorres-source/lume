"""Bateria de Testes Robustos: Engenheiro de Prompt de Imagem (Subetapa 2).

Cobre:
1. Teste Unitário: Planos decupados recebem prompts cinematográficos consistentes com paleta LUME.
2. Teste de Estresse: Processamento em lote de 20 planos sem degradação.
3. Teste de Segurança: Sanitização rigorosa de caracteres nulos e controle de comprimento máximo.
4. Teste de Caos: Resiliência contra planos incompletos ou dados corrompidos.
"""

import pytest
from contratos.estado import criar_estado_inicial
from contratos.plano import Plano
from grafo.base import limpar_operacoes_teste
from grafo.direcao.engenheiro_prompt_imagem import (
    construir_prompt_cinematografico,
    engenheiro_prompt_imagem_node,
)


@pytest.fixture(autouse=True)
def setup_subetapa2():
    limpar_operacoes_teste()


def test_unit_prompt_imagem_generation():
    """1. Teste Unitário: Geração de prompt cinematográfico consistente para planos do episódio."""
    estado = criar_estado_inicial("ep_prompt_test", "A Odisseia", "Polifemo")
    planos = [
        Plano(
            id="ep01_p01_contador",
            bloco_roteiro=1,
            mundo="contador",
            proporcao="16:9",
            camera={"lente_mm": 85},
        ).model_dump(),
        Plano(
            id="ep01_p02_parede",
            bloco_roteiro=1,
            mundo="parede",
            proporcao="2.39",
            marionetes=[
                {"id": "odisseu_v1", "direcao": "dir"},
                {"id": "polifemo_v1", "direcao": "esq"},
            ],
            camera={"lente_mm": 35, "movimento": "pan_direita"},
            fogo={"nivel": 4},
        ).model_dump(),
    ]
    estado["decupagem"]["planos"] = planos

    res = engenheiro_prompt_imagem_node(estado)
    planos_res = res["decupagem"]["planos"]

    assert len(planos_res) == 2
    for p in planos_res:
        prompt = p.get("prompt_imagem")
        assert prompt is not None
        assert "#16110D" in prompt
        assert "#E85D04" in prompt
        assert "cinematic" in prompt.lower()

    # Checa semiótica no plano da parede
    p_parede = planos_res[1]
    assert "facing right towards home" in p_parede["prompt_imagem"]
    assert "Cyclops" in p_parede["prompt_imagem"]


def test_stress_batch_20_planos():
    """2. Teste de Estresse: Processamento de lote com 20 planos sequenciais."""
    estado = criar_estado_inicial("ep_stress", "A Odisseia", "Polifemo")
    planos = [
        Plano(
            id=f"ep_stress_p{i:02d}",
            bloco_roteiro=1 + (i % 3),
            mundo="parede" if i % 2 == 0 else "contador",
            duracao_s=4.0,
        ).model_dump()
        for i in range(20)
    ]
    estado["decupagem"]["planos"] = planos

    res = engenheiro_prompt_imagem_node(estado)
    planos_res = res["decupagem"]["planos"]
    assert len(planos_res) == 20
    for p in planos_res:
        assert len(p["prompt_imagem"]) > 100


def test_security_sanitization():
    """3. Teste de Segurança: Prevenção contra injeção e caracteres nulos."""
    plano_malicioso = {
        "id": "p_malicioso",
        "mundo": "parede\x00malware",
        "parede": "pedra; rm -rf /; \x00",
        "camera": {"lente_mm": 35},
    }
    prompt = construir_prompt_cinematografico(plano_malicioso)
    assert "\x00" not in prompt
    assert len(prompt) <= 1500


def test_chaos_missing_or_corrupted_fields():
    """4. Teste de Caos: Plano sem nenhum metadado padrão sobrevive com defaults cinemáticos."""
    plano_caotico = {"id": "p_caotico"}
    prompt = construir_prompt_cinematografico(plano_caotico)
    assert prompt is not None
    assert "#16110D" in prompt
    assert "Masterpiece cinematic frame" in prompt
