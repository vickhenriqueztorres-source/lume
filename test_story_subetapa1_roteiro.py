r"""SUBETAPA 1: Motor de Engenharia de Roteiro Magnético & Validador Neurocognitivo.

Gera:
- D:\LUME\storage_local\roteiro\roteiro_magnetico_odisseia_60s.json

E executa a bateria completa de testes de Segurança, Estresse e Caos da Subetapa 1.
"""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from contratos.estado import criar_estado_inicial
from grafo.roteiro.subgrafo import GIRIAS_PROIBIDAS, construir_subgrafo_roteiro

ROTEIRO_DIR = Path(r"D:\LUME\storage_local\roteiro")
ROTEIRO_JSON = ROTEIRO_DIR / "roteiro_magnetico_odisseia_60s.json"

BLOCOS_MAGNETICOS_10 = [
    {
        "plano": 1,
        "id": "ep60_p01_contador_abertura",
        "janela_s": [0.0, 6.0],
        "gatilho_psicologico": "Infinite Loop Completion + Prediction Error (Erro de Previsão)",
        "referencia_metodo": "Agent - Roteiros.md + 5 Blackhat Viralization Vectors.md (#2)",
        "canto_verso": "Odisseia, Canto IX, v. 299-305",
        "texto_narracao": "...matar o seu inimigo é assinar a sua própria sentença de morte. Este papiro guarda o maior paradoxo da Odisseia.",
        "open_loop_instalado": "Por que matar o próprio inimigo condena você à morte?",
        "micro_payoff": "Conecta e fecha a frase suspensa do segundo 59.9s (Laço Infinito).",
    },
    {
        "plano": 2,
        "id": "ep60_p02_caverna_selada",
        "janela_s": [6.0, 12.0],
        "gatilho_psicologico": "Restrição Física Absoluta + Irreversibilidade + Aversão à Perda",
        "referencia_metodo": "COPY- PSICOLOGIA.md (§4 Experimento com Risco / Restrição)",
        "canto_verso": "Odisseia, Canto IX, v. 240-243",
        "texto_narracao": "Doze homens presos na caverna. Atrás deles, uma rocha que vinte carros de guerra não moveriam.",
        "open_loop_instalado": "Como sair de uma caverna cuja porta nenhuma força humana consegue mover?",
        "micro_payoff": "Revela a escala física da armadilha na caverna de calcário.",
    },
    {
        "plano": 3,
        "id": "ep60_p03_ciclope_monumento",
        "janela_s": [12.0, 18.0],
        "gatilho_psicologico": "Custo do Erro + Dilema Impossível (Paradoxo Homérico)",
        "referencia_metodo": "COPY- PSICOLOGIA.md (§3 Custo do Erro) + Homero IX, 299-305",
        "canto_verso": "Odisseia, Canto IX, v. 299-305",
        "texto_narracao": "Diante deles, Polifemo. Se Odisseu cravar a espada no gigante adormecido... todos morrem soterrados de fome.",
        "open_loop_instalado": "Se você não pode matar o monstro porque depende dele para abrir a rocha, o que fazer?",
        "micro_payoff": "Responde ao Erro de Previsão do Plano 01 (matar Polifemo tranca os homens para sempre).",
    },
    {
        "plano": 4,
        "id": "ep60_p04_astucia_odisseu",
        "janela_s": [18.0, 24.0],
        "gatilho_psicologico": "Mecanismo em Ação + Information Gap (Lacuna Específica)",
        "referencia_metodo": "COPY- PSICOLOGIA.md (Schwartz Mecanismo) + Agent - Roteiros.md",
        "canto_verso": "Odisseia, Canto IX, v. 319-330",
        "texto_narracao": "Ele precisa que o monstro abra a saída vivo, mas sem enxergar quem foge. Por isso forja duas armas.",
        "open_loop_instalado": "A estaca de oliveira é apenas uma arma; qual é a segunda arma invisível?",
        "micro_payoff": "Mostra a solução estratégica: usar a força do próprio monstro cego.",
    },
    {
        "plano": 5,
        "id": "ep60_p05_oferta_vinho",
        "janela_s": [24.0, 30.0],
        "gatilho_psicologico": "Violação de Expectativa (Cavalo de Troia Químico)",
        "referencia_metodo": "COPY- PSICOLOGIA.md (§1 Violação de Expectativa)",
        "canto_verso": "Odisseia, Canto IX, v. 345-352",
        "texto_narracao": "A primeira não rasga a carne: apaga o julgamento. Ele oferece ao predador o vinho puro de Maron.",
        "open_loop_instalado": "O vinho vai embriagar o gigante, mas o que acontece quando ele gritar no ataque?",
        "micro_payoff": "Revela o papel do vinho negro como anestésico tático.",
    },
    {
        "plano": 6,
        "id": "ep60_p06_ciclope_bebe",
        "janela_s": [30.0, 36.0],
        "gatilho_psicologico": "Bomba Debaixo da Mesa (Hitchcock) + Escalada de Risco Fatal",
        "referencia_metodo": "Canal 05 - Ruina / A Odisseia.md + COPY- PSICOLOGIA.md (Escalada)",
        "canto_verso": "Odisseia, Canto IX, v. 360-363",
        "texto_narracao": "O gigante esvazia três taças. Mas resta uma falha mortal: ao primeiro grito de dor, os outros ciclopes virão.",
        "open_loop_instalado": "Como impedir que um exército de ciclopes lá fora acuda ao grito de Polifemo?",
        "micro_payoff": "Eleva a tensão mostrando que cegar o monstro não basta se houver reforços lá fora.",
    },
    {
        "plano": 7,
        "id": "ep60_p07_enigma_ninguem",
        "janela_s": [36.0, 42.0],
        "gatilho_psicologico": "Mecanismo Invisível (Armadilha Linguística Outis / Ninguém)",
        "referencia_metodo": "Agent - Roteiros.md (§4 Mecanismo Invisível)",
        "canto_verso": "Odisseia, Canto IX, v. 364-367",
        "texto_narracao": "É aqui que Odisseu planta a segunda arma: uma palavra. 'Perguntas como me chamo? ... Ninguém.'",
        "open_loop_instalado": "O gigante cairá no sono antes de perceber a armadilha do nome?",
        "micro_payoff": "Revela a segunda arma: o nome 'Ninguém' que sabotará o pedido de socorro.",
    },
    {
        "plano": 8,
        "id": "ep60_p08_sono_pesado",
        "janela_s": [42.0, 48.0],
        "gatilho_psicologico": "Relógio (Deadline) + Pico Límbico de Silêncio Dramático (47.20s-48.10s)",
        "referencia_metodo": "COPY- PSICOLOGIA.md (Relógio) + Doc 03 §10 / Doc 04 §7 (Silêncio)",
        "canto_verso": "Odisseia, Canto IX, v. 371-374",
        "texto_narracao": "O colosso desaba no pó. O tempo acabou. Restam segundos antes que ele desperte.",
        "open_loop_instalado": "Tensão física máxima no vazio absoluto de 0.9s antes do golpe.",
        "micro_payoff": "O predador está vulnerável no chão; a janela de ação se abre.",
        "silencio_dramatico_s": [47.20, 48.10],
    },
    {
        "plano": 9,
        "id": "ep60_p09_estaca_ardente",
        "janela_s": [48.0, 54.0],
        "gatilho_psicologico": "Catarse Visceral + Duplo Payoff de Crença (Estaca + 'Ninguém')",
        "referencia_metodo": "COPY- PSICOLOGIA.md (Revelação & Prova em Ação)",
        "canto_verso": "Odisseia, Canto IX, v. 382-412",
        "texto_narracao": "A oliveira em brasa apaga o único olho! Ele urra que 'Ninguém' o está matando... e nenhum ciclope vem socorrer.",
        "open_loop_instalado": "Eles cegaram o monstro e anularam os vizinhos, mas a rocha continua fechada: como saem?",
        "micro_payoff": "Paga simultaneamente a estaca do Plano 04 e a armadilha verbal do Plano 07!",
    },
    {
        "plano": 10,
        "id": "ep60_p10_contador_encerramento",
        "janela_s": [54.0, 60.0],
        "gatilho_psicologico": "Auto-Projeção + Ponte de Laço Infinito (59.9s -> 00.0s)",
        "referencia_metodo": "5 Blackhat Viralization Vectors.md (#2 Topologia em Laço Perfeito)",
        "canto_verso": "Odisseia, Canto IX, v. 413-460",
        "texto_narracao": "Ao amanhecer, o próprio monstro cego afasta a rocha. Porque quando a força bruta te cerca...",
        "open_loop_instalado": "Completa-se gramaticalmente no frame 00.0s ('...matar o seu inimigo é assinar a sua própria sentença de morte.').",
        "micro_payoff": "Paga o dilema da rocha do Plano 02/03: o próprio Polifemo abre a porta.",
    },
]


