"""Gera o Diagrama Mermaid do Grafo Compilado do Showrunner (Doc 05 §1).

Salva o diagrama em docs/referencias/grafo-compilado.mmd.
"""

from __future__ import annotations

import os
from grafo.showrunner.grafo import grafo_showrunner


def gerar_diagrama() -> str:
    grafo = grafo_showrunner.get_graph()
    mermaid_code = grafo.draw_mermaid()

    caminho_saida = "docs/referencias/grafo-compilado.mmd"
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8") as f:
        f.write(mermaid_code)

    print(f"Diagrama Mermaid gerado com sucesso em: {caminho_saida}")
    return mermaid_code


if __name__ == "__main__":
    gerar_diagrama()
