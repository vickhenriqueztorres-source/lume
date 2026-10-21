"""Teste Automatizado de Produção: Episódio de 45 Segundos de Ponta a Ponta."""

from pathlib import Path
import pytest
from executar_episodio_45s import executar_producao_45s


def test_producao_completa_episodio_45_segundos():
    """Valida a execução de todos os nós e 10 departamentos gerando episódio de 45s."""
    estado_final, detalhes_video = executar_producao_45s()

    assert estado_final is not None
    assert estado_final["episodio"]["id"] == "ep_lume_45s_odisseia"

    # 8 planos somando exatamente 45.0s
    planos = estado_final["decupagem"]["planos"]
    assert len(planos) == 8
    duracao_total = sum(p["duracao_s"] for p in planos)
    assert duracao_total == 45.0

    # Todos os 8 planos têm Prompts de Imagem, Start Frames e Renders Firefly com Prompt de Vídeo
    assets_planos = estado_final["assets"]["planos"]
    for p in planos:
        p_id = p["id"]
        assert p.get("prompt_imagem") is not None
        assert p.get("storyboard") is not None
        assert p_id in assets_planos
        assert "video_ia" in assets_planos[p_id]
        render_info = assets_planos[p_id]["render"]
        assert render_info["status"] == "concluido"
        assert Path(render_info["caminho"]).exists()

    # Áudio em -14 LUFS
    assert estado_final["audio"]["lufs"] == -14.0

    # Master 4K
    caminho_master = Path("storage_local/master/ep_lume_45s_master_4k.mp4")
    assert caminho_master.exists()
    assert caminho_master.stat().st_size > 500

    # 6 QAs executados
    assert len(estado_final["qa"]) >= 6

    # Publicação estritamente privada
    assert estado_final["episodio"]["publicacao"]["status"] == "privado"

    # 5 Aprovações registradas
    assert len(estado_final["aprovacoes"]) == 5

    # Memória salva na Store
    assert len(estado_final["episodio"]["licoes_gravadas"]) >= 1
