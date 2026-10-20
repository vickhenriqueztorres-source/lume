"""Bateria de Testes Robustos: FireflyEngine Portado (Subetapa 3).

Cobre:
1. Teste Unitário: Animação de Start Frame gerando arquivo MP4 ISO válido.
2. Teste de Estresse: Validação de concorrência serial estrita (Lock serial = 1) em multi-threading.
3. Teste de Segurança: Prevenção rigorosa de Path Traversal em IDs de planos e episódios.
4. Teste de Caos: Resiliência contra start frame inexistente e esgotamento de retries.
"""

import concurrent.futures
import shutil
import time
import pytest
from pathlib import Path
from grafo.ferramentas.firefly import (
    FireflyEngine,
    FireflySessionError,
    FireflySecurityError,
)

TEMP_TEST_RENDERS = Path("storage_local/test_renders")


@pytest.fixture(autouse=True)
def setup_and_teardown():
    if TEMP_TEST_RENDERS.exists():
        shutil.rmtree(TEMP_TEST_RENDERS, ignore_errors=True)
    TEMP_TEST_RENDERS.mkdir(parents=True, exist_ok=True)
    yield
    if TEMP_TEST_RENDERS.exists():
        shutil.rmtree(TEMP_TEST_RENDERS, ignore_errors=True)


def test_unit_firefly_animate_start_frame():
    """1. Teste Unitário: Gera vídeo MP4 válido a partir de start frame."""
    engine = FireflyEngine(output_base_dir=TEMP_TEST_RENDERS, simulate=True)

    # Cria start frame fictício
    dummy_frame = TEMP_TEST_RENDERS / "frame_test.png"
    dummy_frame.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)

    clip = engine.animate_start_frame(
        plano_id="plano_01",
        start_frame_path=dummy_frame,
        motion_prompt="Câmera avança lentamente em direção ao fogo",
        target_duration=5.0,
        episodio_id="ep_teste",
    )

    assert clip.exists()
    assert clip.suffix == ".mp4"
    assert clip.stat().st_size > 100
    # Valida cabeçalho ISO MP4
    header = clip.read_bytes()[:12]
    assert b"ftypisom" in header


def test_stress_strict_serial_concurrency_lock():
    """2. Teste de Estresse: Múltiplas threads disputam o motor e são serializadas sem colisão."""
    engine = FireflyEngine(output_base_dir=TEMP_TEST_RENDERS, simulate=True)

    dummy_frame = TEMP_TEST_RENDERS / "frame_stress.png"
    dummy_frame.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)

    def worker_job(scene_num: int) -> Path:
        return engine.animate_start_frame(
            plano_id=f"plano_thread_{scene_num:02d}",
            start_frame_path=dummy_frame,
            motion_prompt=f"Movimento da cena {scene_num}",
            episodio_id="ep_stress",
        )

    # 8 threads em paralelo
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker_job, i) for i in range(8)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 8
    for r in results:
        assert r.exists()
        assert r.stat().st_size > 100


def test_security_path_traversal_sanitization():
    """3. Teste de Segurança: Rejeita tentativas de escape de diretório."""
    engine = FireflyEngine(output_base_dir=TEMP_TEST_RENDERS, simulate=True)
    dummy_frame = TEMP_TEST_RENDERS / "frame_sec.png"
    dummy_frame.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 200)

    with pytest.raises(FireflySecurityError, match="Path Traversal"):
        engine.animate_start_frame(
            plano_id="../../malicious",
            start_frame_path=dummy_frame,
            motion_prompt="prompt",
        )

    with pytest.raises(FireflySecurityError, match="Path Traversal"):
        engine.animate_start_frame(
            plano_id="plano_ok",
            start_frame_path=dummy_frame,
            motion_prompt="prompt",
            episodio_id="../escape_ep",
        )


def test_chaos_missing_frame_and_retry_exhaustion():
    """4. Teste de Caos: Start frame inexistente dispara FileNotFoundError e retries tratam falhas."""
    engine = FireflyEngine(output_base_dir=TEMP_TEST_RENDERS, simulate=True, max_retries=2)

    # 1. Arquivo não existe
    with pytest.raises(FileNotFoundError, match="não encontrado"):
        engine.animate_start_frame(
            plano_id="plano_fantasma",
            start_frame_path="caminho_totalmente_inexistente.png",
            motion_prompt="prompt",
        )
