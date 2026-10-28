# -*- coding: utf-8 -*-
"""Testes de integração do servidor MCP `canal_lume` e do bridge local no projeto LUME."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from grafo.ferramentas.canal_lume_mcp import (
    CANAL_LUME_MCP_SCRIPT,
    enviar_dica_lume,
    enviar_tema_lume,
    injetar_inbox_no_estado,
    listar_dicas_mcp,
    receber_tema_mcp,
)


def test_config_mcp_arquivos_existem():
    """Verifica se a configuração `canal_lume` foi registrada nos arquivos do projeto."""
    for cfg_name in ("mcp_config.json", ".mcp.json", ".agents/mcp_config.json"):
        cfg_path = Path("d:/LUME") / cfg_name
        assert cfg_path.exists(), f"Arquivo {cfg_path} não encontrado"
        dados = json.loads(cfg_path.read_text(encoding="utf-8"))
        assert "canal_lume" in dados.get("mcpServers", {})
        server = dados["mcpServers"]["canal_lume"]
        assert server["command"] == "python"
        assert server["args"] == [
            r"D:\BRENDA\STUDIO DOCS - YOUTUBE\Canal 06 - Lume\canal_lume_mcp.py"
        ]


def test_fluxo_receber_temas_e_dicas_lume():
    """Testa o envio e recebimento de temas e dicas via `canal_lume_mcp.py`."""
    res_tema = enviar_tema_lume(
        title="O Canto das Sereias e a Cera nos Ouvidos",
        big_idea="O único homem que ouviu a promessa mortal das Sereias amarrado ao mastro e sobreviveu.",
        hook="Todo marinheiro que ouviu essa voz morreu sorrindo nas pedras. Exceto um.",
        myth_or_epic="A Odisseia (Homero)",
        canto_verso="Odisseia, Canto XII, v. 39-200",
        characters=["O Contador", "Odisseu", "Sereias"],
        tips_and_angles="Usar silhueta de corpo de ave com cabeça humana conforme vaso grego (Brief §6.2).",
        schwartz_awareness_level=4,
        thumbnail_layout="B · Escolha",
        thumbnail_words="AMARRE-ME AO MASTRO",
    )
    assert res_tema["status"] == "success"
    tema_id = res_tema["item_id"]
    assert Path(res_tema["lume_file_path"]).exists()

    res_dica = enviar_dica_lume(
        title="Silêncio de 1.5s antes da revelação",
        tip_content="Cortar o crepitar do fogo por 1.5s imediatamente antes do clímax de cada ato (Brief §10).",
        category="audio_sfx",
        apply_to_agent="audio",
    )
    assert res_dica["status"] == "success"

    # Recupera tema e injeta no EstadoEpisodio
    tema_lido = receber_tema_mcp(item_id=tema_id)
    assert tema_lido["status"] == "success"
    assert tema_lido["canto_verso"] == "Odisseia, Canto XII, v. 39-200"

    dicas = listar_dicas_mcp(status="pending")
    assert len(dicas) >= 1

    estado_inicial = {"episodio": {}}
    estado_enriquecido = injetar_inbox_no_estado(estado_inicial, item_id=tema_id)
    assert estado_enriquecido["episodio"]["mcp_item_id"] == tema_id
    assert estado_enriquecido["episodio"]["titulo"] == "O Canto das Sereias e a Cera nos Ouvidos"
    assert len(estado_enriquecido["episodio"]["dicas_mcp"]) >= 1


def test_protocolo_stdio_jsonrpc_mcp():
    """Valida a comunicação JSON-RPC 2.0 via stdio com o script `canal_lume_mcp.py`."""
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_lume_brand_guidelines",
                "arguments": {"section": "Paleta"},
            },
        },
    ]
    stdin_payload = "\n".join(json.dumps(r) for r in requests) + "\n"

    proc = subprocess.run(
        [sys.executable, str(CANAL_LUME_MCP_SCRIPT)],
        input=stdin_payload,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=15,
    )
    assert proc.returncode == 0, f"Erro no MCP: {proc.stderr}"

    lines = [ln.strip() for ln in proc.stdout.strip().splitlines() if ln.strip()]
    assert len(lines) == 3

    resp_init = json.loads(lines[0])
    assert resp_init["result"]["serverInfo"]["name"] == "canal_lume"

    resp_tools = json.loads(lines[1])
    tool_names = {t["name"] for t in resp_tools["result"]["tools"]}
    assert "send_lume_theme" in tool_names
    assert "send_lume_tip" in tool_names
    assert "list_lume_inbox" in tool_names

    resp_call = json.loads(lines[2])
    content_json = json.loads(resp_call["result"]["content"][0]["text"])
    assert content_json["channel"] == "Canal 06 - LUME"
    assert "#16110D" in content_json["brief_markdown"]
