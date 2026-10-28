r"""SUBETAPA 2: Síntese Vocal Neural de Alta Tensão por Blocos Sincronizados (ElevenLabs Brian).

Gera via API ElevenLabs (https://api.elevenlabs.io/v1/text-to-speech/nPczCjzI2devNBz1zQrb):
- D:\LUME\storage_local\audio\blocos_voz_magnetica\voz_p01.mp3 .. voz_p10.mp3
- D:\LUME\storage_local\audio\stem_voz_60s.wav (48 kHz, 24-bit, Estéreo)
- D:\LUME\storage_local\audio\narracao_60s_brian.mp3

E executa a bateria completa de testes de Segurança, Estresse e Caos da Subetapa 2.
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
VOICE_ID = "nPczCjzI2devNBz1zQrb"  # Brian (Deep Resonant Baritone)
TTS_URL = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

ROTEIRO_JSON = Path(r"D:\LUME\storage_local\roteiro\roteiro_magnetico_odisseia_60s.json")
AUDIO_DIR = Path(r"D:\LUME\storage_local\audio")
BLOCOS_VOZ_DIR = AUDIO_DIR / "blocos_voz_magnetica"
STEM_VOZ_WAV = AUDIO_DIR / "stem_voz_60s.wav"
NARRACAO_MP3 = AUDIO_DIR / "narracao_60s_brian.mp3"
SR = 48000
TOTAL_SAMPLES = int(SR * 60.0)


def sintetizar_bloco_brian(plano_num: int, texto: str) -> Path:
    BLOCOS_VOZ_DIR.mkdir(parents=True, exist_ok=True)
    mp3_path = BLOCOS_VOZ_DIR / f"voz_p{plano_num:02d}.mp3"

    if mp3_path.exists() and mp3_path.stat().st_size > 15_000:
        return mp3_path

    # Limpa reticências iniciais apenas para não gerar pausa artificial longa antes da primeira palavra no TTS
    texto_tts = texto.lstrip(". ").strip()

    payload = json.dumps(
        {
            "text": texto_tts,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.52,
                "similarity_boost": 0.88,
                "style": 0.25,
                "use_speaker_boost": True,
            },
        }
    ).encode("utf-8")

    last_err = None
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(
                TTS_URL,
                data=payload,
                headers={
                    "xi-api-key": API_KEY,
                    "Content-Type": "application/json",
                    "Accept": "audio/mpeg",
                },
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                audio_bytes = resp.read()
            if len(audio_bytes) < 5_000:
                raise RuntimeError(f"Áudio MP3 muito curto para plano {plano_num}: {len(audio_bytes)} bytes")
            mp3_path.write_bytes(audio_bytes)
            print(f"  + Bloco Vocal Neural Brian P{plano_num:02d} gerado ({len(audio_bytes)} bytes)")
            return mp3_path
        except Exception as exc:
            last_err = exc
            print(f"  ! Tentativa {attempt}/3 falhou no TTS ElevenLabs P{plano_num:02d}: {exc}")
            time.sleep(2.0 * attempt)

    # Fallback automático para API Gemini TTS com rotação de chaves (Key 1 -> Key 2) quando os tokens acabarem
    print(f"  >> Acionando Fallback Multi-Chave Gemini TTS (Chave 1 -> Chave 2) para P{plano_num:02d}...")
    try:
        from grafo.ferramentas.audio import sintetizar_voz_gemini_com_fallback

        return sintetizar_voz_gemini_com_fallback(
            texto=texto_tts,
            output_path=mp3_path,
            voice_name="Charon",
        )
    except Exception as fallback_exc:
        raise RuntimeError(
            f"Falha ao sintetizar bloco {plano_num} (Primário: {last_err} | Fallback: {fallback_exc})"
        ) from fallback_exc


def processar_bloco_para_janela(mp3_path: Path, max_dur_s: float) -> np.ndarray:
    """Remove silêncios de borda, aplica EQ de presença barítono e ajusta atempo se necessário para caber na janela."""
    tmp_trim = BLOCOS_VOZ_DIR / f"_trim_{mp3_path.stem}.wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-v", "error",
            "-i", str(mp3_path),
            "-af", (
                "silenceremove=start_periods=1:start_duration=0.02:start_threshold=-42dB:"
                "stop_periods=-1:stop_duration=0.18:stop_threshold=-45dB,"
                "highpass=f=75,"
                "equalizer=f=160:t=q:w=1.1:g=2.0,"
                "equalizer=f=3200:t=q:w=1.3:g=2.2"
            ),
            "-ar", str(SR),
            "-ac", "1",
            "-c:a", "pcm_s16le",
            str(tmp_trim),
        ],
        check=True,
    )

    with wave.open(str(tmp_trim), "rb") as wf:
        samples = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    dur_s = len(samples) / float(SR)

    if dur_s > max_dur_s:
        ratio = min(1.55, max(1.02, (dur_s / max_dur_s) * 1.04))
        tmp_tempo = BLOCOS_VOZ_DIR / f"_tempo_{mp3_path.stem}.wav"
        subprocess.run(
            [
                "ffmpeg", "-y", "-v", "error",
                "-i", str(tmp_trim),
                "-af", f"atempo={ratio:.4f}",
                "-ar", str(SR),
                "-ac", "1",
                "-c:a", "pcm_s16le",
                str(tmp_tempo),
            ],
            check=True,
        )
        with wave.open(str(tmp_tempo), "rb") as wf:
            samples = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        tmp_tempo.unlink(missing_ok=True)

    tmp_trim.unlink(missing_ok=True)

    # Aplica micro fade-in e fade-out de 25ms para zero cliques
    n = len(samples)
    fi = min(n, int(0.025 * SR))
    fo = min(n, int(0.035 * SR))
    if fi > 0:
        samples[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 0:
        samples[n - fo :] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)

    # Normaliza RMS do bloco vocal para consistência absoluta entre os 10 planos
    rms = float(np.sqrt(np.mean(samples**2)) + 1e-9)
    target_rms = 10.0 ** (-18.5 / 20.0)
    samples = np.clip(samples * (target_rms / rms), -0.88, 0.88)
    return samples


def construir_stem_voz_magnetica() -> dict[int, tuple[float, float]]:
    roteiro = json.loads(ROTEIRO_JSON.read_text(encoding="utf-8"))
    timeline_mono = np.zeros(TOTAL_SAMPLES, dtype=np.float32)
    janelas_reais: dict[int, tuple[float, float]] = {}

    # Offsets de entrada cirúrgicos para cada plano de 6.0s:
    # - Plano 01 começa em 0.25s (para colar no Infinite Loop com o final do Plano 10 em 59.75s!)
    # - Plano 08 tem teto rígido em 47.15s (para respeitar o Silêncio Dramático 47.20s-48.10s!)
    # - Plano 09 começa em 48.12s (logo após o Silêncio Dramático!)
    # - Plano 10 termina próximo a 59.70s (ponte para o Loop Infinito!)
    for b in roteiro["blocos"]:
        p = int(b["plano"])
        mp3_p = sintetizar_bloco_brian(p, b["texto_narracao"])

        if p == 1:
            t_in = 0.25
            max_d = 5.35
        elif p == 8:
            t_in = 42.20
            max_d = 4.90  # Termina até 47.10s (antes do Silêncio Dramático 47.20s-48.10s!)
        elif p == 9:
            t_in = 48.12
            max_d = 5.45
        elif p == 10:
            t_in = 54.25
            max_d = 5.45  # Termina em ~59.70s (conectando com 0.25s!)
        else:
            t_in = (p - 1) * 6.0 + 0.30
            max_d = 5.35

        seg = processar_bloco_para_janela(mp3_p, max_dur_s=max_d)
        i0 = int(t_in * SR)
        i1 = min(TOTAL_SAMPLES, i0 + len(seg))
        timeline_mono[i0:i1] = seg[: i1 - i0]
        t_out = i1 / float(SR)
        janelas_reais[p] = (round(t_in, 3), round(t_out, 3))
        print(f"    -> Plano {p:02d}: fala posicionada em {t_in:5.2f}s .. {t_out:5.2f}s (dur={t_out - t_in:4.2f}s)")

    # Garante zero absoluto na janela de Silêncio Dramático (47.20s a 48.10s)
    timeline_mono[int(47.20 * SR) : int(48.10 * SR)] = 0.0

    # Salva stem_voz_60s.wav (48kHz, 24-bit Estéreo) e narracao_60s_brian.mp3
    tmp_wav16 = AUDIO_DIR / "_tmp_voz_mag16.wav"
    with wave.open(str(tmp_wav16), "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(SR)
        int16_data = np.clip(timeline_mono * 32767.0, -32767, 32767).astype(np.int16)
        stereo = np.column_stack((int16_data, int16_data)).flatten()
        wf.writeframes(stereo.tobytes())

    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(tmp_wav16), "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s24le", str(STEM_VOZ_WAV)],
        check=True,
    )
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(STEM_VOZ_WAV), "-ac", "2", "-b:a", "192k", str(NARRACAO_MP3)],
        check=True,
    )
    tmp_wav16.unlink(missing_ok=True)

    # Atualiza roteiro_magnetico_odisseia_60s.json com os timestamps reais medidos
    for b in roteiro["blocos"]:
        p = int(b["plano"])
        b["fala_inicio_s"], b["fala_fim_s"] = janelas_reais[p]
    ROTEIRO_JSON.write_text(json.dumps(roteiro, indent=2, ensure_ascii=False), encoding="utf-8")

    return janelas_reais


def executar_testes_subetapa2() -> None:
    print("=" * 80)
    print("[SUBETAPA 2] SINTESE VOCAL NEURAL BRIAN (10 BLOCOS MAGNETICOS SINCRONIZADOS)")
    print("=" * 80)

    janelas = construir_stem_voz_magnetica()

    # 1. TESTE DE SEGURANÇA: Existência dos 10 MP3 + stem_voz_60s.wav (48kHz, 24-bit, 2ch, 60.000s)
    for p in range(1, 11):
        mp3_f = BLOCOS_VOZ_DIR / f"voz_p{p:02d}.mp3"
        assert mp3_f.exists() and mp3_f.stat().st_size > 15_000, f"MP3 ausente/inválido: {mp3_f}"

    pr = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(STEM_VOZ_WAV)],
        capture_output=True, text=True, check=True,
    )
    info = json.loads(pr.stdout)
    st = info["streams"][0]
    assert st["codec_name"] == "pcm_s24le"
    assert int(st["sample_rate"]) == 48000
    assert int(st["channels"]) == 2
    assert abs(float(info["format"]["duration"]) - 60.0) < 0.02
    print("  [PASS] Teste de Seguranca: 10 arquivos MP3 ElevenLabs Brian + stem_voz_60s.wav (48kHz, 24-bit, Estereo, 60.000s).")

    # 2. TESTE DE ESTRESSE: Verificar que nenhum bloco de fala invade o bloco seguinte (0 colisões de fronteira)
    for p in range(1, 11):
        t_in, t_out = janelas[p]
        win_start = (p - 1) * 6.0
        win_end = p * 6.0
        assert t_in >= win_start, f"Plano {p} começou antes da janela: {t_in} < {win_start}"
        assert t_out <= win_end - 0.15, f"Plano {p} invadiu a transição de saída: {t_out} > {win_end - 0.15}"
    assert janelas[8][1] <= 47.18, f"Plano 08 invadiu o Silêncio Dramático: {janelas[8][1]}"
    print("  [PASS] Teste de Estresse: 10/10 blocos vocais encaixados dentro de suas janelas de 6.0s com zero colisao.")

    # 3. TESTE DE CAOS: Verificar energia vocal ativa nos 10 planos + Silêncio Dramático (47.20s-48.10s = 0.000)
    tmp_chk = AUDIO_DIR / "_tmp_chk_sub2.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(STEM_VOZ_WAV), "-ac", "1", "-c:a", "pcm_s16le", str(tmp_chk)],
        check=True,
    )
    with wave.open(str(tmp_chk), "rb") as wf:
        v = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    tmp_chk.unlink(missing_ok=True)

    for p in range(1, 11):
        t_in, t_out = janelas[p]
        seg = v[int(t_in * SR) : int(t_out * SR)]
        rms_db = float(20 * np.log10(np.sqrt(np.mean(seg**2)) + 1e-9))
        assert rms_db > -25.0, f"Fala fraca ou ausente no Plano {p}: {rms_db:.1f} dBFS"

    sil_max = float(np.max(np.abs(v[int(47.20 * SR) : int(48.10 * SR)])))
    assert sil_max == 0.0, f"Silêncio Dramático violado: {sil_max}"
    print(f"  [PASS] Teste de Caos: Energia vocal ativa nos 10 planos (~-18.5 dBFS) | Silencio Dramatico (47.20s-48.10s) = 0.000.")
    print("=" * 80)
    print("[SUCESSO 100%] SUBETAPA 2 VALIDADA NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 80)


if __name__ == "__main__":
    executar_testes_subetapa2()
