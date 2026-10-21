"""Suite de Testes de Estresse, Seguranca e Caos - Subetapa 1 (10 Start Frames 2D LUME)."""

import json
import os
import subprocess
import sys
from pathlib import Path

FRAMES_2D_DIR = Path(r"D:\LUME\storage_local\frames\start_frames_2d")
OLD_FRAMES_DIR = Path(r"D:\LUME\storage_local\frames\start_frames")

EXPECTED_FILES = [f"ep60_2d_p{i:02d}.png" for i in range(1, 11)]


def test_1_seguranca_isolamento():
    """Garante que os start frames originais nao foram deletados nem truncados."""
    print("[TESTE 1 - SEGURANCA] Verificando isolamento do diretorio legado...")
    assert OLD_FRAMES_DIR.exists(), "Diretorio legado start_frames desapareceu!"
    legacy_files = list(OLD_FRAMES_DIR.glob("ep45_*.png")) + list(OLD_FRAMES_DIR.glob("contador_*.png"))
    assert len(legacy_files) >= 5, f"Arquivos legados afetados: encontrados {len(legacy_files)}"
    for lf in legacy_files:
        assert lf.stat().st_size > 50_000, f"Arquivo legado truncado: {lf}"
    print(f"  [PASS] {len(legacy_files)} arquivos legados intactos.")


def test_2_integridade_e_estresse_decodificacao():
    """Valida assinatura PNG, dimensoes, proporcao e decodificacao completa de pixels."""
    print("[TESTE 2 - ESTRESSE/INTEGRIDADE] Auditando os 10 Start Frames 2D...")
    for fname in EXPECTED_FILES:
        fpath = FRAMES_2D_DIR / fname
        assert fpath.is_file(), f"Arquivo ausente: {fpath}"
        size = fpath.stat().st_size
        assert size > 100_000, f"Arquivo muito pequeno ({size} bytes): {fpath}"

        with open(fpath, "rb") as fp:
            magic = fp.read(8)
        assert magic == b"\x89PNG\r\n\x1a\n", f"Assinatura PNG invalida em {fname}: {magic!r}"

        # FFprobe check
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,codec_name,pix_fmt",
            "-of",
            "json",
            str(fpath),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0, f"FFprobe falhou em {fname}: {res.stderr}"
        data = json.loads(res.stdout)
        stream = data["streams"][0]
        w, h = int(stream["width"]), int(stream["height"])
        assert w >= 1024 and h >= 576, f"Resolucao insuficiente em {fname}: {w}x{h}"

        # Teste de estresse de decodificacao completa via FFmpeg
        dec_cmd = ["ffmpeg", "-v", "error", "-i", str(fpath), "-f", "null", "-"]
        dec_res = subprocess.run(dec_cmd, capture_output=True, text=True)
        assert dec_res.returncode == 0 and not dec_res.stderr.strip(), (
            f"Erro de bitstream/decodificacao em {fname}: {dec_res.stderr}"
        )
        print(f"  [PASS] {fname}: {w}x{h} ({size / 1024:.1f} KB) - PNG & Bitstream OK")


def test_3_caos_paleta_chiaroscuro():
    """Audita luminancia e presenca de sombras de carvao (#16110D) + brasa (#E85D04/#FDF0D5)."""
    print("[TESTE 3 - CAOS/ESTETICA] Auditando Chiaroscuro e paleta LUME nos 10 quadros 2D...")
    for fname in EXPECTED_FILES:
        fpath = FRAMES_2D_DIR / fname
        # Extrai pixels RGB reduzidos para 64x36 via ffmpeg rawvideo para analise estatistica
        cmd = [
            "ffmpeg",
            "-v",
            "error",
            "-i",
            str(fpath),
            "-vf",
            "scale=64:36",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ]
        res = subprocess.run(cmd, capture_output=True)
        assert res.returncode == 0, f"Falha ao extrair RGB de {fname}"
        raw = res.stdout
        total_pixels = len(raw) // 3
        assert total_pixels == 64 * 36, f"Total de pixels inesperado: {total_pixels}"

        dark_pixels = 0
        warm_fire_pixels = 0
        lum_sum = 0.0

        for i in range(0, len(raw), 3):
            r, g, b = raw[i], raw[i + 1], raw[i + 2]
            lum = 0.299 * r + 0.587 * g + 0.114 * b
            lum_sum += lum
            if lum < 75:
                dark_pixels += 1
            if r > 140 and r > g * 1.15 and g > b:
                warm_fire_pixels += 1

        avg_lum = lum_sum / total_pixels
        dark_ratio = (dark_pixels / total_pixels) * 100.0
        warm_ratio = (warm_fire_pixels / total_pixels) * 100.0

        assert avg_lum < 135.0, f"{fname} claro demais para Chiaroscuro LUME (avg_lum={avg_lum:.1f})"
        assert dark_ratio >= 25.0, f"{fname} sem sombras densas suficientes ({dark_ratio:.1f}%)"
        assert warm_ratio >= 2.0, f"{fname} sem iluminacao quente de fogo/ambar ({warm_ratio:.1f}%)"
        print(
            f"  [PASS] {fname}: Luminancia Media={avg_lum:.1f}/255 | Sombras={dark_ratio:.1f}% | Luz Fogo/Ambar={warm_ratio:.1f}%"
        )


if __name__ == "__main__":
    print("=" * 75)
    print("EXECUTANDO SUITE DE TESTES ROBUSTOS - SUBETAPA 1 (START FRAMES 2D LUME)")
    print("=" * 75)
    test_1_seguranca_isolamento()
    test_2_integridade_e_estresse_decodificacao()
    test_3_caos_paleta_chiaroscuro()
    print("=" * 75)
    print("[SUCESSO 100%] SUBETAPA 1 VALIDADA NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 75)
