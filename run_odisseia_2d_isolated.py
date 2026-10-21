"""Orquestrador 100% Isolado da Subetapa 3: Renderizacao dos 10 Takes 2D LUME no Firefly (Kling 2.5 Turbo)."""

import logging
import os
import random
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

CODE_ROOT = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation")
LUME_ROOT = Path(r"D:\LUME\storage_local\firefly_lume_root")
DB_PATH = LUME_ROOT / "data" / "firefly_jobs.db"
RENDERS_2D_DIR = Path(r"D:\LUME\storage_local\renders\ep_lume_60s_odisseia_2d")
RENDERS_MASTER_DIR = Path(r"D:\LUME\storage_local\renders\ep_lume_60s_odisseia")
PYTHON_EXE = CODE_ROOT / ".venv" / "Scripts" / "python.exe"

if str(CODE_ROOT) not in sys.path:
    sys.path.insert(0, str(CODE_ROOT))

from firefly_bot.chrome_profile import close_existing_profile_chrome

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-5s | [LUME 2D ISOLATED] %(message)s",
)
logger = logging.getLogger("lume_2d_isolated")


def cleanup_lume_chrome():
    profile_dir = LUME_ROOT / "data" / "chrome_profile"
    try:
        close_existing_profile_chrome(profile_dir)
    except Exception as exc:
        logger.warning(f"Aviso ao fechar Chrome do perfil LUME: {exc}")
    lockfile = profile_dir / "lockfile"
    if lockfile.exists():
        try:
            lockfile.unlink()
        except Exception:
            pass


def ensure_system_running():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE system_state SET status = 'running', reason = NULL, updated_at = ? WHERE singleton = 1",
            (time.time(),),
        )
        conn.commit()


def sync_all_done_2d_takes():
    RENDERS_2D_DIR.mkdir(parents=True, exist_ok=True)
    RENDERS_MASTER_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT name, output_path FROM jobs WHERE name LIKE 'ep60_2d_%' AND status = 'done' AND output_path IS NOT NULL"
        ).fetchall()
    for name, output_path in rows:
        if output_path and os.path.exists(output_path):
            src = Path(output_path)
            dst_2d = RENDERS_2D_DIR / f"{name}.mp4"
            shutil.copy2(src, dst_2d)
            canonical_name = name.replace("ep60_2d_", "ep60_")
            dst_master = RENDERS_MASTER_DIR / f"{canonical_name}.mp4"
            shutil.copy2(src, dst_master)


def get_next_job():
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            """
            SELECT id, name, status, attempts, output_path
            FROM jobs
            WHERE name LIKE 'ep60_2d_%'
              AND status IN ('pending', 'claimed', 'generating', 'stale_generating', 'failed', 'failed-content', 'failed-infra')
            ORDER BY id ASC
            LIMIT 1
            """
        ).fetchone()
    return row


def reset_job_to_pending(job_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status = 'pending', attempts = 0, error = NULL, claimed_at = NULL, generation_started_at = NULL, updated_at = ?
            WHERE id = ?
            """,
            (time.time(), job_id),
        )
        conn.commit()


def mark_job_dead(job_id: int, reason: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE jobs SET status = 'dead', error = ?, updated_at = ? WHERE id = ?",
            (reason, time.time(), job_id),
        )
        conn.commit()


def get_job_info(job_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT id, name, status, output_path, error FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()


def run_one_worker() -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(CODE_ROOT)
    cmd = [
        str(PYTHON_EXE),
        "-m",
        "firefly_bot.main",
        "--root",
        str(LUME_ROOT),
        "--concurrency",
        "1",
        "worker-once",
    ]
    logger.info(f"Executando worker-once isolado (timeout=360s): {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, cwd=str(CODE_ROOT), env=env, timeout=360)
        return res.returncode
    except subprocess.TimeoutExpired:
        logger.warning("Worker-once excedeu 360s! Limpando Chrome isolado LUME...")
        cleanup_lume_chrome()
        return -9


def main():
    logger.info("Iniciando Subetapa 3 Isolada: Renderizacao dos 8 Takes 2D Restantes...")
    sync_all_done_2d_takes()
    tries_map: dict[int, int] = {}

    while True:
        cleanup_lume_chrome()
        ensure_system_running()
        nxt = get_next_job()
        if not nxt:
            logger.info("Todos os 10 takes 2D foram processados com sucesso!")
            break

        job_id, name, status, db_attempts, _ = nxt
        tries_map[job_id] = tries_map.get(job_id, 0) + 1

        if tries_map[job_id] > 3:
            logger.error(f"Job {job_id} ({name}) excedeu 3 tentativas. Marcando como dead.")
            mark_job_dead(job_id, "max_retries_exceeded")
            continue

        reset_job_to_pending(job_id)

        logger.info(f"=== Processando Job {job_id} ({name}) [Tentativa {tries_map[job_id]}/3] ===")
        rc = run_one_worker()
        logger.info(f"Worker finalizou com exit_code={rc}")

        info = get_job_info(job_id)
        if not info:
            break
        _, jname, jstatus, jout, jerr = info
        if jstatus == "done" and jout and os.path.exists(jout):
            sz_mb = os.path.getsize(jout) / (1024 * 1024)
            logger.info(f"[TAKE 2D CONCLUIDO] {jname}: {jout} ({sz_mb:.2f} MB)")
            sync_all_done_2d_takes()
            jitter = random.uniform(4.0, 7.0)
            logger.info(f"Aguardando jitter de {jitter:.1f}s...")
            time.sleep(jitter)
        else:
            logger.warning(f"[RETRY] Job {job_id} ({jname}) terminou com status={jstatus}, erro={jerr}")
            time.sleep(3.0)

    cleanup_lume_chrome()
    sync_all_done_2d_takes()
    logger.info("=== Subetapa 3 Isolada Finalizada ===")


if __name__ == "__main__":
    main()
