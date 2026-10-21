"""Suite de Testes de Estresse, Seguranca e Caos - Subetapa 3 (10 Takes 2D Renderizados no Firefly)."""

import json
import subprocess
from pathlib import Path

RENDERS_2D_DIR = Path(r"D:\LUME\storage_local\renders\ep_lume_60s_odisseia_2d")
RENDERS_MASTER_DIR = Path(r"D:\LUME\storage_local\renders\ep_lume_60s_odisseia")

EXPECTED_2D_NAMES = [
    "ep60_2d_p01_contador_abertura.mp4",
    "ep60_2d_p02_caverna_selada.mp4",
    "ep60_2d_p03_ciclope_monumento.mp4",
    "ep60_2d_p04_astucia_odisseu.mp4",
    "ep60_2d_p05_oferta_vinho.mp4",
    "ep60_2d_p06_ciclope_bebe.mp4",
    "ep60_2d_p07_enigma_ninguem.mp4",
    "ep60_2d_p08_sono_pesado.mp4",
    "ep60_2d_p09_estaca_ardente.mp4",
    "ep60_2d_p10_contador_encerramento.mp4",
]


def test_subetapa3_all_takes():
    print("=" * 75)
    print("EXECUTANDO SUITE DE TESTES ROBUSTOS - SUBETAPA 3 (10 TAKES 2D FIREFLY)")
    print("=" * 75)
    for fname in EXPECTED_2D_NAMES:
        f2d = RENDERS_2D_DIR / fname
        fmaster = RENDERS_MASTER_DIR / fname.replace("ep60_2d_", "ep60_")
        assert f2d.is_file(), f"Take 2D ausente: {f2d}"
        assert fmaster.is_file(), f"Take sincronizado ausente: {fmaster}"
        assert f2d.stat().st_size == fmaster.stat().st_size, f"Divergencia de tamanho em {fname}"
        assert f2d.stat().st_size > 2_000_000, f"Take suspeito/muito pequeno ({f2d.stat().st_size} bytes): {fname}"

        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_format",
            "-show_streams",
            "-of",
            "json",
            str(f2d),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0, f"FFprobe falhou em {fname}"
        data = json.loads(res.stdout)
        dur = float(data["format"]["duration"])
        v = next(s for s in data["streams"] if s["codec_type"] == "video")
        w, h = int(v["width"]), int(v["height"])
        fps = v["r_frame_rate"]

        assert (w, h) == (1920, 1080), f"Resolucao invalida em {fname}: {w}x{h}"
        assert fps == "24/1", f"FPS invalido em {fname}: {fps}"
        assert 4.8 <= dur <= 5.5, f"Duracao fora do padrao nativo Kling (5.04s) em {fname}: {dur}s"

        decode_res = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(f2d), "-f", "null", "-"],
            capture_output=True,
            text=True,
        )
        assert decode_res.returncode == 0 and not decode_res.stderr.strip(), (
            f"Erro de bitstream H.264 em {fname}: {decode_res.stderr}"
        )

        sz_mb = f2d.stat().st_size / (1024 * 1024)
        print(f"  [PASS] {fname:38s} | {w}x{h} @ {fps}fps | {dur:.3f}s | {sz_mb:6.2f} MB | Bitstream OK")

    print("=" * 75)
    print("[SUCESSO 100%] SUBETAPA 3 VALIDADA NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 75)


if __name__ == "__main__":
    test_subetapa3_all_takes()
