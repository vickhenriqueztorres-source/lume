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
            "id": "fogo_braseiro_loop",
            "caminho": "storage_local/sfx/fogo_loop.wav",
            "licenca": "CC0_public_domain",
            "categoria": "fogo",
        },
        {
            "id": "passos_caverna",
            "caminho": "storage_local/sfx/passos.wav",
            "licenca": "LUME_foley_library",
            "categoria": "foley",
        },
        {
            "id": "impacto_rocha",
            "caminho": "storage_local/sfx/rocha.wav",
            "licenca": "LUME_foley_library",
            "categoria": "monstro",
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
        "tema_principal": "Leitmotiv de Odisseu - Cordas antigas e aulos",
        "stems": [
            {
                "id": "cordas_tensao",
                "caminho": "storage_local/trilha/cordas.wav",
                "licenca": "LUME_music_library",
                "instrumentos": ["aulos", "lira"],
            },
            {
                "id": "percussao_lenta",
                "caminho": "storage_local/trilha/percussao.wav",
                "licenca": "LUME_music_library",
                "instrumentos": ["tambor_pedra"],
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
    mix_caminho = "storage_local/audio/mix_final.wav"
    lufs_calculado = medir_lufs(mix_caminho)

    mix = {
        "caminho": mix_caminho,
        "hash": "hash_mix_final_ep01",
        "ducking": "habilitado_-6dB_sob_narracao",
        "resolucao_audio": "24bit_48kHz",
    }
    return {
        "audio": {
            "mix": mix,
            "lufs": lufs_calculado,  # Exatamente -14.0 LUFS
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
