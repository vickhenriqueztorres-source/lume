"""Teste de Integração de Ponta a Ponta: Pipeline de Prompt de Imagem, CLI, Prompt de Vídeo e Firefly.

Verifica a amarração completa da cadeia:
Direção -> Engenheiro Prompt Imagem -> Gerador Imagem CLI -> Storyboard PNG ->
-> Engenheiro Prompt Vídeo -> Firefly Render MP4 -> Revisor Animação -> VFX.
"""

from pathlib import Path
import pytest

from contratos.estado import criar_estado_inicial
from contratos.plano import Plano
from grafo.animacao.subgrafo import construir_subgrafo_animacao, _RENDER_CACHE
from grafo.base import limpar_operacoes_teste
from grafo.direcao.subgrafo import construir_subgrafo_direcao


@pytest.fixture(autouse=True)
def setup_pipeline():
    limpar_operacoes_teste()
    _RENDER_CACHE.clear()
    yield
    _RENDER_CACHE.clear()


def test_pipeline_completo_direcao_para_animacao_firefly():
    """Garante que o fluxo completo de prompts cinemáticos e renderização via Firefly executa com 100% de consistência."""
    # 1. Prepara Estado com Roteiro
    estado = criar_estado_inicial("ep_odisseia_pipeline", "A Odisseia", "Polifemo")
    estado["roteiro"]["blocos"] = [
        {
            "numero": 1,
            "texto": "Na penumbra da caverna de calcário, Odisseu calcula cada passo sob a luz vacilante do fogo.",
            "marcacoes_cena": ["caverna_escura", "braseiro_aceso"],
        },
        {
            "numero": 2,
            "texto": "O gigante Polifemo bloqueia a saída com um rochedo intransponível.",
            "marcacoes_cena": ["rocha_pesada", "gigante_sombra"],
        },
        {
            "numero": 3,
            "texto": "A astúcia se prepara: a ponta da estaca incandesce entre as brasas ardentes.",
            "marcacoes_cena": ["estaca_brasa"],
        },
    ]

    # 2. Executa Subgrafo de Direção
    subgrafo_direcao = construir_subgrafo_direcao()
    res_direcao = subgrafo_direcao.invoke(estado)
    planos_direcao = res_direcao["decupagem"]["planos"]

    assert len(planos_direcao) >= 5

    # 3. Validações da etapa de Imagem pós-Direção
    for p in planos_direcao:
        # Prompt de Imagem foi gerado pelo Engenheiro de Imagem
        prompt_img = p.get("prompt_imagem")
        assert prompt_img is not None, f"Plano {p['id']} sem prompt_imagem"
        assert "#16110D" in prompt_img
        assert "#E85D04" in prompt_img

        # Imagem PNG física foi gerada e gravada no storyboard pelo Gerador CLI
        storyboard_path = p.get("storyboard")
        assert storyboard_path is not None, f"Plano {p['id']} sem storyboard"
        p_path = Path(storyboard_path)
        assert p_path.exists(), f"Arquivo de storyboard não encontrado: {p_path}"
        assert p_path.stat().st_size > 1000
        assert p_path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    # Atualiza o estado com a decupagem gerada
    estado["decupagem"] = res_direcao["decupagem"]

    # 4. Executa Subgrafo de Animação com Firefly
    subgrafo_animacao = construir_subgrafo_animacao()
    res_animacao = subgrafo_animacao.invoke(estado)
    assets_planos = res_animacao["assets"]["planos"]

    # 5. Validações da etapa de Vídeo e Render
    for p in planos_direcao:
        p_id = p["id"]
        # Informações de vídeo IA gravadas em assets.planos conforme Doc 08 §8
        assert p_id in assets_planos
        video_ia = assets_planos[p_id].get("video_ia", {})
        assert "aplicavel" in video_ia

        # Render Firefly foi concluído com sucesso a partir do start frame
        render_info = assets_planos[p_id]["render"]
        assert render_info["status"] == "concluido"
        assert render_info["hash"] is not None

        video_path = Path(render_info["caminho"])
        assert video_path.exists(), f"Vídeo do plano {p_id} não existe: {video_path}"
        assert video_path.stat().st_size > 100
        # Revisor aprovou o render
        assert assets_planos[p_id]["revisao"]["aprovado"] is True
