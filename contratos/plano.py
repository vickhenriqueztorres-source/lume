"""Contrato do Plano (Doc 05 §5).

A unidade atômica de trabalho que trafega via Send entre departamentos.
Define todos os campos cinematográficos e o cálculo determinístico de hash
para cache de renderização.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class MarioneteNoPlano(BaseModel):
    id: str
    distancia_fogo: float = Field(default=0.5, ge=0.0, le=1.0, description="0.0 = colada ao fogo, 1.0 = colada à parede")
    direcao: Literal["esq", "dir", "centro"] = Field(default="dir", description="dir (→ casa) ou esq (← contra)")
    pose_ini: Optional[str] = None
    pose_fim: Optional[str] = None


class CameraNoPlano(BaseModel):
    movimento: str = Field(default="push_in_lento", description="push_in_lento, dolly_lateral, tilt_up, rack_focus, fixo")
    lente_mm: int = Field(default=35, description="35-50mm mundo da parede, 85-135mm mundo do contador")
    inicio: Optional[Dict[str, Any]] = None
    fim: Optional[Dict[str, Any]] = None


class FogoNoPlano(BaseModel):
    nivel: int = Field(default=2, ge=1, le=5, description="1=brasa, 2=calmo, 3=vivo, 4=alto, 5=estouro")
    curva: str = Field(default="estavel", description="subida, descida, estavel, pico")
    tremulacao_hz: float = Field(default=1.0, ge=0.1, le=10.0)


class LuzDeusNoPlano(BaseModel):
    tipo: str = Field(description="caustica_poseidon, raio_zeus, luz_fria_atena, sol_helio")
    lado: str = Field(default="cima", description="cima, baixo, lateral")


class RenderNoPlano(BaseModel):
    caminho: Optional[str] = None
    hash: Optional[str] = None
    status: Literal["pendente", "enviado", "concluido", "falhou"] = "pendente"
    tentativas: int = 0
    erro: Optional[str] = None


class QANoPlano(BaseModel):
    continuidade: Literal["pendente", "ok", "reprovado"] = "pendente"
    notas: List[str] = Field(default_factory=list)


class Plano(BaseModel):
    """Contrato canônico do plano conforme Doc 05 §5."""

    id: str = Field(description="Ex.: ep01_c01_p01")
    bloco_roteiro: int = Field(description="Índice do bloco de roteiro ao qual pertence")
    mundo: Literal["parede", "contador"] = Field(default="parede")
    tipo_plano: Literal["friso", "medio", "close", "insert", "escala", "contador"] = Field(default="medio")
    duracao_s: float = Field(default=5.0, ge=0.5, le=60.0)
    marionetes: List[MarioneteNoPlano] = Field(default_factory=list)
    camera: CameraNoPlano = Field(default_factory=CameraNoPlano)
    fogo: FogoNoPlano = Field(default_factory=FogoNoPlano)
    luz_deus: Optional[LuzDeusNoPlano] = None
    proporcao: Literal["16:9", "2.39", "3:1"] = Field(default="2.39")
    parede: str = Field(default="pedra_calcario", description="Textura da parede")
    transicao_saida: Optional[str] = None
    sfx: List[str] = Field(default_factory=list)
    storyboard: Optional[str] = None
    intencao_visual: Optional[str] = Field(
        default=None,
        description="Intenção visual curta escrita pela Direção para orientar a ação de vídeo IA [adicionado na construção]",
    )
    prompt_imagem: Optional[str] = Field(default=None, description="Prompt cinemático para geração de imagem / start frame")
    prompt_video: Optional[str] = Field(default=None, description="Prompt cinemático de movimento para animação no Firefly")
    render: RenderNoPlano = Field(default_factory=RenderNoPlano)
    qa: QANoPlano = Field(default_factory=QANoPlano)

    def obter_payload_visual(self) -> Dict[str, Any]:
        """Extrai apenas os campos visuais que afetam o render para cálculo do hash de cache."""
        return {
            "mundo": self.mundo,
            "tipo_plano": self.tipo_plano,
            "duracao_s": round(self.duracao_s, 2),
            "marionetes": [m.model_dump() for m in self.marionetes],
            "camera": self.camera.model_dump(),
            "fogo": self.fogo.model_dump(),
            "luz_deus": self.luz_deus.model_dump() if self.luz_deus else None,
            "proporcao": self.proporcao,
            "parede": self.parede,
        }

    def calcular_hash(self) -> str:
        """Calcula o SHA-256 dos campos visuais do plano."""
        return calcular_hash_plano(self)


def calcular_hash_plano(plano: Plano | Dict[str, Any]) -> str:
    """Calcula hash determinístico SHA-256 sobre os campos visuais do contrato do plano.

    Garante que alterações não-visuais (como sfx, notas de qa) não invalidem o render em cache.
    """
    if isinstance(plano, Plano):
        payload = plano.obter_payload_visual()
    elif isinstance(plano, dict):
        p = Plano.model_validate(plano)
        payload = p.obter_payload_visual()
    else:
        raise TypeError(f"Tipo inválido para cálculo de hash: {type(plano)}")

    serializado = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()
