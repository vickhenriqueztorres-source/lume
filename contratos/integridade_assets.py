"""Blindagem Criptográfica Anti-Reuso e Isolamento Estrito de Ativos por Episódio (Subetapa 1).

Garante na raiz do projeto d:\\LUME:
1. Nenhuma imagem (Start Frame) ou vídeo (Take MP4) de episódios anteriores pode ser reutilizado.
2. Nenhum plano dentro do mesmo episódio pode reutilizar a imagem ou vídeo de outro plano.
3. Todo o acervo existente em storage_local/frames, storage_local/renders, storage_local/takes e
   firefly-automation/imagens é catalogado por SHA-256 como 'LEGACY_LOCKED'.
4. Cada novo episódio opera exclusivamente dentro de storage_local/episodios/<episodio_id>/.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

LUME_ROOT_DIR = Path(r"D:\LUME")
STORAGE_LOCAL_DIR = LUME_ROOT_DIR / "storage_local"
EPISODIOS_ISOLADOS_DIR = STORAGE_LOCAL_DIR / "episodios"
REGISTRY_DB_PATH = LUME_ROOT_DIR / "data" / "asset_registry.db"
FIREFLY_AUTOMATION_DIR = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation")


class AssetReuseViolationError(RuntimeError):
    """Exceção fatal disparada quando há tentativa de reutilizar imagem ou vídeo existente."""
    pass


class AssetSimulationViolationError(RuntimeError):
    """Exceção fatal disparada quando um frame ou vídeo é detectado como sintético/simulado."""
    pass


class ParidadeBlocoPlanoViolationError(RuntimeError):
    """Exceção fatal disparada quando a regra '1 Bloco = 1 Start Frame = 1 Vídeo Firefly' é violada."""
    pass


TETO_DURACAO_PLANO_INDIVIDUAL_S = 15.0


def calcular_sha256_arquivo(caminho: Path | str) -> str:
    """Calcula o hash SHA-256 completo de um arquivo em disco."""
    p = Path(caminho)
    if not p.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado para cálculo SHA-256: {p}")
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def obter_conexao_registry(db_path: Optional[Path] = None) -> sqlite3.Connection:
    target = db_path or REGISTRY_DB_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(target), timeout=15.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS asset_registry (
            sha256 TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            episodio_id TEXT NOT NULL,
            plano_id TEXT NOT NULL,
            caminho_original TEXT NOT NULL,
            tamanho_bytes INTEGER NOT NULL,
            criado_em TEXT NOT NULL
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_asset_ep_plano ON asset_registry(episodio_id, plano_id, tipo)"
    )
    return conn


def inicializar_e_indexar_acervo_legado(db_path: Optional[Path] = None) -> Dict[str, int]:
    """Varre todas as pastas legadas e bloqueia seus hashes SHA-256 contra reuso futuro."""
    conn = obter_conexao_registry(db_path)
    pastas_legadas = [
        (STORAGE_LOCAL_DIR / "frames", "start_frame"),
        (STORAGE_LOCAL_DIR / "renders", "firefly_video"),
        (STORAGE_LOCAL_DIR / "takes", "firefly_video"),
        (STORAGE_LOCAL_DIR / "master", "master_video"),
        (FIREFLY_AUTOMATION_DIR / "imagens", "start_frame"),
    ]

    total_bloqueados = 0
    novos_bloqueados = 0
    now_iso = datetime.now().isoformat()

    with conn:
        for pasta, tipo_default in pastas_legadas:
            if not pasta.exists():
                continue
            for arq in sorted(pasta.rglob("*")):
                if not arq.is_file():
                    continue
                if arq.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov"):
                    continue
                try:
                    sz = arq.stat().st_size
                    if sz < 100:
                        continue
                    sha = calcular_sha256_arquivo(arq)
                    row = conn.execute(
                        "SELECT episodio_id FROM asset_registry WHERE sha256 = ?",
                        (sha,),
                    ).fetchone()
                    if row is None:
                        conn.execute(
                            """
                            INSERT INTO asset_registry (
                                sha256, tipo, episodio_id, plano_id, caminho_original, tamanho_bytes, criado_em
                            ) VALUES (?, ?, 'LEGACY_LOCKED', ?, ?, ?, ?)
                            """,
                            (sha, tipo_default, arq.stem, str(arq.resolve()), sz, now_iso),
                        )
                        novos_bloqueados += 1
                    total_bloqueados += 1
                except Exception:
                    continue

    total_db = conn.execute("SELECT COUNT(*) FROM asset_registry WHERE episodio_id = 'LEGACY_LOCKED'").fetchone()[0]
    conn.close()
    return {
        "arquivos_varridos": total_bloqueados,
        "novos_hashes_bloqueados": novos_bloqueados,
        "total_legacy_locked_db": total_db,
    }


def criar_diretorios_episodio_isolado(episodio_id: str) -> Dict[str, Path]:
    """Cria a árvore de diretórios 100% isolada para um novo episódio."""
    if not episodio_id or ".." in episodio_id or "/" in episodio_id or "\\" in episodio_id:
        raise ValueError(f"episodio_id inválido: '{episodio_id}'")

    ep_root = EPISODIOS_ISOLADOS_DIR / episodio_id
    dirs = {
        "root": ep_root,
        "roteiro": ep_root / "roteiro",
        "start_frames": ep_root / "start_frames",
        "renders_firefly": ep_root / "renders_firefly",
        "audio": ep_root / "audio",
        "blocos_voz": ep_root / "audio" / "blocos_voz",
        "legendas": ep_root / "legendas",
        "master": ep_root / "master",
    }
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs


def validar_e_registrar_asset_inedito(
    caminho: Path | str,
    episodio_id: str,
    plano_id: str,
    tipo: str,
    db_path: Optional[Path] = None,
    permitir_mesmo_plano_idempotente: bool = True,
) -> str:
    """Valida que a imagem ou vídeo é 100% inédito (não pertence ao acervo legado nem a outro episódio/plano)."""
    p = Path(caminho).resolve()
    if not p.is_file():
        raise FileNotFoundError(f"Asset ausente para validação: {p}")

    # Proíbe que o arquivo venha de pastas compartilhadas legadas em modo de produção
    str_p = str(p).lower()
    pastas_proibidas = [
        "ep_lume_45s_odisseia",
        "ep_lume_49s_odisseia",
        "ep_lume_60s_odisseia",
        "ep_lume_60s_odisseia_2d",
        "start_frames_2d",
    ]
    for proibida in pastas_proibidas:
        if proibida in str_p and episodio_id.lower() != proibida:
            raise AssetReuseViolationError(
                f"[VIOLAÇÃO ZERO-REUSO] O plano '{plano_id}' do episódio '{episodio_id}' tentou apontar para "
                f"pasta de episódio antigo: {p}"
            )

    sz = p.stat().st_size
    if tipo == "start_frame":
        if sz < 15_000:
            raise AssetSimulationViolationError(
                f"[VIOLAÇÃO DE INTEGRIDADE] Start Frame muito pequeno ou sintético ({sz} bytes): {p}"
            )
        with open(p, "rb") as f:
            head = f.read(8)
        if head != b"\x89PNG\r\n\x1a\n":
            raise AssetSimulationViolationError(f"Start Frame não possui assinatura PNG real: {p}")
    elif tipo == "firefly_video":
        if sz < 50_000:
            raise AssetSimulationViolationError(
                f"[VIOLAÇÃO DE INTEGRIDADE] Vídeo MP4 muito pequeno ou simulado ({sz} bytes): {p}"
            )

    sha = calcular_sha256_arquivo(p)
    conn = obter_conexao_registry(db_path)
    try:
        row = conn.execute(
            "SELECT episodio_id, plano_id, tipo, caminho_original FROM asset_registry WHERE sha256 = ?",
            (sha,),
        ).fetchone()

        if row is not None:
            reg_ep, reg_plano, reg_tipo, reg_path = row
            if reg_ep == "LEGACY_LOCKED":
                raise AssetReuseViolationError(
                    f"[VIOLAÇÃO ZERO-REUSO] Hash SHA-256 ({sha[:16]}...) bloqueado! "
                    f"O arquivo '{p.name}' é idêntico ao ativo legado '{reg_path}'."
                )
            if reg_ep != episodio_id:
                raise AssetReuseViolationError(
                    f"[VIOLAÇÃO ZERO-REUSO] Hash SHA-256 ({sha[:16]}...) já utilizado no episódio '{reg_ep}' "
                    f"(plano '{reg_plano}'). Proibido reutilizar em '{episodio_id}'!"
                )
            if reg_plano != plano_id or not permitir_mesmo_plano_idempotente:
                raise AssetReuseViolationError(
                    f"[VIOLAÇÃO ZERO-REUSO INTERNO] Hash SHA-256 ({sha[:16]}...) duplicado dentro do mesmo episódio "
                    f"'{episodio_id}': plano '{plano_id}' tentou reutilizar o ativo do plano '{reg_plano}'!"
                )
            return sha

        with conn:
            conn.execute(
                """
                INSERT INTO asset_registry (
                    sha256, tipo, episodio_id, plano_id, caminho_original, tamanho_bytes, criado_em
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (sha, tipo, episodio_id, plano_id, str(p), sz, datetime.now().isoformat()),
            )
        return sha
    finally:
        conn.close()


