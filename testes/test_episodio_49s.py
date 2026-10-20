"""Teste Automatizado de Produção: Episódio de 49 Segundos de Ponta a Ponta."""

import pytest
from executar_episodio_49s import executar_producao_49s


def test_producao_completa_episodio_49_segundos():
    """Valida a execução de todos os 48 nós e 10 departamentos gerando episódio de 49s."""
    estado_final = executar_producao_49s()
    
    assert estado_final is not None
    assert estado_final["episodio"]["id"] == "ep_lume_49s_odisseia"
    
    # 8 planos somando exatamente 49.0s
    planos = estado_final["decupagem"]["planos"]
    assert len(planos) == 8
    duracao_total = sum(p["duracao_s"] for p in planos)
    assert duracao_total == 49.0
    
    # Todos os 8 planos têm Start Frames e Renders Firefly
    for p in planos:
        p_id = p["id"]
        assert p.get("storyboard") is not None
        render_info = estado_final["assets"]["planos"][p_id]["render"]
        assert render_info["status"] == "concluido"
        assert render_info["caminho"].endswith(".mp4")
        
    # Áudio em -14 LUFS
    assert estado_final["audio"]["lufs"] == -14.0
    
    # Master 4K
    assert estado_final["master"]["arquivo"]["resolucao"] in {"4K", "3840x2160"}
    
    # 6 QAs executados
    assert len(estado_final["qa"]) >= 6
    
    # Publicação estritamente privada
    assert estado_final["episodio"]["publicacao"]["status"] == "privado"
    
    # 5 Aprovações registradas
    assert len(estado_final["aprovacoes"]) == 5
    
    # Memória salva na Store
    assert len(estado_final["episodio"]["licoes_gravadas"]) >= 1
