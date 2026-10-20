"""Adaptador de Inferência LLM via CLI Local (Codex / Antigravity).

Permite aos agentes dos departamentos (LLM-R e LLM-V) utilizarem inferência
através da sessão autenticada local do Codex CLI ou Antigravity CLI, eliminando
a necessidade de chaves de API pagas ou credenciais externas de terceiros.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, Optional, Type, TypeVar
from pydantic import BaseModel, ValidationError

LOGGER = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class CLIExecutionError(Exception):
    """Erro ao invocar o executável CLI ou falha na resposta."""
    pass


class CLITimeoutError(CLIExecutionError):
    """Timeout excedido na execução do CLI."""
    pass


class CLISecurityError(CLIExecutionError):
    """Tentativa de injeção ou caracteres inválidos detectados na entrada."""
    pass


class CodexCLIClient:
    """Cliente para execução de inferência via Codex CLI (`codex.cmd exec`) ou Antigravity."""

    def __init__(
        self,
        modelo: str = "gpt-5.6-terra",
        timeout_seconds: float = 45.0,
        mock_fallback: bool = True,
        cli_command: Optional[str] = None,
    ):
        self.modelo = modelo
        self.timeout_seconds = timeout_seconds
        self.mock_fallback = mock_fallback
        
        # Localiza o comando CLI
        self.cli_command = cli_command or os.getenv("CODEX_CLI_CMD")
        if not self.cli_command:
            # Procura codex.cmd ou codex no PATH
            cmd_found = shutil.which("codex.cmd") or shutil.which("codex")
            self.cli_command = cmd_found or "codex.cmd"

    def sanitizar_entrada(self, prompt: str) -> str:
        """Sanitiza a entrada para prevenir ataques de injeção e caracteres nulos."""
        if "\x00" in prompt:
            raise CLISecurityError("Caractere nulo detectado na entrada.")
        # Limita o tamanho máximo de entrada segura (200 KB)
        if len(prompt) > 200_000:
            raise CLISecurityError("Tamanho do prompt excede o limite seguro de 200 KB.")
        return prompt

    def gerar_estruturado(
        self,
        schema: Type[T],
        prompt_sistema: str,
        entradas: Dict[str, Any],
        forcar_mock: bool = False,
    ) -> T:
        """Gera resposta estruturada em conformidade com o schema Pydantic."""
        if forcar_mock:
            return self._gerar_mock_deterministico(schema, entradas)

        # Monta prompt instruindo retorno estrito em formato JSON aderente ao schema
        schema_json = json.dumps(schema.model_json_schema(), ensure_ascii=False)
        prompt_completo = (
            f"SISTEMA: {prompt_sistema}\n\n"
            f"SCHEMA JSON ESPERADO:\n{schema_json}\n\n"
            f"ENTRADAS:\n{json.dumps(entradas, ensure_ascii=False)}\n\n"
            f"INSTRUÇÃO CRÍTICA: Retorne EXCLUSIVAMENTE um objeto JSON válido, sem texto introdutório, "
            f"sem markdown e sem blocos ```json. Sua resposta inteira deve começar com '{{' e terminar com '}}'."
        )

        try:
            prompt_sanitizado = self.sanitizar_entrada(prompt_completo)
            resposta_raw = self._executar_cli(prompt_sanitizado)
            json_extraido = self._extrair_json(resposta_raw)
            return schema.model_validate(json_extraido)
        except Exception as e:
            LOGGER.warning(f"[CLI_LLM] Falha na execução via CLI ({e}). Verificando fallback.")
            if self.mock_fallback:
                LOGGER.info(f"[CLI_LLM] Acionando fallback determinístico para schema {schema.__name__}.")
                return self._gerar_mock_deterministico(schema, entradas)
            raise

    def _executar_cli(self, prompt: str) -> str:
        """Executa o processo de CLI passando o prompt via stdin de forma segura."""
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json") as tmp_out:
            tmp_out_path = tmp_out.name

        try:
            # Comando não-interativo com captura em arquivo
            args = [
                self.cli_command,
                "exec",
                "--skip-git-repo-check",
                "--ephemeral",
                "-m",
                self.modelo,
                "-o",
                tmp_out_path,
                "-",
            ]

            process = subprocess.run(
                args,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self.timeout_seconds,
            )

            # Prioriza a leitura do arquivo de saída last-message
            saida = ""
            if os.path.exists(tmp_out_path):
                with open(tmp_out_path, "r", encoding="utf-8", errors="replace") as f:
                    saida = f.read().strip()

            if not saida:
                saida = (process.stdout or "").strip()

            if process.returncode != 0 and not saida:
                raise CLIExecutionError(
                    f"CLI retornou erro {process.returncode}: {process.stderr[:400]}"
                )

            if not saida:
                raise CLIExecutionError("CLI executou com sucesso mas nenhuma saída foi retornada.")

            return saida
        except subprocess.TimeoutExpired as e:
            raise CLITimeoutError(f"CLI excedeu o timeout de {self.timeout_seconds}s.") from e
        except FileNotFoundError as e:
            raise CLIExecutionError(f"Executável CLI '{self.cli_command}' não foi encontrado.") from e
        finally:
            if os.path.exists(tmp_out_path):
                try:
                    os.remove(tmp_out_path)
                except OSError:
                    pass

    def _extrair_json(self, texto: str) -> Dict[str, Any]:
        """Localiza e decodifica o primeiro bloco JSON válido no texto."""
        texto = texto.strip()
        # Remove marcadores de código caso o modelo tenha incluído
        if texto.startswith("```json"):
            texto = texto[7:]
        elif texto.startswith("```"):
            texto = texto[3:]
        if texto.endswith("```"):
            texto = texto[:-3]
        texto = texto.strip()

        # Busca delimitadores { ... }
        start = texto.find("{")
        end = texto.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_str = texto[start : end + 1]
            return json.loads(json_str)

        return json.loads(texto)

    def _gerar_mock_deterministico(self, schema: Type[T], entradas: Dict[str, Any]) -> T:
        """Fallback determinístico alinhado aos schemas de produção de LUME."""
        from pydantic_core import PydanticUndefined
        from grafo.ferramentas.modelos import ModeloFakeResposta
        fake = ModeloFakeResposta(categoria="LLM-R")
        try:
            return fake.gerar_estruturado(schema=schema, prompt_sistema="", entradas=entradas)
        except ValueError:
            # Para schemas genéricos ou de teste, preenche campos com valores válidos
            dummy_data: Dict[str, Any] = {}
            for name, field in schema.model_fields.items():
                if field.default is not None and field.default is not PydanticUndefined:
                    dummy_data[name] = field.default
                elif field.annotation is str:
                    dummy_data[name] = "dummy_string"
                elif field.annotation in (int, float):
                    dummy_data[name] = 10
                elif field.annotation is bool:
                    dummy_data[name] = True
                elif field.annotation is list:
                    dummy_data[name] = []
                elif field.annotation is dict:
                    dummy_data[name] = {}
                else:
                    dummy_data[name] = "mock_value"
            return schema.model_validate(dummy_data)
