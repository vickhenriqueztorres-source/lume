"""Testes de Contratos (Fase A · Critérios de Aceite).

Verifica:
1. Esquemas do estado e inicialização válida.
2. Reducers de append-only para custos, erros, qa e aprovacoes (apenas crescem).
3. Contrato do plano e cálculo determinístico do hash de renderização.
4. Esquemas de respostas de gates humanos.
5. Tabela canônica de 48 agentes batendo com o README §4 e bloqueio de escritas ilegais.
"""

import pytest
from contratos.estado import (
    AprovacaoItem,
    CustoItem,
    ErroItem,
    EstadoEpisodio,
    QAItem,
    append_list_reducer,
    criar_estado_inicial,
    deep_merge_dict,
)
from contratos.gates import RespostaGate
from contratos.mapeamento import (
    AGENTE_PARA_SUBCAMPO,
    validar_escrita_agente,
)
from contratos.plano import (
    CameraNoPlano,
    FogoNoPlano,
    MarioneteNoPlano,
    Plano,
    calcular_hash_plano,
)


def test_criar_estado_inicial_valido():
    """Garante que o estado inicial tem todas as chaves obrigatórias dos 10 departamentos."""
    estado = criar_estado_inicial("ep_odisseia_01", "A Odisseia", "Odisseu contra os deuses")
    assert estado["episodio"]["id"] == "ep_odisseia_01"
    assert estado["episodio"]["mito"] == "A Odisseia"
    assert estado["episodio"]["status"] == "iniciado"

    # Departamentos presentes
    for depto in [
        "episodio",
        "pesquisa",
        "roteiro",
        "decupagem",
        "color_script",
        "elenco",
        "assets",
        "audio",
        "timeline",
        "master",
        "embalagem",
    ]:
        assert depto in estado
        assert isinstance(estado[depto], dict)

    # Listas inegociáveis de append
    for lista in ["qa", "aprovacoes", "custos", "erros"]:
        assert lista in estado
        assert isinstance(estado[lista], list)
        assert len(estado[lista]) == 0


def test_reducers_append_only_nunca_sobrescrevem():
    """Prova que custos, erros, qa e aprovacoes só crescem via reducer."""
    c1 = [CustoItem(autor_no="n1", tokens_entrada=100).model_dump()]
    c2 = [CustoItem(autor_no="n2", tokens_entrada=200).model_dump()]
    merged_custos = append_list_reducer(c1, c2)
    assert len(merged_custos) == 2
    assert merged_custos[0]["tokens_entrada"] == 100
    assert merged_custos[1]["tokens_entrada"] == 200

    e1 = [ErroItem(autor_no="n1", erro="falha1", decisao="refazer").model_dump()]
    e2 = [ErroItem(autor_no="n2", erro="falha2", decisao="escalar").model_dump()]
    merged_erros = append_list_reducer(e1, e2)
    assert len(merged_erros) == 2

    q1 = [QAItem(autor_no="qa1", tipo_verificacao="tecnica", status="aprovado").model_dump()]
    q2 = [QAItem(autor_no="qa2", tipo_verificacao="marca", status="aviso").model_dump()]
    merged_qa = append_list_reducer(q1, q2)
    assert len(merged_qa) == 2

    a1 = [AprovacaoItem(gate_id=1, autor="humano1", status="aprovado").model_dump()]
    a2 = [AprovacaoItem(gate_id=2, autor="humano2", status="editado").model_dump()]
    merged_aprov = append_list_reducer(a1, a2)
    assert len(merged_aprov) == 2


def test_deep_merge_dict_preserva_subcampos():
    """Garante que atualizações parciais de subcampos não apaguem outros dados do departamento."""
    estado_pesquisa = {
        "fontes": [{"id": 1}],
        "nomes_canonicos": {"Ulisses": "Odisseu"},
    }
    update_fatos = {
        "fatos": [{"id": "f1"}],
    }
    merged = deep_merge_dict(estado_pesquisa, update_fatos)
    assert "fontes" in merged
    assert "nomes_canonicos" in merged
    assert "fatos" in merged
    assert merged["fontes"] == [{"id": 1}]
    assert merged["fatos"] == [{"id": "f1"}]


def test_contrato_plano_e_hash_cache():
    """Testa contrato do plano e o cálculo determinístico de hash de render."""
    plano_data = {
        "id": "ep01_c01_p01",
        "bloco_roteiro": 1,
        "mundo": "parede",
        "tipo_plano": "escala",
        "duracao_s": 4.5,
        "marionetes": [
            {"id": "odisseu_v1", "distancia_fogo": 0.8, "direcao": "dir"}
        ],
        "camera": {"movimento": "push_in_lento", "lente_mm": 35},
        "fogo": {"nivel": 3, "curva": "estavel", "tremulacao_hz": 2.0},
        "proporcao": "2.39",
        "parede": "pedra_calcario",
        "sfx": ["vento_marinho"],
    }
    plano = Plano.model_validate(plano_data)
    hash_original = plano.calcular_hash()
    assert isinstance(hash_original, str)
    assert len(hash_original) == 64

    # 1. Mudança em campo não-visual (sfx) NÃO deve mudar o hash de render
    plano.sfx.append("trovao_distante")
    assert plano.calcular_hash() == hash_original

    # 2. Mudança em campo visual (fogo) DEVE mudar o hash
    plano.fogo.nivel = 4
    hash_modificado = plano.calcular_hash()
    assert hash_modificado != hash_original


def test_contratos_gates_validacao():
    """Valida esquemas de respostas dos gates."""
    resp = RespostaGate(
        gate_id=1,
        status="aprovado",
        autor="showrunner_humano",
        comentarios="Roteiro canônico aprovado sem ressalvas.",
    )
    assert resp.status == "aprovado"
    assert resp.gate_id == 1
    assert not resp.simulado

    with pytest.raises(Exception):
        # status inválido deve falhar
        RespostaGate(gate_id=1, status="invalido", autor="teste")


