"""Bateria de Testes Canônica: Engenheiro de Prompt de Vídeo (Doc 08 §9).

Cobre integralmente os casos de teste T1 a T12 definidos na especificação:
- T1: Plano do Contador, nível 2, push_in_lento, keyframe aprovado (sem Hz, sem level, sem pt)
- T2: Plano de parede -> aplicavel: False (Blender headless)
- T3: intencao_visual vazia com narração mencionando canto/lira -> fallback respira, sem termos proibidos
- T4: intencao_visual pedindo 'o Contador sorri' -> ação permitida da lista fechada (nunca sorrir)
- T5: Plano do Contador com fogo nível 4 -> prompt nível 4 + aviso em qa para DoP
- T6: Plano do Contador com câmera fixo -> convertido para push_in_lento + aviso em qa
- T7: Prompt acima do limite -> descarta camada 6 inteira sem cortar frases no meio
- T8: Sem contador_v1 aprovado -> sem job, item em episodio.fila_humana
- T9: Idempotência determinística -> mesmo prompt e mesmo hash para entradas idênticas
- T10: Imutabilidade de decupagem -> estado não tem nenhuma alteração em decupagem
- T11: Revisor automático -> take do velho com lira reprovado pelos 5 motivos
- T12: Adaptador sem negativo -> restrições como frases afirmativas, sem 'no X'
"""

import copy
import pytest
from contratos.estado import criar_estado_inicial
from contratos.plano import Plano
from grafo.base import limpar_operacoes_teste
from grafo.animacao.engenheiro_prompt_video import (
    ACOES_PERMITIDAS,
    BIBLIA_VERSAO,
    construir_prompt_contador,
    engenheiro_prompt_video_node,
    revisar_take_video_ia,
    selecionar_acao_contador,
)


@pytest.fixture(autouse=True)
def setup_teste_engenheiro_prompt_video():
    limpar_operacoes_teste()


def criar_estado_base_contador():
    """Helper para criar estado com aprovação de contador_v1 e configuração padrão."""
    estado = criar_estado_inicial("ep_test_01", "A Odisseia", "Ciclope")
    estado["aprovacoes"].append({
        "item": "contador_v1",
        "status": "aprovado",
        "aprovado_por": "Diretor de Arte",
    })
    return estado


def test_t1_contador_nivel2_push_in_keyframe_aprovado():
    """T1: Plano do Contador, nível 2, push_in_lento, keyframe aprovado.
    
    Verifica:
    - O prompt contém âncora + bíblia + ação + câmera + fogo
    - O negativo contém face, lyre, lantern
    - Não aparece 'Hz', 'level' nem palavras em português no prompt
    """
    estado = criar_estado_base_contador()
    plano = Plano(
        id="ep01_c00_p01",
        bloco_roteiro=1,
        mundo="contador",
        tipo_plano="contador",
        duracao_s=5.0,
        camera={"movimento": "push_in_lento", "lente_mm": 100},
        fogo={"nivel": 2, "curva": "estavel", "tremulacao_hz": 1.0},
        intencao_visual="O Contador estende a mão para o fogo antes de começar a história.",
    ).model_dump()
    estado["decupagem"]["planos"] = [plano]

    res = engenheiro_prompt_video_node(estado)
    video_ia = res["assets"]["planos"]["ep01_c00_p01"]["video_ia"]

    assert video_ia["aplicavel"] is True
    prompt = video_ia["prompt"]
    negativo = video_ia["negativo"]

    # Camadas obrigatórias
    assert "Animate the reference image" in prompt  # Camada 1: Âncora
    assert "A hooded storyteller beside a bronze brazier" in prompt  # Camada 2: Bíblia
    assert "Action: slowly, his right hand moves toward the flames" in prompt  # Camada 3: Ação
    assert "Camera: a very slow push-in" in prompt  # Camada 4: Câmera
    assert "with a subtle handheld breathing motion" in prompt
    assert "Fire: low, steady flames with a gentle, slow flicker" in prompt  # Camada 5: Fogo

    # Negativo separado
    assert negativo is not None
    assert "face" in negativo
    assert "lyre" in negativo
    assert "lantern" in negativo

    # Sem termos técnicos crus ou português
    assert "Hz" not in prompt
    assert "level" not in prompt.lower()
    for termo_pt in ["estavel", "subida", "lento", "fogo", "mao", "historia"]:
        assert termo_pt not in prompt.lower()


def test_t2_plano_de_parede_retorna_nao_aplicavel():
    """T2: Plano de parede -> aplicavel: False; nenhum job enviado ao motor de vídeo."""
    estado = criar_estado_base_contador()
    plano_parede = Plano(
        id="ep01_c01_p02",
        bloco_roteiro=2,
        mundo="parede",
        tipo_plano="medio",
        duracao_s=4.0,
        camera={"movimento": "push_in_lento"},
        fogo={"nivel": 2},
    ).model_dump()
    estado["decupagem"]["planos"] = [plano_parede]

    res = engenheiro_prompt_video_node(estado)
    video_ia = res["assets"]["planos"]["ep01_c01_p02"]["video_ia"]

    assert video_ia["aplicavel"] is False
    assert video_ia.get("motivo") == "parede_delegada_ao_blender_headless"
    assert "prompt" not in video_ia


