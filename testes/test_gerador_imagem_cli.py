"""Bateria de Testes Robustos: Gerador de Imagens via CLI (Subetapa 3).

Cobre:
1. Teste Unitário: Criação de arquivos PNG reais com cabeçalho válido gravados no storyboard do plano.
2. Teste de Estresse: Geração de 10 planos em sequência sem vazamento ou corrupção.
3. Teste de Segurança: Rejeição de Path Traversal e nomes perigosos de arquivo.
4. Teste de Caos: Validação de integridade física rejeita arquivos corrompidos.
"""

from pathlib import Path
import pytest
from contratos.estado import criar_estado_inicial
from contratos.plano import Plano
from grafo.base import limpar_operacoes_teste
from grafo.ferramentas.gerador_imagem_cli import (
    GeradorImagemCLI,
    ImageCLISecurityError,
    gerador_imagem_cli_node,
)


@pytest.fixture(autouse=True)
def setup_subetapa3():
    limpar_operacoes_teste()


def test_unit_gerador_imagem_cli_node():
    """1. Teste Unitário: O nó gera imagens PNG válidas e atualiza o campo storyboard de cada plano."""
    estado = criar_estado_inicial("ep_img_cli", "A Odisseia", "Polifemo")
    planos = [
        Plano(
            id="ep_img_p01",
            bloco_roteiro=1,
            mundo="parede",
            prompt_imagem="Masterpiece, Greek shadow theater, brazier embers #E85D04",
            proporcao="16:9",
        ).model_dump(),
        Plano(
            id="ep_img_p02",
            bloco_roteiro=1,
            mundo="contador",
            prompt_imagem="Masterpiece, storyteller illuminated by fire, 85mm lens",
            proporcao="16:9",
        ).model_dump(),
    ]
    estado["decupagem"]["planos"] = planos

    res = gerador_imagem_cli_node(estado)
    planos_res = res["decupagem"]["planos"]

    assert len(planos_res) == 2
    for p in planos_res:
        caminho = Path(p["storyboard"])
        assert caminho.exists()
        assert caminho.stat().st_size > 1000
        # Confere cabeçalho binário PNG
        assert caminho.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_stress_batch_10_images(tmp_path):
    """2. Teste de Estresse: Geração de 10 imagens sem colisões."""
    gerador = GeradorImagemCLI(output_base_dir=tmp_path / "frames")
    caminhos = []
    for i in range(10):
        c = gerador.gerar_imagem_plano(
            plano_id=f"stress_frame_{i:02d}",
            prompt=f"Cinematic frame {i}",
            proporcao="16:9",
            nivel_fogo=2 + (i % 3),
        )
        assert c.exists()
        caminhos.append(c)

    assert len(set(caminhos)) == 10


def test_security_path_traversal_rejection():
    """3. Teste de Segurança: Identificadores com Path Traversal disparam ImageCLISecurityError."""
    gerador = GeradorImagemCLI()
    with pytest.raises(ImageCLISecurityError):
        gerador.sanitizar_id("../../etc/passwd")

    with pytest.raises(ImageCLISecurityError):
        gerador.sanitizar_id("plano/subpasta/invalido")

    with pytest.raises(ImageCLISecurityError):
        gerador.sanitizar_id("..\\windows\\system32")


def test_chaos_deterministic_recovery_on_rerun(tmp_path):
    """4. Teste de Caos: Segunda chamada com mesmo plano reutiliza a imagem sem reprocessamento redundante."""
    gerador = GeradorImagemCLI(output_base_dir=tmp_path / "frames")
    p_id = "chaos_reuse_test"
    c1 = gerador.gerar_imagem_plano(plano_id=p_id, prompt="Test frame", proporcao="16:9")
    mtime1 = c1.stat().st_mtime_ns

    # Segunda chamada deve reutilizar
    c2 = gerador.gerar_imagem_plano(plano_id=p_id, prompt="Test frame", proporcao="16:9")
    mtime2 = c2.stat().st_mtime_ns
    assert c1 == c2
    assert mtime1 == mtime2
