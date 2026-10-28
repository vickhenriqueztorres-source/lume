"""Testes do Agente e da Skill RAG de Eugene Schwartz (Breakthrough Advertising)."""

from __future__ import annotations

from pathlib import Path
from grafo.roteiro.agente_eugene_schwartz import AgenteEugeneSchwartz


def test_skill_eugene_schwartz_arquivos_instalados():
    skill_dir = Path(r"C:\Users\brend\.gemini\config\skills\eugene-schwartz")
    assert (skill_dir / "SKILL.md").is_file()
    assert (skill_dir / "handler.py").is_file()
    assert (skill_dir / "scripts" / "search_eugene_rag.py").is_file()
    assert (skill_dir / "references" / "principios_breakthrough_advertising.md").is_file()


def test_busca_rag_285_chunks_e_conceitos():
    agente = AgenteEugeneSchwartz()
    chunks_consciencia = agente.buscar_por_conceito(
        query="headline nível de consciência do prospecto",
        concept="niveis_de_consciencia",
        top_k=4,
    )
    assert len(chunks_consciencia) == 4
    for c in chunks_consciencia:
        assert "niveis_de_consciencia" in c["conceitos"]
        assert c["pagina_inicio"] >= 1
        assert len(c["texto"]) > 100


def test_diagnostico_e_geracao_copy_eugene():
    agente = AgenteEugeneSchwartz()
    relatorio = agente.diagnosticar_e_estruturar_copy(
        produto="A Odisseia — O Paradoxo da Caverna de Polifemo",
        nicho="Documentário Mitológico Cinematográfico",
        publico="Espectadores saturados de resumos escolares que buscam tensão psicológica",
        nivel_consciencia=1,
        grau_sofisticacao=5,
        mecanismo_unico="Armadilha Linguística de Outis (Ninguém)",
    )
    assert relatorio["decision"] == "approve"
    assert relatorio["diagnostico"]["awareness_level"] == "unaware"
    assert relatorio["diagnostico"]["market_sophistication_level"] == 5
    assert relatorio["scores"]["score_total"] >= 8.5
    assert len(relatorio["headlines"]) == 3
    assert len(relatorio["fontes_rag_consultadas"]) >= 5
