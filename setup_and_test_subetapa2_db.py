"""Implementacao e Suite de Testes de Seguranca, Estresse e Caos - Subetapa 2 (Fila SQLite 2D)."""

import concurrent.futures
import os
import shutil
import sqlite3
import time
from pathlib import Path

FIREFLY_ROOT = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation")
DB_PATH = FIREFLY_ROOT / "data" / "firefly_jobs.db"
BACKUP_PATH = FIREFLY_ROOT / "data" / "firefly_jobs.db.bak_pre_2d"
IMG_DIR = FIREFLY_ROOT / "imagens"

JOBS_2D = [
    (
        "ep60_2d_p01_contador_abertura",
        "ep60_2d_p01.png",
        "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel art style and dark charcoal ink linework. Action: The hooded Greek storyteller bard slowly unrolls the glowing parchment scroll with his weathered hands as roaring orange flames and bright embers dance and rise from the bronze brazier, casting flickering warm rim light across his cloak. Camera: slow cinematic push-in.",
    ),
    (
        "ep60_2d_p02_caverna_selada",
        "ep60_2d_p02.png",
        "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel art style and dark ink linework. Action: Odysseus and his Greek warriors breathe heavily in terror, their eyes widening as they raise their blazing wooden torches and bronze spears; the orange torch flames flicker dynamically against the dark limestone cave walls and the giant boulder sealing the entrance. Camera: slow dramatic pan and push-in.",
    ),
    (
        "ep60_2d_p03_ciclope_monumento",
        "ep60_2d_p03.png",
        "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel art style and bold ink outlines. Action: The colossal bearded Cyclops Polyphemus steps forward menacingly out of the cave shadows, his massive chest heaving as he tightens his grip on the giant wooden club; his single central amber eye glows and narrows fiercely while orange torchlight flickers from below. Camera: tense low-angle tilt up.",
    ),
    (
        "ep60_2d_p04_astucia_odisseu",
        "ep60_2d_p04.png",
        "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel art style and dark ink linework. Action: Odysseus and his two warriors forcefully carve and sharpen the massive olive-wood stake with their bronze daggers, wood shavings flying as the roaring orange campfire flames dance brightly in the foreground and illuminate their determined faces. Camera: cinematic medium tracking shot.",
    ),
    (
        "ep60_2d_p05_oferta_vinho",
        "ep60_2d_p05.png",
        "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel art style and dark ink linework. Action: Odysseus steps forward and lifts the terracotta amphora and red wineskin higher in offering, speaking boldly while the colossal shadowed Cyclops Polyphemus leans down curiously; the campfire flames crackle and cast dancing orange light on the cave walls. Camera: slow push-in.",
    ),
    (
        "ep60_2d_p06_ciclope_bebe",
        "ep60_2d_p06.png",
        "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel art style and dark ink linework. Action: The giant Cyclops Polyphemus tilts the terracotta amphora back and gulps the dark crimson wine voraciously, red liquid spilling and dripping down his thick beard as Odysseus watches with a cunning smirk beside the crackling orange campfire. Camera: dynamic close-up push-in.",
    ),
    (
        "ep60_2d_p07_enigma_ninguem",
        "ep60_2d_p07.png",
        "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel art style and dark ink linework. Action: Odysseus gestures proudly to his chest declaring his name is Nobody, while the giant Cyclops Polyphemus sways drunkenly on the right, his single eye blinking heavily in stupor as the orange campfire crackles between them. Camera: subtle dramatic zoom.",
    ),
    (
        "ep60_2d_p08_sono_pesado",
        "ep60_2d_p08.png",
        "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel art style and dark ink linework. Action: The colossal Cyclops Polyphemus snores in deep drunken slumber on the cave floor beside the spilled wine amphora while Odysseus and his armed warriors creep forward stealthily through the dark shadows backlit by the flickering campfire. Camera: slow tense creeping push-in.",
    ),
    (
        "ep60_2d_p09_estaca_ardente",
        "ep60_2d_p09.png",
        "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel art style and bold ink outlines. Action: Odysseus and his three Greek warriors charge forward in fierce unison, thrusting the massive olive-wood stake whose tip roars with blazing incandescent orange flames and flying sparks straight toward the shadowed Cyclops. Camera: fast dramatic action push-in.",
    ),
    (
        "ep60_2d_p10_contador_encerramento",
        "ep60_2d_p10.png",
        "Animate this 2D hand-drawn Western animation frame. Keep the exact 2D cel-shaded graphic novel art style and dark ink linework. Action: In the cave background, the giant Polyphemus writhes and roars in agony clutching his blinded eye, while in the foreground the hooded Storyteller stands motionless as warm orange embers and thick smoke swirl upward from the bronze brazier. Camera: slow pull-back fade into shadow.",
    ),
]


