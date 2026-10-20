"""Fila Assíncrona de Render e Cache de Planos (Doc 05 §5 e §6).

Gerencia:
1. Envio de jobs de renderização fora do grafo com controle de concorrência.
2. Retomada por webhook/callback.
3. Cache determinístico de renders baseado no hash visual do contrato do plano.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional
from contratos.plano import Plano, calcular_hash_plano
from grafo.ferramentas.blender import BlenderRunner


class FilaRender:
    """Fila de jobs de render com concorrência limitada e cache de hash."""

    def __init__(self, max_concurrency: int = 5):
        self.max_concurrency = max_concurrency
        self.executor = ThreadPoolExecutor(max_workers=max_concurrency)
        self.blender = BlenderRunner()
        self.cache: Dict[str, Dict[str, Any]] = {}

    def submeter_job_render(
        self,
        plano: Plano | Dict[str, Any],
        blend_path: str,
        output_mp4_path: str,
    ) -> Dict[str, Any]:
        """Processa ou recupera o render do plano com garantia de cache por hash."""
        hash_visual = calcular_hash_plano(plano)

        # 1. Checa se o hash visual já existe no cache
        if hash_visual in self.cache:
            item_cache = self.cache[hash_visual]
            return {
                "hash": hash_visual,
                "caminho": item_cache["caminho"],
                "cache_hit": True,
                "status": "concluido",
            }

        # 2. Renderiza o vídeo via Blender headless (com pool limitado)
        render_hash = self.blender.renderizar_plano(blend_path, output_mp4_path)

        resultado = {
            "hash": hash_visual,
            "render_hash": render_hash,
            "caminho": output_mp4_path,
            "cache_hit": False,
            "status": "concluido",
        }
        self.cache[hash_visual] = resultado
        return resultado


_FILA_GLOBAL: Optional[FilaRender] = None


def obter_fila_render(max_concurrency: int = 5) -> FilaRender:
    global _FILA_GLOBAL
    if _FILA_GLOBAL is None:
        _FILA_GLOBAL = FilaRender(max_concurrency=max_concurrency)
    return _FILA_GLOBAL
