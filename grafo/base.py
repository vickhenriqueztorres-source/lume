"""Infraestrutura Base para Execução de Nós de Agentes (Doc 05 §6 e Regras 1-10).

Garante que todos os nós:
1. Gravem assinatura: `versao` + `autor_no`.
2. Respeitem o subcampo permitido via `validar_escrita_agente`.
3. Registrem custos automaticamente em `custos` (append).
4. Garantam idempotência em efeitos colaterais através de chave de operação.
5. Capturem erros de execução e registrem em `erros` (append).
"""

from __future__ import annotations

import functools
import hashlib
from typing import Any, Callable, Dict, Optional
from contratos.estado import CustoItem, ErroItem
from contratos.mapeamento import validar_escrita_agente


# Cache local de chaves de operação idempotentes por thread/execução
_OPERACOES_EXECUTADAS: set[str] = set()


def gerar_chave_idempotencia(agente_id: str, contexto: Any) -> str:
    """Gera hash determinístico para chave de operação idempotente."""
    conteudo = f"{agente_id}:{str(contexto)}"
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()


def registrar_operacao_efeito_colateral(chave_op: str) -> bool:
    """Retorna True se a operação já foi executada (evitando re-execução após interrupt)."""
    if chave_op in _OPERACOES_EXECUTADAS:
        return True
    _OPERACOES_EXECUTADAS.add(chave_op)
    return False


def limpar_operacoes_teste() -> None:
    """Auxiliar para testes."""
    _OPERACOES_EXECUTADAS.clear()


def no_agente(
    agente_id: str,
    categoria_modelo: Optional[str] = None,
    tokens_padrao: int = 250,
):
    """Decorator padronizado para nós do LangGraph que assegura cumprimento das regras inegociáveis."""

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(state: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
            try:
                # Executa o nó
                resultado = func(state, *args, **kwargs)
                if not isinstance(resultado, dict):
                    return resultado

                # 1. Valida escrita estrita
                if not validar_escrita_agente(agente_id, resultado):
                    raise PermissionError(
                        f"Agente '{agente_id}' tentou escrever fora do seu subcampo autorizado: {list(resultado.keys())}"
                    )

                # 2. Injeta auditoria nos campos de departamento
                for key, val in resultado.items():
                    if isinstance(val, dict) and key not in {"custos", "erros", "qa", "aprovacoes"}:
                        val.setdefault("autor_no", agente_id)
                        val.setdefault("versao", 1)

                # 3. Registra custos automaticamente (append)
                custo = CustoItem(
                    autor_no=agente_id,
                    tokens_entrada=tokens_padrao,
                    tokens_saida=tokens_padrao // 2,
                    chamadas_api=1,
                    categoria_modelo=categoria_modelo,
                ).model_dump()

                custos_existentes = resultado.get("custos", [])
                resultado["custos"] = custos_existentes + [custo]

                return resultado

            except Exception as e:
                # Registra erro no estado (append)
                erro = ErroItem(
                    autor_no=agente_id,
                    erro=str(e),
                    tentativa=1,
                    decisao="escalar" if isinstance(e, PermissionError) else "refazer",
                ).model_dump()
                return {
                    "erros": [erro],
                }

        return wrapper

    return decorator