def setup_subetapa2():
    print("[SETUP] 1. Criando backup atomico do banco SQLite...")
    shutil.copy2(DB_PATH, BACKUP_PATH)
    assert BACKUP_PATH.exists() and BACKUP_PATH.stat().st_size == DB_PATH.stat().st_size

    print("[SETUP] 2. Higienizando fila antiga e inserindo os 10 Jobs 2D...")
    now = time.time()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Garante que nenhum job antigo fique pendente
    c.execute(
        "UPDATE jobs SET status='done' WHERE status IN ('pending', 'claimed', 'generating', 'stale_generating') AND name NOT LIKE 'ep60_2d_%'"
    )
    # Remove eventuais registros duplicados de ep60_2d_ se re-executado
    c.execute("DELETE FROM jobs WHERE name LIKE 'ep60_2d_%'")

    for name, img_file, prompt in JOBS_2D:
        img_path = str((IMG_DIR / img_file).resolve())
        c.execute(
            """
            INSERT INTO jobs (
                name, prompt, image_path, status, attempts,
                model, resolution, aspect_ratio, duration_seconds, generate_audio, updated_at
            ) VALUES (?, ?, ?, 'pending', 0, 'Kling 2.5 Turbo', '1080p', '16:9', 5, 0, ?)
            """,
            (name, prompt, img_path, now),
        )

    c.execute(
        "UPDATE system_state SET status='running', reason=NULL, updated_at=? WHERE singleton=1",
        (now,),
    )
    conn.commit()
    conn.close()
    print("[SETUP] 10 Jobs 2D inseridos com sucesso.")


def test_1_seguranca_backup_integrity():
    print("[TESTE 1 - SEGURANCA] Verificando PRAGMA integrity_check no DB ativo e no Backup...")
    for path in (DB_PATH, BACKUP_PATH):
        conn = sqlite3.connect(path)
        res = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()
        assert res == "ok", f"Falha de integridade SQLite em {path}: {res}"
    print("  [PASS] Banco ativo e backup integros (PRAGMA integrity_check = ok).")


def test_2_caos_integridade_referencial():
    print("[TESTE 2 - CAOS/REFERENCIAL] Validando os 10 Jobs 2D pendentes...")
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, name, status, attempts, model, resolution, aspect_ratio, duration_seconds, image_path, prompt FROM jobs WHERE status='pending' ORDER BY id ASC"
    ).fetchall()
    conn.close()

    assert len(rows) == 10, f"Esperados 10 jobs pending, encontrados {len(rows)}"
    seen_names = set()
    for r in rows:
        jid, name, st, att, model, res, ar, dur, img_path, prompt = r
        assert name.startswith("ep60_2d_p"), f"Nome invalido na fila: {name}"
        assert name not in seen_names, f"Nome duplicado: {name}"
        seen_names.add(name)
        assert st == "pending" and att == 0
        assert model == "Kling 2.5 Turbo" and res == "1080p" and ar == "16:9" and dur == 5
        assert os.path.isfile(img_path), f"Imagem de referencia inexistente: {img_path}"
        assert "2D hand-drawn" in prompt, f"Prompt sem trava de estilo 2D no job {jid}"
        print(f"  [PASS] Job ID {jid} ({name}) -> {Path(img_path).name} [OK]")


def _worker_read_check(idx: int) -> int:
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cnt = conn.execute("SELECT COUNT(*) FROM jobs WHERE status='pending'").fetchone()[0]
    conn.close()
    return cnt


def test_3_estresse_concorrencia_sqlite():
    print("[TESTE 3 - ESTRESSE] Disparando 50 leituras concorrentes no SQLite...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
        results = list(ex.map(_worker_read_check, range(50)))
    assert all(r == 10 for r in results), f"Inconsistencia nas leituras concorrentes: {set(results)}"
    print("  [PASS] 50/50 transacoes concorrentes executadas sem lock error.")


if __name__ == "__main__":
    print("=" * 75)
    print("EXECUTANDO SUBETAPA 2: SETUP E TESTES ROBUSTOS DA FILA SQLITE 2D")
    print("=" * 75)
    setup_subetapa2()
    test_1_seguranca_backup_integrity()
    test_2_caos_integridade_referencial()
    test_3_estresse_concorrencia_sqlite()
    print("=" * 75)
    print("[SUCESSO 100%] SUBETAPA 2 VALIDADA NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 75)