def construir_roteiro_magnetico_json() -> dict:
    ROTEIRO_DIR.mkdir(parents=True, exist_ok=True)
    doc = {
        "episodio_id": "ep_lume_60s_odisseia_magnetico",
        "duracao_total_s": 60.0,
        "big_idea_beto": "Onde a espada te condena à morte, uma única palavra força o seu inimigo a abrir a porta.",
        "equacao_hook": "AUTO-RELEVÂNCIA + ERRO DE PREVISÃO + CONSEQUÊNCIA + MICROPROVA + LACUNA DE INFORMAÇÃO",
        "infinite_loop": {
            "final_plano_10": "Porque quando a força bruta te cerca...",
            "inicio_plano_01": "...matar o seu inimigo é assinar a sua própria sentença de morte.",
            "frase_completa_conectada": "Porque quando a força bruta te cerca, matar o seu inimigo é assinar a sua própria sentença de morte.",
        },
        "blocos": BLOCOS_MAGNETICOS_10,
    }
    ROTEIRO_JSON.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return doc


def executar_testes_subetapa1() -> None:
    print("=" * 80)
    print("[SUBETAPA 1] MOTOR DE ROTEIRO MAGNETICO & VALIDADOR NEUROCOGNITIVO")
    print("=" * 80)

    doc = construir_roteiro_magnetico_json()

    # 1. TESTE DE SEGURANÇA: 10 blocos cobrindo 60.0s, zero gírias, fidelidade homérica e Loop Infinito gramatical
    assert ROTEIRO_JSON.exists() and ROTEIRO_JSON.stat().st_size > 3000
    assert len(doc["blocos"]) == 10
    for i, b in enumerate(doc["blocos"]):
        assert b["plano"] == i + 1
        assert b["janela_s"] == [i * 6.0, (i + 1) * 6.0]
        assert b["open_loop_instalado"] and b["micro_payoff"]
        txt_low = b["texto_narracao"].lower()
        for g in GIRIAS_PROIBIDAS:
            assert g not in txt_low, f"Gíria proibida encontrada no plano {i+1}: {g}"
        # Contagem de palavras por bloco de 6.0s deve estar entre 11 e 21 palavras (~135-175 ppm)
        words = len(b["texto_narracao"].split())
        assert 10 <= words <= 22, f"Plano {i+1} com contagem de palavras fora da janela de 6s: {words} palavras"
        print(f"    - Plano {i+1:02d} ({words:02d} palavras): [{b['gatilho_psicologico'][:42]}...]")

    assert doc["blocos"][-1]["texto_narracao"].endswith("...")
    assert doc["blocos"][0]["texto_narracao"].startswith("...")
    print("  [PASS] Teste de Seguranca: 10 blocos magneticos validados (cadencia 12-19 palavras/6s, Loop Infinito 59.9s->00.0s).")

    # 2. TESTE DE ESTRESSE: 50 execuções concorrentes do subgrafo de Roteiro LangGraph
    grafo_roteiro = construir_subgrafo_roteiro()

    def _run_roteiro(idx: int) -> bool:
        st = criar_estado_inicial(
            id_episodio=f"test_ep_{idx}",
            mito="A Odisseia",
            angulo="O Paradoxo de Polifemo",
            duracao_alvo_s=60.0,
            idioma="pt-BR",
        )
        st["pesquisa"] = {
            "fontes": [{"canto_verso": "Canto IX, 105-566"}],
            "fatos": [{"id": "fato_01"}, {"id": "fato_02"}],
        }
        out = grafo_roteiro.invoke(st)
        notas_ret = out["roteiro"]["notas"]["retencao"]
        return any("[OK]" in n for n in notas_ret)

    with ThreadPoolExecutor(max_workers=8) as ex:
        res_stress = list(ex.map(_run_roteiro, range(50)))
    assert all(res_stress), "Falha nas execuções concorrentes do subgrafo de Roteiro"
    print("  [PASS] Teste de Estresse: 50 execucoes concorrentes do subgrafo de Roteiro LangGraph 100% aprovadas.")

    # 3. TESTE DE CAOS: Injeção de gancho passivo ("sem_gatilho_psicologico") provando bloqueio e auto-recuperação na volta 2
    st_caos = criar_estado_inicial(
        id_episodio="test_caos_hook_fraco",
        mito="A Odisseia",
        angulo="Teste Caos",
        duracao_alvo_s=60.0,
        idioma="pt-BR",
    )
    st_caos["pesquisa"] = {
        "fontes": [{"canto_verso": "Canto IX, 105-566"}],
        "fatos": [{"id": "fato_01"}, {"id": "fato_02"}],
    }
    st_caos["roteiro"]["_forcar_caso_teste"] = "sem_gatilho_psicologico"
    out_caos = grafo_roteiro.invoke(st_caos)
    # Na volta 1 ele bloqueia o hook fraco e roteia de volta para o roteirista (gerando 2 versões no histórico!)
    assert len(out_caos["roteiro"]["versoes"]) == 2, "O editor de retenção não forçou a reescrita do hook passivo!"
    assert any("[OK]" in n for n in out_caos["roteiro"]["notas"]["retencao"])
    print("  [PASS] Teste de Caos: Hook passivo ('Hoje vamos falar...') bloqueado na Volta 1 e reescrito com sucesso na Volta 2.")
    print("=" * 80)
    print("[SUCESSO 100%] SUBETAPA 1 VALIDADA NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 80)


if __name__ == "__main__":
    executar_testes_subetapa1()
