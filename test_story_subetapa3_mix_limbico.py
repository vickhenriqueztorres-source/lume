r"""SUBETAPA 3: Picos Límbicos Psicoacústicos, Laço Infinito Sonoro e Re-Mixagem Master -14.0 LUFS.

Implementa:
1. Topologia em Laço Perfeito Acústico (59.5s -> 00.5s contínuo na Lira e Braseiro, conforme 5 Blackhat Viralization Vectors #2)
2. Picos Límbicos Sub-Graves nas viradas cognitivas (00.15s, 06.0s, 12.0s, 24.0s, 36.0s, 48.10s, conforme Vector #5)
3. Silêncio Dramático Absoluto (47.20s - 48.10s = 0.000)
4. Sidechain Ducking Dinâmico sobre os 10 novos blocos vocais magnéticos do Brian + Calibração EBU R128 (-14.0 LUFS / <= -1.0 dBTP)
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import wave
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from test_plano5_mixagem_master import calcular_envelope_sidechain, ler_stereo_f32, medir_ebur128

AUDIO_DIR = Path(r"D:\LUME\storage_local\audio")
STEM_VOZ = AUDIO_DIR / "stem_voz_60s.wav"
STEM_BGM = AUDIO_DIR / "stem_bgm_60s.wav"
STEM_SFX = AUDIO_DIR / "stem_sfx_60s.wav"
MASTER_WAV = AUDIO_DIR / "master_audio_60s.wav"
MIX_FINAL_WAV = AUDIO_DIR / "mix_final.wav"
MASTER_MP3 = AUDIO_DIR / "master_audio_60s.mp3"
SR = 48000
TOTAL_SAMPLES = int(SR * 60.0)


def injetar_picos_limbicos_e_loop_infinito(bgm: np.ndarray, sfx: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    bgm_out = bgm.copy()
    sfx_out = sfx.copy()

    # 1. Topologia em Laço Perfeito (Infinite Loop Audio):
    # Faz o último 1.0s (59.0s-60.0s) de BGM e SFX convergir suavemente para o timbre do primeiro 1.0s (0.0s-1.0s)
    loop_len = int(1.0 * SR)
    alpha = np.linspace(0.0, 0.85, loop_len, dtype=np.float32)[:, None]
    bgm_out[-loop_len:] = (1.0 - alpha) * bgm_out[-loop_len:] + alpha * bgm_out[:loop_len]
    sfx_out[-loop_len:] = (1.0 - alpha) * sfx_out[-loop_len:] + alpha * sfx_out[:loop_len]

    # Micro crossfade de 15ms nas extremidades para evitar clique no loop 60.0s -> 0.0s sem zerar a energia!
    edge = int(0.015 * SR)
    mid_val_bgm = 0.5 * (bgm_out[edge] + bgm_out[-edge])
    for i in range(edge):
        w = i / float(edge)
        bgm_out[i] = (1.0 - w) * mid_val_bgm + w * bgm_out[i]
        bgm_out[-(i + 1)] = (1.0 - w) * mid_val_bgm + w * bgm_out[-(i + 1)]

    # 2. Picos Límbicos (Vector #5 — Pattern Interrupts sub-graves orgânicos nas 6 viradas cognitivas)
    limbic_times = [0.15, 6.00, 12.00, 24.00, 36.00, 48.10]
    dur_pulse = int(0.38 * SR)
    t_p = np.linspace(0.0, 0.38, dur_pulse, dtype=np.float32)
    # Sub-drop orgânico (frequência descendo de 78Hz para 36Hz com envelope exponencial)
    freq_sweep = 78.0 * np.exp(-2.1 * t_p)
    phase = 2.0 * np.pi * np.cumsum(freq_sweep) / SR
    sub_pulse = (np.sin(phase) * np.exp(-5.5 * t_p) * 0.24).astype(np.float32)
    sub_stereo = np.column_stack((sub_pulse, sub_pulse))

    for lt in limbic_times:
        idx = int(lt * SR)
        end_idx = min(TOTAL_SAMPLES, idx + dur_pulse)
        sfx_out[idx:end_idx] += sub_stereo[: end_idx - idx]

    # 3. Garante Silêncio Dramático Absoluto (47.20s a 48.10s)
    sil_i0 = int(47.20 * SR)
    sil_i1 = int(48.10 * SR)
    bgm_out[sil_i0:sil_i1, :] = 0.0
    sfx_out[sil_i0:sil_i1, :] = 0.0

    return bgm_out, sfx_out


def construir_master_magnetico_60s() -> tuple[float, float, float, float]:
    voz = ler_stereo_f32(STEM_VOZ)[:TOTAL_SAMPLES]
    bgm_raw = ler_stereo_f32(STEM_BGM)[:TOTAL_SAMPLES]
    sfx_raw = ler_stereo_f32(STEM_SFX)[:TOTAL_SAMPLES]

    bgm, sfx = injetar_picos_limbicos_e_loop_infinito(bgm_raw, sfx_raw)

    sc_env = calcular_envelope_sidechain(voz, attack_ms=22.0, release_ms=340.0)

    # Sidechain Ducking calibrado para os 10 blocos magnéticos:
    bgm_gain_curve = (0.54 * (1.0 - sc_env) + 0.19 * sc_env)[:, None]
    sfx_gain_curve = (0.70 * (1.0 - sc_env) + 0.34 * sc_env)[:, None]

    voz_bus = voz * 1.18
    bgm_ducked = bgm * bgm_gain_curve
    sfx_ducked = sfx * sfx_gain_curve

    speech_mask = sc_env > 0.6
    rms_voz_speech = float(20 * np.log10(np.sqrt(np.mean(voz_bus[speech_mask] ** 2)) + 1e-9))
    rms_bgm_speech = float(20 * np.log10(np.sqrt(np.mean(bgm_ducked[speech_mask] ** 2)) + 1e-9))
    snr_voz_bgm_db = rms_voz_speech - rms_bgm_speech

    mix_raw = voz_bus + bgm_ducked + sfx_ducked

    # Silêncio Dramático Absoluto (47.20s a 48.10s)
    sil_i0 = int(47.20 * SR)
    sil_i1 = int(48.10 * SR)
    mix_raw[sil_i0:sil_i1, :] = 0.0

    # Preserva energia contínua no fim (59.5s-60.0s) para o Infinite Loop, aplicando apenas micro-suavização de 10ms
    edge10 = int(0.010 * SR)
    mix_raw[:edge10] *= np.linspace(0.25, 1.0, edge10, dtype=np.float32)[:, None]
    mix_raw[-edge10:] *= np.linspace(1.0, 0.25, edge10, dtype=np.float32)[:, None]

    peak_raw = float(np.max(np.abs(mix_raw)))
    if peak_raw > 0:
        mix_raw = mix_raw * (0.80 / peak_raw)

    tmp_pre = AUDIO_DIR / "_tmp_mag_pre.wav"
    with wave.open(str(tmp_pre), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        int16_pre = np.clip(mix_raw * 32767.0, -32767, 32767).astype(np.int16)
        wf.writeframes(int16_pre.tobytes())

    cur_lufs, _ = medir_ebur128(tmp_pre)
    delta_db = -14.0 - cur_lufs
    tmp_cal = AUDIO_DIR / "_tmp_mag_cal.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(tmp_pre),
            "-af", f"volume={delta_db:.2f}dB,alimiter=limit=0.86:attack=5:release=50:level=disabled",
            "-ar", str(SR),
            "-ac", "2",
            "-c:a", "pcm_s24le",
            str(tmp_cal),
        ],
        check=True,
    )

    cal_lufs, _ = medir_ebur128(tmp_cal)
    fine_db = -14.0 - cal_lufs
    if abs(fine_db) > 0.05:
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(tmp_cal),
                "-af", f"volume={fine_db:.2f}dB,alimiter=limit=0.87:attack=5:release=50:level=disabled",
                "-ar", str(SR),
                "-ac", "2",
                "-c:a", "pcm_s24le",
                str(MASTER_WAV),
            ],
            check=True,
        )
    else:
        shutil.copy2(tmp_cal, MASTER_WAV)

    tmp_pre.unlink(missing_ok=True)
    tmp_cal.unlink(missing_ok=True)

    shutil.copy2(MASTER_WAV, MIX_FINAL_WAV)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(MASTER_WAV), "-ac", "2", "-b:a", "320k", str(MASTER_MP3)],
        check=True,
    )

    final_lufs, final_tp = medir_ebur128(MASTER_WAV)
    return final_lufs, final_tp, snr_voz_bgm_db, rms_voz_speech


def executar_testes_subetapa3() -> None:
    print("=" * 80)
    print("[SUBETAPA 3] PICOS LIMBICOS, LOOP INFINITO SONORO & MIXAGEM MASTER -14.0 LUFS")
    print("=" * 80)

    final_lufs, final_tp, snr_db, _ = construir_master_magnetico_60s()

    # 1. TESTE DE SEGURANÇA: WAV 48kHz, 24-bit Estéreo, 60.000s
    pr = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(MASTER_WAV)],
        capture_output=True, text=True, check=True,
    )
    info = json.loads(pr.stdout)
    st = info["streams"][0]
    assert st["codec_name"] == "pcm_s24le" and int(st["sample_rate"]) == 48000 and int(st["channels"]) == 2
    assert abs(float(info["format"]["duration"]) - 60.0) < 0.02
    print("  [PASS] Teste de Seguranca: master_audio_60s.wav (pcm_s24le, 48kHz, Estereo, 60.000s).")

    # 2. TESTE DE ESTRESSE: EBU R128 (-14.0 LUFS ±0.25), True Peak <= -1.0 dBTP, Voz >= +6 dB sobre música
    assert -14.25 <= final_lufs <= -13.75, f"LUFS fora da meta: {final_lufs}"
    assert final_tp <= -1.0, f"True Peak acima de -1.0 dBTP: {final_tp}"
    assert snr_db >= 6.0, f"SNR Voz/BGM abaixo de 6dB: {snr_db}"
    print(
        f"  [PASS] Teste de Estresse: Loudness = {final_lufs:.1f} LUFS | True Peak = {final_tp:.2f} dBTP | SNR Voz/BGM = +{snr_db:.2f} dB."
    )

    # 3. TESTE DE CAOS: Continuidade do Infinite Loop (59.0s-60.0s -> 00.0s-01.0s) + Silêncio Dramático 0.000
    arr = ler_stereo_f32(MASTER_WAV)
    rms_tail_db = float(20 * np.log10(np.sqrt(np.mean(arr[int(59.0 * SR) : int(60.0 * SR)] ** 2)) + 1e-9))
    rms_head_db = float(20 * np.log10(np.sqrt(np.mean(arr[int(0.0 * SR) : int(1.0 * SR)] ** 2)) + 1e-9))
    assert rms_tail_db > -28.0 and rms_head_db > -28.0, f"Loop infinito sem cama contínua ({rms_tail_db:.1f}dB -> {rms_head_db:.1f}dB)"

    sil_max = float(np.max(np.abs(arr[int(47.25 * SR) : int(48.05 * SR)])))
    assert sil_max < 0.0005, f"Silêncio Dramático violado: {sil_max}"
    print(
        f"  [PASS] Teste de Caos: Continuidade Loop Infinito (59-60s={rms_tail_db:.1f}dBFS -> 00-01s={rms_head_db:.1f}dBFS) | "
        f"Silencio Dramatico (47.25s-48.05s) = {sil_max:.6f}."
    )
    print("=" * 80)
    print("[SUCESSO 100%] SUBETAPA 3 VALIDADA NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 80)


if __name__ == "__main__":
    executar_testes_subetapa3()
