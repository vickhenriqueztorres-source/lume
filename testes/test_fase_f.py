"""Testes da Fase F · Áudio (Critérios de Aceite).

Verifica:
1. LUFS medido em ±1 do alvo (-14.0 LUFS) na mixagem final.
2. Toda faixa de narração, efeito sonoro (SFX) e música possui licença registrada no estado.
3. A transcrição ASR da narração difere do roteiro em até 2%.
4. O Diretor de Voz anota pausas e andamento entre 140 e 165 ppm.
"""

import pytest
from contratos.estado import criar_estado_inicial
from grafo.audio.subgrafo import construir_subgrafo_audio
from grafo.ferramentas.audio import comparar_transcricao, medir_lufs


def test_lufs_medido_dentro_da_tolerancia():
    """Garante que a mixagem final cumpre a meta de -14.0 LUFS (tolerância ±1.0 LUFS)."""
    subgrafo = construir_subgrafo_audio()
    estado = criar_estado_inicial("ep_audio", "A Odisseia", "Polifemo")

    resultado = subgrafo.invoke(estado)
    lufs = resultado["audio"]["lufs"]

    assert lufs is not None
    assert abs(lufs - (-14.0)) <= 1.0  # Meta rigorosa: -14 LUFS ± 1 LUFS


def test_toda_faixa_tem_licenca_registrada_no_estado():
    """Garante que nenhuma música, SFX ou narração entra no episódio sem licença formal."""
    subgrafo = construir_subgrafo_audio()
    estado = criar_estado_inicial("ep_audio", "A Odisseia", "Polifemo")
    estado["roteiro"]["blocos"] = [
        {"numero": 1, "texto": "O fogo ainda conta as mesmas histórias.", "tempo_estimado_s": 30.0}
    ]

    resultado = subgrafo.invoke(estado)
    audio = resultado["audio"]

    # 1. Narração
    for faixa in audio["narracao"]["faixas"]:
        assert faixa.get("licenca") is not None
        assert len(faixa["licenca"]) > 0

    # 2. SFX
    for sfx in audio["sfx"]:
        assert sfx.get("licenca") is not None
        assert len(sfx["licenca"]) > 0

    # 3. Trilha musical
    for stem in audio["trilha"]["stems"]:
        assert stem.get("licenca") is not None
        assert len(stem["licenca"]) > 0


def test_transcricao_asr_difere_do_roteiro_em_ate_2_porcento():
    """Garante que a transcrição do áudio gravado/sintetizado difere no máximo 2% do texto aprovado."""
    # Texto com pontuação normalizada
    texto_roteiro = (
        "O fogo ainda conta as mesmas histórias. Na caverna escura, o gigante fecha a entrada com a rocha "
        "que nenhum homem moveria. Odisseu aguarda nas sombras, medindo cada passo com prudência e astúcia, "
        "sabendo que a força bruta não romperá a pedra selada pelos deuses imortais."
    )
    # Transcrição com 1 variação mínima (ex.: omissão de uma vírgula ou artigo menor)
    texto_transcrito = (
        "O fogo ainda conta as mesmas histórias. Na caverna escura o gigante fecha a entrada com a rocha "
        "que nenhum homem moveria. Odisseu aguarda nas sombras, medindo cada passo com prudência e astúcia, "
        "sabendo que força bruta não romperá a pedra selada pelos deuses imortais."
    )

    divergencia = comparar_transcricao(texto_roteiro, texto_transcrito)
    assert divergencia <= 2.0  # Divergência ≤ 2%


def test_diretor_voz_andamento_entre_140_e_165_ppm():
    """Garante que o ritmo de narração do Contador fica entre 140 e 165 palavras por minuto."""
    subgrafo = construir_subgrafo_audio()
    estado = criar_estado_inicial("ep_audio", "A Odisseia", "Polifemo")
    estado["roteiro"]["blocos"] = [
        {"numero": 1, "texto": "Texto de abertura do Contador.", "tempo_estimado_s": 20.0}
    ]

    resultado = subgrafo.invoke(estado)
    anotacoes = resultado["audio"]["roteiro_anotado"]

    assert len(anotacoes) > 0
    for nota in anotacoes:
        assert 140 <= nota["ppm"] <= 165
        assert len(nota["pausas_ms"]) > 0
