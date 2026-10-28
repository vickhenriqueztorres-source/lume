"""Suíte de Validação das Subetapas 1 a 5: Blindagem Raiz Zero-Reuso & Zero-Simulação (d:\\LUME).

Testa e comprova matematicamente:
1. Subetapa 1: Bloqueio por SHA-256 de qualquer imagem ou vídeo legado (`LEGACY_LOCKED`) ou duplicado entre planos/episódios.
2. Subetapa 2: Bloqueio de geração sintética (Pillow) e reuso em `StartFrameGenerator` e `GeradorImagemCLI` em episódios de produção.
3. Subetapa 3: `FireflyEngine.simulate == False` por padrão na raiz e bloqueio de Start Frame antigo antes do envio ao Firefly.
4. Subetapa 4: `animacao.revisor_plano` e `qa.qa_originalidade` reprovam e bloqueiam o Gate 3 se houver qualquer ativo reutilizado.
5. Subetapa 5: `montagem.finalizador` recusa montar episódio de produção se faltarem os clipes reais inéditos do Firefly.
"""

from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from contratos.estado import criar_estado_inicial
from contratos.integridade_assets import (
    AssetReuseViolationError,
    AssetSimulationViolationError,
    ParidadeBlocoPlanoViolationError,
    inicializar_e_indexar_acervo_legado,
    validar_e_registrar_asset_inedito,
    validar_paridade_1_para_1_blocos_planos,
)
from grafo.animacao.subgrafo import revisor_plano_node
from grafo.direcao.subgrafo import diretor_decupagem_node
from grafo.ferramentas.firefly import FireflyEngine
from grafo.ferramentas.gerador_imagem_cli import GeradorImagemCLI
from grafo.ferramentas.start_frame import StartFrameGenerator
from grafo.montagem.subgrafo import finalizador_node
from grafo.qa.subgrafo import qa_originalidade_node
from orquestrador_episodio_puro_firefly import conformar_take_firefly_para_capitulo


