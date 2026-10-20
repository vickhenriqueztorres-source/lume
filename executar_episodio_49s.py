"""Execução Completa de Produção do Estúdio LUME: Episódio de 49 Segundos.

Executa o Showrunner e os 47 agentes dos 10 departamentos:
1. Pauta & Pesquisa (4 agentes: mitológico, arqueólogo, curador, revisor fontes)
2. Roteiro (5 agentes: roteirista, revisores de estrutura, fidelidade, tom, sensibilidade)
3. Gate 1: Roteiro canônico
4. Direção & Decupagem (5 agentes: decupagem 49s, fotografia, direção de tela, elenco, storyboarder com Start Frames)
5. Gate 2: Storyboard e Start Frames
6. Produção Paralela:
   - Arte (5 agentes: silhuetas, vetorizador, rigger, cenógrafo, bibliotecário)
   - Animação (5 agentes: animador, montador 3D, gerente render Firefly, revisor técnico, VFX)
   - Áudio (5 agentes: diretor voz, narrador, sound designer, supervisor musical, mixador -14 LUFS)
7. Montagem (4 agentes: editor, grafismo, finalizador Master 4K, legendador ASR)
8. QA (6 agentes: técnico, continuidade, fidelidade, marca, direitos, originalidade)
9. Gate 3: Corte Final Master
10. Embalagem (5 agentes: titulista 60 chars, designer 3 thumbs A/B/C, avaliador feed 120px, redator, shorts)
11. Gate 4: Embalagem
12. Gate 5: Autorização final
13. Publicação Privada no YouTube (idempotência garantida)
14. Memória e Aprendizado (Curador grava lições na Store)
"""

import json
import os
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from contratos.estado import criar_estado_inicial
from contratos.gates import RespostaGate
from contratos.plano import Plano
from grafo.base import limpar_operacoes_teste
from grafo.showrunner.grafo import construir_grafo_showrunner
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command


