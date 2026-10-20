"""Cliente e Factory de Modelos por Categoria (Doc 05 §3 e Regra 8).

Categorias suportadas:
- LLM-R: Raciocínio, estruturação e escrita
- LLM-V: Multimodal com visão computacional
- IMG: Geração e inspeção de imagem
- TTS: Voz e síntese de áudio
- ASR: Transcrição fonética e verificação de áudio

Todo acesso a modelo é desacoplado de nomes de provedores ou modelos comerciais,
utilizando configuração declarativa em config/modelos.yaml e fakes determinísticos
para garantia de testes reproduzíveis e custo zero na construção (Regra 12).
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Type, TypeVar
import yaml
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

_CONFIG_MODELOS: Optional[Dict[str, Any]] = None


def carregar_config_modelos() -> Dict[str, Any]:
    global _CONFIG_MODELOS
    if _CONFIG_MODELOS is None:
        caminho = os.path.join(os.path.dirname(__file__), "..", "..", "config", "modelos.yaml")
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                _CONFIG_MODELOS = yaml.safe_load(f) or {}
        else:
            _CONFIG_MODELOS = {"categorias": {}}
    return _CONFIG_MODELOS


class ModeloFakeResposta:
    """Mock determinístico configurável para execução offline e testes."""

    def __init__(self, categoria: str):
        self.categoria = categoria

    def gerar_estruturado(
        self,
        schema: Type[T],
        prompt_sistema: str,
        entradas: Dict[str, Any],
        forcar_invalido: Optional[str] = None,
    ) -> T:
        """Gera resposta determinística aderente ao schema Pydantic solicitado."""
        nome_schema = schema.__name__

        # Suporte a casos de teste com falhas provocadas
        if forcar_invalido == "giria":
            # Roteirista gerando gíria proibida
            return schema.model_validate({
                "versao": 1,
                "blocos": [
                    {
                        "numero": 1,
                        "texto": "E aí galera, mano, tipo assim, Polifemo ficou doidão e fechou a caverna.",
                        "marcacoes_cena": ["[CENA: CONTADOR]"],
                        "fatos_referenciados": ["fato_01"],
                        "tempo_estimado_s": 25.0,
                    }
                ],
            })
        elif forcar_invalido == "fato_inventado":
            # Roteirista gerando fato sem correspondente na pesquisa
            return schema.model_validate({
                "versao": 1,
                "blocos": [
                    {
                        "numero": 1,
                        "texto": "Odisseu sacou um canhão a laser e destruiu os deuses do Olimpo.",
                        "marcacoes_cena": ["[CENA: PAREDE]"],
                        "fatos_referenciados": ["fato_inexistente_laser"],
                        "tempo_estimado_s": 30.0,
                    }
                ],
            })
        elif forcar_invalido == "gancho_longo":
            # Roteirista gerando gancho de abertura > 45s
            return schema.model_validate({
                "versao": 1,
                "blocos": [
                    {
                        "numero": 1,
                        "texto": "Uma introdução prolixa e demorada que se arrasta por muito tempo sem revelar a ameaça...",
                        "marcacoes_cena": ["[CENA: CONTADOR]"],
                        "fatos_referenciados": ["fato_01"],
                        "tempo_estimado_s": 75.0,  # Ultrapassa o teto de 45 segundos
                    }
                ],
            })

        # Respostas padrão canônicas por schema
        if nome_schema == "PesquisadorFontesOutput":
            return schema.model_validate({
                "fontes": [
                    {
                        "canto_verso": "Canto IX, 105-566",
                        "obra": "Odisseia",
                        "autor": "Homero",
                        "texto_original": "Cíclope Polifemo e a fuga sob os carneiros.",
                        "traducao_pt": "Odisseu cega o Cíclope Polifemo com a estaca aquecida no fogo.",
                        "dominio_publico": True,
                        "url_ou_referencia": "Perseus Digital Library: Hom. Od. 9.105",
                    }
                ],
                "nomes_canonicos": {"Ulisses": "Odisseu", "Ciclope": "Polifemo"},
            })

        if nome_schema == "VerificadorFatosOutput":
            return schema.model_validate({
                "fatos": [
                    {
                        "id": "fato_01",
                        "descricao": "Odisseu oferece vinho puro a Polifemo antes de atacá-lo.",
                        "fontes_confirmadas": ["Canto IX, 105-566"],
                        "variante_ou_tardia": False,
                        "grau_certeza": "canonica",
                    },
                    {
                        "id": "fato_02",
                        "descricao": "Odisseu diz chamar-se Ninguém (Outis).",
                        "fontes_confirmadas": ["Canto IX, 105-566"],
                        "variante_ou_tardia": False,
                        "grau_certeza": "canonica",
                    },
                ],
                "controversias": [],
            })

        if nome_schema == "AnalistaReferenciaOutput":
            return schema.model_validate({
                "metricas_ritmo": {"media_duracao_plano_s": 5.0, "cortes_ppm": 12.0},
                "densidade_cortes_ppm": 12.0,
                "lacunas_identificadas": ["Ausência de física real de sombras nos concorrentes"],
            })

        if nome_schema == "AnalistaDemandaOutput":
            return schema.model_validate({
                "angulos_ranqueados": [
                    {
                        "angulo": "O Erro Fatal de Polifemo: A Mente Contra a Força",
                        "volume_busca_estimado": "Alto",
                        "concorrencia": "Média",
                        "score": 9.4,
                    }
                ],
                "angulo_recomendado": "O Erro Fatal de Polifemo: A Mente Contra a Força",
            })

        if nome_schema == "ArquitetoEstruturaOutput":
            return schema.model_validate({
                "atos": [
                    {"ato": 1, "titulo": "A Caverna e o Monstro", "tempo_alvo_s": 360.0},
                    {"ato": 2, "titulo": "O Vinho e a Astúcia", "tempo_alvo_s": 420.0},
                    {"ato": 3, "titulo": "A Fuga nas Sombras", "tempo_alvo_s": 400.0},
                    {"ato": 4, "titulo": "A Maldição de Poseidon", "tempo_alvo_s": 260.0},
                ],
                "blocos": [
                    {
                        "numero": 1,
                        "ato": 1,
                        "tempo_alvo_s": 35.0,
                        "funcao_dramatica": "Gancho inicial e apresentação da ameaça",
                        "fatos_chave": ["fato_01"],
                    },
                    {
                        "numero": 2,
                        "ato": 2,
                        "tempo_alvo_s": 50.0,
                        "funcao_dramatica": "O plano da estaca e o vinho",
                        "fatos_chave": ["fato_01", "fato_02"],
                    },
                ],
                "tempo_total_previsto_s": 1440.0,
            })

        if nome_schema == "RoteiristaOutput":
            return schema.model_validate({
                "versao": 1,
                "blocos": [
                    {
                        "numero": 1,
                        "texto": "O fogo ainda conta as mesmas histórias. Na caverna escura, o gigante fecha a entrada com a rocha que nenhum homem moveria.",
                        "marcacoes_cena": ["[CENA: MUNDO_CONTADOR]", "[CENA: PAREDE_CAVERNA]"],
                        "fatos_referenciados": ["fato_01"],
                        "tempo_estimado_s": 35.0,
                    },
                    {
                        "numero": 2,
                        "texto": "Ele oferece a taça de vinho doce trazido de Ísmaro. 'Bebe, Polifemo. Pergunta meu nome? Ninguém me chama meu pai e minha mãe.'",
                        "marcacoes_cena": ["[CENA: PAREDE_TACA_FOGO]"],
                        "fatos_referenciados": ["fato_02"],
                        "tempo_estimado_s": 50.0,
                    },
                ],
            })

        raise ValueError(f"Schema sem mock configurado em ModeloFakeResposta: {nome_schema}")


def obter_cliente_modelo(categoria: str) -> ModeloFakeResposta:
    """Factory de cliente de modelo por categoria (LLM-R, LLM-V, IMG, TTS, ASR)."""
    config = carregar_config_modelos()
    cat_config = config.get("categorias", {}).get(categoria, {})
    # Por padrão, utiliza o fake determinístico
    return ModeloFakeResposta(categoria=categoria)