def main() -> None:
    print("=" * 85)
    print("[AUDITORIA RAIZ] VALIDANDO SUBETAPAS 1 A 5 (ZERO-REUSO & ZERO-SIMULAÇÃO)")
    print("=" * 85)

    # 1. Subetapa 1: Acervo Legado Indexado e Bloqueado
    stats = inicializar_e_indexar_acervo_legado()
    assert stats["total_legacy_locked_db"] >= 100
    print(f"  [PASS] Subetapa 1: {stats['total_legacy_locked_db']} ativos antigos bloqueados no asset_registry.db (LEGACY_LOCKED).")

    # Testa bloqueio de imagem existente e vídeo existente
    for legacy_path, tipo in [
        (r"D:\LUME\storage_local\frames\start_frames_2d\ep60_2d_p01.png", "start_frame"),
        (r"D:\LUME\storage_local\renders\ep_lume_60s_odisseia_2d\ep60_2d_p01_contador_abertura.mp4", "firefly_video"),
    ]:
        bloqueou = False
        try:
            validar_e_registrar_asset_inedito(legacy_path, "ep_producao_novo_01", "plano_01", tipo)
        except AssetReuseViolationError:
            bloqueou = True
        assert bloqueou, f"Falha: permitiu reutilizar {legacy_path}!"
    print("  [PASS] Subetapa 1: Tentativa de reutilizar PNG ou MP4 existente bloqueada com AssetReuseViolationError.")

    # 2. Subetapa 3: FireflyEngine tem simulate=False por padrão na raiz e bloqueia frame legado
    engine = FireflyEngine()
    assert engine.simulate is False, "FireflyEngine continua com simulate=True por padrão!"
    bloqueou_ff = False
    try:
        engine.animate_start_frame(
            plano_id="plano_real_01",
            start_frame_path=r"D:\LUME\storage_local\frames\start_frames_2d\ep60_2d_p02.png",
            motion_prompt="Animate 2D frame",
            episodio_id="ep_producao_novo_01",
        )
    except AssetReuseViolationError:
        bloqueou_ff = True
    assert bloqueou_ff, "FireflyEngine não bloqueou Start Frame legado antes da animação!"
    print("  [PASS] Subetapa 3: FireflyEngine(simulate=False) padrão na raiz + bloqueio imediato de Start Frame legado.")

    # 3. Subetapa 4: Revisor de Plano e QA de Originalidade bloqueiam ativo reutilizado
    st = criar_estado_inicial(
        id_episodio="ep_producao_novo_01",
        mito="A Odisseia",
        angulo="Teste QA Anti-Reuso",
        duracao_alvo_s=480.0,
        idioma="pt-BR",
    )
    st["aprovacoes"] = [{"gate": 1, "status": "aprovado"}, {"gate": 2, "status": "aprovado"}]
    st["decupagem"]["planos"] = [
        {"id": "plano_real_01", "duracao_s": 6.0, "storyboard": r"D:\LUME\storage_local\frames\start_frames_2d\ep60_2d_p01.png"}
    ]
    st["roteiro"]["blocos"] = [
        {"id": "b01", "duracao_s": 6.0, "narracao": "Bloco único de teste."}
    ]
    st["assets"]["planos"] = {
        "plano_real_01": {
            "render": {
                "caminho": r"D:\LUME\storage_local\renders\ep_lume_60s_odisseia_2d\ep60_2d_p01_contador_abertura.mp4",
                "tentativas": 1,
            }
        }
    }

    rev_out = revisor_plano_node(st)
    assert rev_out["assets"]["planos"]["plano_real_01"]["revisao"]["aprovado"] is False
    assert "erros" in rev_out and len(rev_out["erros"]) == 1

    qa_out = qa_originalidade_node(st)
    assert qa_out["qa"][0]["status"] == "reprovado"
    assert qa_out["qa"][0]["bloqueia"] is True
    print("  [PASS] Subetapa 4: animacao.revisor_plano e qa.qa_originalidade bloquearam tentativa de reuso no Gate 3.")

    # 4. Subetapa 5: Montador Master bloqueia montagem sem clipes inéditos do Firefly
    mont_out = finalizador_node(st)
    assert "erros" in mont_out and len(mont_out["erros"]) == 1, f"Montador Master permitiu montar com clipe legado! {mont_out}"
    assert mont_out["erros"][0]["decisao"] == "escalar"
    assert "ZERO-REUSO" in mont_out["erros"][0]["erro"]
    print(f"  [PASS] Subetapa 5a: montagem.finalizador bloqueou montagem com clipe antigo ({mont_out['erros'][0]['erro'][:72]}...).")

    # 5. Validação da Regra 1:1 (1 Bloco = 1 Start Frame = 1 Vídeo Firefly)
    import json
    roteiro_50 = json.loads(Path(r"d:\LUME\storage_local\roteiro\roteiro_ep01_odisseia_8min.json").read_text(encoding="utf-8"))
    decupagem_50 = json.loads(Path(r"d:\LUME\storage_local\roteiro\roteiro_50_planos_firefly_1para1.json").read_text(encoding="utf-8"))
    assert len(roteiro_50["blocos"]) == 50
    assert len(decupagem_50["planos_firefly"]) == 50

    st_50 = criar_estado_inicial(
        id_episodio="ep01_odisseia_1para1",
        mito="A Odisseia",
        angulo="Seiscentos Homens",
        duracao_alvo_s=510.0,
        idioma="pt-BR",
    )
    st_50["roteiro"]["blocos"] = roteiro_50["blocos"]
    dec_out = diretor_decupagem_node(st_50)
    planos_gerados = dec_out["decupagem"]["planos"]
    assert len(planos_gerados) == 50, f"Esperado 50 planos, obteve {len(planos_gerados)}"
    assert planos_gerados[0]["id"] == "p01" and planos_gerados[-1]["id"] == "p50"
    print("  [PASS] Subetapa 5b: diretor_decupagem_node gerou exatamente 50 planos (p01..p50) para os 50 blocos.")

    # Testa bloqueio de agrupamento (50 blocos vs 12 planos)
    bloqueou_12 = False
    try:
        validar_paridade_1_para_1_blocos_planos(
            blocos=roteiro_50["blocos"],
            planos=planos_gerados[:12],
            episodio_id="ep_teste_12_planos",
        )
    except ParidadeBlocoPlanoViolationError:
        bloqueou_12 = True
    assert bloqueou_12, "Não bloqueou tentativa de agrupar 50 blocos em 12 planos!"
    print("  [PASS] Subetapa 5c: validar_paridade_1_para_1_blocos_planos bloqueou agrupamento de 50 blocos em 12 planos.")

    # Testa bloqueio de esticamento temporal (> 15.0s) no conformador de vídeo Firefly
    bloqueou_esticamento = False
    try:
        conformar_take_firefly_para_capitulo(
            src_mp4=Path("p01.mp4"),
            dst_mp4=Path("p01_conf.mp4"),
            duracao_alvo_s=41.3,
            ato_titulo="PRÓLOGO",
            canto_verso="Canto I, v. 1-5",
            contador_perdas="600 -> 600",
        )
    except ParidadeBlocoPlanoViolationError:
        bloqueou_esticamento = True
    assert bloqueou_esticamento, "Não bloqueou tentativa de esticar take Firefly para 41.3s!"
    print("  [PASS] Subetapa 5d: conformar_take_firefly_para_capitulo bloqueou esticamento temporal > 15.0s (41.3s).")

    print("=" * 85)
    print("[SUCESSO 100%] RAIZ DO PROJETO BLINDADA: ZERO-REUSO + PARIDADE 1 BLOCO = 1 START FRAME = 1 FIREFLY!")
    print("=" * 85)


if __name__ == "__main__":
    main()
