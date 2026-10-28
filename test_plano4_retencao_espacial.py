r"""PLANO 4: Engenharia de Retenção (Micro-Hooks, Cortes J/L, Espacialização Estéreo 3D e Silêncio Dramático).

Monta o barramento completo de Efeitos Sonoros e Foley de 60.00s:
- D:\LUME\storage_local\audio\stem_sfx_60s.wav (48 kHz, 24-bit, Estéreo 3D)

E executa a bateria completa de testes de Segurança, Estresse e Caos do Plano 4.
"""

from __future__ import annotations

import json
import subprocess
import sys
import wave
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

AUDIO_DIR = Path(r"D:\LUME\storage_local\audio")
SFX_REAL_DIR = Path(r"D:\LUME\storage_local\sfx\real_2d")
CUESHEET_JSON = AUDIO_DIR / "cuesheet_psicoacustico_60s.json"
STEM_SFX_WAV = AUDIO_DIR / "stem_sfx_60s.wav"
SR = 48000
TOTAL_SAMPLES = int(SR * 60.0)


def ler_stereo_f32(wav_path: Path) -> np.ndarray:
    tmp_16 = wav_path.parent / f"_tmp16_p4_{wav_path.stem}.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(wav_path), "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(tmp_16)],
        check=True,
    )
    with wave.open(str(tmp_16), "rb") as wf:
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    tmp_16.unlink(missing_ok=True)
    return raw.reshape(-1, 2)


def aplicar_pan_e_ganho(seg: np.ndarray, pan: float, gain_db: float, fi_s: float = 0.08, fo_s: float = 0.15) -> np.ndarray:
    """Aplica lei de potência constante de pan (-1.0 Esquerda a +1.0 Direita), ganho em dB e micro-fades."""
    out = seg.copy()
    n = len(out)
    fi = min(n, int(fi_s * SR))
    fo = min(n, int(fo_s * SR))
    if fi > 0:
        out[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    if fo > 0:
        out[n - fo :] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]

    # Constant-power pan
    angle = (pan + 1.0) * (np.pi / 4.0)
    gain_lin = float(10.0 ** (gain_db / 20.0))
    left_g = float(np.cos(angle) * np.sqrt(2.0) * gain_lin)
    right_g = float(np.sin(angle) * np.sqrt(2.0) * gain_lin)

    out[:, 0] *= left_g
    out[:, 1] *= right_g
    return out


def montar_barramento_sfx_60s() -> Path:
    cuesheet = json.loads(CUESHEET_JSON.read_text(encoding="utf-8"))
    cache_sfx: dict[str, np.ndarray] = {}

    bus = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float32)

    for plano in cuesheet["planos"]:
        for cue in plano["sfx_cues"]:
            sid = cue["id"]
            if sid not in cache_sfx:
                spath = SFX_REAL_DIR / f"{sid}.wav"
                if not spath.exists():
                    raise FileNotFoundError(f"SFX ausente: {spath}")
                cache_sfx[sid] = ler_stereo_f32(spath)

            src = cache_sfx[sid]
            i0 = int(cue["inicio_s"] * SR)
            i1 = min(TOTAL_SAMPLES, int(cue["fim_s"] * SR))
            need = i1 - i0
            if need <= 0:
                continue

            if len(src) < need:
                reps = (need // len(src)) + 2
                seg = np.tile(src, (reps, 1))[:need]
            else:
                seg = src[:need]

            pan = float(cue.get("pan", 0.0))
            gain_db = float(cue.get("gain_db", 0.0))
            processed = aplicar_pan_e_ganho(seg, pan=pan, gain_db=gain_db)
            bus[i0:i1] += processed

    # Impõe o Silêncio Dramático Absoluto (47.20s a 48.10s) com fade-out rápido de 40ms antes de 47.20s
    sil_i0 = int(47.20 * SR)
    sil_i1 = int(48.10 * SR)
    fade_pre = int(0.04 * SR)
    bus[sil_i0 - fade_pre : sil_i0] *= np.linspace(1.0, 0.0, fade_pre, dtype=np.float32)[:, None]
    bus[sil_i0:sil_i1, :] = 0.0

    # Normaliza pico do barramento de SFX para -2.5 dBFS (0.75) preservando dinâmica de impacto
    peak = float(np.max(np.abs(bus)))
    if peak > 0:
        bus = bus * (0.75 / peak)
    bus[sil_i0:sil_i1, :] = 0.0

    tmp_sfx = AUDIO_DIR / "_tmp_bus_sfx.wav"
    with wave.open(str(tmp_sfx), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        int16_bus = np.clip(bus * 32767.0, -32767, 32767).astype(np.int16)
        wf.writeframes(int16_bus.tobytes())

    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(tmp_sfx),
            "-ar", str(SR),
            "-ac", "2",
            "-c:a", "pcm_s24le",
            str(STEM_SFX_WAV),
        ],
        check=True,
    )
    tmp_sfx.unlink(missing_ok=True)
    return STEM_SFX_WAV


