"""Testes da Fase H · Embalagem + Publicação (Critérios de Aceite).

Verifica:
1. 3 títulos concisos com ≤ 60 caracteres cada.
2. 3 thumbnails nos layouts A, B e C, com wordmark inferior esquerdo e canto inferior direito livre.
3. Avaliador de feed simula resolução de 120 px e classifica ranking de CTR.
4. Publicador realiza upload em modo estritamente privado.
5. Retomada do nó de publicação após interrupção não duplica o upload (idempotência).
"""

import pytest
from contratos.estado import criar_estado_inicial
from grafo.base import limpar_operacoes_teste
from grafo.embalagem.subgrafo import construir_subgrafo_embalagem
from grafo.ferramentas.youtube import YouTubePublisher
from grafo.publicacao.subgrafo import construir_subgrafo_publicacao, publicador_node


def test_tres_titulos_menores_ou_iguais_a_60_caracteres():
    """Garante que todos os 3 títulos gerados respeitam o limite de 60 caracteres do YouTube."""
    subgrafo = construir_subgrafo_embalagem()
    estado = criar_estado_inicial("ep_embalagem", "A Odisseia", "Polifemo")

    resultado = subgrafo.invoke(estado)
    titulos = resultado["embalagem"]["titulos"]

    assert len(titulos) == 3
    for t in titulos:
        assert len(t) <= 60
        assert len(t) > 10


def test_tres_thumbs_layouts_a_b_c_com_regras_visuais():
    """Garante que são geradas 3 thumbs nos layouts A, B, C com regras da identidade visual LUME."""
    subgrafo = construir_subgrafo_embalagem()
    estado = criar_estado_inicial("ep_embalagem", "A Odisseia", "Polifemo")

    resultado = subgrafo.invoke(estado)
    thumbs = resultado["embalagem"]["thumbs"]

    assert len(thumbs) == 3
    layouts = {thumb["layout"] for thumb in thumbs}
    assert layouts == {"A", "B", "C"}

    for thumb in thumbs:
        # Doc 03 §8: Wordmark no canto inferior esquerdo e canto inferior direito livre
        assert thumb["posicao_wordmark"] == "inferior_esquerdo"
        assert thumb["canto_inferior_direito_livre"] is True


def test_avaliador_feed_ranqueia_em_120px():
    """Garante que o Avaliador de Feed mede a legibilidade em miniatura (120 px) e aponta a vencedora."""
    subgrafo = construir_subgrafo_embalagem()
    estado = criar_estado_inicial("ep_embalagem", "A Odisseia", "Polifemo")

    resultado = subgrafo.invoke(estado)
    ranking = resultado["embalagem"]["ranking"]

    assert len(ranking) == 3
    vencedoras = [r for r in ranking if r.get("vencedor")]
    assert len(vencedoras) == 1
    assert "score_120px" in ranking[0]
    assert ranking[0]["score_120px"] > 7.0


def test_publicador_upload_estritamente_privado_e_idempotencia():
    """Garante que o upload é estritamente privado e que a retomada não duplica o envio."""
    limpar_operacoes_teste()
    estado = criar_estado_inicial("ep_pub_01", "A Odisseia", "Polifemo")
    estado["master"]["arquivo"] = {"caminho": "storage_local/master/ep01.mp4"}
    estado["embalagem"]["titulos"] = ["A Armadilha do Cíclope"]

    # 1. Primeiro upload
    res1 = publicador_node(estado)
    pub1 = res1["episodio"]["publicacao"]
    assert pub1["status"] == "privado"  # Regra Inegociável 10
    assert "reexecucao_evitada" not in pub1 or pub1["reexecucao_evitada"] is False

    # 2. Retomada / reexecução com o mesmo estado (mesma chave de operação)
    estado["episodio"]["publicacao"] = pub1
    res2 = publicador_node(estado)
    pub2 = res2["episodio"]["publicacao"]

    # Deve reaproveitar o mesmo video_id sem duplicar
    assert pub2["video_id"] == pub1["video_id"]
    assert pub2.get("reexecucao_evitada") is True