def validar_paridade_1_para_1_blocos_planos(
    blocos: List[Dict],
    planos: List[Dict],
    episodio_id: str = "ep_producao",
    teto_duracao_s: float = TETO_DURACAO_PLANO_INDIVIDUAL_S,
) -> bool:
    """Garante a regra raiz: 1 Bloco de Roteiro = 1 Plano Visual = 1 Start Frame IA = 1 Vídeo Firefly.

    Proíbe agrupar múltiplos blocos num único capítulo visual (ex: 50 blocos -> 12 planos)
    e proíbe qualquer plano com duração superior a `teto_duracao_s` (15.0s).
    """
    if not blocos:
        raise ParidadeBlocoPlanoViolationError(
            f"[VIOLAÇÃO 1:1] O episódio '{episodio_id}' não possui blocos de roteiro para decupagem."
        )
    if not planos:
        raise ParidadeBlocoPlanoViolationError(
            f"[VIOLAÇÃO 1:1] O episódio '{episodio_id}' possui {len(blocos)} blocos, mas 0 planos decupados."
        )
    if len(planos) != len(blocos):
        raise ParidadeBlocoPlanoViolationError(
            f"[VIOLAÇÃO 1:1 BLOQUEADA] O roteiro de '{episodio_id}' possui {len(blocos)} blocos, mas a decupagem "
            f"possui {len(planos)} planos! É proibido agrupar múltiplos blocos na mesma cena visual. "
            f"Cada bloco DEVE ter exatamente 1 Start Frame IA e 1 Vídeo Firefly ({len(blocos)} == {len(blocos)})."
        )

    ids_vistos = set()
    for idx, (bloco, plano) in enumerate(zip(blocos, planos), start=1):
        pid = str(plano.get("id", "")).strip()
        if not pid:
            raise ParidadeBlocoPlanoViolationError(
                f"[VIOLAÇÃO 1:1] Plano no índice {idx} de '{episodio_id}' não possui 'id'."
            )
        if pid in ids_vistos:
            raise ParidadeBlocoPlanoViolationError(
                f"[VIOLAÇÃO 1:1] ID de plano duplicado '{pid}' no episódio '{episodio_id}'."
            )
        ids_vistos.add(pid)

        # Verifica duração individual do plano
        if "janela_s" in plano and isinstance(plano["janela_s"], (list, tuple)) and len(plano["janela_s"]) == 2:
            dur = float(plano["janela_s"][1]) - float(plano["janela_s"][0])
        else:
            dur = float(plano.get("duracao_s", bloco.get("tempo_estimado_s", 10.2)))

        if dur <= 0.0 or dur > teto_duracao_s:
            raise ParidadeBlocoPlanoViolationError(
                f"[VIOLAÇÃO 1:1 DURAÇÃO] O plano '{pid}' (bloco {idx}) de '{episodio_id}' tem duração de {dur:.2f}s "
                f"(máximo permitido por bloco: {teto_duracao_s:.1f}s). Proibido esticar 1 vídeo Firefly para vários blocos!"
            )

        # Se ambos tiverem janela_s, exige sincronia exata entre bloco e plano
        if "janela_s" in bloco and "janela_s" in plano:
            b_ini, b_fim = float(bloco["janela_s"][0]), float(bloco["janela_s"][1])
            p_ini, p_fim = float(plano["janela_s"][0]), float(plano["janela_s"][1])
            if abs(b_ini - p_ini) > 0.05 or abs(b_fim - p_fim) > 0.05:
                raise ParidadeBlocoPlanoViolationError(
                    f"[VIOLAÇÃO 1:1 JANELA] Descompasso temporal no bloco {idx} ('{pid}'): "
                    f"bloco=[{b_ini:.2f}s, {b_fim:.2f}s] vs plano=[{p_ini:.2f}s, {p_fim:.2f}s]."
                )

    return True