def executar_testes_plano4() -> None:
    print("=" * 80)
    print("[PLANO 4] MONTANDO BARRAMENTO SFX 3D ESTEREO COM J/L CUTS E SILENCIO DRAMATICO")
    print("=" * 80)

    montar_barramento_sfx_60s()
    arr = ler_stereo_f32(STEM_SFX_WAV)

    # 1. TESTE DE SEGURANÇA: Compatibilidade de Fase Estéreo e Formato 24-bit 48kHz
    assert STEM_SFX_WAV.exists() and STEM_SFX_WAV.stat().st_size > 15_000_000
    left = arr[:, 0]
    right = arr[:, 1]
    corr = float(np.corrcoef(left, right)[0, 1])
    stereo_diff = float(np.mean(np.abs(left - right)))
    assert 0.10 <= corr <= 0.99, f"Correlação de fase estéreo fora da faixa segura: {corr:.4f}"
    assert stereo_diff > 0.005, f"Barramento SFX está mono (diff={stereo_diff:.5f})"
    print(f"  [PASS] Teste de Seguranca: stem_sfx_60s.wav (24-bit Estereo) | Correlacao Fase={corr:.3f} | StereoDiff={stereo_diff:.4f}.")

    # 2. TESTE DE ESTRESSE: Verificar presença de SFX ativo em todos os 10 planos + Pan Direcional (Odisseu Esq vs Polifemo Dir)
    for p_idx in range(10):
        s0 = p_idx * 6
        s1 = min(47, s0 + 6) if p_idx == 7 else s0 + 6
        seg = arr[s0 * SR : s1 * SR]
        rms_db = float(20 * np.log10(np.sqrt(np.mean(seg**2)) + 1e-9))
        assert rms_db > -35.0, f"Plano {p_idx+1} sem SFX ativo (RMS={rms_db:.1f} dBFS)"
        print(f"    - Plano {p_idx+1:02d} ({s0:02d}s-{s0+6:02d}s): SFX RMS = {rms_db:.1f} dBFS")

    # No Plano 03 (Polifemo à direita, pan=+0.30), energia R > L; no Plano 04 (Odisseu à esquerda, pan=-0.25), energia L > R
    p03_l = float(np.sqrt(np.mean(arr[12 * SR : 17 * SR, 0] ** 2)))
    p03_r = float(np.sqrt(np.mean(arr[12 * SR : 17 * SR, 1] ** 2)))
    p04_l = float(np.sqrt(np.mean(arr[18 * SR : 23 * SR, 0] ** 2)))
    p04_r = float(np.sqrt(np.mean(arr[18 * SR : 23 * SR, 1] ** 2)))
    assert p03_r > p03_l, f"Perspectiva direcional falhou no Plano 03 (L={p03_l:.4f}, R={p03_r:.4f})"
    assert p04_l > p04_r, f"Perspectiva direcional falhou no Plano 04 (L={p04_l:.4f}, R={p04_r:.4f})"
    print("  [PASS] Teste de Estresse: 10/10 planos com SFX ativo e Panoramizacao Direcional 3D validada (Odisseu=L, Polifemo=R).")

    # 3. TESTE DE CAOS: Verificar Silêncio Dramático Absoluto (47.22s-48.08s = 0.000) seguido de Explosão do Clímax em 48.10s
    sil_seg = arr[int(47.22 * SR) : int(48.08 * SR)]
    climax_seg = arr[int(48.10 * SR) : int(54.00 * SR)]
    max_sil = float(np.max(np.abs(sil_seg)))
    peak_climax_db = float(20 * np.log10(np.max(np.abs(climax_seg)) + 1e-9))
    assert max_sil == 0.0, f"Ruído detectado no Silêncio Dramático: {max_sil}"
    assert peak_climax_db > -8.0, f"Impacto do clímax fraco: {peak_climax_db:.1f} dBFS"
    print(f"  [PASS] Teste de Caos: Silencio Dramatico Absoluto (0.000) -> Explosao Climax P09 (Peak={peak_climax_db:.1f} dBFS).")
    print("=" * 80)
    print("[SUCESSO 100%] PLANO 4 VALIDADO NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 80)


if __name__ == "__main__":
    executar_testes_plano4()
