# -*- coding: utf-8 -*-
"""
Cliente e Bridge Local do MCP `canal_lume` dentro do repositório `d:/LUME`.
Conecta o pipeline LangGraph ao servidor `D:\\BRENDA\\STUDIO DOCS - YOUTUBE\\Canal 06 - Lume\\canal_lume_mcp.py`,
permitindo consumir temas, dicas editoriais e roteiros recebidos via MCP.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

CANAL_LUME_MCP_SCRIPT = Path(
    r"D:\BRENDA\STUDIO DOCS - YOUTUBE\Canal 06 - Lume\canal_lume_mcp.py"
)


def _carregar_modulo_mcp():
    """Carrega dinamicamente o módulo `canal_lume_mcp.py` da pasta do Canal 06."""
    if not CANAL_LUME_MCP_SCRIPT.exists():
        raise FileNotFoundError(
            f"Script MCP do Canal Lume não encontrado em: {CANAL_LUME_MCP_SCRIPT}"
        )
    spec = importlib.util.spec_from_file_location("canal_lume_mcp", str(CANAL_LUME_MCP_SCRIPT))
    if spec is None or spec.loader is None:
        raise ImportError(f"Não foi possível carregar {CANAL_LUME_MCP_SCRIPT}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["canal_lume_mcp"] = mod
    spec.loader.exec_module(mod)
    return mod


def receber_tema_mcp(item_id: Optional[str] = None) -> Dict[str, Any]:
    """Busca o tema pendente mais recente (ou por `item_id`) enviado via MCP `canal_lume`."""
    mod = _carregar_modulo_mcp()
    return mod.get_lume_inbox_item(item_id=item_id, item_type="theme")


def listar_dicas_mcp(status: str = "pending", limit: int = 10) -> List[Dict[str, Any]]:
    """Lista dicas editoriais/técnicas (`tips`) enviadas via MCP para o projeto LUME."""
    mod = _carregar_modulo_mcp()
    res = mod.list_lume_inbox(item_type="tip", status=status, limit=limit)
    return res.get("items", [])


def enviar_tema_lume(**kwargs: Any) -> Dict[str, Any]:
    """Atalho programático para `send_lume_theme`."""
    mod = _carregar_modulo_mcp()
    return mod.send_lume_theme(**kwargs)


def enviar_dica_lume(**kwargs: Any) -> Dict[str, Any]:
    """Atalho programático para `send_lume_tip`."""
    mod = _carregar_modulo_mcp()
    return mod.send_lume_tip(**kwargs)


def injetar_inbox_no_estado(state: Dict[str, Any], item_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Enriquece o `EstadoEpisodio` com o tema pendente e as dicas ativas do MCP `canal_lume`,
    caso ainda não estejam preenchidos no estado.
    """
    novo_estado = dict(state)
    episodio = dict(novo_estado.get("episodio") or {})

    tema = receber_tema_mcp(item_id=item_id)
    if tema.get("status") == "success":
        episodio.setdefault("mcp_item_id", tema.get("id"))
        episodio.setdefault("titulo", tema.get("title"))
        episodio.setdefault("mito", tema.get("category"))
        episodio.setdefault("big_idea", tema.get("big_idea"))
        episodio.setdefault("hook_sugerido", tema.get("hook"))
        episodio.setdefault("canto_verso", tema.get("canto_verso"))

    dicas = listar_dicas_mcp(status="pending", limit=10)
    if dicas:
        episodio["dicas_mcp"] = [
            {"id": d["id"], "titulo": d["title"], "categoria": d["category"]}
            for d in dicas
        ]

    novo_estado["episodio"] = episodio
    return novo_estado


if __name__ == "__main__":
    _mod = _carregar_modulo_mcp()
    _mod.main()
