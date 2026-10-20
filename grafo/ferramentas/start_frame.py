"""Gerador de Start Frames e Ativos Visuais (IMG) para o Estúdio LUME.

Gera frames cinematográficos limpos (sem texto, logos ou marcas d'água)
para teatro de sombras, silhuetas e braseiro, prontos para animação no Firefly.
Paleta canônica (Doc 03):
- Silhueta: #16110D (preto carvão quente)
- Fogo braseiro: #E85D04 (laranja incandescente)
- Luz divina: #FDF0D5 (âmbar suave)
- Pedra de fundo: #2B2621 (cinza ardósia quente)
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFilter

LOGGER = logging.getLogger(__name__)


class StartFrameSecurityError(Exception):
    """Tentativa de Path Traversal ou caminho inseguro detectada."""
    pass


class StartFrameGenerationError(Exception):
    """Erro durante a geração ou gravação da imagem."""
    pass


class StartFrameGenerator:
    """Gerador de Start Frames limpos em 16:9 ou 9:16."""

    def __init__(self, output_base_dir: str | Path = "storage_local/frames"):
        self.output_base_dir = Path(output_base_dir)

    def sanitizar_identificador(self, id_str: str) -> str:
        """Sanitiza o identificador para evitar Path Traversal e injeção de caracteres."""
        if ".." in id_str or "/" in id_str or "\\" in id_str:
            raise StartFrameSecurityError(f"Identificador inválido ou tentativa de Path Traversal: '{id_str}'")
        # Permite apenas alfanumérico, hífen e sublinhado
        sanitizado = re.sub(r"[^a-zA-Z0-9_\-]", "", id_str)
        if not sanitizado:
            raise StartFrameSecurityError(f"Identificador resultou em string vazia após sanitização: '{id_str}'")
        return sanitizado

    def obter_dimensoes(self, proporcao: str = "16:9") -> Tuple[int, int]:
        """Retorna (largura, altura) conforme a proporção."""
        if proporcao in ("9:16", "vertical"):
            return (1080, 1920)
        # Padrão: 16:9 widescreen
        return (1920, 1080)

    def gerar_start_frame(
        self,
        plano_id: str,
        prompt: str = "",
        proporcao: str = "16:9",
        nivel_fogo: int = 2,
        direcao_olhar: str = "D",
    ) -> Path:
        """Gera um arquivo PNG de Start Frame no disco."""
        id_sanitizado = self.sanitizar_identificador(plano_id)
        largura, altura = self.obter_dimensoes(proporcao)

        target_dir = self.output_base_dir / "start_frames"
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise StartFrameGenerationError(f"Falha ao criar diretório '{target_dir}': {e}") from e

        out_path = target_dir / f"{id_sanitizado}.png"

        try:
            # 1. Base: parede de pedra escura com textura de braseiro (#2B2621)
            img = Image.new("RGB", (largura, altura), color=(43, 38, 33))
            draw = ImageDraw.Draw(img)

            # 2. Gradiente radial de luz de fogo na base (#E85D04)
            # Centro da fogueira no rodapé
            fogo_y = altura
            fogo_x = largura // 4 if direcao_olhar == "D" else (largura * 3) // 4
            raio_max = int(altura * (0.6 + 0.1 * min(nivel_fogo, 5)))

            for r in range(raio_max, 0, -25):
                alpha = int(40 * (1.0 - r / raio_max))
                # Cor do fogo quente
                draw.ellipse(
                    [(fogo_x - r, fogo_y - r // 2), (fogo_x + r, fogo_y + r // 2)],
                    fill=(int(43 + alpha * 3.5), int(38 + alpha * 1.5), int(33 + alpha * 0.2)),
                )

            # 3. Silhueta de marionete / teatro de sombras (#16110D)
            # Posicionamento dramático conforme a direção de tela (olha para a direita D ou esquerda E)
            cor_silhueta = (22, 17, 13)  # #16110D
            centro_x = largura // 2
            centro_y = int(altura * 0.6)
            raio_silhueta_x = int(largura * 0.18)
            raio_silhueta_y = int(altura * 0.35)

            draw.ellipse(
                [(centro_x - raio_silhueta_x, centro_y - raio_silhueta_y),
                 (centro_x + raio_silhueta_x, centro_y + raio_silhueta_y)],
                fill=cor_silhueta,
            )

            # 4. Vinheta de borda suave (escurecimento atmosférico)
            img = img.filter(ImageFilter.SMOOTH_MORE)
            img.save(out_path, format="PNG", optimize=True)

            LOGGER.info(f"[START_FRAME] Frame gerado com sucesso: {out_path} ({largura}x{altura})")
            return out_path

        except Exception as e:
            if isinstance(e, (StartFrameSecurityError, StartFrameGenerationError)):
                raise
            raise StartFrameGenerationError(f"Erro ao renderizar imagem do start frame: {e}") from e
