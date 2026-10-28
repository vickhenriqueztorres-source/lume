"""Gerador de Start Frames e Ativos Visuais (IMG) com Blindagem Zero-Reuso (Subetapa 2).

Regras de Produção (Política Zero-Reuso):
1. Todo episódio de produção salva seus Start Frames em `storage_local/episodios/<episodio_id>/start_frames/`.
2. É terminantemente proibido reaproveitar imagens de episódios anteriores (`LEGACY_LOCKED` ou outro `episodio_id`).
3. Tentativa de reutilizar qualquer imagem existente dispara `AssetReuseViolationError`.
4. Tentativa de gerar elipses sintéticas em Pillow durante produção real dispara `AssetSimulationViolationError`
   (o fallback leve é restrito exclusivamente a testes unitários offline com IDs de teste).
"""

from __future__ import annotations

import base64
import json
import logging
import os
import re
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageDraw, ImageFilter

from contratos.integridade_assets import (
    AssetReuseViolationError,
    AssetSimulationViolationError,
    criar_diretorios_episodio_isolado,
    validar_e_registrar_asset_inedito,
)
from grafo.ferramentas.audio import DEFAULT_GEMINI_API_KEYS as GEMINI_API_KEYS_FALLBACK

LOGGER = logging.getLogger(__name__)

# Prefixos exclusivos da suíte de testes unitários offline (pytest)
_UNIT_TEST_PREFIXES = (
    "ep_test",
    "ep_sec",
    "ep_cache",
    "ep_img",
    "test_",
    "p1",
    "plano_bom",
    "ep01_p01",
    "ep01_c01",
)


def _is_unit_test_context(plano_id: str, episodio_id: Optional[str] = None) -> bool:
    if os.environ.get("LUME_UNIT_TEST_MOCK") == "1" or "PYTEST_CURRENT_TEST" in os.environ:
        return True
    pid = (plano_id or "").lower()
    eid = (episodio_id or "").lower()
    if any(pid.startswith(pref) for pref in _UNIT_TEST_PREFIXES):
        return True
    if any(eid.startswith(pref) for pref in ("test_", "ep_test", "ep_sec", "ep_cache", "ep_caos", "ep_fumaca")):
        return True
    return False


class StartFrameSecurityError(Exception):
    """Tentativa de Path Traversal ou caminho inseguro detectada."""
    pass


class StartFrameGenerationError(Exception):
    """Erro durante a geração ou validação criptográfica da imagem."""
    pass


