"""Motor de Automação e Execução do Adobe Firefly com Blindagem Zero-Reuso (Subetapa 3).

Regras na Raiz do Projeto:
1. `simulate: bool = False` é o padrão obrigatório de produção.
2. É proibido usar `zoompan` (FFmpeg) ou gravar bytes MP4 vazios em episódios de produção.
3. Antes de animar no Firefly, o Start Frame é validado contra o `asset_registry.db` para garantir que é 100% inédito.
4. Após o download do MP4 pelo Firefly (`Kling 2.5 Turbo`), o vídeo é validado no `firefly_jobs.db` (`status='done'`)
   e registrado no `asset_registry.db` no diretório isolado `storage_local/episodios/<episodio_id>/renders_firefly/`.
"""

from __future__ import annotations

import json
import logging
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
from pathlib import Path
from typing import Optional

from contratos.integridade_assets import (
    AssetReuseViolationError,
    AssetSimulationViolationError,
    criar_diretorios_episodio_isolado,
    validar_e_registrar_asset_inedito,
)
from grafo.ferramentas.start_frame import _is_unit_test_context

LOGGER = logging.getLogger(__name__)

FIREFLY_REPO = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation")
LUME_FIREFLY_ROOT = Path(r"D:\LUME\storage_local\firefly_lume_root")


class FireflySessionError(Exception):
    """Erro crítico na sessão de renderização do Adobe Firefly."""
    pass


class FireflySecurityError(Exception):
    """Tentativa de Path Traversal ou violação de segurança detectada."""
    pass


def limpar_locks_chrome_firefly(profile_dir: Path) -> None:
    """Remove locks órfãos do perfil Chrome antes de iniciar o worker do Firefly."""
    for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile"):
        lf = profile_dir / lock_name
        if lf.exists():
            try:
                lf.unlink()
            except Exception:
                pass


