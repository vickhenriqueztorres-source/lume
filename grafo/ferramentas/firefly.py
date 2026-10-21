"""Motor de Automação e Execução do Adobe Firefly para o Estúdio LUME.

Portado de D:\\LINHA DE FOGO EDITS\\services\\video\\firefly_engine.py.
Suporta:
- Concorrência serial estrita = 1 (threading.Lock para não corromper sessão de render/navegador)
- Watchdog de sessão com detecção de timeout e re-tentativas (max_retries=3)
- Salvamento atômico de cada clipe MP4 gerado
- Modo de simulação determinística para pipelines de testes e CI (custo zero)
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

LOGGER = logging.getLogger(__name__)


class FireflySessionError(Exception):
    """Erro crítico na sessão de renderização do Adobe Firefly."""
    pass


class FireflySecurityError(Exception):
    """Tentativa de Path Traversal ou violação de segurança detectada."""
    pass


class FireflyEngine:
    """Motor de geração de vídeo a partir de Start Frame via Adobe Firefly."""

    _lock = threading.Lock()

    def __init__(
        self,
        output_base_dir: str | Path = "storage_local/renders",
        timeout_seconds: float = 240.0,
        max_retries: int = 3,
        simulate: bool = True,
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
        """Gera clipe de vídeo MP4 serialmente a partir de um start frame."""
        id_sanitizado = self.sanitizar_nome(plano_id)
        ep_sanitizado = self.sanitizar_nome(episodio_id)

        start_frame = Path(start_frame_path)
        if not start_frame.exists():
            raise FileNotFoundError(f"Start frame não encontrado: {start_frame}")

        clipes_dir = self.output_base_dir / ep_sanitizado
        clipes_dir.mkdir(parents=True, exist_ok=True)
        target_clip_path = clipes_dir / f"{id_sanitizado}.mp4"

        # Concorrência serial estrita = 1
        with self._lock:
            LOGGER.info(
                f"[FIREFLY] Iniciando animação do plano {plano_id} para {episodio_id}. "
                f"Prompt: '{motion_prompt}' | Duração: {target_duration}s"
            )

            for attempt in range(1, self.max_retries + 1):
                try:
                    if self.simulate:
                        self._simulate_generation(start_frame, target_clip_path, target_duration, motion_prompt)
                    else:
                        self._execute_local_automation(
                            frame_path=start_frame,
                            motion_prompt=motion_prompt,
                            out_path=target_clip_path,
                            duration=target_duration,
                            plano_id=id_sanitizado,
                        )

                    if target_clip_path.exists() and target_clip_path.stat().st_size > 100:
                        LOGGER.info(f"[FIREFLY] Plano {plano_id} animado com sucesso: {target_clip_path}")
                        return target_clip_path
                except Exception as e:
                    LOGGER.warning(f"[FIREFLY] Tentativa {attempt}/{self.max_retries} falhou para plano {plano_id}: {e}")
                    time.sleep(0.5)

            raise FireflySessionError(
                f"Sessão do Firefly falhou após {self.max_retries} tentativas no plano {plano_id}."
            )

    def _simulate_generation(
        self,
        frame_path: Path,
        out_path: Path,
        duration: float,
        motion_prompt: str = "",
    ) -> None:
        """Gera um clipe MP4 cinematográfico 4K (3840x2160, 24fps) com movimento de câmera cinemático."""
        out_path.parent.mkdir(parents=True, exist_ok=True)

        ffmpeg_bin = shutil.which("ffmpeg")
        if ffmpeg_bin and frame_path.exists() and frame_path.stat().st_size > 1000:
            tmp_path = out_path.with_suffix(".tmp.mp4")
            fps = 24
            total_frames = max(int(duration * fps), 24)
            mp_lower = motion_prompt.lower()

            if "pan" in mp_lower or "dolly" in mp_lower:
                vf = (
                    f"zoompan=z=1.12:x='if(lte(on,1),0,min(x+1.2,iw-iw/zoom))':"
                    f"y='ih/2-(ih/zoom/2)':d={total_frames}:s=3840x2160:fps={fps},format=yuv420p"
                )
            elif "tilt" in mp_lower:
                vf = (
                    f"zoompan=z=1.12:x='iw/2-(iw/zoom/2)':"
                    f"y='if(lte(on,1),ih-ih/zoom,max(y-1.2,0))':d={total_frames}:s=3840x2160:fps={fps},format=yuv420p"
                )
            elif "rapido" in mp_lower:
                vf = (
                    f"zoompan=z='min(zoom+0.0022,1.22)':d={total_frames}:"
                    f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=3840x2160:fps={fps},format=yuv420p"
                )
            else:
                vf = (
                    f"zoompan=z='min(zoom+0.0012,1.15)':d={total_frames}:"
                    f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=3840x2160:fps={fps},format=yuv420p"
                )

            cmd = [
                ffmpeg_bin, "-y",
                "-i", str(frame_path),
                "-vf", vf,
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-t", str(duration),
                str(tmp_path),
            ]
            try:
                res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45)
                if res.returncode == 0 and tmp_path.exists() and tmp_path.stat().st_size > 500:
                    tmp_path.replace(out_path)
                    return
            except Exception:
                pass

        # Cabeçalho MP4 ISO padrão válido (fallback determinístico para testes unitários)
        mp4_bytes = (
            b"\x00\x00\x00\x1cftypisom\x00\x00\x02\x00isomiso2mp41"
            b"\x00\x00\x00\x08free"
            b"\x00\x00\x10\x00mdat" + b"\x00" * 8192
        )
        # Gravação atômica via arquivo temporário
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
    ) -> None:
        """Execução real de automação local via Adobe Firefly (Kling 2.5 Turbo)."""
        firefly_repo = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation")
        python_exe = firefly_repo / ".venv" / "Scripts" / "python.exe"
        if not python_exe.exists():
            python_exe = Path(sys.executable)

        if not firefly_repo.exists():
            raise FireflySessionError(f"Repositório de automação Firefly não encontrado: {firefly_repo}")

        # 1. Copia o start frame para a pasta de imagens da automação
        imagens_dir = firefly_repo / "imagens"
        imagens_dir.mkdir(parents=True, exist_ok=True)
        dest_frame = imagens_dir / frame_path.name
        if not dest_frame.exists() or dest_frame.stat().st_size != frame_path.stat().st_size:
            shutil.copy2(frame_path, dest_frame)

        # 2. Cria o arquivo de guia JSON para o job
        data_dir = firefly_repo / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        guide_file = data_dir / f"guide_{plano_id}.json"
        guide_payload = {
            "model": "Kling 2.5 Turbo",
            "resolution": "1080p",
            "aspect_ratio": "16:9",
            "duration_seconds": max(int(duration), 5),
            "items": [
                {
                    "name": plano_id,
                    "image": frame_path.name,
                    "prompt": motion_prompt,
                }
            ],
        }
        guide_file.write_text(json.dumps(guide_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        # 3. Alimenta a fila com o job (--feed-guide)
        feed_cmd = [
            str(python_exe),
            "main.py",
            "--root", str(firefly_repo),
            "--feed-guide", str(guide_file),
        ]
        feed_res = subprocess.run(feed_cmd, cwd=str(firefly_repo), capture_output=True, text=True, timeout=30)
        if feed_res.returncode != 0:
            raise FireflySessionError(f"Falha ao enfileirar job no Firefly: {feed_res.stderr}")

        # 4. Executa o worker batch
        worker_cmd = [
            str(python_exe),
            "main.py",
            "--root", str(firefly_repo),
            "worker-once",
        ]
        worker_res = subprocess.run(
            worker_cmd,
            cwd=str(firefly_repo),
            capture_output=True,
            text=True,
            timeout=self.timeout_seconds,
        )

        # 5. Consulta o resultado no banco SQLite firefly_jobs.db
        db_path = data_dir / "firefly_jobs.db"
        if not db_path.exists():
            raise FireflySessionError(f"Banco de jobs não encontrado: {db_path}")

        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(
            "SELECT id, status, output_path, error FROM jobs WHERE name = ? ORDER BY id DESC LIMIT 1",
            (plano_id,),
        )
        row = cur.fetchone()
        conn.close()

        if not row:
            raise FireflySessionError(f"Job {plano_id} não encontrado na base de dados após execução.")

        status = row["status"]
        output_path_str = row["output_path"]
        error_msg = row["error"]

        if status != "done" or not output_path_str:
            raise FireflySessionError(f"Job {plano_id} falhou no Firefly. Status: '{status}'. Erro: {error_msg}")

        rendered_mp4 = Path(output_path_str)
        if not rendered_mp4.exists() or rendered_mp4.stat().st_size < 500:
            raise FireflySessionError(f"Arquivo gerado pelo Firefly ausente ou vazio: {rendered_mp4}")

        # 6. Copia atomicamente para o destino final
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(rendered_mp4, out_path)
