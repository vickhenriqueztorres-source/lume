"""Contratos dos Gates Humanos (Doc 05 §7).

Define os esquemas das cargas úteis dos interrupts e das respostas humanas
validadas, garantindo o registro formal em `aprovacoes` como evidência
de contribuição humana.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class RespostaGate(BaseModel):
    """Resposta estruturada do humano ou simulação aprovada no Gate."""

    gate_id: int = Field(ge=1, le=5, description="Número do gate (1 a 5)")
    status: Literal["aprovado", "editado", "refazer"] = Field(description="Decisão humana")
    autor: str = Field(default="operador", description="Identificação do humano ou 'simulado_teste'")
    comentarios: str = Field(default="", description="Feedback ou justificativa")
    ajustes: Optional[Dict[str, Any]] = Field(default=None, description="Modificações manuais se status=editado")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    simulado: bool = Field(default=False, description="Flag explícita indicando resposta de teste")


class PayloadGateRoteiro(BaseModel):
    """O que o humano vê no Gate 1."""
    titulo: str
    versao: int
    blocos: List[Dict[str, Any]]
    notas_retencao: List[str]
    notas_fidelidade: List[str]
    notas_tom: List[str]
    fontes: List[Dict[str, Any]]


class PayloadGateStoryboard(BaseModel):
    """O que o humano vê no Gate 2."""
    total_planos: int
    duracao_total_s: float
    animatic_caminho: Optional[str]
    color_script: Dict[str, Any]
    planos_preview: List[Dict[str, Any]]


class PayloadGateCorteFinal(BaseModel):
    """O que o humano vê no Gate 3."""
    master_caminho: Optional[str]
    duracao_total_s: float
    lufs_medido: Optional[float]
    relatorios_qa: List[Dict[str, Any]]
    marcas_tempo: List[Dict[str, Any]]


class PayloadGateEmbalagem(BaseModel):
    """O que o humano vê no Gate 4."""
    titulos: List[str]
    thumbs: List[Dict[str, Any]]
    ranking_feed: List[Dict[str, Any]]
    descricao: str
    shorts: List[Dict[str, Any]]


class PayloadGatePublicacao(BaseModel):
    """O que o humano vê no Gate 5 (opcional)."""
    video_id: str
    status_atual: Literal["privado"]
    verificacoes_youtube: Dict[str, Any]
    agendamento_sugerido: Optional[str]
