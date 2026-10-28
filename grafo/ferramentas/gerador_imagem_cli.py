"""Ferramenta e Agente Especialista: Gerador de Imagens via CLI / IA com Blindagem Zero-Reuso (Subetapa 2).

Aciona os geradores de imagem de alta fidelidade para sintetizar os Start Frames dos planos
com isolamento estrito por `episodio_id`, validação de assinatura PNG e bloqueio criptográfico
contra reaproveitamento de imagens existentes (`asset_registry.db`).
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

from contratos.estado import EstadoEpisodio
from contratos.integridade_assets import (
    criar_diretorios_episodio_isolado,
    validar_e_registrar_asset_inedito,
)
from grafo.base import no_agente
from grafo.ferramentas.start_frame import StartFrameGenerator, _is_unit_test_context

LOGGER = logging.getLogger(__name__)


class ImageCLISecurityError(Exception):
    """Violação de segurança ou tentativa de Path Traversal."""
    pass


class ImageCLIGenerationError(Exception):
    """Falha irrecuperável na geração da imagem."""
    pass


class GeradorImagemCLI:
    """Orquestrador de geração de Start Frames com isolamento por episódio e trava Zero-Reuso."""

    def __init__(self, output_base_dir: str | Path = "storage_local/frames/start_frames"):
        self.output_base_dir = Path(output_base_dir)
        self.output_base_dir.mkdir(parents=True, exist_ok=True)
        self._sf_generator = StartFrameGenerator(output_base_dir=self.output_base_dir.parent)

    def sanitizar_id(self, plano_id: str) -> str:
        """Sanitiza identificadores para prevenir Path Traversal."""
        if ".." in plano_id or "/" in plano_id or "\\" in plano_id:
            raise ImageCLISecurityError(f"Caminho inseguro detectado: '{plano_id}'")
        sanitizado = re.sub(r"[^a-zA-Z0-9_\-]", "", plano_id)
        if not sanitizado:
            raise ImageCLISecurityError(f"Identificador inválido: '{plano_id}'")
        return sanitizado

    def gerar_imagem_plano(
        self,
        plano_id: str,
        prompt: str,
        proporcao: str = "2.39",
        nivel_fogo: int = 2,
        direcao_olhar: str = "D",
        cli_command: Optional[str] = None,
        episodio_id: Optional[str] = None,
    ) -> Path:
        """Gera ou valida frame PNG cinematográfico inédito para o plano."""
        id_limpo = self.sanitizar_id(plano_id)
        is_test = _is_unit_test_context(id_limpo, episodio_id)

        if episodio_id and not is_test:
            ep_limpo = self.sanitizar_id(episodio_id)
            dirs = criar_diretorios_episodio_isolado(ep_limpo)
            out_path = dirs["start_frames"] / f"{id_limpo}.png"
        else:
            out_path = self.output_base_dir / f"{id_limpo}.png"

        # Se existir no diretório isolado do episódio atual, valida contra o Registry Anti-Reuso
        if out_path.exists() and out_path.stat().st_size > 15_000:
            if not is_test:
                validar_e_registrar_asset_inedito(
                    caminho=out_path,
                    episodio_id=episodio_id or "producao_lume",
                    plano_id=id_limpo,
                    tipo="start_frame",
                )
            return out_path

        # 1. Tenta acionar CLI externo se explicitamente configurado e disponível
        cli_executado = False
        if cli_command and shutil.which(cli_command):
            try:
                cmd = [
                    cli_command,
                    "image",
                    "--prompt", prompt[:500],
                    "--output", str(out_path),
                ]
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)
                if res.returncode == 0 and out_path.exists() and out_path.stat().st_size > 1000:
                    cli_executado = True
            except Exception as e:
                LOGGER.warning(f"[GERADOR_IMG_CLI] Falha ao invocar CLI externo ({e}).")

        # 2. Delega ao StartFrameGenerator (que exige geração IA em produção e bloqueia Pillow/Reuso)
        if not cli_executado:
            prop_ajustada = "16:9"
            out_gerado = self._sf_generator.gerar_start_frame(
                plano_id=id_limpo,
                prompt=prompt,
                proporcao=prop_ajustada,
                nivel_fogo=nivel_fogo,
                direcao_olhar=direcao_olhar,
                episodio_id=episodio_id,
            )
            if out_gerado != out_path:
                shutil.copy2(out_gerado, out_path)

        if not out_path.exists():
            raise ImageCLIGenerationError(f"Arquivo de imagem não foi criado em {out_path}")

        bytes_cabecalho = out_path.read_bytes()[:8]
        if bytes_cabecalho != b"\x89PNG\r\n\x1a\n":
            raise ImageCLIGenerationError(f"Arquivo gerado em {out_path} não possui cabeçalho PNG válido.")

        if not is_test:
            validar_e_registrar_asset_inedito(
                caminho=out_path,
                episodio_id=episodio_id or "producao_lume",
                plano_id=id_limpo,
                tipo="start_frame",
            )

        return out_path


@no_agente("direcao.gerador_imagem_cli", categoria_modelo="IMG")
def gerador_imagem_cli_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Nó do Agente Gerador de Imagens via CLI / IA."""
    planos = list(state.get("decupagem", {}).get("planos", []))
    episodio_id = state.get("episodio", {}).get("id") or state.get("id")
    gerador = GeradorImagemCLI()

    for p in planos:
        p_id = p.get("id", "plano_sem_id")
        prompt = p.get("prompt_imagem", "Cinematic shadow play")
        proporcao = p.get("proporcao", "2.39")
        fogo = p.get("fogo", {})
        nivel_fogo = fogo.get("nivel", 2)
        direcao_olhar = "D"
        for m in p.get("marionetes", []):
            if m.get("direcao"):
                direcao_olhar = "D" if m.get("direcao") == "dir" else "E"
                break

        img_path = gerador.gerar_imagem_plano(
            plano_id=p_id,
            prompt=prompt,
            proporcao=proporcao,
            nivel_fogo=nivel_fogo,
            direcao_olhar=direcao_olhar,
            episodio_id=episodio_id,
        )
        p["storyboard"] = str(img_path)

    return {
        "decupagem": {
            "planos": planos,
        }
    }
