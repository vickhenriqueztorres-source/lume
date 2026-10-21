"""Mapeamento Canônico de Agentes e Subcampos Permitidos (Doc 05 §2 e Agentes README §4).

Define rigorosamente a matriz de permissões de escrita de cada um dos 48 agentes.
Utilizado para validação estática e em tempo de execução para garantir que nenhum
agente escreva fora do seu departamento ou subcampo.
"""

from __future__ import annotations

from typing import Dict, List, Set

# Mapeamento estrito: Agente ID -> Lista de subcampos permitidos
# Formato: "campo.subcampo" ou "campo"
AGENTE_PARA_SUBCAMPO: Dict[str, List[str]] = {
    # Supervisor
    "showrunner": [
        "episodio.status",
        "episodio.rota",
        "episodio.orcamento",
        "episodio.fila_humana",
        "episodio.licoes_aplicadas",
    ],
    # 1 · Pesquisa
    "pesquisa.pesquisador_fontes": [
        "pesquisa.fontes",
        "pesquisa.nomes_canonicos",
    ],
    "pesquisa.verificador_fatos": [
        "pesquisa.fatos",
        "pesquisa.controversias",
    ],
    "pesquisa.analista_referencia": [
        "pesquisa.referencia",
    ],
    "pesquisa.analista_demanda": [
        "pesquisa.angulos",
    ],
    # 2 · Roteiro
    "roteiro.arquiteto_estrutura": [
        "roteiro.esqueleto",
    ],
    "roteiro.roteirista": [
        "roteiro.blocos",
        "roteiro.versoes",
    ],
    "roteiro.editor_retencao": [
        "roteiro.notas.retencao",
    ],
    "roteiro.revisor_fidelidade": [
        "roteiro.notas.fidelidade",
    ],
    "roteiro.revisor_tom": [
        "roteiro.notas.tom",
    ],
    # 3 · Direção
    "direcao.diretor_decupagem": [
        "decupagem.planos",
    ],
    "direcao.diretor_fotografia": [
        "color_script",
        "decupagem.planos",  # enriquece fogo, luz_deus, proporcao
    ],
    "direcao.supervisor_direcao_tela": [
        "decupagem.correcoes_direcao",
    ],
    "direcao.diretor_arte": [
        "elenco",
    ],
    "direcao.storyboarder": [
        "decupagem.animatic",
        "decupagem.planos",  # enriquece storyboard
    ],
    # 4 · Arte & Marionetes
    "arte.designer_silhuetas": [
        "assets.marionetes",
    ],
    "arte.vetorizador": [
        "assets.marionetes",  # atualiza svg
    ],
    "arte.rigger": [
        "assets.marionetes",  # atualiza rig
    ],
    "arte.cenografo": [
        "assets.cenarios",
    ],
    "arte.bibliotecario": [
        "assets.indice",
    ],
    # 5 · Animação & Render
    "animacao.animador_plano": [
        "assets.planos",  # cena
    ],
    "animacao.montador_cena_3d": [
        "assets.planos",  # blend
    ],
    "animacao.gerente_render": [
        "assets.planos",  # render
    ],
    "animacao.revisor_plano": [
        "assets.planos",  # revisao
    ],
    "animacao.vfx": [
        "assets.planos",  # vfx
    ],
    # 6 · Áudio
    "audio.diretor_voz": [
        "audio.roteiro_anotado",
    ],
    "audio.narrador": [
        "audio.narracao",
    ],
    "audio.sound_designer": [
        "audio.sfx",
    ],
    "audio.supervisor_musical": [
        "audio.trilha",
    ],
    "audio.mixador": [
        "audio.mix",
        "audio.lufs",
    ],
    # 7 · Montagem & Finalização
    "montagem.editor": [
        "timeline",
    ],
    "montagem.grafismo": [
        "timeline.camadas_motion",
    ],
    "montagem.finalizador": [
        "master.arquivo",
        "master.capitulos",
    ],
    "montagem.legendador": [
        "master.legendas",
    ],
    # 8 · Embalagem
    "embalagem.titulista": [
        "embalagem.titulos",
    ],
    "embalagem.designer_thumbnail": [
        "embalagem.thumbs",
    ],
    "embalagem.avaliador_feed": [
        "embalagem.ranking",
    ],
    "embalagem.redator_metadados": [
        "embalagem.metadados",
    ],
    "embalagem.cortador_shorts": [
        "embalagem.shorts",
    ],
    # 9 · QA (append na lista qa)
    "qa.qa_tecnico": [
        "qa",
    ],
    "qa.qa_continuidade": [
        "qa",
    ],
    "qa.qa_fidelidade": [
        "qa",
    ],
    "qa.qa_marca": [
        "qa",
    ],
    "qa.qa_direitos": [
        "qa",
    ],
    "qa.qa_originalidade": [
        "qa",
    ],
    # 10 · Publicação & Aprendizado
    "publicacao.publicador": [
        "episodio.publicacao",
    ],
    "publicacao.analista_desempenho": [
        "episodio.desempenho",
    ],
    "publicacao.curador_memoria": [
        "episodio.licoes_gravadas",
    ],
}

# Campos de append universais acessíveis por qualquer nó
CAMPOS_APPEND_UNIVERSAIS: Set[str] = {"custos", "erros"}

# Extensões especializadas de produção (engenharia de prompts e geração CLI)
AGENTES_EXTENSAO: Dict[str, List[str]] = {
    "direcao.engenheiro_prompt_imagem": ["decupagem.planos"],
    "direcao.gerador_imagem_cli": ["decupagem.planos"],
    "animacao.engenheiro_prompt_video": ["assets.planos", "qa", "episodio.fila_humana"],
}


def obter_departamento(agente_id: str) -> str:
    """Extrai o nome do departamento a partir do ID do agente."""
    if agente_id == "showrunner":
        return "supervisor"
    return agente_id.split(".")[0]


def validar_escrita_agente(agente_id: str, updates: Dict[str, Any]) -> bool:
    """Valida se o dicionário retornado pelo nó escreve exclusivamente nos subcampos permitidos."""
    if agente_id in AGENTES_EXTENSAO:
        subcampos_permitidos = AGENTES_EXTENSAO[agente_id]
    elif agente_id in AGENTE_PARA_SUBCAMPO:
        subcampos_permitidos = AGENTE_PARA_SUBCAMPO[agente_id]
    else:
        raise ValueError(f"Agente desconhecido: {agente_id}")

    for key, value in updates.items():
        if key in CAMPOS_APPEND_UNIVERSAIS:
            continue

        if key in subcampos_permitidos:
            continue

        # Verifica subcampos aninhados
        prefixo_encontrado = False
        for permitido in subcampos_permitidos:
            if permitido.startswith(f"{key}."):
                prefixo_encontrado = True
                break
            if permitido == key:
                prefixo_encontrado = True
                break

        if not prefixo_encontrado:
            return False

    return True
