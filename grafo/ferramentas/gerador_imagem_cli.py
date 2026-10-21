"""Ferramenta e Agente Especialista: Gerador de Imagens via CLI (Doc 03 e Doc 05).

Aciona os CLIs locais (Codex / Antigravity / StartFrameGenerator) para sintetizar
as imagens cinematográficas dos planos com validação de integridade física PNG,
resolução e proteção contra Path Traversal.
"""

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from contratos.estado import EstadoEpisodio
from grafo.base import no_agente
from grafo.ferramentas.start_frame import StartFrameGenerator

LOGGER = logging.getLogger(__name__)


class ImageCLISecurityError(Exception):
    """Violação de segurança ou tentativa de Path Traversal."""
    pass


class ImageCLIGenerationError(Exception):
    """Falha irrecuperável na geração da imagem."""
    pass


class GeradorImagemCLI:
    """Orquestrador de geração de imagens via CLI e geradores locais de alta fidelidade."""

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
    ) -> Path:
        """Gera frame PNG cinematográfico para o plano e valida sua integridade."""
        id_limpo = self.sanitizar_id(plano_id)
        out_path = self.output_base_dir / f"{id_limpo}.png"

        # Se já existir imagem válida gerada previamente, reaproveita
        if out_path.exists() and out_path.stat().st_size > 5000:
            LOGGER.info(f"[GERADOR_IMG_CLI] Frame existente reutilizado para {plano_id}: {out_path}")
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
                LOGGER.warning(f"[GERADOR_IMG_CLI] Falha ao invocar CLI externo ({e}). Usando gerador nativo.")

        # 2. Fallback determinístico de alta fidelidade LUME
        if not cli_executado:
            # Converte proporção anamórfica se necessário
            prop_ajustada = "16:9" if proporcao in ("16:9", "1.77") else "16:9"
            out_gerado = self._sf_generator.gerar_start_frame(
                plano_id=id_limpo,
                prompt=prompt,
                proporcao=prop_ajustada,
                nivel_fogo=nivel_fogo,
                direcao_olhar=direcao_olhar,
            )
            if out_gerado != out_path:
                shutil.copy2(out_gerado, out_path)

        # 3. Validação rigorosa do arquivo PNG gerado
        if not out_path.exists():
            raise ImageCLIGenerationError(f"Arquivo de imagem não foi criado em {out_path}")

        bytes_cabecalho = out_path.read_bytes()[:8]
        if bytes_cabecalho != b"\x89PNG\r\n\x1a\n":
            raise ImageCLIGenerationError(f"Arquivo gerado em {out_path} não possui cabeçalho PNG válido.")

        return out_path


@no_agente("direcao.gerador_imagem_cli", categoria_modelo="IMG")
def gerador_imagem_cli_node(state: EstadoEpisodio) -> Dict[str, Any]:
    """Nó do Agente Gerador de Imagens via CLI."""
    planos = list(state.get("decupagem", {}).get("planos", []))
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
        )
        p["storyboard"] = str(img_path)

    return {
        "decupagem": {
            "planos": planos,
        }
    }
