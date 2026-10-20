"""Checkpointer e Persistência do Grafo (Doc 05 §6 e Regra 6).

Gerencia a persistência de checkpoints com suporte a:
- SQLite (desenvolvimento local e testes de fumaça persistentes)
- Memory (testes unitários isolados)
- Postgres (produção 24/7)
"""

from __future__ import annotations

import os
import sqlite3
from typing import Any, Optional
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore


_STORE_SINGLETON: Optional[BaseStore] = None


def obter_store() -> BaseStore:
    """Retorna o Store compartilhado para biblioteca de marionetes e lições aprendidas."""
    global _STORE_SINGLETON
    if _STORE_SINGLETON is None:
        _STORE_SINGLETON = InMemoryStore()
    return _STORE_SINGLETON


def limpar_store_teste() -> None:
    """Limpa o Store para isolamento entre execuções de teste."""
    global _STORE_SINGLETON
    _STORE_SINGLETON = InMemoryStore()


def obter_checkpointer(
    tipo: Optional[str] = None,
    sqlite_path: str = "storage_local/checkpoints.db",
) -> BaseCheckpointSaver:
    """Retorna o checkpointer configurado conforme limites.yaml ou variável de ambiente."""
    tipo_selecionado = tipo or os.getenv("LUME_CHECKPOINTER_TIPO", "memory").lower()

    if tipo_selecionado == "postgres":
        postgres_uri = os.getenv("POSTGRES_URI")
        if not postgres_uri:
            # Fallback seguro para SQLite conforme Regra 6 de Decisões Sem Perguntar
            tipo_selecionado = "sqlite"
        else:
            try:
                # Tenta instanciar PostgresSaver se pacote e conexão estiverem disponíveis
                from langgraph.checkpoint.postgres import PostgresSaver
                # Retorna instância conectada
                return PostgresSaver.from_conn_string(postgres_uri)
            except Exception:
                tipo_selecionado = "sqlite"

    if tipo_selecionado == "sqlite":
        os.makedirs(os.path.dirname(sqlite_path) or ".", exist_ok=True)
        conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        return SqliteSaver(conn)

    # Padrão: MemorySaver
    return MemorySaver()
