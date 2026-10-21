"""Suite de Testes de Estresse, Seguranca e Caos - Subetapa 5 (Auditoria Frame-a-Frame do Master 2D 60s)."""

import subprocess
from pathlib import Path

MASTER_PATH = Path(r"D:\LUME\storage_local\master\lume_odisseia_60s_master.mp4")
ARTIFACT_DIR = Path(r"C:\Users\brend\.gemini\antigravity\brain\3b5e0170-6ee3-479d-9a76-5894259c6e51")

TIMESTAMPS = [3, 9, 15, 21, 27, 33, 39, 45, 51, 57]


def extract_raw_rgb(video_path: Path, ts: float) -> bytes:
    cmd = [
        "ffmpeg",
        "-v",
        "error",
        "-ss",
        f"{ts:.2f}",
        "-i",
        str(video_path),
        "-frames:v",
        "1",
        "-vf",
        "scale=320:180",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-",
    ]
    res = subprocess.run(cmd, capture_output=True)
    assert res.returncode == 0 and len(res.stdout) == 320 * 180 * 3, f"Falha ao extrair raw RGB em {ts}s"
    return res.stdout


def test_subetapa5_auditoria_visual():
    print("=" * 75)
    print("EXECUTANDO SUITE DE TESTES ROBUSTOS - SUBETAPA 5 (AUDITORIA FRAME-A-FRAME)")
    print("=" * 75)

    # 1. Extracao dos 10 quadros do Master Final 2D para o diretorio de artefatos
    print("[TESTE 1 - EXTRACAO E INTEGRIDADE] Extraindo 10 quadros do Master 2D 60s...")
    for idx, ts in enumerate(TIMESTAMPS, start=1):
        out_png = ARTIFACT_DIR / f"master_2d_frame_{ts:02d}s.png"
        cmd = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-ss",
            str(ts),
            "-i",
            str(MASTER_PATH),
            "-frames:v",
            "1",
            "-update",
            "1",
            str(out_png),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        assert res.returncode == 0 and out_png.is_file() and out_png.stat().st_size > 500_000, (
            f"Falha na extracao do frame {ts}s: {res.stderr}"
        )
        print(f"  [PASS] Plano {idx:02d} ({ts:02d}s) -> {out_png.name} ({out_png.stat().st_size / 1024:.1f} KB)")

    # 2. Teste de Caos Anti-Congelamento (Movimento Real em Todos os 10 Planos do Master)
    print("[TESTE 2 - CAOS ANTI-FRAME-CONGELADO] Verificando delta de movimento real nos 10 planos...")
    for idx, ts in enumerate(TIMESTAMPS, start=1):
        rgb_a = extract_raw_rgb(MASTER_PATH, ts - 1.0)
        rgb_b = extract_raw_rgb(MASTER_PATH, ts + 1.0)
        diff_sum = sum(abs(a - b) for a, b in zip(rgb_a, rgb_b))
        mean_diff = diff_sum / len(rgb_a)
        assert mean_diff > 1.2, f"Plano {idx:02d} ({ts}s) parece congelado! Delta={mean_diff:.3f}"
        print(f"  [PASS] Plano {idx:02d} ({ts-1}s -> {ts+1}s): Movimento 2D ativo | Delta Medio Pixel = {mean_diff:.2f}/255")

    # 3. Teste de Estresse Estetico (Chiaroscuro LUME nos 10 Planos do Master)
    print("[TESTE 3 - ESTRESSE ESTETICO] Auditando Chiaroscuro LUME nos 10 planos do Master...")
    for idx, ts in enumerate(TIMESTAMPS, start=1):
        rgb = extract_raw_rgb(MASTER_PATH, float(ts))
        n_pix = 320 * 180
        dark_count = 0
        warm_count = 0
        lum_sum = 0.0
        for i in range(0, len(rgb), 3):
            r, g, b = rgb[i], rgb[i + 1], rgb[i + 2]
            lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
            lum_sum += lum
            if lum < 70:
                dark_count += 1
            if r > g + 15 and g >= b:
                warm_count += 1
        avg_lum = lum_sum / n_pix
        dark_pct = (dark_count / n_pix) * 100.0
        warm_pct = (warm_count / n_pix) * 100.0
        assert dark_pct >= 50.0, f"Plano {idx:02d} ({ts}s) perdeu Chiaroscuro: {dark_pct:.1f}% sombras"
        assert warm_pct >= 1.0, f"Plano {idx:02d} ({ts}s) sem luz ambar/fogo: {warm_pct:.1f}%"
        print(
            f"  [PASS] Plano {idx:02d} ({ts:02d}s): Luminancia={avg_lum:4.1f}/255 | Sombras={dark_pct:4.1f}% | Luz Fogo/Ambar={warm_pct:4.1f}%"
        )

    print("=" * 75)
    print("[SUCESSO 100%] SUBETAPA 5 VALIDADA NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 75)


if __name__ == "__main__":
    test_subetapa5_auditoria_visual()
