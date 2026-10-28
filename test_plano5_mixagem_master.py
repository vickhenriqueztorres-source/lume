r"""PLANO 5: Mixagem Broadcast Multicanal (Sidechain Ducking + EQ Pocket + Masterização -14.0 LUFS / -1.0 dBTP 24-bit Estéreo).

Combina os 3 barramentos (Stems 48kHz 24-bit Estéreo):
1. D:\LUME\storage_local\audio\stem_voz_60s.wav
2. D:\LUME\storage_local\audio\stem_bgm_60s.wav
3. D:\LUME\storage_local\audio\stem_sfx_60s.wav

E gera o Master Broadcast Final:
- D:\LUME\storage_local\audio\master_audio_60s.wav (48 kHz, 24-bit, Estéreo, -14.0 LUFS, TP <= -1.0 dBTP)
- D:\LUME\storage_local\audio\mix_final.wav
- D:\LUME\storage_local\audio\master_audio_60s.mp3 (320 kbps Estéreo)
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

AUDIO_DIR = Path(r"D:\LUME\storage_local\audio")
STEM_VOZ = AUDIO_DIR / "stem_voz_60s.wav"
STEM_BGM = AUDIO_DIR / "stem_bgm_60s.wav"
STEM_SFX = AUDIO_DIR / "stem_sfx_60s.wav"
MASTER_WAV = AUDIO_DIR / "master_audio_60s.wav"
MIX_FINAL_WAV = AUDIO_DIR / "mix_final.wav"
MASTER_MP3 = AUDIO_DIR / "master_audio_60s.mp3"
SR = 48000
TOTAL_SAMPLES = int(SR * 60.0)


def ler_stereo_f32(wav_path: Path) -> np.ndarray:
    tmp_16 = wav_path.parent / f"_tmp16_p5_{wav_path.stem}.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(wav_path), "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(tmp_16)],
        check=True,
    )
    with wave.open(str(tmp_16), "rb") as wf:
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    tmp_16.unlink(missing_ok=True)
    return raw.reshape(-1, 2)


def calcular_envelope_sidechain(voz_stereo: np.ndarray, attack_ms: float = 25.0, release_ms: float = 380.0) -> np.ndarray:
    """Detector de envelope vocal RMS suave com ataque rápido (25ms) e release musical (380ms)."""
    voz_mono = np.abs(np.mean(voz_stereo, axis=1))
    # Janela móvel de 20ms para detecção de energia de fala
    win = int(0.020 * SR)
    kernel = np.ones(win, dtype=np.float32) / win
    rms_inst = np.sqrt(np.convolve(voz_mono**2, kernel, mode="same") + 1e-12)

    # Normaliza detector entre 0.0 (silêncio) e 1.0 (fala ativa)
    active = np.clip((rms_inst - 0.008) / 0.045, 0.0, 1.0)

    # Suavização assimétrica (ataque rápido / release lento) em blocos de 5ms (240 samples)
    step = 240
    n_steps = len(active) // step
    coarse = active[: n_steps * step].reshape(n_steps, step).mean(axis=1)
    env_coarse = np.zeros_like(coarse)

    alpha_att = float(np.exp(-step / (attack_ms * 0.001 * SR)))
    alpha_rel = float(np.exp(-step / (release_ms * 0.001 * SR)))

    cur = 0.0
    for i, val in enumerate(coarse):
        if val > cur:
            cur = alpha_att * cur + (1.0 - alpha_att) * float(val)
        else:
            cur = alpha_rel * cur + (1.0 - alpha_rel) * float(val)
        env_coarse[i] = cur

    env = np.repeat(env_coarse, step)
    if len(env) < len(voz_mono):
        env = np.pad(env, (0, len(voz_mono) - len(env)), mode="edge")
    return env[: len(voz_mono)]


def medir_ebur128(wav_path: Path) -> tuple[float, float]:
    """Retorna (Integrated LUFS, True Peak dBTP) medidos via filtro oficial ebur128 do FFmpeg."""
    cmd = ["ffmpeg", "-nostats", "-i", str(wav_path), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    m_i = re.findall(r"I:\s*([-\d\.]+)\s*LUFS", res.stderr)
    m_tp = re.findall(r"Peak:\s*([-\d\.]+)\s*dBFS", res.stderr)
    i_lufs = float(m_i[-1]) if m_i else -99.0
    tp_db = float(m_tp[-1]) if m_tp else 0.0
    return i_lufs, tp_db


def construir_master_audio_60s() -> tuple[float, float, float, float]:
    voz = ler_stereo_f32(STEM_VOZ)[:TOTAL_SAMPLES]
    bgm = ler_stereo_f32(STEM_BGM)[:TOTAL_SAMPLES]
    sfx = ler_stereo_f32(STEM_SFX)[:TOTAL_SAMPLES]

    sc_env = calcular_envelope_sidechain(voz, attack_ms=25.0, release_ms=380.0)

    # Ganho base e Sidechain Ducking:
    # - Voz: 1.15x (Frente limpa e presente)
    # - BGM: Nas pausas da voz (sc_env=0) sobe para 0.56; durante a fala (sc_env=1) reduz para 0.21 (-8.5 dB de ducking!)
    # - SFX: Nas pausas da voz (sc_env=0) sobe para 0.72; durante a fala (sc_env=1) reduz para 0.36 (-6.0 dB de ducking!)
    bgm_gain_curve = (0.56 * (1.0 - sc_env) + 0.21 * sc_env)[:, None]
    sfx_gain_curve = (0.72 * (1.0 - sc_env) + 0.36 * sc_env)[:, None]

    voz_bus = voz * 1.15
    bgm_ducked = bgm * bgm_gain_curve
    sfx_ducked = sfx * sfx_gain_curve

    # Mede a relação Voz vs Música nos trechos com fala ativa (sc_env > 0.6)
    speech_mask = sc_env > 0.6
    rms_voz_speech = float(20 * np.log10(np.sqrt(np.mean(voz_bus[speech_mask] ** 2)) + 1e-9))
    rms_bgm_speech = float(20 * np.log10(np.sqrt(np.mean(bgm_ducked[speech_mask] ** 2)) + 1e-9))
    snr_voz_bgm_db = rms_voz_speech - rms_bgm_speech

    mix_raw = voz_bus + bgm_ducked + sfx_ducked

    # Garante Silêncio Dramático Absoluto (47.20s a 48.10s)
    sil_i0 = int(47.20 * SR)
    sil_i1 = int(48.10 * SR)
    mix_raw[sil_i0:sil_i1, :] = 0.0

    # Fade-out suave nos últimos 0.8s (59.2s a 60.0s)
    fo_len = int(0.8 * SR)
    mix_raw[-fo_len:] *= np.linspace(1.0, 0.0, fo_len, dtype=np.float32)[:, None]

    # Soft-knee limiter preventivo a -1.5 dBFS (0.841) antes da calibração LUFS
    peak_raw = float(np.max(np.abs(mix_raw)))
    if peak_raw > 0:
        mix_raw = mix_raw * (0.80 / peak_raw)

    tmp_pre = AUDIO_DIR / "_tmp_mix_pre_lufs.wav"
    with wave.open(str(tmp_pre), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        int16_pre = np.clip(mix_raw * 32767.0, -32767, 32767).astype(np.int16)
        wf.writeframes(int16_pre.tobytes())

    # Passo 1: Mede LUFS do mix_pre e aplica ganho linear exato + limiter em -1.2 dBTP (0.871)
    cur_lufs, _ = medir_ebur128(tmp_pre)
    delta_db = -14.0 - cur_lufs
    tmp_cal = AUDIO_DIR / "_tmp_mix_cal.wav"
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

    # Passo 2: Ajuste fino de precisão para cravar -14.0 LUFS (±0.15 LU) e manter Silêncio Dramático zerado
    cal_lufs, cal_tp = medir_ebur128(tmp_cal)
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

    # Sincroniza cópias de contrato (mix_final.wav e master_audio_60s.mp3)
    shutil.copy2(MASTER_WAV, MIX_FINAL_WAV)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(MASTER_WAV), "-ac", "2", "-b:a", "320k", str(MASTER_MP3)],
        check=True,
    )

    final_lufs, final_tp = medir_ebur128(MASTER_WAV)
    return final_lufs, final_tp, snr_voz_bgm_db, rms_voz_speech


def executar_testes_plano5() -> None:
    print("=" * 80)
    print("[PLANO 5] MIXAGEM BROADCAST MULTICANAL (SIDECHAIN DUCKING + EBU R128 24-BIT)")
    print("=" * 80)

    final_lufs, final_tp, snr_voz_bgm_db, rms_voz = construir_master_audio_60s()

    # 1. TESTE DE SEGURANÇA: WAV 48kHz, 24-bit (pcm_s24le), 2 Canais (Estéreo), 60.000s exatos
    pr = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(MASTER_WAV)],
        capture_output=True, text=True, check=True,
    )
    d = json.loads(pr.stdout)
    st = d["streams"][0]
    assert st["codec_name"] == "pcm_s24le", f"Esperado pcm_s24le, obtido {st['codec_name']}"
    assert int(st["sample_rate"]) == 48000
    assert int(st["channels"]) == 2
    assert abs(float(d["format"]["duration"]) - 60.0) < 0.02
    print(
        f"  [PASS] Teste de Seguranca: master_audio_60s.wav (pcm_s24le, 48kHz, 2 Canais Estereo, {MASTER_WAV.stat().st_size} bytes)."
    )

    # 2. TESTE DE ESTRESSE: Conformidade EBU R128 (-14.0 LUFS ±0.3) e True Peak <= -1.0 dBTP + Relação Voz/Música >= 6 dB
    assert -14.3 <= final_lufs <= -13.7, f"Loudness fora da norma: {final_lufs} LUFS"
    assert final_tp <= -1.0, f"True Peak violou teto de -1.0 dBTP: {final_tp} dBTP"
    assert snr_voz_bgm_db >= 6.0, f"Voz abaixo de +6dB sobre a música: {snr_voz_bgm_db:.2f} dB"
    print(
        f"  [PASS] Teste de Estresse: Loudness Integrado = {final_lufs:.1f} LUFS | True Peak = {final_tp:.2f} dBTP (<= -1.0 dBTP) | "
        f"Voz Acima da Musica = +{snr_voz_bgm_db:.2f} dB."
    )

    # 3. TESTE DE CAOS: Ausência de amostras clipadas (0.0 dBFS) + Silêncio Dramático preservado no Master Final
    master_arr = ler_stereo_f32(MASTER_WAV)
    max_sample = float(np.max(np.abs(master_arr)))
    clipped_samples = int(np.sum(np.abs(master_arr) >= 0.995))
    sil_window = master_arr[int(47.25 * SR) : int(48.05 * SR)]
    sil_max = float(np.max(np.abs(sil_window)))

    assert clipped_samples == 0, f"Detectadas {clipped_samples} amostras clipadas!"
    assert sil_max < 0.0005, f"Silêncio Dramático contaminado no Master: {sil_max}"
    print(
        f"  [PASS] Teste de Caos: 0 amostras clipadas (MaxSample={max_sample:.4f}) | "
        f"Silencio Dramatico (47.25s-48.05s) = {sil_max:.6f} abs."
    )
    print("=" * 80)
    print("[SUCESSO 100%] PLANO 5 VALIDADO NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 80)


if __name__ == "__main__":
    executar_testes_plano5()
