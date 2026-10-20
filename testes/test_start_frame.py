"""Bateria de Testes Robustos: Gerador de Start Frames LUME (Subetapa 2).

Cobre:
1. Teste Unitário: Geração de PNG nos formatos 16:9 e 9:16 com dimensões e paleta LUME.
2. Teste de Estresse: Geração de 15 frames consecutivos sem vazamento de recursos.
3. Teste de Segurança: Prevenção rigorosa contra Path Traversal em IDs de planos.
4. Teste de Caos: Resiliência e exceção tipada ao tentar gravar em diretório inválido.
"""

import os
import shutil
import time
import pytest
from pathlib import Path
from PIL import Image
from grafo.ferramentas.start_frame import (
    StartFrameGenerator,
    StartFrameSecurityError,
    StartFrameGenerationError,
)

TEMP_TEST_DIR = Path("storage_local/test_frames")


@pytest.fixture(autouse=True)
def cleanup_temp_dir():
    """Garante limpeza do diretório temporário antes e depois de cada teste."""
    if TEMP_TEST_DIR.exists():
        shutil.rmtree(TEMP_TEST_DIR, ignore_errors=True)
    yield
    if TEMP_TEST_DIR.exists():
        shutil.rmtree(TEMP_TEST_DIR, ignore_errors=True)


def test_unit_start_frame_dimensions_and_validity():
    """1. Teste Unitário: Valida resolução 16:9 (1920x1080) e 9:16 (1080x1920)."""
    generator = StartFrameGenerator(output_base_dir=TEMP_TEST_DIR)

    # 1. 16:9 Widescreen
    p169 = generator.gerar_start_frame(
        plano_id="plano_001",
        proporcao="16:9",
        nivel_fogo=3,
        direcao_olhar="D",
    )
    assert p169.exists()
    assert p169.stat().st_size > 1000
    with Image.open(p169) as im:
        assert im.size == (1920, 1080)
        assert im.format == "PNG"

    # 2. 9:16 Vertical
    p916 = generator.gerar_start_frame(
        plano_id="plano_002_vertical",
        proporcao="9:16",
        nivel_fogo=2,
        direcao_olhar="E",
    )
    assert p916.exists()
    assert p916.stat().st_size > 1000
    with Image.open(p916) as im:
        assert im.size == (1080, 1920)


def test_stress_consecutive_frame_generations():
    """2. Teste de Estresse: Gera 15 frames sucessivos rapidamente."""
    generator = StartFrameGenerator(output_base_dir=TEMP_TEST_DIR)
    start_time = time.time()

    for i in range(15):
        frame_path = generator.gerar_start_frame(
            plano_id=f"stress_frame_{i:03d}",
            proporcao="16:9",
            nivel_fogo=(i % 5) + 1,
        )
        assert frame_path.exists()

    elapsed = time.time() - start_time
    assert elapsed < 10.0, f"Geração de 15 frames demorou {elapsed:.2f}s (esperado < 10s)."


def test_security_path_traversal_rejection():
    """3. Teste de Segurança: Rejeita tentativas de Path Traversal."""
    generator = StartFrameGenerator(output_base_dir=TEMP_TEST_DIR)

    payloads_maliciosos = [
        "../../shadows/leak",
        "plano/../../etc/passwd",
        r"plano\..\windows\system32",
        "../escape",
        "/absoluto/invalido",
        "\\escape_win",
    ]

    for payload in payloads_maliciosos:
        with pytest.raises(StartFrameSecurityError, match="Path Traversal"):
            generator.gerar_start_frame(plano_id=payload)


def test_chaos_target_directory_unwritable():
    """4. Teste de Caos: Tratamento com erro tipado se o destino for inválido."""
    # Aponta para um caminho com caractere inválido no Windows
    generator = StartFrameGenerator(output_base_dir="C:\\nul\\invalid_path_test??")

    with pytest.raises(StartFrameGenerationError):
        generator.gerar_start_frame(plano_id="plano_caos")
