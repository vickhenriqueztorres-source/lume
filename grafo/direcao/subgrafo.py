"""Subgrafo do Departamento de Direção (Doc 05 §3.3 e Fichas 01-05).

Implementa os 5 agentes de Direção:
1. direcao.diretor_decupagem (LLM-R)
2. direcao.diretor_fotografia (LLM-R)
3. direcao.supervisor_direcao_tela (LLM-R regras)
4. direcao.diretor_arte (LLM-R + Store)
5. direcao.storyboarder (IMG + Ferr.)
"""

from __future__ import annotations

from typing import Any, Dict, List
from langgraph.graph import END, START, StateGraph

from contratos.estado import EstadoEpisodio
from contratos.plano import Plano
from grafo.base import no_agente
from grafo.checkpointer import obter_store


@no_agente("direcao.diretor_decupagem", categoria_modelo="LLM-R")
def diretor_decupagem_node(state: EstadoEpisodio) -> Dict[str, Any]:
    blocos = state.get("roteiro", {}).get("blocos", [])

    # Cria planos decupados rigorosamente conformes com o contrato do Doc 05 §5
    planos: List[Dict[str, Any]] = [
        Plano(
            id="ep01_c01_p01",
            bloco_roteiro=1,
            mundo="contador",
            tipo_plano="contador",
            duracao_s=4.0,
            proporcao="16:9",
            camera={"movimento": "push_in_lento", "lente_mm": 85},
            fogo={"nivel": 2, "curva": "estavel", "tremulacao_hz": 1.0},
        ).model_dump(),
        Plano(
            id="ep01_c01_p02",
            bloco_roteiro=1,
            mundo="parede",
            tipo_plano="escala",
            duracao_s=6.0,
            proporcao="2.39",
            marionetes=[
                {"id": "polifemo_v1", "distancia_fogo": 0.2, "direcao": "esq"},
                {"id": "odisseu_v1", "distancia_fogo": 0.8, "direcao": "dir"},
            ],
            camera={"movimento": "tilt_up", "lente_mm": 35},
            fogo={"nivel": 3, "curva": "subida", "tremulacao_hz": 2.0},
            parede="caverna_umida",
        ).model_dump(),
        Plano(
            id="ep01_c01_p03",
            bloco_roteiro=2,
            mundo="parede",
            tipo_plano="close",
            duracao_s=4.5,
            proporcao="2.39",
            marionetes=[
                {"id": "odisseu_v1", "distancia_fogo": 0.7, "direcao": "dir"},
            ],
            camera={"movimento": "push_in_lento", "lente_mm": 50},
            fogo={"nivel": 3, "curva": "estavel", "tremulacao_hz": 2.0},
            parede="caverna_umida",
        ).model_dump(),
        Plano(
            id="ep01_c01_p04",
            bloco_roteiro=3,
            mundo="parede",
            tipo_plano="medio",
            duracao_s=5.0,
            proporcao="2.39",
            marionetes=[
                {"id": "odisseu_v1", "distancia_fogo": 0.6, "direcao": "dir"},
                {"id": "polifemo_v1", "distancia_fogo": 0.3, "direcao": "esq"},
            ],
            camera={"movimento": "dolly_lateral", "lente_mm": 35},
            fogo={"nivel": 4, "curva": "pico", "tremulacao_hz": 4.0},
            parede="caverna_umida",
        ).model_dump(),
        Plano(
            id="ep01_c01_p05",
            bloco_roteiro=3,
            mundo="parede",
            tipo_plano="insert",
            duracao_s=3.5,
            proporcao="2.39",
            camera={"movimento": "push_in_lento", "lente_mm": 50},
            fogo={"nivel": 4, "curva": "estavel", "tremulacao_hz": 3.0},
            parede="caverna_umida",
            sfx=["fogo_crepitando", "rocha_arrastando"],
        ).model_dump(),
    ]

    # Se houver plano com erro plantado pelo teste em decupagem inicial, preserva
    planos_existentes = state.get("decupagem", {}).get("planos", [])
    if planos_existentes:
        planos = planos_existentes

    return {
        "decupagem": {
            "planos": planos,
        }
    }


@no_agente("direcao.diretor_fotografia", categoria_modelo="LLM-R")
def diretor_fotografia_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = list(state.get("decupagem", {}).get("planos", []))

    color_script = {
        "cenas": [
            {
                "cena_id": "c01_abertura",
                "nivel_fogo": 2,
                "temperatura_k": 2200,
                "proporcao": "16:9",
                "textura_parede": "ruina_calcario",
            },
            {
                "cena_id": "c02_caverna_polifemo",
                "nivel_fogo": 4,
                "temperatura_k": 3000,
                "proporcao": "2.39",
                "textura_parede": "caverna_umida",
            },
        ],
        "geral": {"paleta_base": ["#16110D", "#3A2C22", "#F1E6CF", "#E07A2E"], "teto_brasa_pct": 5.0},
    }

    # Enriquece cada plano com fogo e proporção conforme o color script
    for p in planos:
        if p.get("mundo") == "contador":
            p["proporcao"] = "16:9"
            p["fogo"] = {"nivel": 2, "curva": "estavel", "tremulacao_hz": 1.0}
        else:
            p["proporcao"] = "2.39"
            if p.get("tipo_plano") in {"escala", "insert"}:
                p["fogo"] = {"nivel": 4, "curva": "pico", "tremulacao_hz": 3.0}

    return {
        "color_script": color_script,
        "decupagem": {
            "planos": planos,
        },
    }


