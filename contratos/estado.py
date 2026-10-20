"""Estado do Episódio (Doc 05 §2 + Agentes README §4).

Contrato canônico do estado global compartilhado entre Showrunner e os
10 departamentos no LangGraph 1.x.
"""

from __future__ import annotations

import operator
from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict
from pydantic import BaseModel, Field


def deep_merge_dict(a: Optional[Dict[str, Any]], b: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Mescla recursivamente dois dicionários de departamento para suportar subcampos."""
    res = dict(a or {})
    if not b:
        return res
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(res.get(k), dict):
            res[k] = deep_merge_dict(res[k], v)
        else:
            res[k] = v
    return res


def append_list_reducer(a: Optional[List[Any]], b: Optional[List[Any]]) -> List[Any]:
    """Reducer inegociável de append-only para listas que nunca sobrescrevem e previnem eco de subgrafos."""
    lista_a = list(a or [])
    lista_b = list(b or [])
    if not lista_b:
        return lista_a
    if not lista_a:
        return lista_b
    if lista_a == lista_b:
        return lista_a
    # Se lista_b for extensão direta de lista_a (subgrafo preservou a lista e adicionou itens ao final)
    if len(lista_b) > len(lista_a) and lista_b[:len(lista_a)] == lista_a:
        return lista_b
    # Se lista_a for extensão de lista_b
    if len(lista_a) > len(lista_b) and lista_a[:len(lista_b)] == lista_b:
        return lista_a
    # Acrescenta apenas os novos elementos
    novos = []
    for item in lista_b:
        if item not in lista_a and item not in novos:
            novos.append(item)
    return lista_a + novos


# ============================================================================
# Modelos Pydantic para validação e auditoria (versão + autor_no)
# ============================================================================

class RegistroAuditoria(BaseModel):
    versao: int = Field(default=1, ge=1)
    autor_no: str = Field(description="Identificador do nó agente que realizou a escrita")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CustoItem(BaseModel):
    autor_no: str
    tokens_entrada: int = 0
    tokens_saida: int = 0
    segundos_gpu: float = 0.0
    chamadas_api: int = 1
    custo_estimado_usd: float = 0.0
    categoria_modelo: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ErroItem(BaseModel):
    autor_no: str
    erro: str
    tentativa: int = 1
    decisao: Literal["refazer", "alternativa", "escalar", "ignorar_aviso"]
    detalhes: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class QAItem(BaseModel):
    autor_no: str
    tipo_verificacao: str
    status: Literal["aprovado", "reprovado", "aviso"]
    bloqueia: bool = True
    departamento_alvo: Optional[str] = None
    motivo: str = ""
    detalhes: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AprovacaoItem(BaseModel):
    gate_id: int
    autor: str
    status: Literal["aprovado", "editado", "refazer"]
    comentarios: str = ""
    ajustes: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    simulado: bool = False


# ============================================================================
# Schemas dos 10 Departamentos + Showrunner
# ============================================================================

class EpisodioSubcampo(BaseModel):
    id: str
    mito: str
    angulo: str
    duracao_alvo_s: float = 1440.0  # ~24 minutos
    idioma: str = "pt-BR"
    status: str = "iniciado"
    rota: Optional[str] = None
    orcamento: Dict[str, Any] = Field(default_factory=lambda: {"teto_usd": 150.0, "gasto_atual_usd": 0.0})
    fila_humana: List[Dict[str, Any]] = Field(default_factory=list)
    licoes_aplicadas: List[Dict[str, Any]] = Field(default_factory=list)
    publicacao: Optional[Dict[str, Any]] = None
    desempenho: Optional[Dict[str, Any]] = None
    licoes_gravadas: List[Dict[str, Any]] = Field(default_factory=list)
    versao: int = 1
    autor_no: str = "showrunner"


class PesquisaSubcampo(BaseModel):
    fontes: List[Dict[str, Any]] = Field(default_factory=list)
    nomes_canonicos: Dict[str, str] = Field(default_factory=dict)
    fatos: List[Dict[str, Any]] = Field(default_factory=list)
    controversias: List[str] = Field(default_factory=list)
    referencia: Dict[str, Any] = Field(default_factory=dict)
    angulos: List[Dict[str, Any]] = Field(default_factory=list)
    versao: int = 1
    autor_no: str = "pesquisa"


class RoteiroSubcampo(BaseModel):
    esqueleto: Dict[str, Any] = Field(default_factory=dict)
    blocos: List[Dict[str, Any]] = Field(default_factory=list)
    versoes: List[Dict[str, Any]] = Field(default_factory=list)
    notas: Dict[str, List[str]] = Field(
        default_factory=lambda: {"retencao": [], "fidelidade": [], "tom": []}
    )
    voltas: int = 0
    versao: int = 1
    autor_no: str = "roteiro"


class DecupagemSubcampo(BaseModel):
    planos: List[Dict[str, Any]] = Field(default_factory=list)
    correcoes_direcao: List[Dict[str, Any]] = Field(default_factory=list)
    animatic: Optional[Dict[str, Any]] = None
    versao: int = 1
    autor_no: str = "direcao"


class ColorScriptSubcampo(BaseModel):
    cenas: List[Dict[str, Any]] = Field(default_factory=list)
    geral: Dict[str, Any] = Field(default_factory=dict)
    versao: int = 1
    autor_no: str = "direcao.diretor_fotografia"


class ElencoSubcampo(BaseModel):
    marionetes_usadas: List[str] = Field(default_factory=list)
    novas_a_criar: List[Dict[str, Any]] = Field(default_factory=list)
    reaproveitadas: List[str] = Field(default_factory=list)
    versao: int = 1
    autor_no: str = "direcao.diretor_arte"


class AssetsSubcampo(BaseModel):
    marionetes: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    cenarios: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    indice: List[Dict[str, Any]] = Field(default_factory=list)
    planos: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    versao: int = 1
    autor_no: str = "arte"


class AudioSubcampo(BaseModel):
    roteiro_anotado: List[Dict[str, Any]] = Field(default_factory=list)
    narracao: Dict[str, Any] = Field(default_factory=dict)
    sfx: List[Dict[str, Any]] = Field(default_factory=list)
    trilha: Dict[str, Any] = Field(default_factory=dict)
    mix: Dict[str, Any] = Field(default_factory=dict)
    lufs: Optional[float] = None
    versao: int = 1
    autor_no: str = "audio"


class TimelineSubcampo(BaseModel):
    otio_json: Optional[str] = None
    versao_corte: int = 1
    camadas_motion: List[Dict[str, Any]] = Field(default_factory=list)
    versao: int = 1
    autor_no: str = "montagem"


class MasterSubcampo(BaseModel):
    arquivo: Optional[Dict[str, Any]] = None
    capitulos: List[Dict[str, Any]] = Field(default_factory=list)
    legendas: Dict[str, str] = Field(default_factory=dict)
    versao: int = 1
    autor_no: str = "montagem.finalizador"


class EmbalagemSubcampo(BaseModel):
    titulos: List[str] = Field(default_factory=list)
    thumbs: List[Dict[str, Any]] = Field(default_factory=list)
    ranking: List[Dict[str, Any]] = Field(default_factory=list)
    metadados: Dict[str, Any] = Field(default_factory=dict)
    shorts: List[Dict[str, Any]] = Field(default_factory=list)
    versao: int = 1
    autor_no: str = "embalagem"


# ============================================================================
# TypedDict do Estado Global do LangGraph (Doc 05 §2)
# ============================================================================

class EstadoEpisodio(TypedDict, total=False):
    """Estado canônico do episódio no runtime do LangGraph."""

    # Departamentos com merge recursivo
    episodio: Annotated[Dict[str, Any], deep_merge_dict]
    pesquisa: Annotated[Dict[str, Any], deep_merge_dict]
    roteiro: Annotated[Dict[str, Any], deep_merge_dict]
    decupagem: Annotated[Dict[str, Any], deep_merge_dict]
    color_script: Annotated[Dict[str, Any], deep_merge_dict]
    elenco: Annotated[Dict[str, Any], deep_merge_dict]
    assets: Annotated[Dict[str, Any], deep_merge_dict]
    audio: Annotated[Dict[str, Any], deep_merge_dict]
    timeline: Annotated[Dict[str, Any], deep_merge_dict]
    master: Annotated[Dict[str, Any], deep_merge_dict]
    embalagem: Annotated[Dict[str, Any], deep_merge_dict]

    # Listas inegociáveis de append-only
    qa: Annotated[List[Dict[str, Any]], append_list_reducer]
    aprovacoes: Annotated[List[Dict[str, Any]], append_list_reducer]
    custos: Annotated[List[Dict[str, Any]], append_list_reducer]
    erros: Annotated[List[Dict[str, Any]], append_list_reducer]


def criar_estado_inicial(
    id_episodio: str,
    mito: str,
    angulo: str,
    duracao_alvo_s: float = 1440.0,
    idioma: str = "pt-BR",
) -> EstadoEpisodio:
    """Cria um estado inicial canônico e válido para inicialização do Showrunner."""
    return {
        "episodio": EpisodioSubcampo(
            id=id_episodio,
            mito=mito,
            angulo=angulo,
            duracao_alvo_s=duracao_alvo_s,
            idioma=idioma,
            status="iniciado",
        ).model_dump(),
        "pesquisa": PesquisaSubcampo().model_dump(),
        "roteiro": RoteiroSubcampo().model_dump(),
        "decupagem": DecupagemSubcampo().model_dump(),
        "color_script": ColorScriptSubcampo().model_dump(),
        "elenco": ElencoSubcampo().model_dump(),
        "assets": AssetsSubcampo().model_dump(),
        "audio": AudioSubcampo().model_dump(),
        "timeline": TimelineSubcampo().model_dump(),
        "master": MasterSubcampo().model_dump(),
        "embalagem": EmbalagemSubcampo().model_dump(),
        "qa": [],
        "aprovacoes": [],
        "custos": [],
        "erros": [],
    }
