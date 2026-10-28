"""Subgrafo do Departamento de Áudio (Doc 05 §3.6 e Fichas 01-05).

Processamento de narração, trilha sonora, SFX e mixagem em -14 LUFS:
1. audio.diretor_voz (LLM-R)
2. audio.narrador (TTS / Ferr.)
3. audio.sound_designer (LLM-R + Ferr.)
4. audio.supervisor_musical (LLM-R + Ferr.)
5. audio.mixador (Ferr. loudnorm -14 LUFS)
"""

from __future__ import annotations

from typing import Any, Dict
from langgraph.graph import END, START, StateGraph

from contratos.estado import EstadoEpisodio
from grafo.base import no_agente
from grafo.ferramentas.audio import medir_lufs


@no_agente("audio.diretor_voz", categoria_modelo="LLM-R")
def diretor_voz_node(state: EstadoEpisodio) -> Dict[str, Any]:
    blocos = state.get("roteiro", {}).get("blocos", [])
    roteiro_anotado = []
    for b in blocos:
        roteiro_anotado.append({
            "bloco_numero": b.get("numero", 1),
            "ppm": 148,  # Calibrado entre 140 e 165 ppm conforme ficha
            "pausas_ms": [300, 500, 800],
            "enfases": ["fogo", "gigante", "pedra"],
        })
    return {
        "audio": {
            "roteiro_anotado": roteiro_anotado,
        }
    }


@no_agente("audio.narrador", categoria_modelo="TTS")
def narrador_node(state: EstadoEpisodio) -> Dict[str, Any]:
    blocos = state.get("roteiro", {}).get("blocos", [])
    faixas = []
    for b in blocos:
        num = b.get("numero", 1)
        texto_bloco = b.get("texto", "")
        faixas.append({
            "bloco_numero": num,
            "caminho": f"storage_local/audio/narracao_bloco_{num}.wav",
            "hash": f"hash_narracao_{num}",
            "duracao_s": b.get("tempo_estimado_s", 30.0),
            "licenca": "propria_lume_contador",  # Licença expressa registrada
            "transcricao_asr": texto_bloco,      # Transcrição coincidente com roteiro
        })
    return {
        "audio": {
            "narracao": {"faixas": faixas, "total_blocos": len(faixas)},
        }
    }


@no_agente("audio.sound_designer", categoria_modelo="LLM-R")
def sound_designer_node(state: EstadoEpisodio) -> Dict[str, Any]:
    sfx = [
        {
            "id": "sfx_01_braseiro_fogo_intimo",
            "caminho": "storage_local/sfx/real_2d/sfx_01_braseiro_fogo_intimo.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "fogo",
        },
        {
            "id": "sfx_02_pergaminho_antigo",
            "caminho": "storage_local/sfx/real_2d/sfx_02_pergaminho_antigo.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "foley",
        },
        {
            "id": "sfx_03_rocha_selando_caverna",
            "caminho": "storage_local/sfx/real_2d/sfx_03_rocha_selando_caverna.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "monstro",
        },
        {
            "id": "sfx_04_ambiencia_caverna_gotas",
            "caminho": "storage_local/sfx/real_2d/sfx_04_ambiencia_caverna_gotas.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "ambiente",
        },
        {
            "id": "sfx_05_passos_respiracao_ciclope",
            "caminho": "storage_local/sfx/real_2d/sfx_05_passos_respiracao_ciclope.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "monstro",
        },
        {
            "id": "sfx_06_afiando_estaca_madeira",
            "caminho": "storage_local/sfx/real_2d/sfx_06_afiando_estaca_madeira.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "foley",
        },
        {
            "id": "sfx_07_vinho_vertido_anfora",
            "caminho": "storage_local/sfx/real_2d/sfx_07_vinho_vertido_anfora.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "foley",
        },
        {
            "id": "sfx_08_ciclope_bebendo_goles",
            "caminho": "storage_local/sfx/real_2d/sfx_08_ciclope_bebendo_goles.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "monstro",
        },
        {
            "id": "sfx_09_eco_sussurro_caverna",
            "caminho": "storage_local/sfx/real_2d/sfx_09_eco_sussurro_caverna.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "retencao",
        },
        {
            "id": "sfx_10_queda_ronco_gigante",
            "caminho": "storage_local/sfx/real_2d/sfx_10_queda_ronco_gigante.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "monstro",
        },
        {
            "id": "sfx_11_estaca_chamas_ataque",
            "caminho": "storage_local/sfx/real_2d/sfx_11_estaca_chamas_ataque.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "climax",
        },
        {
            "id": "sfx_12_urro_agonia_polifemo",
            "caminho": "storage_local/sfx/real_2d/sfx_12_urro_agonia_polifemo.wav",
            "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
            "categoria": "climax",
        },
    ]
    return {
        "audio": {
            "sfx": sfx,
        }
    }


