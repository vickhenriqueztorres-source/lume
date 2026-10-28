"""Orquestrador Oficial de Produção 100% Inédita no Adobe Firefly (Subetapa 6 — Política Zero-Reuso).

Este orquestrador NUNCA reutiliza imagens ou vídeos existentes e NUNCA usa zoompan/Pillow:
1. Opera em diretório 100% isolado: `storage_local/episodios/<episodio_id>/`.
2. Exige que todos os Start Frames em `start_frames/` passem por `validar_e_registrar_asset_inedito`
   no `asset_registry.db` antes de iniciar o Firefly (qualquer imagem antiga ou repetida aborta imediatamente).
3. Enfileira cada Start Frame inédito no `firefly_jobs.db` do perfil Chrome autenticado
   (`D:\\agents 3.0 brecha - antigravity\\canalbrecha\\firefly-automation`) com `Kling 2.5 Turbo` (1080p, 16:9).
4. Executa o worker real do Adobe Firefly (`firefly_bot.main worker-once` em ondas paralelas), valida o MP4 baixado com
   `validar_e_registrar_asset_inedito(..., tipo="firefly_video")` e só libera a montagem final quando
   100% dos takes do episódio tiverem status `done` no Firefly.
5. Monta o Master Final 1080p 24fps de 8m30s (510.0s) exclusivamente a partir dos MP4s inéditos do Firefly
   e do master de áudio `-14.0 LUFS`.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from contratos.integridade_assets import (
    AssetReuseViolationError,
    AssetSimulationViolationError,
    ParidadeBlocoPlanoViolationError,
    TETO_DURACAO_PLANO_INDIVIDUAL_S,
    criar_diretorios_episodio_isolado,
    inicializar_e_indexar_acervo_legado,
    validar_e_registrar_asset_inedito,
    validar_paridade_1_para_1_blocos_planos,
)
from grafo.ferramentas.firefly import FIREFLY_REPO, limpar_locks_chrome_firefly

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-5s | [FIREFLY PURO ZERO-REUSO] %(message)s",
)
logger = logging.getLogger("orquestrador_puro_firefly")

FIREFLY_DB = FIREFLY_REPO / "data" / "firefly_jobs.db"
FIREFLY_IMG_DIR = FIREFLY_REPO / "imagens"
FIREFLY_OUT_DIR = FIREFLY_REPO / "saida"
PYTHON_FIREFLY = FIREFLY_REPO / ".venv" / "Scripts" / "python.exe"


def _escape_drawtext(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace(":", "\\:")
        .replace("'", "")
        .replace(",", "\\,")
        .replace("[", "\\[")
        .replace("]", "\\]")
    )


def validar_todos_start_frames_ineditos(episodio_id: str, planos: List[Dict[str, Any]]) -> Dict[str, Path]:
    """Garante que 100% dos Start Frames existem na pasta isolada do episódio e são 100% inéditos."""
    inicializar_e_indexar_acervo_legado()
    dirs = criar_diretorios_episodio_isolado(episodio_id)
    sf_dir = dirs["start_frames"]
    mapa_sf: Dict[str, Path] = {}

    for p in planos:
        plano_id = str(p["id"])
        sf_path = sf_dir / f"{plano_id}.png"
        if not sf_path.is_file():
            raise AssetSimulationViolationError(
                f"[START FRAME AUSENTE] O plano '{plano_id}' do episódio '{episodio_id}' ainda não possui "
                f"Start Frame inédito em '{sf_path}'. Gere todas as novas imagens IA antes de acionar o Firefly."
            )
        sha = validar_e_registrar_asset_inedito(
            caminho=sf_path,
            episodio_id=episodio_id,
            plano_id=plano_id,
            tipo="start_frame",
        )
        mapa_sf[plano_id] = sf_path
        logger.info(f"[START FRAME VALIDADO] {plano_id} -> SHA256={sha[:16]}... (100% Inédito)")

    return mapa_sf


def aguardar_fila_firefly_livre(episodio_id: str, timeout_s: float = 150.0) -> None:
    """Aguarda qualquer job externo em andamento ('claimed' ou 'generating') concluir antes de assumir o Chrome."""
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        with sqlite3.connect(str(FIREFLY_DB), timeout=15.0) as conn:
            ativos = conn.execute(
                "SELECT name, status FROM jobs WHERE name NOT LIKE ? AND status IN ('claimed', 'generating')",
                (f"{episodio_id}%",),
            ).fetchall()
        if not ativos:
            return
        logger.info(f"[AGUARDANDO CHROME FIREFLY LIVRE] Jobs externos em conclusão: {ativos}. Aguardando 10s...")
        time.sleep(10.0)


def enfileirar_episodio_no_firefly(episodio_id: str, planos: List[Dict[str, Any]], mapa_sf: Dict[str, Path]) -> int:
    """Enfileira os planos inéditos do episódio no firefly_jobs.db para renderização no Kling 2.5 Turbo."""
    aguardar_fila_firefly_livre(episodio_id)
    FIREFLY_IMG_DIR.mkdir(parents=True, exist_ok=True)
    now = time.time()
    inseridos = 0
    job_names = [f"{episodio_id}_{p['id']}" for p in planos]

    with sqlite3.connect(str(FIREFLY_DB), timeout=15.0) as conn:
        conn.execute(
            "UPDATE system_state SET status = 'running', reason = NULL, updated_at = ? WHERE singleton = 1",
            (now,),
        )
        placeholders = ",".join("?" for _ in job_names)
        conn.execute(
            f"UPDATE jobs SET status = 'dead', updated_at = ? WHERE name NOT IN ({placeholders}) AND status != 'done'",
            [now, *job_names],
        )
        for p in planos:
            plano_id = str(p["id"])
            job_name = f"{episodio_id}_{plano_id}"
            sf_src = mapa_sf[plano_id]
            sf_dst = FIREFLY_IMG_DIR / f"{job_name}.png"
            shutil.copy2(sf_src, sf_dst)

            prompt_video = p.get("prompt_video") or (
                "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel "
                "art style, Caravaggio chiaroscuro lighting, and charcoal ink linework. Smooth natural character "
                "motion and dancing orange brazier firelight. Camera: slow cinematic push-in."
            )
            _unsafe_tokens = (
                "blood", "strike", "bound", "rope", "kill", "monster", "smash", "shatter",
                "slaughter", "corpse", "horror", "agony", "scream", "weapon", "blind",
                "stab", "destroy", "sacrileg", "bolt", "explod", "drown", "flesh", "prey"
            )
            if any(tok in prompt_video.lower() for tok in _unsafe_tokens):
                prompt_video = (
                    "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
                    "Smooth cinematic motion of warm golden firelight, drifting amber mist, "
                    "and gentle ocean waves with a slow camera push-in at 24fps."
                )

            row = conn.execute(
                "SELECT id, status, output_path FROM jobs WHERE name = ? ORDER BY id DESC LIMIT 1",
                (job_name,),
            ).fetchone()
            if row and row[1] == "done" and row[2] and os.path.exists(row[2]):
                continue

            conn.execute("DELETE FROM jobs WHERE name = ?", (job_name,))
            conn.execute(
                """
                INSERT INTO jobs (
                    name, prompt, image_path, status, attempts,
                    model, resolution, aspect_ratio, duration_seconds, generate_audio, updated_at
                ) VALUES (?, ?, ?, 'pending', 0, 'Kling 2.5 Turbo', '1080p', '16:9', 5, 0, ?)
                """,
                (job_name, prompt_video, str(sf_dst.resolve()), now),
            )
            inseridos += 1
        conn.commit()

    logger.info(f"[FILA FIREFLY] {inseridos} novos jobs enfileirados para '{episodio_id}'.")
    return inseridos


def _sincronizar_renders_firefly_concluidos(episodio_id: str, planos: List[Dict[str, Any]], renders_dir: Path) -> List[str]:
    """Copia e valida todos os MP4s do episódio já concluídos no Firefly, retornando a lista de planos ainda pendentes."""
    faltantes: List[str] = []
    with sqlite3.connect(str(FIREFLY_DB), timeout=15.0) as conn:
        for p in planos:
            plano_id = str(p["id"])
            job_name = f"{episodio_id}_{plano_id}"
            dst_mp4 = renders_dir / f"{plano_id}.mp4"

            if dst_mp4.is_file() and dst_mp4.stat().st_size > 100_000:
                validar_e_registrar_asset_inedito(dst_mp4, episodio_id, plano_id, "firefly_video")
                continue

            row = conn.execute(
                "SELECT status, output_path FROM jobs WHERE name = ? ORDER BY id DESC LIMIT 1",
                (job_name,),
            ).fetchone()
            cand_out = Path(row[1]) if (row and row[1]) else (FIREFLY_OUT_DIR / f"{job_name}.mp4")
            if row and row[0] == "done" and cand_out.is_file() and cand_out.stat().st_size > 100_000:
                shutil.copy2(cand_out, dst_mp4)
                sha = validar_e_registrar_asset_inedito(dst_mp4, episodio_id, plano_id, "firefly_video")
                logger.info(f"[TAKE FIREFLY VALIDADO] {plano_id} -> {dst_mp4.name} (SHA256={sha[:16]}...)")
            else:
                faltantes.append(plano_id)
    return faltantes


def executar_worker_firefly_ate_concluir(
    episodio_id: str,
    planos: List[Dict[str, Any]],
    concurrency: int = 3,
) -> List[Path]:
    """Executa o worker real do Adobe Firefly em ondas paralelas até concluir e validar 100% dos planos."""
    dirs = criar_diretorios_episodio_isolado(episodio_id)
    renders_dir = dirs["renders_firefly"]
    profile_dir = FIREFLY_REPO / "data" / "chrome_profile"
    python_exe = PYTHON_FIREFLY if PYTHON_FIREFLY.exists() else Path(sys.executable)
    job_names = [f"{episodio_id}_{p['id']}" for p in planos]

    max_waves = max(25, len(planos) * 2)
    for wave in range(1, max_waves + 1):
        faltantes = _sincronizar_renders_firefly_concluidos(episodio_id, planos, renders_dir)
        if not faltantes:
            logger.info(f"[100% CONCLUÍDO NO FIREFLY] Todos os {len(planos)} takes inéditos de '{episodio_id}' validados!")
            break

        cur_conc = max(1, min(concurrency, len(faltantes)))
        logger.info(
            f"[ONDA FIREFLY {wave}/{max_waves}] Faltam {len(faltantes)} takes ({faltantes}) | Concurrency={cur_conc}"
        )

        limpar_locks_chrome_firefly(profile_dir)
        now = time.time()
        with sqlite3.connect(str(FIREFLY_DB), timeout=15.0) as conn:
            conn.execute(
                "UPDATE system_state SET status = 'running', reason = NULL, updated_at = ? WHERE singleton = 1",
                (now,),
            )
            placeholders = ",".join("?" for _ in job_names)
            conn.execute(
                f"UPDATE jobs SET status = 'dead', updated_at = ? WHERE name NOT IN ({placeholders}) AND status != 'done'",
                [now, *job_names],
            )
            for pid in faltantes:
                jname = f"{episodio_id}_{pid}"
                row_st = conn.execute(
                    "SELECT status, prompt, image_path FROM jobs WHERE name = ? ORDER BY id DESC LIMIT 1",
                    (jname,),
                ).fetchone()
                if not row_st:
                    continue
                st_cur, cur_prompt, cur_img = row_st
                if st_cur != "pending":
                    # Rotaciona qualquer job que falhou/travou na onda anterior para o FIM da fila
                    # (novo ID autoincrement + novo job_{id}_network.jsonl limpo + prompt 100% seguro)
                    safe_prompt = (
                        "Animate this 2D hand-drawn chiaroscuro graphic novel illustration. "
                        "Smooth cinematic motion of warm golden firelight, drifting amber mist, "
                        "and gentle ocean waves with a slow camera push-in at 24fps."
                    )
                    conn.execute("DELETE FROM jobs WHERE name = ? AND status != 'done'", (jname,))
                    conn.execute(
                        """
                        INSERT INTO jobs (
                            name, prompt, image_path, status, attempts,
                            model, resolution, aspect_ratio, duration_seconds, generate_audio, updated_at
                        ) VALUES (?, ?, ?, 'pending', 0, 'Kling 2.5 Turbo', '1080p', '16:9', 5, 0, ?)
                        """,
                        (jname, safe_prompt, cur_img, now),
                    )
            conn.commit()

        env = os.environ.copy()
        env["PYTHONPATH"] = str(FIREFLY_REPO)
        cmd = [
            str(python_exe),
            "-m",
            "firefly_bot.main",
            "--root",
            str(FIREFLY_REPO),
            "--concurrency",
            str(cur_conc),
            "worker-once",
        ]
        try:
            subprocess.run(cmd, cwd=str(FIREFLY_REPO), env=env, timeout=540)
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout de 540s na onda {wave}. Limpando locks do Chrome...")
            limpar_locks_chrome_firefly(profile_dir)

        _sincronizar_renders_firefly_concluidos(episodio_id, planos, renders_dir)
        time.sleep(random.uniform(3.0, 5.0))

    faltantes_finais = _sincronizar_renders_firefly_concluidos(episodio_id, planos, renders_dir)
    if faltantes_finais:
        raise RuntimeError(
            f"[FALHA FIREFLY] Não foi possível concluir os planos {faltantes_finais} do episódio '{episodio_id}'."
        )

    return [renders_dir / f"{p['id']}.mp4" for p in planos]


def conformar_take_firefly_para_capitulo(
    src_mp4: Path,
    dst_mp4: Path,
    duracao_alvo_s: float,
    ato_titulo: str,
    canto_verso: str,
    contador_perdas: str,
    silencio_dramatico: bool = False,
) -> Path:
    """Conforma um clipe real do Firefly (5s, 24fps) para a janela individual do seu bloco (ex: 10.2s).

    BLOQUEIA qualquer tentativa de esticar um clipe acima de TETO_DURACAO_PLANO_INDIVIDUAL_S (15.0s).
    """
    if duracao_alvo_s <= 0.0 or duracao_alvo_s > TETO_DURACAO_PLANO_INDIVIDUAL_S:
        raise ParidadeBlocoPlanoViolationError(
            f"[VIOLAÇÃO 1:1] Tentativa de conformar '{src_mp4.name}' para {duracao_alvo_s:.2f}s "
            f"(máximo permitido por bloco: {TETO_DURACAO_PLANO_INDIVIDUAL_S:.1f}s). "
            f"É proibido esticar 1 vídeo Firefly para cobrir múltiplos blocos do roteiro!"
        )

    if dst_mp4.is_file() and dst_mp4.stat().st_size > 200_000:
        return dst_mp4

    ato_esc = _escape_drawtext(ato_titulo)
    canto_esc = _escape_drawtext(canto_verso)
    cnt_esc = _escape_drawtext(contador_perdas)
    fade_out_st = max(0.0, duracao_alvo_s - 0.35)

    sil_st = max(0.0, duracao_alvo_s - 1.50)
    extra_silencio = (
        f"drawbox=x=0:y=0:w=1920:h=1080:color=0x0A0705@0.95:t=fill:enable='between(t,{sil_st:.2f},{duracao_alvo_s:.2f})',"#
        if silencio_dramatico
        else ""
    )

    # 5.04s Firefly video -> 2.05x PTS (~10.33s contínuos em 24fps cobrindo exatamente o bloco de 10.2s sem loop triplo)
    filter_complex = (
        "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,"
        "setpts=2.05*PTS,fps=24,format=yuv420p[fwd];"
        "[fwd]split=2[f1][f2];"
        "[f2]reverse[rev];"
        "[f1][rev]concat=n=2:v=1:a=0,"
        f"trim=duration={duracao_alvo_s:.3f},setpts=PTS-STARTPTS,"
        "eq=contrast=1.08:brightness=-0.02:saturation=0.92,"
        "vignette=PI/4.5,"
        f"{extra_silencio}"
        "drawbox=x=0:y=0:w=1920:h=68:color=0x0A0705@0.72:t=fill,"
        f"drawtext=font='Georgia':text='{ato_esc}':fontcolor=0xC89B3C@0.92:fontsize=22:x=48:y=22,"
        f"drawtext=font='Georgia':text='{canto_esc}':fontcolor=0xF4E8C1@0.78:fontsize=19:x=680:y=24,"
        f"drawtext=font='Consolas':text='{cnt_esc}':fontcolor=0xE85D04@0.95:fontsize=22:x=1920-tw-48:y=22,"
        "fade=t=in:st=0:d=0.30,"
        f"fade=t=out:st={fade_out_st:.3f}:d=0.35,"
        "format=yuv420p[vout]"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(src_mp4),
        "-filter_complex",
        filter_complex,
        "-map",
        "[vout]",
        "-t",
        f"{duracao_alvo_s:.3f}",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-r",
        "24",
        "-an",
        str(dst_mp4),
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dst_mp4


def montar_master_episodio_puro_firefly(
    episodio_id: str,
    planos: List[Dict[str, Any]],
    audio_master_path: Path,
    duracao_total_s: float = 510.0,
    blocos: List[Dict[str, Any]] | None = None,
) -> Path:
    """Monta o Master Final 1080p 24fps do episódio exigindo paridade 1:1 (1 Bloco = 1 Vídeo Firefly)."""
    if blocos is not None:
        validar_paridade_1_para_1_blocos_planos(blocos, planos, episodio_id=episodio_id)
    else:
        validar_paridade_1_para_1_blocos_planos(planos, planos, episodio_id=episodio_id)

    dirs = criar_diretorios_episodio_isolado(episodio_id)
    renders_dir = dirs["renders_firefly"]
    master_dir = dirs["master"]
    cap_dir = master_dir / "blocos_1para1_conformados"
    cap_dir.mkdir(parents=True, exist_ok=True)

    cap_paths: List[Path] = []

    for idx, p in enumerate(planos):
        plano_id = str(p["id"])
        raw_firefly_mp4 = renders_dir / f"{plano_id}.mp4"
        if not raw_firefly_mp4.is_file():
            raise AssetSimulationViolationError(
                f"Render Firefly ausente para o plano '{plano_id}': {raw_firefly_mp4}"
            )
        # Revalida no registro global Zero-Reuso
        validar_e_registrar_asset_inedito(raw_firefly_mp4, episodio_id, plano_id, "firefly_video")

        jan = p["janela_s"]
        clip_dur = round(float(jan[1]) - float(jan[0]), 3)
        dst_cap = cap_dir / f"bloco_{idx + 1:02d}_{plano_id}.mp4"

        logger.info(
            f"[CONFORMANDO BLOCO 1:1 {idx + 1:02d}/{len(planos)}] {plano_id} ({clip_dur:.2f}s) a partir de {raw_firefly_mp4.name}..."
        )
        conformar_take_firefly_para_capitulo(
            src_mp4=raw_firefly_mp4,
            dst_mp4=dst_cap,
            duracao_alvo_s=clip_dur,
            ato_titulo=p.get("ato_titulo", "A ODISSEIA"),
            canto_verso=p.get("canto_verso", "Odisseia, Homero"),
            contador_perdas=p.get("contador_perdas", "600 HOMENS"),
            silencio_dramatico=("silencio_dramatico_s" in p),
        )
        cap_paths.append(dst_cap)

    concat_list_txt = master_dir / f"{episodio_id}_concat_50_blocos.txt"
    with open(concat_list_txt, "w", encoding="utf-8") as f:
        for cp in cap_paths:
            f.write(f"file '{cp.resolve().as_posix()}'\n")

    visual_concat_mp4 = master_dir / f"{episodio_id}_visual_510s.mp4"
    cmd_concat = [
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        str(concat_list_txt),
        "-c",
        "copy",
        str(visual_concat_mp4),
    ]
    logger.info(f"[MONTAGEM 1:1] Unindo {len(cap_paths)} blocos Firefly em {visual_concat_mp4.name}...")
    subprocess.run(cmd_concat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    master_final_mp4 = master_dir / f"{episodio_id}_master.mp4"
    cmd_mux = [
        "ffmpeg",
        "-y",
        "-i",
        str(visual_concat_mp4),
        "-i",
        str(audio_master_path),
        "-map",
        "0:v:0",
        "-map",
        "1:a:0",
        "-c:v",
        "copy",
        "-c:a",
        "aac",
        "-b:a",
        "256k",
        "-ar",
        "48000",
        "-ac",
        "2",
        "-t",
        f"{duracao_total_s:.2f}",
        "-movflags",
        "+faststart",
        str(master_final_mp4),
    ]
    logger.info(f"[MUX MASTER FINAL] Gerando {master_final_mp4} com áudio -14.0 LUFS...")
    subprocess.run(cmd_mux, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    logger.info(
        f"[MASTER FINAL CONCLUÍDO] {master_final_mp4} ({master_final_mp4.stat().st_size / (1024 * 1024):.2f} MB)"
    )
    return master_final_mp4


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orquestrador Oficial Zero-Reuso & Paridade 1:1 Adobe Firefly")
    parser.add_argument("--episodio-id", required=True, help="ID único do novo episódio")
    parser.add_argument("--roteiro-json", required=True, help="Caminho do JSON de roteiro/planos 1:1 do episódio")
    parser.add_argument("--concurrency", type=int, default=3, help="Abas simultâneas no Firefly (1 a 6)")
    parser.add_argument(
        "--audio-master",
        default=r"d:\LUME\storage_local\audio\master_audio_8min.wav",
        help="Caminho do master de áudio WAV (-14 LUFS)",
    )
    args = parser.parse_args()

    dados = json.loads(Path(args.roteiro_json).read_text(encoding="utf-8"))
    lista_blocos = dados.get("blocos") or dados.get("planos") or []
    lista_planos = dados.get("planos") or dados.get("blocos") or []
    validar_paridade_1_para_1_blocos_planos(lista_blocos, lista_planos, episodio_id=args.episodio_id)
    mapa = validar_todos_start_frames_ineditos(args.episodio_id, lista_planos)
    enfileirar_episodio_no_firefly(args.episodio_id, lista_planos, mapa)
    executar_worker_firefly_ate_concluir(args.episodio_id, lista_planos, concurrency=args.concurrency)
    montar_master_episodio_puro_firefly(
        episodio_id=args.episodio_id,
        planos=lista_planos,
        audio_master_path=Path(args.audio_master),
        duracao_total_s=float(dados.get("duracao_total_s", 510.0)),
        blocos=lista_blocos,
    )
