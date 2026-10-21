"""Suite de Testes de Estresse, Seguranca e Caos - Subetapa 4 (Master Broadcast 60.00s 2D LUME)."""

import hashlib
import json
import re
import subprocess
from pathlib import Path

MASTER_PATH = Path(r"D:\LUME\storage_local\master\lume_odisseia_60s_master.mp4")
MASTER_2D_PATH = Path(r"D:\LUME\storage_local\master\lume_odisseia_60s_2d_master.mp4")


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def test_subetapa4_master_broadcast():
    print("=" * 75)
    print("EXECUTANDO SUITE DE TESTES ROBUSTOS - SUBETAPA 4 (MASTER 60.00s 2D LUME)")
    print("=" * 75)

    # 1. Seguranca e Identidade Byte-a-Byte
    print("[TESTE 1 - SEGURANCA] Verificando existencia, tamanho e hash SHA-256...")
    assert MASTER_PATH.is_file(), f"Master ausente: {MASTER_PATH}"
    assert MASTER_2D_PATH.is_file(), f"Copia Master 2D ausente: {MASTER_2D_PATH}"
    sz_mb = MASTER_PATH.stat().st_size / (1024 * 1024)
    assert sz_mb > 25.0, f"Master suspeito/muito pequeno: {sz_mb:.2f} MB"
    h1 = sha256_file(MASTER_PATH)
    h2 = sha256_file(MASTER_2D_PATH)
    assert h1 == h2, "Divergencia SHA-256 entre master principal e copia 2D"
    print(f"  [PASS] {MASTER_PATH.name} ({sz_mb:.2f} MB) | SHA-256={h1[:16]}...")

    # 2. Precisao Temporal e Geometria Broadcast
    print("[TESTE 2 - PRECISAO TEMPORAL] Auditando ffprobe (60.000s, 1920x1080 @ 24fps)...")
    res = subprocess.run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(MASTER_PATH)],
        capture_output=True,
        text=True,
    )
    assert res.returncode == 0, f"ffprobe falhou: {res.stderr}"
    data = json.loads(res.stdout)
    dur = float(data["format"]["duration"])
    v_stream = next(s for s in data["streams"] if s["codec_type"] == "video")
    a_stream = next(s for s in data["streams"] if s["codec_type"] == "audio")

    w, h = int(v_stream["width"]), int(v_stream["height"])
    fps = v_stream["r_frame_rate"]
    nb_frames = int(v_stream.get("nb_frames", 0))
    v_codec = v_stream["codec_name"]
    a_codec = a_stream["codec_name"]

    assert (w, h) == (1920, 1080), f"Resolucao invalida: {w}x{h}"
    assert fps == "24/1", f"FPS invalido: {fps}"
    assert abs(dur - 60.0) <= 0.05, f"Duracao fora de 60.00s: {dur:.3f}s"
    assert nb_frames == 1440, f"Contagem de quadros diferente de 1440: {nb_frames}"
    print(
        f"  [PASS] Duracao={dur:.3f}s | Quadros={nb_frames} | {w}x{h} @ {fps}fps | Video={v_codec} | Audio={a_codec}"
    )

    # 3. Caos de Decodificacao Completa (1.440 quadros)
    print("[TESTE 3 - CAOS DE BITSTREAM] Decodificando todos os 1.440 quadros H.264/AAC...")
    dec = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(MASTER_PATH), "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    assert dec.returncode == 0 and not dec.stderr.strip(), f"Erros de bitstream no Master: {dec.stderr}"
    print("  [PASS] 1.440 quadros e stream AAC decodificados com 0 erros!")

    # 4. Conformidade Broadcast EBU R128 (-14.0 LUFS)
    print("[TESTE 4 - ESTRESSE DE AUDIO EBU R128] Medindo Loudness Integrado...")
    r128 = subprocess.run(
        ["ffmpeg", "-nostats", "-i", str(MASTER_PATH), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"],
        capture_output=True,
        text=True,
    )
    matches = re.findall(r"I:\s*(-?\d+\.\d+)\s*LUFS", r128.stderr)
    assert matches, "Nao foi possivel extrair LUFS do Master"
    lufs = float(matches[-1])
    assert -14.5 <= lufs <= -13.5, f"Loudness fora da norma EBU R128 (-14.0 LUFS): {lufs} LUFS"
    print(f"  [PASS] Loudness Integrado EBU R128 = {lufs:.1f} LUFS (Alvo: -14.0 LUFS)")

    print("=" * 75)
    print("[SUCESSO 100%] SUBETAPA 4 VALIDADA NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 75)


if __name__ == "__main__":
    test_subetapa4_master_broadcast()