def auditar_completude_1para1_episodio(episodio_id: str, total_blocos: int) -> Dict[str, List[str]]:
    """Audita fisicamente se o diretório isolado do episódio possui N Start Frames inéditos e N Vídeos Firefly inéditos."""
    if total_blocos <= 0:
        raise ParidadeBlocoPlanoViolationError("total_blocos deve ser > 0.")

    dirs = criar_diretorios_episodio_isolado(episodio_id)
    sf_dir = dirs["start_frames"]
    rf_dir = dirs["renders_firefly"]

    sfs_validados: List[str] = []
    videos_validados: List[str] = []

    for idx in range(1, total_blocos + 1):
        pid = f"p{idx:02d}"
        sf_path = sf_dir / f"{pid}.png"
        mp4_path = rf_dir / f"{pid}.mp4"

        if not sf_path.is_file():
            raise ParidadeBlocoPlanoViolationError(
                f"[START FRAME 1:1 AUSENTE] Bloco {idx:02d}/{total_blocos} de '{episodio_id}' não possui '{sf_path}'."
            )
        if not mp4_path.is_file():
            raise ParidadeBlocoPlanoViolationError(
                f"[VÍDEO FIREFLY 1:1 AUSENTE] Bloco {idx:02d}/{total_blocos} de '{episodio_id}' não possui '{mp4_path}'."
            )

        sha_sf = validar_e_registrar_asset_inedito(sf_path, episodio_id, pid, "start_frame")
        sha_mp4 = validar_e_registrar_asset_inedito(mp4_path, episodio_id, pid, "firefly_video")
        sfs_validados.append(sha_sf)
        videos_validados.append(sha_mp4)

    return {
        "start_frames_sha256": sfs_validados,
        "firefly_videos_sha256": videos_validados,
    }