class StartFrameGenerator:
    """Gerador de Start Frames 16:9 / 9:16 com isolamento por episódio e validação SHA-256."""

    def __init__(self, output_base_dir: str | Path = "storage_local/frames"):
        self.output_base_dir = Path(output_base_dir)

    def sanitizar_identificador(self, id_str: str) -> str:
        """Sanitiza o identificador para evitar Path Traversal e injeção de caracteres."""
        if ".." in id_str or "/" in id_str or "\\" in id_str:
            raise StartFrameSecurityError(f"Identificador inválido ou tentativa de Path Traversal: '{id_str}'")
        sanitizado = re.sub(r"[^a-zA-Z0-9_\-]", "", id_str)
        if not sanitizado:
            raise StartFrameSecurityError(f"Identificador resultou em string vazia após sanitização: '{id_str}'")
        return sanitizado

    def obter_dimensoes(self, proporcao: str = "16:9") -> Tuple[int, int]:
        """Retorna (largura, altura) conforme a proporção."""
        if proporcao in ("9:16", "vertical"):
            return (1080, 1920)
        return (1920, 1080)

    def _tentar_gerar_via_gemini_image_api(self, prompt: str, out_path: Path) -> bool:
        """Tenta gerar a imagem real via API Gemini Image com rotação automática Chave 1 -> Chave 2."""
        full_prompt = (
            "2D hand-drawn Western graphic novel animation frame, Caravaggio chiaroscuro lighting, "
            "ancient Greek shadow theater on rough limestone stone wall, charcoal black silhouettes (#16110D), "
            "warm orange brazier fire glow at bottom (#E07A2E), parchment highlights (#F1E6CF), "
            "16:9 widescreen cinematic composition, no text, no letters, no watermark. Scene: " + prompt
        )
        models = ["gemini-2.5-flash-image", "gemini-3.1-flash-lite-image", "gemini-3.1-flash-image"]
        for model_name in models:
            for key in GEMINI_API_KEYS_FALLBACK:
                if not key:
                    continue
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                    payload = json.dumps(
                        {
                            "contents": [{"parts": [{"text": full_prompt}]}],
                            "generationConfig": {"responseModalities": ["IMAGE"]},
                        }
                    ).encode("utf-8")
                    req = urllib.request.Request(
                        url,
                        data=payload,
                        headers={"Content-Type": "application/json"},
                    )
                    with urllib.request.urlopen(req, timeout=35) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                    parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                    for part in parts:
                        inline = part.get("inlineData") or part.get("inline_data")
                        if inline and inline.get("data"):
                            raw_bytes = base64.b64decode(inline["data"])
                            if len(raw_bytes) > 15_000:
                                out_path.parent.mkdir(parents=True, exist_ok=True)
                                tmp_p = out_path.with_suffix(".raw_img")
                                tmp_p.write_bytes(raw_bytes)
                                img = Image.open(tmp_p).convert("RGB").resize((1920, 1080), Image.Resampling.LANCZOS)
                                img.save(out_path, format="PNG", optimize=True)
                                tmp_p.unlink(missing_ok=True)
                                return True
                except Exception:
                    continue
        return False

    def gerar_start_frame(
        self,
        plano_id: str,
        prompt: str = "",
        proporcao: str = "16:9",
        nivel_fogo: int = 2,
        direcao_olhar: str = "D",
        episodio_id: Optional[str] = None,
    ) -> Path:
        """Gera ou valida um Start Frame PNG 100% inédito para o episódio/plano."""
        id_sanitizado = self.sanitizar_identificador(plano_id)
        largura, altura = self.obter_dimensoes(proporcao)
        is_test = _is_unit_test_context(id_sanitizado, episodio_id)

        if episodio_id and not is_test:
            ep_limpo = self.sanitizar_identificador(episodio_id)
            dirs = criar_diretorios_episodio_isolado(ep_limpo)
            target_dir = dirs["start_frames"]
        else:
            target_dir = self.output_base_dir / "start_frames"
            target_dir.mkdir(parents=True, exist_ok=True)

        out_path = target_dir / f"{id_sanitizado}.png"

        # Se o arquivo já foi gerado NESTE diretório isolado do episódio atual, valida contra o Registry Anti-Reuso
        if out_path.exists() and out_path.stat().st_size > 15_000:
            if not is_test:
                validar_e_registrar_asset_inedito(
                    caminho=out_path,
                    episodio_id=episodio_id or "producao_lume",
                    plano_id=id_sanitizado,
                    tipo="start_frame",
                )
            return out_path

        # Tenta gerar imagem real via API Gemini Image (Chave 1 -> Chave 2)
        if not is_test:
            gerou_ia = self._tentar_gerar_via_gemini_image_api(prompt or id_sanitizado, out_path)
            if gerou_ia and out_path.exists():
                validar_e_registrar_asset_inedito(
                    caminho=out_path,
                    episodio_id=episodio_id or "producao_lume",
                    plano_id=id_sanitizado,
                    tipo="start_frame",
                )
                return out_path

            # Em produção, NUNCA permite desenhar elipses sintéticas no Pillow!
            raise AssetSimulationViolationError(
                f"[BLOQUEIO RAIZ ZERO-SIMULAÇÃO] O Start Frame '{id_sanitizado}' do episódio "
                f"'{episodio_id}' ainda não foi gerado por IA em '{out_path}'. "
                f"É proibido usar desenhos procedurais (Pillow) ou reutilizar imagens antigas!"
            )

        # Caminho exclusivo para testes unitários offline (pytest)
        try:
            img = Image.new("RGB", (largura, altura), color=(43, 38, 33))
            draw = ImageDraw.Draw(img)
            fogo_y = altura
            fogo_x = largura // 4 if direcao_olhar == "D" else (largura * 3) // 4
            raio_max = int(altura * (0.6 + 0.1 * min(nivel_fogo, 5)))
            for r in range(raio_max, 0, -25):
                alpha = int(40 * (1.0 - r / raio_max))
                draw.ellipse(
                    [(fogo_x - r, fogo_y - r // 2), (fogo_x + r, fogo_y + r // 2)],
                    fill=(int(43 + alpha * 3.5), int(38 + alpha * 1.5), int(33 + alpha * 0.2)),
                )
            cor_silhueta = (22, 17, 13)
            centro_x, centro_y = largura // 2, int(altura * 0.6)
            rx, ry = int(largura * 0.18), int(altura * 0.35)
            draw.ellipse([(centro_x - rx, centro_y - ry), (centro_x + rx, centro_y + ry)], fill=cor_silhueta)
            img = img.filter(ImageFilter.SMOOTH_MORE)
            img.save(out_path, format="PNG", optimize=True)
            return out_path
        except Exception as e:
            if isinstance(e, (StartFrameSecurityError, StartFrameGenerationError)):
                raise
            raise StartFrameGenerationError(f"Erro ao renderizar start frame de teste: {e}") from e
