"""Testes unitários de rotação e fallback de chaves de API quando os tokens acabam."""

from __future__ import annotations

import io
import json
import urllib.error
import pytest

from grafo.ferramentas.audio import (
    DEFAULT_GEMINI_API_KEYS,
    erro_indica_fim_de_tokens,
    obter_chaves_api_audio,
    requisitar_gemini_com_fallback,
)


class _FakeHTTPResponse:
    def __init__(self, body: dict):
        self._raw = json.dumps(body).encode("utf-8")

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def test_pool_padrao_contem_duas_chaves_em_ordem(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEYS", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_1", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY_2", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    chaves = obter_chaves_api_audio()
    assert len(chaves) == 2
    assert chaves[0] == "ENV_GEMINI_API_KEY_1"
    assert chaves[1] == "ENV_GEMINI_API_KEY_2"
    assert chaves == DEFAULT_GEMINI_API_KEYS


def test_fallback_automatico_quando_chave_1_esgota_tokens():
    urls_chamadas = []

    def fake_urlopen(req, timeout=60):
        urls_chamadas.append(req.full_url)
        if DEFAULT_GEMINI_API_KEYS[0] in req.full_url:
            raise urllib.error.HTTPError(
                url=req.full_url,
                code=429,
                msg="RESOURCE_EXHAUSTED: Quota/tokens exceeded",
                hdrs=None,
                fp=io.BytesIO(b'{"error": {"status": "RESOURCE_EXHAUSTED"}}'),
            )
        return _FakeHTTPResponse({"candidates": [{"content": {"parts": [{"inlineData": {"data": "AA=="}}]}}]})

    resp = requisitar_gemini_com_fallback(
        model_name="gemini-2.5-flash-preview-tts",
        payload={"contents": []},
        urlopen_fn=fake_urlopen,
    )

    assert len(urls_chamadas) == 2
    assert DEFAULT_GEMINI_API_KEYS[0] in urls_chamadas[0]
    assert DEFAULT_GEMINI_API_KEYS[1] in urls_chamadas[1]
    assert "candidates" in resp


def test_erro_quando_todas_as_chaves_esgotam_tokens():
    def fake_urlopen_sempre_429(req, timeout=60):
        raise urllib.error.HTTPError(
            url=req.full_url,
            code=429,
            msg="Too Many Requests",
            hdrs=None,
            fp=io.BytesIO(b"quota exceeded"),
        )

    with pytest.raises(RuntimeError, match="Todas as 2 chaves de API falharam"):
        requisitar_gemini_com_fallback(
            model_name="gemini-2.5-flash-preview-tts",
            payload={"contents": []},
            urlopen_fn=fake_urlopen_sempre_429,
        )


def test_deteccao_erros_de_cota_e_tokens():
    err_429 = urllib.error.HTTPError("http://test", 429, "Quota exceeded", None, io.BytesIO(b""))
    assert erro_indica_fim_de_tokens(err_429) is True
    assert erro_indica_fim_de_tokens(RuntimeError("RESOURCE_EXHAUSTED: tokens limit")) is True