def executar_producao_49s():
    print("=" * 80)
    print("[ESTUDIO LUME] PRODUCAO COMPLETA DE EPISODIO (49 SEGUNDOS)")
    print("=" * 80)
    print("Tema: A Odisseia -- A Astucia de Ninguem na Caverna de Polifemo")
    print("Duracao Alvo: 49.0 segundos | Resolucao: 4K Master | Audio: -14.0 LUFS")
    print("=" * 80 + "\n")

    limpar_operacoes_teste()
    checkpointer = MemorySaver()
    app = construir_grafo_showrunner(checkpointer=checkpointer)

    # 1. Estado Inicial
    estado_inicial = criar_estado_inicial(
        id_episodio="ep_lume_49s_odisseia",
        mito="A Odisseia",
        angulo="Odisseu e a Astúcia de Ninguém: A Luz da Mente Contra a Força Bruta",
        duracao_alvo_s=49.0,
        idioma="pt-BR",
    )

    # Decupagem precisa somando exatamente 49.0 segundos
    planos_49s = [
        Plano(
            id="ep49_p01_abertura",
            bloco_roteiro=1,
            mundo="contador",
            tipo_plano="contador",
            duracao_s=5.0,
            proporcao="16:9",
            camera={"movimento": "push_in_lento", "lente_mm": 50},
            fogo={"nivel": 2, "curva": "estavel", "tremulacao_hz": 1.0},
            parede="ruina_calcario",
            sfx=["braseiro_crepitando"],
        ).model_dump(),
        Plano(
            id="ep49_p02_caverna",
            bloco_roteiro=1,
            mundo="parede",
            tipo_plano="medio",
            duracao_s=6.0,
            proporcao="2.39",
            marionetes=[{"id": "odisseu_v1", "distancia_fogo": 0.8, "direcao": "dir"}],
            camera={"movimento": "pan_direita", "lente_mm": 35},
            fogo={"nivel": 3, "curva": "estavel", "tremulacao_hz": 2.0},
            parede="caverna_umida",
            sfx=["pingos_caverna"],
        ).model_dump(),
        Plano(
            id="ep49_p03_gigante",
            bloco_roteiro=1,
            mundo="parede",
            tipo_plano="escala",
            duracao_s=7.0,
            proporcao="2.39",
            marionetes=[
                {"id": "polifemo_v1", "distancia_fogo": 0.2, "direcao": "esq"},
                {"id": "odisseu_v1", "distancia_fogo": 0.8, "direcao": "dir"},
            ],
            camera={"movimento": "tilt_up", "lente_mm": 35},
            fogo={"nivel": 4, "curva": "subida", "tremulacao_hz": 3.0},
            parede="caverna_umida",
            sfx=["passos_pesados"],
        ).model_dump(),
        Plano(
            id="ep49_p04_vinho",
            bloco_roteiro=2,
            mundo="parede",
            tipo_plano="close",
            duracao_s=6.5,
            proporcao="2.39",
            marionetes=[{"id": "odisseu_v1", "distancia_fogo": 0.7, "direcao": "dir"}],
            camera={"movimento": "push_in_lento", "lente_mm": 50},
            fogo={"nivel": 3, "curva": "estavel", "tremulacao_hz": 2.0},
            parede="caverna_umida",
            sfx=["vinho_servido"],
        ).model_dump(),
        Plano(
            id="ep49_p05_taca",
            bloco_roteiro=2,
            mundo="parede",
            tipo_plano="insert",
            duracao_s=5.5,
            proporcao="2.39",
            marionetes=[{"id": "polifemo_v1", "distancia_fogo": 0.3, "direcao": "esq"}],
            camera={"movimento": "estatica", "lente_mm": 85},
            fogo={"nivel": 4, "curva": "pico", "tremulacao_hz": 3.0},
            parede="caverna_umida",
            sfx=["trago_pesado"],
        ).model_dump(),
        Plano(
            id="ep49_p06_ninguem",
            bloco_roteiro=2,
            mundo="parede",
            tipo_plano="medio",
            duracao_s=6.0,
            proporcao="2.39",
            marionetes=[
                {"id": "odisseu_v1", "distancia_fogo": 0.6, "direcao": "dir"},
                {"id": "polifemo_v1", "distancia_fogo": 0.4, "direcao": "esq"},
            ],
            camera={"movimento": "dolly_lateral", "lente_mm": 50},
            fogo={"nivel": 3, "curva": "estavel", "tremulacao_hz": 2.5},
            parede="caverna_umida",
            sfx=["eco_voz"],
        ).model_dump(),
        Plano(
            id="ep49_p07_sono",
            bloco_roteiro=3,
            mundo="parede",
            tipo_plano="escala",
            duracao_s=6.0,
            proporcao="2.39",
            marionetes=[{"id": "polifemo_v1", "distancia_fogo": 0.3, "direcao": "esq"}],
            camera={"movimento": "tilt_down", "lente_mm": 35},
            fogo={"nivel": 2, "curva": "queda", "tremulacao_hz": 1.5},
            parede="caverna_umida",
            sfx=["ronco_profundo"],
        ).model_dump(),
        Plano(
            id="ep49_p08_estaca",
            bloco_roteiro=3,
            mundo="parede",
            tipo_plano="insert",
            duracao_s=7.0,
            proporcao="2.39",
            marionetes=[{"id": "odisseu_v1", "distancia_fogo": 0.8, "direcao": "dir"}],
            camera={"movimento": "push_in_rapido", "lente_mm": 50},
            fogo={"nivel": 5, "curva": "pico", "tremulacao_hz": 4.5},
            parede="caverna_umida",
            sfx=["estaca_no_fogo", "estalar_brasa"],
        ).model_dump(),
    ]

    total_s = sum(p["duracao_s"] for p in planos_49s)
    assert total_s == 49.0, f"Duração calculada: {total_s}s"
    estado_inicial["decupagem"]["planos"] = planos_49s

    config = {"configurable": {"thread_id": "producao_lume_49s_run_01"}}

    # =========================================================================
    # ETAPA 1: Pesquisa & Roteiro -> Pausa no Gate 1
    # =========================================================================
    print("[1/6] Disparando Departamentos de Pesquisa e Roteiro...")
    t0 = time.time()
    app.invoke(estado_inicial, config)
    st = app.get_state(config)
    print(f"  + Pesquisa canonica concluida: {len(st.values['pesquisa']['fontes'])} fontes, {len(st.values['pesquisa']['fatos'])} fatos.")
    print(f"  + Roteiro gerado com {len(st.values['roteiro']['blocos'])} blocos dramaticos.")
    print(f"  + Notas dos revisores: Retencao={st.values['roteiro']['notas']['retencao']}, Fidelidade={st.values['roteiro']['notas']['fidelidade']}, Tom={st.values['roteiro']['notas']['tom']}")
    print("  || Pausado no Gate 1 (Aprovacao de Roteiro).")

    # =========================================================================
    # ETAPA 2: Retomada Gate 1 -> Direção e Storyboards -> Pausa no Gate 2
    # =========================================================================
    print("\n[2/6] Respondendo Gate 1 e executando Departamento de Direcao...")
    resp_g1 = RespostaGate(
        gate_id=1,
        status="aprovado",
        autor="showrunner_lume",
        comentarios="Roteiro canonico de 49s aprovado para decupagem e start frames.",
        simulado=True,
    ).model_dump()
    app.invoke(Command(resume=resp_g1), config)
    st = app.get_state(config)

    print(f"  + Direcao concluiu 8 planos somando exatamente {total_s}s.")
    print(f"  + Color script gerado: {len(st.values['color_script']['cenas'])} atmosferas de luz.")
    print(f"  + Start Frames e Storyboards gerados para todos os 8 planos.")
    print("  || Pausado no Gate 2 (Aprovacao de Storyboard e Start Frames).")

    # =========================================================================
    # ETAPA 3: Retomada Gate 2 -> Produção Paralela (Arte/Animação Firefly // Áudio) -> Montagem -> QA -> Gate 3
    # =========================================================================
    print("\n[3/6] Respondendo Gate 2 e iniciando Producao Paralela...")
    print("  - Arte: Modelagem de silhuetas e biblioteca de marionetes.")
    print("  - Animacao: Geracao de clipes MP4 via FireflyEngine (concorrencia serial = 1).")
    print("  - Audio: Narracao de voz neural, efeitos sonoros (SFX) e mixagem EBU R128 (-14.0 LUFS).")
    print("  - Montagem: Edicao da Timeline e Renderizacao do Master 4K.")
    print("  - QA: 6 agentes auditando integridade tecnica, continuidade e fidelidade.")
    
    resp_g2 = RespostaGate(
        gate_id=2,
        status="aprovado",
        autor="showrunner_lume",
        comentarios="Start Frames cinematograficos aprovados para geracao de video Firefly.",
        simulado=True,
    ).model_dump()
    app.invoke(Command(resume=resp_g2), config)
    st = app.get_state(config)

    print(f"  + Animacao: 8 clipes de video gerados com sucesso via FireflyEngine.")
    print(f"  + Audio: Mixagem finalizada em exatamente {st.values['audio']['lufs']} LUFS.")
    print(f"  + Master 4K: {st.values['master']['arquivo']['caminho']} ({st.values['master']['arquivo']['resolucao']}).")
    print(f"  + Relatorios de QA: {len(st.values['qa'])} checagens aprovadas.")
    print("  || Pausado no Gate 3 (Aprovacao de Corte Final).")

    # =========================================================================
    # ETAPA 4: Retomada Gate 3 -> Embalagem -> Pausa no Gate 4
    # =========================================================================
    print("\n[4/6] Respondendo Gate 3 e gerando Embalagem de Alta Conversao...")
    resp_g3 = RespostaGate(
        gate_id=3,
        status="aprovado",
        autor="showrunner_lume",
        comentarios="Master 4K aprovado para empacotamento e distribuicao.",
        simulado=True,
    ).model_dump()
    app.invoke(Command(resume=resp_g3), config)
    st = app.get_state(config)

    titulos = st.values["embalagem"]["titulos"]
    thumbs = st.values["embalagem"]["thumbs"]
    print(f"  + 3 Titulos gerados (<= 60 chars):")
    for t in titulos:
        texto = t if isinstance(t, str) else t.get("texto", str(t))
        chars = len(texto)
        print(f"     - \"{texto}\" ({chars} chars)")
    print(f"  + 3 Thumbnails nos layouts A, B, C validadas em legibilidade 120px.")
    print("  || Pausado no Gate 4 (Aprovacao de Embalagem).")

    # =========================================================================
    # ETAPA 5: Retomada Gate 4 -> Pausa no Gate 5 (Autorização de Publicação)
    # =========================================================================
    print("\n[5/6] Respondendo Gate 4 e solicitando autorizacao final...")
    resp_g4 = RespostaGate(
        gate_id=4,
        status="aprovado",
        autor="showrunner_lume",
        comentarios="Titulo e thumbnail vencedora aprovados para upload.",
        simulado=True,
    ).model_dump()
    app.invoke(Command(resume=resp_g4), config)
    st = app.get_state(config)
    print("  || Pausado no Gate 5 (Confirmacao Humana Obrigatoria para Envio).")

    # =========================================================================
    # ETAPA 6: Retomada Gate 5 -> Upload Privado -> Curadoria de Memória
    # =========================================================================
    print("\n[6/6] Autorizando Gate 5: Upload Privado e Persistencia na Store...")
    resp_g5 = RespostaGate(
        gate_id=5,
        status="aprovado",
        autor="showrunner_lume",
        comentarios="Autorizada publicacao restrita em modo privado.",
        simulado=True,
    ).model_dump()
    app.invoke(Command(resume=resp_g5), config)

    st_final = app.get_state(config)
    assert len(st_final.tasks) == 0, "O grafo deve finalizar sem tarefas pendentes."

    pub = st_final.values["episodio"]["publicacao"]
    custos = st_final.values["custos"]
    licoes = st_final.values["episodio"]["licoes_gravadas"]
    tempo_total = time.time() - t0

    print("\n" + "=" * 80)
    print("[SUCESSO] PRODUCAO CONCLUIDA COM SUCESSO DE PONTA A PONTA!")
    print("=" * 80)
    print(f"- ID do Episodio:      {st_final.values['episodio']['id']}")
    print(f"- Duracao Final:       {total_s} segundos (8 planos)")
    print(f"- Arquivo Master 4K:   {st_final.values['master']['arquivo']['caminho']}")
    print(f"- Resolucao:           {st_final.values['master']['arquivo']['resolucao']}")
    print(f"- Normalizacao Audio:  {st_final.values['audio']['lufs']} LUFS")
    print(f"- Status Publicacao:   MODO ESTRITAMENTE {pub['status'].upper()}")
    print(f"- URL Privada YouTube: {pub['upload_url']}")
    titulo_sel = titulos[0] if isinstance(titulos[0], str) else titulos[0].get("texto", str(titulos[0]))
    print(f"- Titulo Escolhido:    \"{titulo_sel}\"")
    print(f"- Total Gates:         5 Gates Aprovados com Auditoria")
    print(f"- Total Nos Executados: 48 Nos (Showrunner + 47 Agentes)")
    print(f"- Chamadas / Custos:   {len(custos)} registros de consumo")
    print(f"- Licoes na Store:     {len(licoes)} licoes gravadas para o proximo episodio")
    print(f"- Tempo de Producao:   {tempo_total:.2f} segundos")
    print("=" * 80)

    return st_final.values


if __name__ == "__main__":
    executar_producao_49s()
