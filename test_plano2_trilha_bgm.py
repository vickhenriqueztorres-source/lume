r"""PLANO 2: Geração Neural da Trilha Musical de Fundo (BGM) por Atos Dramáticos.

Gera via ElevenLabs Sound Generation API (https://api.elevenlabs.io/v1/sound-generation):
1. D:\LUME\storage_local\trilha\real_2d\bgm_01_lira_abertura_fechamento.wav (12.0s)
2. D:\LUME\storage_local\trilha\real_2d\bgm_02_drone_aulos_caverna.wav (18.0s)
3. D:\LUME\storage_local\trilha\real_2d\bgm_03_percussao_tensao_astucia.wav (22.0s)
4. D:\LUME\storage_local\trilha\real_2d\bgm_04_coro_climax_epico.wav (10.0s)

E monta o barramento musical completo de 60.00s em 48kHz 24-bit Estéreo:
- D:\LUME\storage_local\audio\stem_bgm_60s.wav
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_KEY = "sk_8f80d72d864e38dd6babe6a5a34e0d74295fce2e45b56ae0"
SOUND_GEN_URL = "https://api.elevenlabs.io/v1/sound-generation"

TRILHA_DIR = Path(r"D:\LUME\storage_local\trilha\real_2d")
AUDIO_DIR = Path(r"D:\LUME\storage_local\audio")
STEM_BGM_WAV = AUDIO_DIR / "stem_bgm_60s.wav"
SR = 48000
TOTAL_SAMPLES = int(SR * 60.0)

BGM_SPECS = [
    {
        "id": "bgm_01_lira_abertura_fechamento",
        "duration_seconds": 12.0,
        "prompt_influence": 0.65,
        "prompt": (
            "Ancient Greek lyre and kithara playing a slow, dark, solemn three-note descending "
            "melody in Phrygian mode, warm acoustic plucked strings with natural stone temple "
            "reverb, cinematic mythological soundtrack, no vocals."
        ),
    },
    {
        "id": "bgm_02_drone_aulos_caverna",
        "duration_seconds": 18.0,
        "prompt_influence": 0.65,
        "prompt": (
            "Dark ominous ancient Greek ambient soundtrack, deep resonant bowed contrabass "
            "drone and mournful ancient aulos woodwind flute, mysterious and claustrophobic "
            "cave tension, low frequency cinematic dread, atmospheric."
        ),
    },
    {
        "id": "bgm_03_percussao_tensao_astucia",
        "duration_seconds": 22.0,
        "prompt_influence": 0.65,
        "prompt": (
            "Suspenseful ancient ritual soundtrack, slow rhythmic deep skin drum heartbeat "
            "pulse with tense plucked ancient strings building anticipation and cunning tension, "
            "dark mythological film score."
        ),
    },
    {
        "id": "bgm_04_coro_climax_epico",
        "duration_seconds": 10.0,
        "prompt_influence": 0.70,
        "prompt": (
            "Epic dark ancient Greek climax soundtrack, powerful deep male choir chanting "
            "wordlessly with thunderous ritual war drums and dramatic low brass swell, "
            "visceral mythological catharsis."
        ),
    },
]


def gerar_stem_elevenlabs(spec: dict) -> Path:
    TRILHA_DIR.mkdir(parents=True, exist_ok=True)
    wav_path = TRILHA_DIR / f"{spec['id']}.wav"
    mp3_tmp = TRILHA_DIR / f"_{spec['id']}_raw.mp3"

    if wav_path.exists() and wav_path.stat().st_size > 200_000:
        print(f"  + Stem BGM já existente e válido: {wav_path.name}")
        return wav_path

    payload = json.dumps(
        {
            "text": spec["prompt"],
            "duration_seconds": spec["duration_seconds"],
            "prompt_influence": spec["prompt_influence"],
        }
    ).encode("utf-8")

    last_err = None
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(
                SOUND_GEN_URL,
                data=payload,
                headers={
                    "xi-api-key": API_KEY,
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                mp3_bytes = resp.read()
            if len(mp3_bytes) < 10_000:
                raise RuntimeError(f"Payload MP3 muito pequeno: {len(mp3_bytes)} bytes")
            mp3_tmp.write_bytes(mp3_bytes)

            # Converte para WAV 48kHz, 24-bit Estéreo com EQ Pocket (abre espaço em 1.5kHz para voz e corta sub <35Hz)
            cmd = [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(mp3_tmp),
                "-af", (
                    "highpass=f=35,"
                    "equalizer=f=1400:t=q:w=1.2:g=-3.5,"
                    "equalizer=f=2800:t=q:w=1.4:g=-3.0,"
                    "stereotools=mlev=0.95:slev=1.25,"
                    "alimiter=limit=0.90"
                ),
                "-ar", str(SR),
                "-ac", "2",
                "-c:a", "pcm_s24le",
                str(wav_path),
            ]
            subprocess.run(cmd, check=True)
            mp3_tmp.unlink(missing_ok=True)
            print(f"  + Gerado via ElevenLabs Neural Audio: {wav_path.name} ({wav_path.stat().st_size} bytes)")
            return wav_path
        except Exception as exc:
            last_err = exc
            print(f"  ! Tentativa {attempt}/3 falhou para {spec['id']}: {exc}")
            time.sleep(2.0 * attempt)

    raise RuntimeError(f"Falha ao gerar {spec['id']}: {last_err}")


def ler_stereo_f32(wav_path: Path) -> np.ndarray:
    tmp_16 = wav_path.parent / f"_tmp16_{wav_path.stem}.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(wav_path), "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(tmp_16)],
        check=True,
    )
    with wave.open(str(tmp_16), "rb") as wf:
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    tmp_16.unlink(missing_ok=True)
    return raw.reshape(-1, 2)


def aplicar_envelope(arr: np.ndarray, fade_in_s: float, fade_out_s: float) -> np.ndarray:
    out = arr.copy()
    n = len(out)
    fi = min(n, int(fade_in_s * SR))
    fo = min(n, int(fade_out_s * SR))
    if fi > 0:
        out[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)[:, None]
    if fo > 0:
        out[n - fo :] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)[:, None]
    return out


def montar_barramento_bgm_60s(stems: dict[str, Path]) -> Path:
    s1 = ler_stereo_f32(stems["bgm_01_lira_abertura_fechamento"])
    s2 = ler_stereo_f32(stems["bgm_02_drone_aulos_caverna"])
    s3 = ler_stereo_f32(stems["bgm_03_percussao_tensao_astucia"])
    s4 = ler_stereo_f32(stems["bgm_04_coro_climax_epico"])

    bus = np.zeros((TOTAL_SAMPLES, 2), dtype=np.float32)

    def _add_segment(src: np.ndarray, start_s: float, end_s: float, fi_s: float, fo_s: float, gain: float) -> None:
        i0 = int(start_s * SR)
        i1 = min(TOTAL_SAMPLES, int(end_s * SR))
        need = i1 - i0
        if need <= 0:
            return
        if len(src) < need:
            reps = (need // len(src)) + 2
            seg = np.tile(src, (reps, 1))[:need]
        else:
            seg = src[:need]
        seg = aplicar_envelope(seg, fi_s, fo_s) * gain
        bus[i0:i1] += seg

    # Ato 1 (0.0s - 6.8s): Lira Grega & Sonic Logo LUME
    _add_segment(s1, 0.0, 6.8, 0.15, 1.2, 0.85)

    # Ato 2 (5.6s - 24.8s): Drone Grave + Aulos na Caverna & Polifemo
    _add_segment(s2, 5.6, 24.8, 1.2, 1.4, 0.80)

    # Ato 3 (23.4s - 47.20s): Percussão de Pele & Cordas Tensas (Astúcia e Vinho) -> corta exatamente no Silêncio Dramático!
    _add_segment(s3, 23.4, 47.20, 1.4, 0.12, 0.85)

    # SILÊNCIO DRAMÁTICO ABSOLUTO: 47.20s a 48.10s (0.000 em ambos os canais!)

    # Ato 4 (48.10s - 55.0s): Explosão do Coro Masculino Épico + Tambores no Ataque da Estaca em Chamas!
    _add_segment(s4, 48.10, 55.0, 0.05, 1.2, 1.00)

    # Ato 5 (53.8s - 60.0s): Retorno Solene da Lira Grega fechando o Loop Infinito
    _add_segment(s1, 53.8, 60.0, 1.0, 1.2, 0.85)

    # Garante zero absoluto na janela de Silêncio Dramático (47.20s - 48.10s)
    bus[int(47.20 * SR) : int(48.10 * SR), :] = 0.0

    # Normaliza o pico do barramento musical para -3.0 dBFS (0.707) antes do Mixador
    peak = float(np.max(np.abs(bus)))
    if peak > 0:
        bus = bus * (0.707 / peak)
    bus[int(47.20 * SR) : int(48.10 * SR), :] = 0.0

    tmp_bus = AUDIO_DIR / "_tmp_bus_bgm.wav"
    with wave.open(str(tmp_bus), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        int16_bus = np.clip(bus * 32767.0, -32767, 32767).astype(np.int16)
        wf.writeframes(int16_bus.tobytes())

    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(tmp_bus),
            "-ar", str(SR),
            "-ac", "2",
            "-c:a", "pcm_s24le",
            str(STEM_BGM_WAV),
        ],
        check=True,
    )
    tmp_bus.unlink(missing_ok=True)
    return STEM_BGM_WAV


def executar_testes_plano2() -> None:
    print("=" * 80)
    print("[PLANO 2] GERANDO 4 STEMS MUSICAIS NEURAIS (ELEVENLABS) & BARRAMENTO BGM 60S")
    print("=" * 80)

    stems_map: dict[str, Path] = {}
    for spec in BGM_SPECS:
        stems_map[spec["id"]] = gerar_stem_elevenlabs(spec)

    montar_barramento_bgm_60s(stems_map)

    # 1. TESTE DE SEGURANÇA: Existência, tamanho, 48kHz, 24-bit, Estéreo nos 4 stems + stem_bgm_60s.wav
    for sid, spath in list(stems_map.items()) + [("stem_bgm_60s", STEM_BGM_WAV)]:
        assert spath.exists() and spath.stat().st_size > 500_000, f"Arquivo inválido: {spath}"
        pr = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(spath)],
            capture_output=True, text=True, check=True,
        )
        d = json.loads(pr.stdout)
        st = d["streams"][0]
        assert st["codec_name"] == "pcm_s24le"
        assert int(st["sample_rate"]) == 48000
        assert int(st["channels"]) == 2
    print("  [PASS] Teste de Seguranca: 4 stems BGM + stem_bgm_60s.wav validados em WAV 48kHz 24-bit Estereo.")

    # 2. TESTE DE ESTRESSE: Auditoria Espectral FFT nos 4 stems provando riqueza harmônica real (anti-senoide)
    def _audit_spectrum(spath: Path) -> tuple[str, float, float]:
        arr = ler_stereo_f32(spath)
        mono = np.mean(arr, axis=1)
        rms_db = float(20 * np.log10(np.sqrt(np.mean(mono**2)) + 1e-9))
        fft_mag = np.abs(np.fft.rfft(mono))
        max_bin_ratio = float(np.max(fft_mag) / (np.sum(fft_mag) + 1e-9))
        return spath.name, rms_db, max_bin_ratio

    with ThreadPoolExecutor(max_workers=4) as ex:
        spec_results = list(ex.map(_audit_spectrum, stems_map.values()))

    for name, rms_db, max_bin_ratio in spec_results:
        assert rms_db > -30.0, f"Stem {name} muito baixo: {rms_db:.1f} dBFS"
        # Uma senoide pura tem max_bin_ratio > 0.35; áudio acústico rico tem < 0.05
        assert max_bin_ratio < 0.08, f"Stem {name} parece senoide sintética (ratio={max_bin_ratio:.4f})"
        print(f"    - {name}: RMS={rms_db:.1f} dBFS | MaxBinRatio={max_bin_ratio:.5f} (Acustico Real OK)")
    print("  [PASS] Teste de Estresse: Riqueza harmonica espectral (FFT) comprovada nos 4 stems musicais.")

    # 3. TESTE DE CAOS: Verificar cobertura contínua nos Atos 1-5 e Silêncio Dramático Absoluto em 47.20s-48.10s
    bgm_arr = ler_stereo_f32(STEM_BGM_WAV)
    sil_slice = bgm_arr[int(47.22 * SR) : int(48.08 * SR), :]
    assert float(np.max(np.abs(sil_slice))) == 0.0, "BGM vazou dentro do Silêncio Dramático!"

    # Verifica que há música ativa no meio da caverna (ex: 15s e 35s, onde antes era mudo!)
    rms_15s = float(20 * np.log10(np.sqrt(np.mean(bgm_arr[14 * SR : 17 * SR] ** 2)) + 1e-9))
    rms_35s = float(20 * np.log10(np.sqrt(np.mean(bgm_arr[33 * SR : 36 * SR] ** 2)) + 1e-9))
    rms_50s = float(20 * np.log10(np.sqrt(np.mean(bgm_arr[49 * SR : 52 * SR] ** 2)) + 1e-9))
    assert rms_15s > -28.0 and rms_35s > -28.0 and rms_50s > -25.0
    # Verifica imagem estéreo real (L != R)
    stereo_diff = float(np.mean(np.abs(bgm_arr[:, 0] - bgm_arr[:, 1])))
    assert stereo_diff > 0.001, f"BGM não possui abertura estéreo real (diff={stereo_diff})"

    print(
        f"  [PASS] Teste de Caos: Cobertura BGM ativa (15s={rms_15s:.1f}dB, 35s={rms_35s:.1f}dB, 50s={rms_50s:.1f}dB) | "
        f"Silencio Dramatico=0.000 | StereoDiff={stereo_diff:.4f}."
    )
    print("=" * 80)
    print("[SUCESSO 100%] PLANO 2 VALIDADO NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 80)


if __name__ == "__main__":
    executar_testes_plano2()