def test_t3_intencao_vazia_com_narracao_lira_fallback_respira():
    """T3: intencao_visual vazia e narração que fala em 'canto' e 'lira' -> ação respira, sem termos musicais."""
    estado = criar_estado_base_contador()
    estado["roteiro"]["blocos"] = [
        {"numero": 1, "texto": "Ele canta a odisseia ao som da lira de ouro."}
    ]
    plano = Plano(
        id="ep01_c00_p03",
        bloco_roteiro=1,
        mundo="contador",
        tipo_plano="contador",
        intencao_visual="",  # Vazia propositalmente
    ).model_dump()
    estado["decupagem"]["planos"] = [plano]

    res = engenheiro_prompt_video_node(estado)
    prompt = res["assets"]["planos"]["ep01_c00_p03"]["video_ia"]["prompt"]

    assert "Action: slowly, his shoulders rise and fall with a slow breath" in prompt
    assert "sing" not in prompt.lower()
    assert "song" not in prompt.lower()
    assert "lyre" not in prompt.lower()
    assert "instrument" not in prompt.lower()


def test_t4_intencao_sorriso_mapeada_para_acao_permitida():
    """T4: intencao_visual pedindo 'o Contador sorri' -> devolve ação da lista fechada (nunca 'sorrir')."""
    acao_id, adverbio = selecionar_acao_contador("O Contador sorri com ironia")
    assert acao_id in ACOES_PERMITIDAS
    assert acao_id != "sorrir"
    assert "smile" not in ACOES_PERMITIDAS[acao_id]


def test_t5_contador_com_fogo_nivel_4_gera_prompt_e_aviso_qa():
    """T5: Plano do Contador com fogo nível 4 -> Prompt gerado com nível 4 + aviso em qa para o DoP."""
    estado = criar_estado_base_contador()
    plano = Plano(
        id="ep01_c00_p05",
        bloco_roteiro=1,
        mundo="contador",
        tipo_plano="contador",
        fogo={"nivel": 4, "curva": "subida"},
        intencao_visual="Ele aproxima a mão das chamas altas",
    ).model_dump()
    estado["decupagem"]["planos"] = [plano]

    res = engenheiro_prompt_video_node(estado)
    prompt = res["assets"]["planos"]["ep01_c00_p05"]["video_ia"]["prompt"]
    avisos_qa = res.get("qa", [])

    assert "tall roaring flames with a strong, irregular flicker" in prompt
    assert any("fogo nivel 4" in a.get("mensagem", "").lower() for a in avisos_qa)


def test_t6_contador_camera_fixo_troca_para_push_in_com_aviso():
    """T6: Plano do Contador com câmera fixo -> Troca para push_in_lento + aviso."""
    estado = criar_estado_base_contador()
    plano = Plano(
        id="ep01_c00_p06",
        bloco_roteiro=1,
        mundo="contador",
        tipo_plano="contador",
        camera={"movimento": "fixo"},
    ).model_dump()
    estado["decupagem"]["planos"] = [plano]

    res = engenheiro_prompt_video_node(estado)
    prompt = res["assets"]["planos"]["ep01_c00_p06"]["video_ia"]["prompt"]
    avisos_qa = res.get("qa", [])

    assert "a very slow push-in" in prompt
    assert "subtle handheld breathing motion" in prompt
    assert any("camera fixa convertido" in a.get("mensagem", "").lower() for a in avisos_qa)


def test_t7_prompt_acima_do_limite_descarta_camada_6_sem_cortar_frases():
    """T7: Prompt acima do limite do adaptador -> Sai a camada 6 inteira; camadas 1 a 4 intactas."""
    plano = Plano(
        id="ep01_c00_p07",
        bloco_roteiro=1,
        mundo="contador",
        tipo_plano="contador",
        intencao_visual="O Contador estende a mão para o fogo antes de começar a história.",
    ).model_dump()

    # Adaptador com limite curto que força descarte da camada 6
    cfg_limite_curto = {
        "limite_caracteres": 780,
        "aceita_negativo": True,
    }
    prompt, _, _ = construir_prompt_contador(plano, cfg_limite_curto)

    # Verifica que a atmosfera (camada 6) foi descartada
    assert "A few embers rise irregularly" not in prompt
    # Verifica que as camadas 1 a 4 estão intactas
    assert "Animate the reference image" in prompt
    assert "A hooded storyteller beside a bronze brazier" in prompt
    assert "Action: slowly, his right hand moves toward the flames" in prompt
    assert "Camera: a very slow push-in" in prompt
    assert "Fire: low, steady flames" in prompt
    # Nenhuma frase cortada no meio: o prompt termina em ponto final
    assert prompt.strip().endswith(".")


