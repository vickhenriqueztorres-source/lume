"""Esquemas de Saída dos 48 Agentes (Doc 05 §3 e Fichas Individuais).

Define esquemas Pydantic para as saídas estruturadas dos agentes em todos os departamentos.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 0. Supervisor
# ---------------------------------------------------------------------------
class ShowrunnerDecisao(BaseModel):
    proximo_passo: str
    status_episodio: str
    rota: Optional[str] = None
    acao_orcamento: Literal["continuar", "pausar_teto", "escalar"] = "continuar"
    escalada_humana: Optional[Dict[str, Any]] = None
    licoes_a_injetar: List[Dict[str, Any]] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# 1. Pesquisa
# ---------------------------------------------------------------------------
class FonteItem(BaseModel):
    canto_verso: str
    obra: str
    autor: str
    texto_original: str
    traducao_pt: str
    dominio_publico: bool = True
    url_ou_referencia: str


class PesquisadorFontesOutput(BaseModel):
    fontes: List[FonteItem]
    nomes_canonicos: Dict[str, str] = Field(description="Ex.: Ulisses -> Odisseu")


class FatoItem(BaseModel):
    id: str
    descricao: str
    fontes_confirmadas: List[str]
    variante_ou_tardia: bool = False
    grau_certeza: Literal["canonica", "variante", "apocrifa"] = "canonica"


class VerificadorFatosOutput(BaseModel):
    fatos: List[FatoItem]
    controversias: List[str] = Field(default_factory=list)


class AnalistaReferenciaOutput(BaseModel):
    metricas_ritmo: Dict[str, Any]
    densidade_cortes_ppm: float
    lacunas_identificadas: List[str]


class DemandaAnguloItem(BaseModel):
    angulo: str
    volume_busca_estimado: str
    concorrencia: str
    score: float


class AnalistaDemandaOutput(BaseModel):
    angulos_ranqueados: List[DemandaAnguloItem]
    angulo_recomendado: str


# ---------------------------------------------------------------------------
# 2. Roteiro
# ---------------------------------------------------------------------------
class BlocoEsqueleto(BaseModel):
    numero: int
    ato: int
    tempo_alvo_s: float
    funcao_dramatica: str
    fatos_chave: List[str]


class ArquitetoEstruturaOutput(BaseModel):
    atos: List[Dict[str, Any]]
    blocos: List[BlocoEsqueleto]
    tempo_total_previsto_s: float


class BlocoRoteiro(BaseModel):
    numero: int
    texto: str
    marcacoes_cena: List[str]
    fatos_referenciados: List[str]
    tempo_estimado_s: float


class RoteiristaOutput(BaseModel):
    versao: int
    blocos: List[BlocoRoteiro]


class NotaRevisao(BaseModel):
    bloco_numero: Optional[int] = None
    tipo: str
    gravidade: Literal["bloqueante", "aviso", "sugestao"]
    mensagem: str


class EditorRetencaoOutput(BaseModel):
    aprovado: bool
    gancho_duracao_s: float
    open_loops_identificados: List[int]
    notas: List[NotaRevisao]


class RevisorFidelidadeOutput(BaseModel):
    aprovado: bool
    frases_sem_fato: List[str]
    notas: List[NotaRevisao]


class RevisorTomOutput(BaseModel):
    aprovado: bool
    palavras_por_minuto: float
    cliches_detectados: List[str]
    notas: List[NotaRevisao]


# ---------------------------------------------------------------------------
# 3. Direção
# ---------------------------------------------------------------------------
class DiretorDecupagemOutput(BaseModel):
    planos: List[Dict[str, Any]]
    total_planos: int


class FotografiaCena(BaseModel):
    cena_id: str
    nivel_fogo: int = Field(ge=1, le=5)
    proporcao: Literal["16:9", "2.39", "3:1"]
    parede: str
    luz_deus: Optional[Dict[str, str]] = None


class DiretorFotografiaOutput(BaseModel):
    color_script: List[FotografiaCena]
    ajustes_por_plano: Dict[str, Dict[str, Any]]


class CorrecaoDirecaoTela(BaseModel):
    plano_id: str
    direcao_original: str
    direcao_corrigida: str
    motivo: str


class SupervisorDirecaoTelaOutput(BaseModel):
    aprovado: bool
    correcoes: List[CorrecaoDirecaoTela]


class ElencoItem(BaseModel):
    marionete_id: str
    personagem: str
    status: Literal["biblioteca", "nova_a_criar"]
    descricao_visual: str


class DiretorArteOutput(BaseModel):
    marionetes_usadas: List[str]
    novas_a_criar: List[ElencoItem]
    reaproveitadas: List[str]


class StoryboardOutput(BaseModel):
    animatic_caminho: Optional[str]
    quadros_por_plano: Dict[str, str]


# ---------------------------------------------------------------------------
# 4. Arte & Marionetes
# ---------------------------------------------------------------------------
class DesignerSilhuetasOutput(BaseModel):
    marionete_id: str
    png_caminho: str
    png_hash: str
    estilo_figura_negra: bool = True
    furos_luz: List[str]


class VetorizadorOutput(BaseModel):
    marionete_id: str
    svg_caminho: str
    svg_hash: str
    preto_absoluto: bool = True


class PivoRig(BaseModel):
    nome_junta: str
    x: float
    y: float


class RiggerOutput(BaseModel):
    marionete_id: str
    rig_caminho: str
    pivos: List[PivoRig]


class CenografoOutput(BaseModel):
    cenario_id: str
    tipo: str
    textura_caminho: str
    textura_hash: str


class BibliotecarioOutput(BaseModel):
    ativos_registrados: List[Dict[str, Any]]
    total_ativos: int


# ---------------------------------------------------------------------------
# 5. Animação & Render
# ---------------------------------------------------------------------------
class AnimadorPlanoOutput(BaseModel):
    plano_id: str
    cena_parametrizada: Dict[str, Any]


class MontadorCena3DOutput(BaseModel):
    plano_id: str
    blend_caminho: str
    blend_hash: str


class GerenteRenderOutput(BaseModel):
    plano_id: str
    video_caminho: Optional[str]
    video_hash: Optional[str]
    status: Literal["concluido", "falhou"]
    job_id: str


class RevisorPlanoOutput(BaseModel):
    plano_id: str
    aprovado: bool
    motivo: Optional[str] = None
    tentativa: int = 1


class VFXOutput(BaseModel):
    plano_id: str
    camadas_vfx: List[Dict[str, Any]]
    caminho_composto: Optional[str]


# ---------------------------------------------------------------------------
# 6. Áudio
# ---------------------------------------------------------------------------
class MarcacaoVoz(BaseModel):
    bloco_numero: int
    ppm: int
    pausas_ms: List[int]
    enfases: List[str]


class DiretorVozOutput(BaseModel):
    roteiro_anotado: List[MarcacaoVoz]


class NarradorOutput(BaseModel):
    bloco_numero: int
    audio_caminho: str
    audio_hash: str
    duracao_s: float


class SoundDesignerOutput(BaseModel):
    sfx_utilizados: List[Dict[str, Any]]


class SupervisorMusicalOutput(BaseModel):
    stems_trilha: List[Dict[str, Any]]


class MixadorOutput(BaseModel):
    mix_caminho: str
    mix_hash: str
    lufs_medido: float = -14.0


# ---------------------------------------------------------------------------
# 7. Montagem & Finalização
# ---------------------------------------------------------------------------
class EditorOutput(BaseModel):
    timeline_otio: str
    versao_corte: int
    duracao_total_s: float


class GrafismoOutput(BaseModel):
    camadas_grafismo: List[Dict[str, Any]]


class FinalizadorOutput(BaseModel):
    master_caminho: str
    master_hash: str
    resolucao: str = "4K"
    capitulos: List[Dict[str, Any]]


class LegendadorOutput(BaseModel):
    legendas_srt: Dict[str, str]  # idioma -> srt


# ---------------------------------------------------------------------------
# 8. Embalagem
# ---------------------------------------------------------------------------
class TitulistaOutput(BaseModel):
    titulos: List[str]


class ThumbItem(BaseModel):
    layout: Literal["A", "B", "C"]
    caminho: str
    hash: str
    elementos: Dict[str, Any]


class DesignerThumbnailOutput(BaseModel):
    thumbs: List[ThumbItem]


class AvaliadorFeedOutput(BaseModel):
    ranking_thumbs: List[Dict[str, Any]]
    thumb_vencedora_layout: str


class RedatorMetadadosOutput(BaseModel):
    descricao: str
    tags: List[str]
    capitulos_formatados: str


class CortadorShortsOutput(BaseModel):
    shorts: List[Dict[str, Any]]


# ---------------------------------------------------------------------------
# 9. QA
# ---------------------------------------------------------------------------
class QARelatorioOutput(BaseModel):
    verificacao: str
    aprovado: bool
    bloqueia: bool
    departamento_alvo: Optional[str] = None
    motivo: str = ""
    metricas: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# 10. Publicação & Aprendizado
# ---------------------------------------------------------------------------
class PublicadorOutput(BaseModel):
    video_id: str
    status: Literal["privado"]
    upload_url: str
    chave_idempotencia: str


class AnalistaDesempenhoOutput(BaseModel):
    video_id: str
    ctr_48h: Optional[float] = None
    retencao_media_pct: Optional[float] = None
    queda_retencao_timecodes: List[str] = Field(default_factory=list)


class CuradorMemoriaOutput(BaseModel):
    licoes_geradas: List[Dict[str, Any]]