class FireflyEngine:
    """Motor de geração de vídeo a partir de Start Frame via Adobe Firefly (simulate=False por padrão)."""

    _lock = threading.Lock()

    def __init__(
        self,
        output_base_dir: str | Path = "storage_local/renders",
        timeout_seconds: float = 360.0,
        max_retries: int = 3,
        simulate: bool = False,
    ) -> None:
        self.output_base_dir = Path(output_base_dir)
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.simulate = simulate

    def sanitizar_nome(self, nome: str) -> str:
        """Sanitiza strings de identificação para prevenir Path Traversal."""
        if ".." in nome or "/" in nome or "\\" in nome:
            raise FireflySecurityError(f"Caminho inseguro ou tentativa de Path Traversal: '{nome}'")
        sanitizado = re.sub(r"[^a-zA-Z0-9_\-]", "", nome)
        if not sanitizado:
            raise FireflySecurityError(f"Nome vazio após sanitização: '{nome}'")
        return sanitizado

    def animate_start_frame(
        self,
        plano_id: str,
        start_frame_path: Path | str,
        motion_prompt: str,
        target_duration: float = 5.0,
        episodio_id: str = "lume_ep",
    ) -> Path:
        """Gera clipe de vídeo MP4 serialmente no Adobe Firefly a partir de um Start Frame inédito."""
        id_sanitizado = self.sanitizar_nome(plano_id)
        ep_sanitizado = self.sanitizar_nome(episodio_id)
        is_test = self.simulate or _is_unit_test_context(id_sanitizado, ep_sanitizado)

        start_frame = Path(start_frame_path)
        if not start_frame.exists():
            raise FileNotFoundError(f"Start frame não encontrado: {start_frame}")

        if not is_test:
            # 1. Valida que o Start Frame é 100% inédito antes mesmo de enviar ao Firefly
            validar_e_registrar_asset_inedito(
                caminho=start_frame,
                episodio_id=ep_sanitizado,
                plano_id=id_sanitizado,
                tipo="start_frame",
            )
            dirs = criar_diretorios_episodio_isolado(ep_sanitizado)
            clipes_dir = dirs["renders_firefly"]
        else:
            clipes_dir = self.output_base_dir / ep_sanitizado
            clipes_dir.mkdir(parents=True, exist_ok=True)

        target_clip_path = clipes_dir / f"{id_sanitizado}.mp4"

        # Se o clipe já foi renderizado pelo Firefly NESTA pasta isolada do episódio atual, valida no Registry
        if not is_test and target_clip_path.exists() and target_clip_path.stat().st_size > 500_000:
            validar_e_registrar_asset_inedito(
                caminho=target_clip_path,
                episodio_id=ep_sanitizado,
                plano_id=id_sanitizado,
                tipo="firefly_video",
            )
            return target_clip_path

        with self._lock:
            LOGGER.info(
                f"[FIREFLY] Iniciando animação do plano {plano_id} para {episodio_id} (simulate={is_test}). "
                f"Prompt: '{motion_prompt}' | Duração: {target_duration}s"
            )

            for attempt in range(1, self.max_retries + 1):
                try:
                    if is_test:
                        self._simulate_generation_for_unit_tests(
                            start_frame, target_clip_path, target_duration, motion_prompt
                        )
                    else:
                        self._execute_local_automation(
                            frame_path=start_frame,
                            motion_prompt=motion_prompt,
                            out_path=target_clip_path,
                            duration=target_duration,
                            plano_id=id_sanitizado,
                            episodio_id=ep_sanitizado,
                        )
                        validar_e_registrar_asset_inedito(
                            caminho=target_clip_path,
                            episodio_id=ep_sanitizado,
                            plano_id=id_sanitizado,
                            tipo="firefly_video",
                        )

                    if target_clip_path.exists() and target_clip_path.stat().st_size > 100:
                        LOGGER.info(f"[FIREFLY] Plano {plano_id} animado com sucesso: {target_clip_path}")
                        return target_clip_path
                except (AssetReuseViolationError, AssetSimulationViolationError):
                    raise
                except Exception as e:
                    LOGGER.warning(f"[FIREFLY] Tentativa {attempt}/{self.max_retries} falhou para plano {plano_id}: {e}")
                    time.sleep(1.0)

            raise FireflySessionError(
                f"Sessão do Firefly falhou após {self.max_retries} tentativas no plano {plano_id}."
            )

    def _simulate_generation_for_unit_tests(
        self,
        frame_path: Path,
        out_path: Path,
        duration: float,
        motion_prompt: str = "",
    ) -> None:
        """Exclusivo para testes unitários offline (pytest). Proibido em episódios de produção."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        mp4_bytes = (
            b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41"
            b"\x00\x00\x00\x08free"
            b"\x00\x00\x10\x00mdat" + b"\x00" * 8192
        )
        tmp_path = out_path.with_suffix(".tmp.mp4")
        tmp_path.write_bytes(mp4_bytes)
        tmp_path.replace(out_path)

    def _execute_local_automation(
        self,
        frame_path: Path,
        motion_prompt: str,
        out_path: Path,
        duration: float,
        plano_id: str = "shot",
        episodio_id: str = "lume_ep",
    ) -> None:
        """Execução real de automação local via Adobe Firefly (Kling 2.5 Turbo) na conta logada."""
        python_exe = FIREFLY_REPO / ".venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = Path(sys.executable)

        if not FIREFLY_REPO.exists():
            raise FireflySessionError(f"Repositório de automação Firefly não encontrado: {FIREFLY_REPO}")

        profile_dir = FIREFLY_REPO / "data" / "chrome_profile"
        limpar_locks_chrome_firefly(profile_dir)

        # 1. Copia o Start Frame inédito com nome exclusivo do episódio+plano
        imagens_dir = FIREFLY_REPO / "imagens"
        imagens_dir.mkdir(parents=True, exist_ok=True)
        job_unique_name = f"{episodio_id}_{plano_id}"
        dest_frame_name = f"{job_unique_name}.png"
        dest_frame = imagens_dir / dest_frame_name
        shutil.copy2(frame_path, dest_frame)

        # 2. Insere o job diretamente no firefly_jobs.db e garante system_state='running'
        data_dir = FIREFLY_REPO / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / "firefly_jobs.db"
        now_ts = time.time()

        with sqlite3.connect(str(db_path), timeout=15.0) as conn:
            conn.execute(
                "UPDATE system_state SET status = 'running', reason = NULL, updated_at = ? WHERE singleton = 1",
                (now_ts,),
            )
            conn.execute("DELETE FROM jobs WHERE name = ?", (job_unique_name,))
            conn.execute(
                """
                INSERT INTO jobs (
                    name, prompt, image_path, status, attempts,
                    model, resolution, aspect_ratio, duration_seconds, generate_audio, updated_at
                ) VALUES (?, ?, ?, 'pending', 0, 'Kling 2.5 Turbo', '1080p', '16:9', 5, 0, ?)
                """,
                (job_unique_name, motion_prompt, str(dest_frame.resolve()), now_ts),
            )
            conn.commit()

        # 3. Executa o worker real do Firefly
        env = os.environ.copy()
        env["PYTHONPATH"] = str(FIREFLY_REPO)
        worker_cmd = [
            str(python_exe),
            "-m",
            "firefly_bot.main",
            "--root",
            str(FIREFLY_REPO),
            "--concurrency",
            "1",
            "worker-once",
        ]
        subprocess.run(
            worker_cmd,
            cwd=str(FIREFLY_REPO),
            env=env,
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
        )

        # 4. Verifica o status real no firefly_jobs.db
        conn = sqlite3.connect(str(db_path), timeout=15.0)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT id, status, output_path, error FROM jobs WHERE name = ? ORDER BY id DESC LIMIT 1",
            (job_unique_name,),
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            raise FireflySessionError(f"Job {job_unique_name} não encontrado no firefly_jobs.db após execução.")

        status = row["status"]
        output_path_str = row["output_path"]
        error_msg = row["error"]

        if status != "done" or not output_path_str:
            raise FireflySessionError(
                f"Job {job_unique_name} não concluiu no Firefly. Status='{status}', Erro='{error_msg}'"
            )

        rendered_mp4 = Path(output_path_str)
        if not rendered_mp4.exists() or rendered_mp4.stat().st_size < 500_000:
            raise FireflySessionError(
                f"Arquivo gerado pelo Firefly ausente ou menor que 500KB: {rendered_mp4}"
            )

        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(rendered_mp4, out_path)