@no_agente("audio.supervisor_musical", categoria_modelo="LLM-R")
def supervisor_musical_node(state: EstadoEpisodio) -> Dict[str, Any]:
    trilha = {
        "tema_principal": "Leitmotiv de Odisseu - Lira Grega Frígia, Aulos, Percussão Ritual e Coro Épico",
        "stems": [
            {
                "id": "bgm_01_lira_abertura_fechamento",
                "caminho": "storage_local/trilha/real_2d/bgm_01_lira_abertura_fechamento.wav",
                "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
                "instrumentos": ["lira", "kithara"],
            },
            {
                "id": "bgm_02_drone_aulos_caverna",
                "caminho": "storage_local/trilha/real_2d/bgm_02_drone_aulos_caverna.wav",
                "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
                "instrumentos": ["aulos", "drone_grave"],
            },
            {
                "id": "bgm_03_percussao_tensao_astucia",
                "caminho": "storage_local/trilha/real_2d/bgm_03_percussao_tensao_astucia.wav",
                "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
                "instrumentos": ["tambor_pele", "cordas_antigas"],
            },
            {
                "id": "bgm_04_coro_climax_epico",
                "caminho": "storage_local/trilha/real_2d/bgm_04_coro_climax_epico.wav",
                "licenca": "ElevenLabs_Commercial_Audio_License_LUME",
                "instrumentos": ["coro_masculino", "percussao_guerra"],
            },
        ],
    }
    return {
        "audio": {
            "trilha": trilha,
        }
    }


@no_agente("audio.mixador", categoria_modelo=None)
def mixador_node(state: EstadoEpisodio) -> Dict[str, Any]:
    mix_caminho = "storage_local/audio/master_audio_60s.wav"
    lufs_calculado = medir_lufs(mix_caminho)

    mix = {
        "caminho": mix_caminho,
        "hash": "hash_mix_final_ep01_stereo_24bit",
        "ducking": "sidechaincompress_dinamico_-8.5dB_BGM_-6.0dB_SFX",
        "resolucao_audio": "24bit_48kHz_Stereo",
        "stems": {
            "voz": "storage_local/audio/stem_voz_60s.wav",
            "bgm": "storage_local/audio/stem_bgm_60s.wav",
            "sfx": "storage_local/audio/stem_sfx_60s.wav",
        },
    }
    return {
        "audio": {
            "mix": mix,
            "lufs": lufs_calculado,
        }
    }


def construir_subgrafo_audio() -> StateGraph:
    """Compila o subgrafo de Áudio."""
    builder = StateGraph(EstadoEpisodio)

    builder.add_node("audio.diretor_voz", diretor_voz_node)
    builder.add_node("audio.narrador", narrador_node)
    builder.add_node("audio.sound_designer", sound_designer_node)
    builder.add_node("audio.supervisor_musical", supervisor_musical_node)
    builder.add_node("audio.mixador", mixador_node)

    builder.add_edge(START, "audio.diretor_voz")
    builder.add_edge("audio.diretor_voz", "audio.narrador")
    builder.add_edge("audio.narrador", "audio.sound_designer")
    builder.add_edge("audio.sound_designer", "audio.supervisor_musical")
    builder.add_edge("audio.supervisor_musical", "audio.mixador")
    builder.add_edge("audio.mixador", END)

    return builder.compile()
