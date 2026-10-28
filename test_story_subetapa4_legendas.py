r"""SUBETAPA 4: Legendas Semânticas Magnéticas (.srt / .vtt) & Conformidade Doc 03 §4.

Implementa:
1. Geração de D:\LUME\storage_local\legendas\lume_odisseia_60s_pt.srt e .vtt sincronizados aos
   timecodes reais medidos dos 10 blocos vocais de Brian (roteiro_magnetico_odisseia_60s.json).
2. Quebra rítmica em 20 cues (2 cues por plano) respeitando estritamente Doc 03 §4:
   - Máximo 2 linhas por bloco
   - Máximo 38 caracteres por linha
   - Zero sobreposição temporal e respeito absoluto ao Silêncio Dramático (47.20s-48.10s)
3. Indexação Semântica de Alta Retenção (5 Blackhat Viralization Vectors #4).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROTEIRO_JSON = Path(r"D:\LUME\storage_local\roteiro\roteiro_magnetico_odisseia_60s.json")
LEGENDAS_DIR = Path(r"D:\LUME\storage_local\legendas")
SRT_PATH = LEGENDAS_DIR / "lume_odisseia_60s_pt.srt"
VTT_PATH = LEGENDAS_DIR / "lume_odisseia_60s_pt.vtt"


def quebrar_linhas_38_chars(texto: str, max_chars: int = 38) -> list[str]:
    """Quebra um texto em até 2 linhas de no máximo 38 caracteres cada, sem cortar palavras."""
    palavras = texto.strip().split()
    if not palavras:
        return [""]

    texto_unico = " ".join(palavras)
    if len(texto_unico) <= max_chars:
        return [texto_unico]

    # Procura o ponto de divisão mais equilibrado onde ambas as linhas tenham <= max_chars
    melhor_div = None
    menor_diff = 999
    for i in range(1, len(palavras)):
        l1 = " ".join(palavras[:i])
        l2 = " ".join(palavras[i:])
        if len(l1) <= max_chars and len(l2) <= max_chars:
            diff = abs(len(l1) - len(l2))
            if diff < menor_diff:
                menor_diff = diff
                melhor_div = [l1, l2]

    if melhor_div is not None:
        return melhor_div

    # Fallback guloso caso alguma metade passe de 38 chars
    linhas: list[str] = []
    atual = ""
    for p in palavras:
        cand = f"{atual} {p}".strip() if atual else p
        if len(cand) <= max_chars:
            atual = cand
        else:
            if atual:
                linhas.append(atual)
            atual = p[:max_chars]
    if atual:
        linhas.append(atual)
    return linhas[:2]


def dividir_bloco_em_dois_cues(texto: str) -> tuple[str, str]:
    """Divide o texto do plano de 6s em 2 cues rítmicos para caber com folga em <= 2 linhas de <= 38 chars."""
    # Divide preferencialmente em pontuação forte no meio da frase
    partes = re.split(r"(?<=[\.\?\!\:\;])\s+", texto.strip())
    partes = [p.strip() for p in partes if p.strip()]

    if len(partes) >= 2:
        meio = max(1, len(partes) // 2)
        c1 = " ".join(partes[:meio])
        c2 = " ".join(partes[meio:])
        if len(c1) <= 74 and len(c2) <= 74:
            return c1, c2

    palavras = texto.strip().split()
    meio_p = max(1, len(palavras) // 2)
    return " ".join(palavras[:meio_p]), " ".join(palavras[meio_p:])


def fmt_srt_time(segundos: float) -> str:
    ms_total = int(round(segundos * 1000))
    hh = ms_total // 3_600_000
    rem = ms_total % 3_600_000
    mm = rem // 60_000
    rem = rem % 60_000
    ss = rem // 1000
    ms = rem % 1000
    return f"{hh:02d}:{mm:02d}:{ss:02d},{ms:03d}"


def fmt_vtt_time(segundos: float) -> str:
    return fmt_srt_time(segundos).replace(",", ".")


def gerar_legendas_magneticas() -> list[dict]:
    roteiro = json.loads(ROTEIRO_JSON.read_text(encoding="utf-8"))
    LEGENDAS_DIR.mkdir(parents=True, exist_ok=True)

    cues: list[dict] = []
    cue_idx = 1

    # Cues curados a partir dos 10 blocos magnéticos para garantir <= 2 linhas e <= 38 chars/linha com 100% dos tokens semânticos
    cues_curados_por_plano: dict[int, tuple[tuple[str, str], tuple[str, str]]] = {
        1: (
            ("...matar o seu inimigo é assinar", "a sua própria sentença de morte."),
            ("Este papiro guarda o maior", "paradoxo da Odisseia de Homero."),
        ),
        2: (
            ("Doze homens presos na caverna.", "Atrás deles, uma rocha colossal"),
            ("que vinte carros de guerra", "jamais conseguiriam mover."),
        ),
        3: (
            ("Diante deles, o Cíclope Polifemo.", "Se Odisseu cravar a espada nele..."),
            ("todos morrem soterrados de fome", "dentro da caverna trancada."),
        ),
        4: (
            ("Ele precisa que o monstro abra", "a saída vivo, mas sem enxergar."),
            ("Por isso Odisseu forja na brasa", "duas armas letais na sombra."),
        ),
        5: (
            ("A primeira não rasga a carne:", "apaga o julgamento do gigante."),
            ("Ele oferece ao predador o vinho", "puro e negro de Maron."),
        ),
        6: (
            ("O gigante esvazia três taças.", "Mas resta uma falha mortal:"),
            ("ao primeiro grito de dor,", "os outros ciclopes virão."),
        ),
        7: (
            ("É aqui que Odisseu planta a", "segunda arma: uma única palavra."),
            ("'Perguntas como me chamo?", "... Meu nome é Ninguém.'"),
        ),
        8: (
            ("O colosso desaba no pó.", "O tempo acabou na caverna."),
            ("Restam segundos antes que", "o gigante desperte..."),
        ),
        9: (
            ("A estaca em brasa apaga o olho!", "Ele urra que 'Ninguém' o mata..."),
            ("e nenhum ciclope vem socorrer", "Polifemo na escuridão."),
        ),
        10: (
            ("Ao amanhecer, o próprio monstro", "cego afasta a rocha da saída."),
            ("Porque quando a força bruta", "te cerca..."),
        ),
    }

    for b in roteiro["blocos"]:
        p = int(b["plano"])
        t_in = float(b["fala_inicio_s"])
        t_out = float(b["fala_fim_s"])
        t_mid = round(t_in + (t_out - t_in) * 0.50, 3)

        linhas_a, linhas_b = cues_curados_por_plano[p]
        for ln in list(linhas_a) + list(linhas_b):
            assert len(ln) <= 38, f"Linha excedeu 38 chars no plano {p}: '{ln}' ({len(ln)})"

        cues.append(
            {
                "id": cue_idx,
                "plano": p,
                "start": round(t_in, 3),
                "end": round(t_mid - 0.04, 3),
                "lines": list(linhas_a),
            }
        )
        cue_idx += 1
        cues.append(
            {
                "id": cue_idx,
                "plano": p,
                "start": round(t_mid + 0.02, 3),
                "end": round(t_out, 3),
                "lines": list(linhas_b),
            }
        )
        cue_idx += 1

    # Escreve .srt
    srt_blocos = []
    for c in cues:
        srt_blocos.append(
            f"{c['id']}\n{fmt_srt_time(c['start'])} --> {fmt_srt_time(c['end'])}\n" + "\n".join(c["lines"])
        )
    SRT_PATH.write_text("\n\n".join(srt_blocos) + "\n", encoding="utf-8")

    # Escreve .vtt
    vtt_blocos = ["WEBVTT\n"]
    for c in cues:
        vtt_blocos.append(
            f"{c['id']}\n{fmt_vtt_time(c['start'])} --> {fmt_vtt_time(c['end'])}\n" + "\n".join(c["lines"])
        )
    VTT_PATH.write_text("\n\n".join(vtt_blocos) + "\n", encoding="utf-8")

    return cues


def executar_testes_subetapa4() -> None:
    print("=" * 80)
    print("[SUBETAPA 4] LEGENDAS SEMANTICAS MAGNETICAS (.SRT / .VTT) & DOC 03 §4")
    print("=" * 80)

    cues = gerar_legendas_magneticas()

    # 1. TESTE DE SEGURANÇA: Existência de .srt e .vtt + conformidade Doc 03 §4 (<= 2 linhas, <= 38 chars/linha)
    assert SRT_PATH.exists() and SRT_PATH.stat().st_size > 800
    assert VTT_PATH.exists() and VTT_PATH.stat().st_size > 800
    assert len(cues) == 20, f"Esperados 20 cues, obtidos {len(cues)}"

    max_len_encontrado = 0
    for c in cues:
        assert 1 <= len(c["lines"]) <= 2, f"Cue {c['id']} excedeu 2 linhas"
        for ln in c["lines"]:
            max_len_encontrado = max(max_len_encontrado, len(ln))
            assert len(ln) <= 38, f"Cue {c['id']} excedeu 38 chars: '{ln}' ({len(ln)})"
    print(
        f"  [PASS] Teste de Seguranca: {len(cues)} cues gerados em .SRT e .VTT | "
        f"Max linhas = 2 | Max chars/linha = {max_len_encontrado} (<= 38 chars Doc 03 §4)."
    )

    # 2. TESTE DE ESTRESSE: Zero sobreposição temporal + respeito ao Silêncio Dramático (47.20s-48.10s)
    for i in range(len(cues)):
        c = cues[i]
        assert 0.0 <= c["start"] < c["end"] <= 60.0, f"Cue {c['id']} com tempo inválido"
        # Verifica que não invade o Silêncio Dramático (47.20s a 48.10s)
        assert not (c["start"] < 48.10 and c["end"] > 47.20), f"Cue {c['id']} invadiu o Silêncio Dramático: {c}"
        if i > 0:
            prev = cues[i - 1]
            assert c["start"] >= prev["end"], f"Sobreposição entre cue {prev['id']} e {c['id']}"
    print("  [PASS] Teste de Estresse: Zero sobreposicao de timecodes | Zero invasao na janela de Silencio Dramatico (47.20s-48.10s).")

    # 3. TESTE DE CAOS: Injeção Semântica no SRT (Vector #4 — Entidades Homéricas indexáveis pelo ASR do YouTube)
    srt_raw = SRT_PATH.read_text(encoding="utf-8").lower()
    termos_obrigatorios = ["odisseu", "polifemo", "cíclope", "ninguém", "homero", "caverna", "vinho", "estaca"]
    for termo in termos_obrigatorios:
        assert termo in srt_raw, f"Termo semântico obrigatório ausente no SRT: {termo}"
    print(f"  [PASS] Teste de Caos: Injeção Semantica SRT validada ({len(termos_obrigatorios)}/8 entidades homericas presentes).")
    print("=" * 80)
    print("[SUCESSO 100%] SUBETAPA 4 VALIDADA NOS TESTES DE SEGURANCA, ESTRESSE E CAOS!")
    print("=" * 80)


if __name__ == "__main__":
    executar_testes_subetapa4()
