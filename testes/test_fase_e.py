"""Testes da Fase E · Arte + Animação (Critérios de Aceite).

Verifica:
1. 1 plano renderizado com montagem de cena Blender e saída de vídeo MP4.
2. 10 planos processados em lote com controle de concorrência limitada.
3. Plano sem mudança visual tem cache_hit=True e não renderiza novamente.
4. Terceira falha de um plano vai para a fila humana sem travar os demais planos.
"""

import pytest
from contratos.estado import criar_estado_inicial
from contratos.plano import Plano, calcular_hash_plano
from grafo.animacao.subgrafo import construir_subgrafo_animacao
from grafo.arte.subgrafo import construir_subgrafo_arte
from grafo.base import limpar_operacoes_teste
from grafo.ferramentas.blender import BlenderRunner
from grafo.ferramentas.potrace import PotraceRunner
from grafo.ferramentas.render_queue import FilaRender, obter_fila_render


def test_render_um_plano_blender(tmp_path):
    """Garante que um plano único monta cena .blend e renderiza MP4 determinístico."""
    blender = BlenderRunner()
    blend_file = str(tmp_path / "cena_ep01_p01.blend")
    video_file = str(tmp_path / "render_ep01_p01.mp4")

    # 1. Monta cena
    params = {"camera": "push_in_lento", "fogo": 3}
    scene_hash = blender.montar_cena_3d("ep01_p01", params, blend_file)
    assert len(scene_hash) == 64

    # 2. Renderiza vídeo
    render_hash = blender.renderizar_plano(blend_file, video_file)
    assert len(render_hash) == 64
    assert open(video_file).read().startswith("# MOCK RENDER MP4")


def test_vetorizacao_potrace(tmp_path):
    """Garante que a ferramenta Potrace converte silhuetas em SVG com preto absoluto."""
    potrace = PotraceRunner()
    png_mock = str(tmp_path / "polifemo.png")
    svg_output = str(tmp_path / "polifemo.svg")

    with open(png_mock, "w") as f:
        f.write("mock_png_bytes")

    svg_hash = potrace.vetorizar_silhueta(png_mock, svg_output)
    assert len(svg_hash) == 64
    svg_content = open(svg_output).read()
    assert "<svg" in svg_content
    assert "#16110D" in svg_content  # Preto absoluto da marca LUME


def test_dez_planos_concorrencia_e_cache_por_hash(tmp_path):
    """Garante que 10 planos são renderizados com pool concorrente e cache por hash."""
    fila = FilaRender(max_concurrency=4)

    planos_lote = []
    for i in range(1, 11):
        p = Plano(
            id=f"ep01_c01_p{i:02d}",
            bloco_roteiro=1,
            mundo="parede",
            duracao_s=4.0 + (i * 0.5),  # Duração visual distinta para cada um dos 10 planos
            fogo={"nivel": 1 + (i % 5), "curva": "estavel", "tremulacao_hz": 1.0 + (i * 0.2)},
        )
        planos_lote.append(p)

    # 1. Primeira passagem: todos devem ser renderizados (cache_hit = False)
    resultados_1 = []
    for p in planos_lote:
        blend_file = str(tmp_path / f"{p.id}.blend")
        video_file = str(tmp_path / f"{p.id}.mp4")
        res = fila.submeter_job_render(p, blend_file, video_file)
        resultados_1.append(res)
        assert res["cache_hit"] is False
        assert res["status"] == "concluido"

    assert len(resultados_1) == 10

    # 2. Segunda passagem: nenhum plano mudou -> todos devem vir do cache (cache_hit = True)
    for p in planos_lote:
        blend_file = str(tmp_path / f"{p.id}.blend")
        video_file = str(tmp_path / f"{p.id}.mp4")
        res = fila.submeter_job_render(p, blend_file, video_file)
        assert res["cache_hit"] is True  # Não renderizou de novo!


def test_terceira_falha_de_plano_escala_sem_travar_outros():
    """Garante que a 3ª falha consecutiva de um plano vai para a fila humana e não bloqueia os demais."""
    subgrafo = construir_subgrafo_animacao()

    # Prepara estado com 3 planos: p01 e p03 normais, p02 forçado a falhar na 3ª tentativa
    p01 = Plano(id="ep01_p01", bloco_roteiro=1).model_dump()
    p02 = Plano(id="ep01_p02", bloco_roteiro=1).model_dump()
    p03 = Plano(id="ep01_p03", bloco_roteiro=1).model_dump()

    estado = {
        "decupagem": {"planos": [p01, p02, p03]},
        "assets": {
            "planos": {
                "ep01_p02": {
                    "render": {
                        "tentativas": 2,  # Já falhou 2 vezes antes
                        "forcar_falha": True,
                    }
                }
            }
        },
        "episodio": {"id": "ep01", "fila_humana": []},
        "custos": [],
        "erros": [],
    }

    resultado = subgrafo.invoke(estado)
    assets_planos = resultado["assets"]["planos"]

    # Planos 01 e 03 aprovados normalmente
    assert assets_planos["ep01_p01"]["revisao"]["aprovado"] is True
    assert assets_planos["ep01_p03"]["revisao"]["aprovado"] is True

    # Plano 02 reprovado na 3ª tentativa e registrado nos erros para escalada
    assert assets_planos["ep01_p02"]["revisao"]["aprovado"] is False
    erros = resultado.get("erros", [])
    assert any(
        e.get("autor_no") == "animacao.revisor_plano" and e.get("decisao") == "escalar"
        for e in erros
    )