def test_tabela_mapeamento_48_agentes():
    """Garante que todos os 48 nós estão mapeados e que a validação de escrita funciona."""
    # 1 Showrunner + 47 agentes = 48 agentes
    assert len(AGENTE_PARA_SUBCAMPO) == 48

    # Showrunner
    assert "showrunner" in AGENTE_PARA_SUBCAMPO
    # Pesquisa (4)
    assert "pesquisa.pesquisador_fontes" in AGENTE_PARA_SUBCAMPO
    assert "pesquisa.verificador_fatos" in AGENTE_PARA_SUBCAMPO
    assert "pesquisa.analista_referencia" in AGENTE_PARA_SUBCAMPO
    assert "pesquisa.analista_demanda" in AGENTE_PARA_SUBCAMPO
    # Roteiro (5)
    assert "roteiro.arquiteto_estrutura" in AGENTE_PARA_SUBCAMPO
    assert "roteiro.roteirista" in AGENTE_PARA_SUBCAMPO
    assert "roteiro.editor_retencao" in AGENTE_PARA_SUBCAMPO
    assert "roteiro.revisor_fidelidade" in AGENTE_PARA_SUBCAMPO
    assert "roteiro.revisor_tom" in AGENTE_PARA_SUBCAMPO
    # Direção (5)
    assert "direcao.diretor_decupagem" in AGENTE_PARA_SUBCAMPO
    assert "direcao.diretor_fotografia" in AGENTE_PARA_SUBCAMPO
    assert "direcao.supervisor_direcao_tela" in AGENTE_PARA_SUBCAMPO
    assert "direcao.diretor_arte" in AGENTE_PARA_SUBCAMPO
    assert "direcao.storyboarder" in AGENTE_PARA_SUBCAMPO
    # Arte (5)
    assert "arte.designer_silhuetas" in AGENTE_PARA_SUBCAMPO
    assert "arte.vetorizador" in AGENTE_PARA_SUBCAMPO
    assert "arte.rigger" in AGENTE_PARA_SUBCAMPO
    assert "arte.cenografo" in AGENTE_PARA_SUBCAMPO
    assert "arte.bibliotecario" in AGENTE_PARA_SUBCAMPO
    # Animação (5)
    assert "animacao.animador_plano" in AGENTE_PARA_SUBCAMPO
    assert "animacao.montador_cena_3d" in AGENTE_PARA_SUBCAMPO
    assert "animacao.gerente_render" in AGENTE_PARA_SUBCAMPO
    assert "animacao.revisor_plano" in AGENTE_PARA_SUBCAMPO
    assert "animacao.vfx" in AGENTE_PARA_SUBCAMPO
    # Áudio (5)
    assert "audio.diretor_voz" in AGENTE_PARA_SUBCAMPO
    assert "audio.narrador" in AGENTE_PARA_SUBCAMPO
    assert "audio.sound_designer" in AGENTE_PARA_SUBCAMPO
    assert "audio.supervisor_musical" in AGENTE_PARA_SUBCAMPO
    assert "audio.mixador" in AGENTE_PARA_SUBCAMPO
    # Montagem (4)
    assert "montagem.editor" in AGENTE_PARA_SUBCAMPO
    assert "montagem.grafismo" in AGENTE_PARA_SUBCAMPO
    assert "montagem.finalizador" in AGENTE_PARA_SUBCAMPO
    assert "montagem.legendador" in AGENTE_PARA_SUBCAMPO
    # Embalagem (5)
    assert "embalagem.titulista" in AGENTE_PARA_SUBCAMPO
    assert "embalagem.designer_thumbnail" in AGENTE_PARA_SUBCAMPO
    assert "embalagem.avaliador_feed" in AGENTE_PARA_SUBCAMPO
    assert "embalagem.redator_metadados" in AGENTE_PARA_SUBCAMPO
    assert "embalagem.cortador_shorts" in AGENTE_PARA_SUBCAMPO
    # QA (6)
    assert "qa.qa_tecnico" in AGENTE_PARA_SUBCAMPO
    assert "qa.qa_continuidade" in AGENTE_PARA_SUBCAMPO
    assert "qa.qa_fidelidade" in AGENTE_PARA_SUBCAMPO
    assert "qa.qa_marca" in AGENTE_PARA_SUBCAMPO
    assert "qa.qa_direitos" in AGENTE_PARA_SUBCAMPO
    assert "qa.qa_originalidade" in AGENTE_PARA_SUBCAMPO
    # Publicação (3)
    assert "publicacao.publicador" in AGENTE_PARA_SUBCAMPO
    assert "publicacao.analista_desempenho" in AGENTE_PARA_SUBCAMPO
    assert "publicacao.curador_memoria" in AGENTE_PARA_SUBCAMPO


def test_validar_escrita_agente_impede_invasao_de_departamento():
    """Valida que um agente não pode escrever fora do seu subcampo autorizado."""
    # Pesquisador de fontes só pode escrever em pesquisa (fontes / nomes_canonicos) + custos/erros
    assert validar_escrita_agente("pesquisa.pesquisador_fontes", {"pesquisa": {"fontes": []}, "custos": []})

    # Tentar escrever em roteiro deve ser rejeitado
    assert not validar_escrita_agente("pesquisa.pesquisador_fontes", {"roteiro": {"blocos": []}})

    # Tentar escrever em decupagem deve ser rejeitado
    assert not validar_escrita_agente("roteiro.roteirista", {"decupagem": {"planos": []}})
