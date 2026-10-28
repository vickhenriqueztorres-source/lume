r"""PLANO 6: Integração no Subgrafo de Áudio, Remux do Master 2D e Auditoria Final dos 48 Agentes.

Executa:
1. executar_producao_60s() completo (48 Agentes + 5 Gates Humanos + Remux xfade 1080p 24fps com novo áudio Estéreo -14.0 LUFS)
2. Bateria de Testes de Segurança, Estresse e Caos sobre o vídeo Master final:
   - D:\LUME\storage_local\master\lume_odisseia_60s_master.mp4
   - D:\LUME\storage_local\master\lume_odisseia_60s_2d_master.mp4
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import wave
from pathlib import Path
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from executar_episodio_60s import executar_producao_60s

MASTER_MP4 = Path(r"D:\LUME\storage_local\master\lume_odisseia_60s_master.mp4")
MASTER_2D_MP4 = Path(r"D:\LUME\storage_local\master\lume_odisseia_60s_2d_master.mp4")
AUDIO_DIR = Path(r"D:\LUME\storage_local\audio")
SR = 48000


def executar_testes_plano6() -> None:
    print("=" * 80)
    print("[PLANO 6] EXECUTANDO ESTEIRA COMPLETA (48 AGENTES + 5 GATES) & REMUX MASTER 2D")
    print("=" * 80)

    out_master = executar_producao_60s()
    assert out_master == MASTER_MP4 and MASTER_MP4.exists() and MASTER_2D_MP4.exists()

    # 1. TESTE DE SEGURANÇA: Streams H.264 1080p 24fps + AAC 48kHz 2 Canais (Estéreo) + Hash SHA-256 idêntico
    h1 = hashlib.sha256(MASTER_MP4.read_bytes()).hexdigest()
    h2 = hashlib.sha256(MASTER_2D_MP4.read_bytes()).hexdigest()
    assert h1 == h2, "Hashes divergem entre lume_odisseia_60s_master.mp4 e lume_odisseia_60s_2d_master.mp4"

    pr = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", str(MASTER_MP4)],
        capture_output=True, text=True, check=True,
    )
    info = json.loads(pr.stdout)
    v_stream = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    a_stream = [s for s in info["streams"] if s["codec_type"] == "audio"][0]

    assert v_stream["codec_name"] == "h264"
    assert int(v_stream["width"]) == 1920 and int(v_stream["height"]) == 1080
    assert v_stream["r_frame_rate"] == "24/1"
    assert int(v_stream["nb_frames"]) == 1440

    assert a_stream["codec_name"] == "aac"
    assert int(a_stream["sample_rate"]) == 48000
    assert int(a_stream["channels"]) == 2, f"Áudio do MP4 deveria ser Estéreo (2 canais), obtido {a_stream['channels']}"
    assert abs(float(info["format"]["duration"]) - 60.0) < 0.05

    print(
        f"  [PASS] Teste de Seguranca: Master MP4 validado (1920x1080 @ 24fps, 1440 quadros, AAC 48kHz 2 Canais Estereo, "
        f"SHA-256={h1[:16]}...)."
    )

    # 2. TESTE DE ESTRESSE: Decodificação integral de Bitstream (0 erros) + Medição EBU R128 diretamente no MP4
    dec = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(MASTER_MP4), "-f", "null", "-"],
        capture_output=True, text=True,
    )
    assert dec.returncode == 0 and dec.stderr.strip() == "", f"Erro de bitstream: {dec.stderr}"

    eb = subprocess.run(
        ["ffmpeg", "-nostats", "-i", str(MASTER_MP4), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    m_i = re.findall(r"I:\s*([-\d\.]+)\s*LUFS", eb.stderr)
    m_tp = re.findall(r"Peak:\s*([-\d\.]+)\s*dBFS", eb.stderr)
    mp4_lufs = float(m_i[-1])
    mp4_tp = float(m_tp[-1])
    assert -14.3 <= mp4_lufs <= -13.7, f"LUFS no MP4 fora da faixa: {mp4_lufs}"
    assert mp4_tp <= -0.8, f"True Peak no MP4 fora da faixa: {mp4_tp}"
    print(
        f"  [PASS] Teste de Estresse: Bitstream 100% integro (0 erros) | MP4 Loudness = {mp4_lufs:.1f} LUFS | True Peak = {mp4_tp:.2f} dBTP."
    )

    # 3. TESTE DE CAOS: Extração da trilha de áudio do MP4 final e verificação de Estéreo Real, Silêncio Dramático e Energia nos 10 Planos
    tmp_extracted = AUDIO_DIR / "_tmp_mp4_extracted.wav"
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-i", str(MASTER_MP4), "-vn", "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", str(tmp_extracted)],
        check=True,
    )
    with wave.open(str(tmp_extracted), "rb") as wf:
        raw = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    tmp_extracted.unlink(missing_ok=True)
    arr = raw.reshape(-1, 2)

    stereo_diff = float(np.mean(np.abs(arr[:, 0] - arr[:, 1])))
    assert stereo_diff > 0.005, f"Áudio extraído do MP4 perdeu imagem estéreo (diff={stereo_diff})"

    sil_seg = arr[int(47.28 * SR) : int(48.02 * SR)]
    sil_rms_db = float(20 * np.log10(np.sqrt(np.mean(sil_seg**2)) + 1e-9))
    assert sil_rms_db < -60.0, f"Silêncio Dramático no MP4 falhou ({sil_rms_db:.1f} dBFS)"

    print("    Auditoria Acustica dos 10 Planos no MP4 Final:")
    for p_idx in range(10):
        s0 = p_idx * 6
        s1 = s0 + 6
        seg = arr[s0 * SR : s1 * SR]
        rms_db = float(20 * np.log10(np.sqrt(np.mean(seg**2)) + 1e-9))
        peak_db = float(20 * np.log10(np.max(np.abs(seg)) + 1e-9))
        assert rms_db > -24.0 and peak_db < -0.5
        print(f"      * Plano {p_idx+1:02d} ({s0:02d}s-{s1:02d}s): RMS={rms_db:5.1f} dBFS | Peak={peak_db:5.2f} dBFS")

    print(
        f"  [PASS] Teste de Caos: Imagem Estereo Real no MP4 (diff={stereo_diff:.4f}) | "
        f"Silencio Dramatico (47.28s-48.02s) = {sil_rms_db:.1f} dBFS."
    )
    print("=" * 80)
    print("[SUCESSO 100%] PLANO 6 VALIDADO NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 80)


if __name__ == "__main__":
    executar_testes_plano6()
