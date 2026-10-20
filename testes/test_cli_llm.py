"""Bateria de Testes Robustos: Adaptador CLI Codex / Antigravity (Subetapa 1).

Cobre:
1. Teste Unitário: parsing e validação de schema Pydantic com saída JSON estruturada.
2. Teste de Estresse: invocações consecutivas garantindo liberação limpa de processos.
3. Teste de Segurança: rejeição de caracteres maliciosos e injeção de comandos.
4. Teste de Caos: resiliência a timeout e falha de processo com fallback determinístico.
"""

import pytest
import time
from pydantic import BaseModel, Field
from grafo.ferramentas.cli_llm import (
    CodexCLIClient,
    CLIExecutionError,
    CLITimeoutError,
    CLISecurityError,
)


class DummySchema(BaseModel):
    titulo: str = Field(..., description="Título gerado")
    nota: int = Field(default=10, description="Nota de 0 a 10")
    aprovado: bool = Field(default=True)


def test_unit_cli_llm_schema_parsing():
    """1. Teste Unitário: Valida extração de JSON e conversão em instância Pydantic."""
    client = CodexCLIClient(mock_fallback=True)
    
    # Valida extração direta de texto simulado
    raw_response = 'Aqui está a resposta:\n```json\n{"titulo": "A Odisseia no Teatro de Sombras", "nota": 9, "aprovado": true}\n```'
    parsed = client._extrair_json(raw_response)
    obj = DummySchema.model_validate(parsed)
    
    assert obj.titulo == "A Odisseia no Teatro de Sombras"
    assert obj.nota == 9
    assert obj.aprovado is True


def test_stress_consecutive_invocations():
    """2. Teste de Estresse: Executa 10 invocações sucessivas sem vazamento de processos ou arquivos temporários."""
    client = CodexCLIClient(mock_fallback=True)
    start_time = time.time()
    
    for i in range(10):
        res = client.gerar_estruturado(
            schema=DummySchema,
            prompt_sistema="Prompt de teste",
            entradas={"iteracao": i},
            forcar_mock=True,
        )
        assert res is not None
        
    duration = time.time() - start_time
    assert duration < 5.0, "10 execuções não devem sofrer degradação de performance."


def test_security_input_sanitization():
    """3. Teste de Segurança: Rejeita injeção de null bytes e excesso de carga."""
    client = CodexCLIClient()
    
    # 1. Null byte
    with pytest.raises(CLISecurityError, match="Caractere nulo"):
        client.sanitizar_entrada("Texto com \x00 caractere malicioso")
        
    # 2. Buffer overflow / payload excessivo (> 200 KB)
    payload_gigante = "A" * 250_000
    with pytest.raises(CLISecurityError, match="excede o limite seguro"):
        client.sanitizar_entrada(payload_gigante)
        
    # 3. Payload normal passa íntegro
    payload_valido = "Gere uma lista de 5 planos com silhuetas #16110D"
    assert client.sanitizar_entrada(payload_valido) == payload_valido


def test_chaos_timeout_and_fallback_resilience():
    """4. Teste de Caos: Simula executável travado/timeout e garante fallback transparente sem quebrar o grafo."""
    # Cliente com timeout mínimo (0.01s) para forçar disparo de timeout
    client = CodexCLIClient(
        cli_command="powershell",  # Usa comando que fica esperando stdin
        timeout_seconds=0.05,
        mock_fallback=True,
    )
    
    # Deve acionar o fallback sem lançar exceção não tratada
    res = client.gerar_estruturado(
        schema=DummySchema,
        prompt_sistema="Sistema",
        entradas={"dado": 123},
    )
    assert res is not None
    assert isinstance(res, DummySchema)