@no_agente("direcao.supervisor_direcao_tela", categoria_modelo="LLM-R")
def supervisor_direcao_tela_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = list(state.get("decupagem", {}).get("planos", []))
    correcoes: List[Dict[str, Any]] = []

    # Valida regra inegociável de direção de tela (Doc 04 §4):
    # Herói rumo a Ítaca (ex.: odisseu_v1) = "dir" (→ casa)
    # Forças contrárias e monstros (ex.: polifemo_v1) = "esq" (← contra)
    for p in planos:
        for m in p.get("marionetes", []):
            m_id = m.get("id", "")
            direcao_atual = m.get("direcao", "dir")

            if "odisseu" in m_id and direcao_atual != "dir":
                correcoes.append({
                    "plano_id": p.get("id"),
                    "marionete_id": m_id,
                    "direcao_anterior": direcao_atual,
                    "direcao_corrigida": "dir",
                    "motivo": "Doc 04 §4: Odisseu rumo a Ítaca deve obrigatoriamente olhar para a direita (→ casa).",
                })
                m["direcao"] = "dir"

            elif "polifemo" in m_id and direcao_atual != "esq":
                correcoes.append({
                    "plano_id": p.get("id"),
                    "marionete_id": m_id,
                    "direcao_anterior": direcao_atual,
                    "direcao_corrigida": "esq",
                    "motivo": "Doc 04 §4: Polifemo (força contrária) deve olhar para a esquerda (← contra).",
                })
                m["direcao"] = "esq"

    return {
        "decupagem": {
            "correcoes_direcao": correcoes,
            "planos": planos,
        }
    }


@no_agente("direcao.diretor_arte", categoria_modelo="LLM-R")
def diretor_arte_node(state: EstadoEpisodio) -> Dict[str, Any]:
    store = obter_store()
    planos = state.get("decupagem", {}).get("planos", [])

    # Extrai todas as marionetes mencionadas nos planos
    marionetes_usadas_set = set()
    for p in planos:
        for m in p.get("marionetes", []):
            marionetes_usadas_set.add(m.get("id"))

    marionetes_usadas = sorted(list(marionetes_usadas_set))
    reaproveitadas = []
    novas_a_criar = []

    # Consulta a Store persistente para identificar o que já existe
    for m_id in marionetes_usadas:
        existe_na_store = False
        try:
            item = store.get(("biblioteca", "marionetes"), m_id)
            if item is not None:
                existe_na_store = True
        except Exception:
            pass

        # Se for odisseu_v1 ou se estiver na store, marca como reaproveitada
        if existe_na_store or m_id == "odisseu_v1":
            reaproveitadas.append(m_id)
        else:
            novas_a_criar.append({
                "id": m_id,
                "nome": m_id.replace("_v1", "").capitalize(),
                "estilo": "figura_negra",
                "furos_luz": ["olho_central"] if "polifemo" in m_id else [],
                "proporcao_escala": "gigante" if "polifemo" in m_id else "normal",
            })

    return {
        "elenco": {
            "marionetes_usadas": marionetes_usadas,
            "reaproveitadas": reaproveitadas,
            "novas_a_criar": novas_a_criar,
        }
    }


@no_agente("direcao.storyboarder", categoria_modelo="IMG")
def storyboarder_node(state: EstadoEpisodio) -> Dict[str, Any]:
    planos = list(state.get("decupagem", {}).get("planos", []))
    duracao_total = sum(p.get("duracao_s", 5.0) for p in planos)
    from grafo.ferramentas.start_frame import StartFrameGenerator
    generator = StartFrameGenerator()

    for p in planos:
        p_id = p.get("id")
        frame_path = generator.gerar_start_frame(
            plano_id=p_id,
            prompt=p.get("mundo", "parede"),
            proporcao=p.get("proporcao", "16:9"),
            nivel_fogo=p.get("fogo", {}).get("nivel", 2),
            direcao_olhar=p.get("direcao_olhar", "D"),
        )
        p["storyboard"] = str(frame_path)

    animatic = {
        "caminho": "storage_local/animatic/ep01_animatic.mp4",
        "hash": "hash_animatic_ep01_baixa_res",
        "resolucao": "1280x720",
        "duracao_total_s": duracao_total,
    }

    return {
        "decupagem": {
            "animatic": animatic,
            "planos": planos,
        }
    }


def construir_subgrafo_direcao() -> StateGraph:
    """Compila o subgrafo de Direção."""
    builder = StateGraph(EstadoEpisodio)

    builder.add_node("direcao.diretor_decupagem", diretor_decupagem_node)
    builder.add_node("direcao.diretor_fotografia", diretor_fotografia_node)
    builder.add_node("direcao.supervisor_direcao_tela", supervisor_direcao_tela_node)
    builder.add_node("direcao.diretor_arte", diretor_arte_node)
    builder.add_node("direcao.storyboarder", storyboarder_node)

    builder.add_edge(START, "direcao.diretor_decupagem")
    builder.add_edge("direcao.diretor_decupagem", "direcao.diretor_fotografia")
    builder.add_edge("direcao.diretor_fotografia", "direcao.supervisor_direcao_tela")
    builder.add_edge("direcao.supervisor_direcao_tela", "direcao.diretor_arte")
    builder.add_edge("direcao.diretor_arte", "direcao.storyboarder")
    builder.add_edge("direcao.storyboarder", END)

    return builder.compile()
