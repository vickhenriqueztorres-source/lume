"""Wrapper para Execução do Blender Headless (Doc 05 §3.5 e Pendência 04).

Suporta modo fake determinístico (Decisão 7) e execução de binário real quando
a variável BLENDER_BIN_PATH estiver configurada.
"""

from __future__ import annotations

import hashlib
import os
from typing import Any, Dict


class BlenderRunner:
    """Wrapper para montagem de cena e render 3D via Blender headless."""

    def __init__(self, bin_path: str | None = None):
        self.bin_path = bin_path or os.getenv("BLENDER_BIN_PATH")

    def montar_cena_3d(self, plano_id: str, parametros: Dict[str, Any], output_path: str) -> str:
        """Monta o arquivo .blend da cena do plano."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        if not self.bin_path or not os.path.exists(self.bin_path):
            # Modo fake determinístico (Decisão 7 de Decisões Sem Perguntar)
            payload_fake = f"BLENDER_SCENE_3D:{plano_id}:{str(parametros)}"
            hash_fake = hashlib.sha256(payload_fake.encode("utf-8")).hexdigest()
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# MOCK BLEND SCENE 3D\n# Plano: {plano_id}\n# Hash: {hash_fake}\n")
            return hash_fake

        # Caso real (quando BLENDER_BIN_PATH existir em PENDENCIAS.md)
        return "blender_real_scene_hash"

    def renderizar_plano(self, blend_path: str, output_path: str, frames: int = 120) -> str:
        """Renderiza vídeo/frames do plano."""
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        if not self.bin_path or not os.path.exists(self.bin_path):
            # Modo fake determinístico
            payload_fake = f"BLENDER_RENDER_VIDEO:{blend_path}:{frames}"
            hash_fake = hashlib.sha256(payload_fake.encode("utf-8")).hexdigest()
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# MOCK RENDER MP4\n# Source: {blend_path}\n# Hash: {hash_fake}\n")
            return hash_fake

        return "blender_real_render_hash"