def test_t8_sem_contador_v1_aprovado_vai_para_fila_humana():
    """T8: Sem contador_v1 aprovado -> Nenhum job; item na fila humana."""
    estado = criar_estado_inicial("ep_test_sem_gate", "A Odisseia", "Ciclope")
    # Sem aprovação de contador_v1 em aprovacoes nem em assets
    plano = Plano(
        id="ep01_c00_p08",
        bloco_roteiro=1,
        mundo="contador",
        tipo_plano="contador",
    ).model_dump()
    estado["decupagem"]["planos"] = [plano]

    res = engenheiro_prompt_video_node(estado)
    video_ia = res["assets"]["planos"]["ep01_c00_p08"]["video_ia"]

    assert video_ia["aplicavel"] is False
    assert video_ia.get("status") == "aguardando_aprovacao_keyframe"

    fila_humana = res.get("episodio", {}).get("fila_humana", [])
    assert len(fila_humana) == 1
    assert fila_humana[0]["item"] == "contador_v1"
    assert fila_humana[0]["plano_id"] == "ep01_c00_p08"


def test_t9_idempotencia_mesma_entrada_mesmo_prompt_e_hash():
    """T9: Mesma entrada duas vezes -> Mesmo prompt e mesmo hash (idempotência)."""
    estado1 = criar_estado_base_contador()
    estado2 = criar_estado_base_contador()

    plano = Plano(
        id="ep01_c00_p09",
        bloco_roteiro=1,
        mundo="contador",
        tipo_plano="contador",
        intencao_visual="O Contador respira fundo antes de narrar.",
    ).model_dump()
    estado1["decupagem"]["planos"] = [copy.deepcopy(plano)]
    estado2["decupagem"]["planos"] = [copy.deepcopy(plano)]

    res1 = engenheiro_prompt_video_node(estado1)
    res2 = engenheiro_prompt_video_node(estado2)

    v1 = res1["assets"]["planos"]["ep01_c00_p09"]["video_ia"]
    v2 = res2["assets"]["planos"]["ep01_c00_p09"]["video_ia"]

    assert v1["prompt"] == v2["prompt"]
    assert v1["hash"] == v2["hash"]
    assert len(v1["hash"]) == 64


def test_t10_funcao_pura_nao_modifica_decupagem():
    """T10: Qualquer plano -> O estado depois do nó não tem nenhuma mudança em decupagem."""
    estado = criar_estado_base_contador()
    plano_original = Plano(
        id="ep01_c00_p10",
        bloco_roteiro=1,
        mundo="contador",
        tipo_plano="contador",
    ).model_dump()
    decupagem_copia = copy.deepcopy([plano_original])
    estado["decupagem"]["planos"] = [plano_original]

    res = engenheiro_prompt_video_node(estado)

    # 1. O nó não retorna a chave decupagem
    assert "decupagem" not in res
    # 2. O array original de planos em estado permanece inalterado
    assert estado["decupagem"]["planos"] == decupagem_copia


def test_t11_take_atual_velho_com_lira_reprovado_pelo_revisor():
    """T11: Take atual (velho com lira) no Revisor -> Reprovado com os 5 motivos definidos."""
    take_reprovado = {
        "confianca_rosto": 0.98,
        "rosto_visivel": True,
        "instrumento": True,
        "segunda_fonte_luz": True,
        "tipo_fogo": "lareira",
        "area_carvao_pct": 0.15,
        "area_brasa_pct": 0.03,
    }

    resultado = revisar_take_video_ia(take_reprovado)
    assert resultado["aprovado"] is False
    motivos = set(resultado["motivos"])

    assert "rosto_visivel" in motivos
    assert "instrumento" in motivos
    assert "segunda_fonte_luz" in motivos
    assert "lareira" in motivos
    assert "area_carvao_baixa" in motivos


def test_t12_adaptador_sem_negativo_usa_frases_afirmativas():
    """T12: Adaptador sem campo de negativo -> Restrições aparecem como frases afirmativas; sem 'no X'."""
    plano = Plano(
        id="ep01_c00_p12",
        bloco_roteiro=1,
        mundo="contador",
        tipo_plano="contador",
    ).model_dump()

    cfg_sem_negativo = {
        "limite_caracteres": 1200,
        "aceita_negativo": False,
    }
    prompt, negativo, _ = construir_prompt_contador(plano, cfg_sem_negativo)

    assert negativo is None
    # Frases afirmativas incorporadas
    assert "The hood fully conceals the face" in prompt
    assert "solitary illumination source" in prompt
    assert "remain completely empty" in prompt
    # Nenhuma frase proibida 'no face', 'no instrument'
    assert "no face" not in prompt.lower()
    assert "no instrument" not in prompt.lower()
    assert "no morphing" not in prompt.lower()
