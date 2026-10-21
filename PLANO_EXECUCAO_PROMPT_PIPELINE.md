# Plano Cirúrgico de Execução: Pipeline de Engenharia de Prompts (Imagem & Vídeo) e Firefly

## 1. Análise Cirúrgica dos Pontos de Falha e Gaps Arquiteturais

Identificamos com precisão os 5 pontos onde o pipeline estava incompleto ou vulnerável:

1. **Lacuna Contratual (`contratos/plano.py` e `contratos/agentes.py`):**
   - O contrato `Plano` não possuía os campos `prompt_imagem` e `prompt_video` para rastreabilidade e persistência durável no estado do LangGraph.
   - Os schemas de saída tipados dos novos agentes especialistas não existiam no catálogo de agentes.

2. **Ausência do Engenheiro de Prompt de Imagem pós-Direção:**
   - O `storyboarder_node` gerava imagens diretamente de forma procedural/mecânica, sem um agente dedicado especialista na semiótica cinematográfica de LUME (paleta `#16110D`, `#E85D04`, `#FDF0D5`, iluminação de braseiro, texturas de calcário e chiaroscuro).
   - Faltava garantia de consistência visual filme-a-filme (reutilização das diretrizes dos personagens e mundo de sombras).

3. **Falta de Agente e Ferramenta de Geração de Imagem via CLI:**
   - Inexistência de um wrapper unificado para acionar a geração de imagens por linha de comando (CLI Codex / Antigravity / Motor Visual) com validação de formato PNG, dimensões 16:9 ou 2.39 e prevenção de Path Traversal.

4. **Prompt de Movimento Estático no Render Firefly (`grafo/animacao/subgrafo.py`):**
   - O nó `gerente_render` utilizava um prompt fixo: `motion_prompt = f"Movimento de camera {movimento} com teatro de sombras"`.
   - O texto dramático do `roteiro.blocos`, as marcações de cena, a tensão narrativa e a física das chamas eram completamente ignorados na animação.

5. **Acoplamento no Grafo LangGraph:**
   - O fluxo de Direção e Animação precisava amarrar formalmente os nós:
     - Em Direção: `storyboarder` -> `engenheiro_prompt_imagem` -> `gerador_imagem_cli`.
     - No Gate 2: Exibir storyboard com prompts cinematográficos e frames já validados.
     - Em Animação: `animador_plano` -> `montador_cena_3d` -> `engenheiro_prompt_video` -> `gerente_render` (Firefly).

---

## 2. Plano Geral Cirúrgico

```
   ┌────────────────────────────────────────────────────────┐
   │                DIREÇÃO & STORYBOARD                    │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │         ENGENHEIRO DE PROMPT DE IMAGEM                 │
   │  (Gera prompts cinemáticos ultra-consistentes LUME)     │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │             GERADOR DE IMAGEM VIA CLI                  │
   │   (Chama CLIs / Cria Start Frames PNG validados)       │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │         GATE 2: APROVAÇÃO HUMANA DE STORYBOARD         │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │         ENGENHEIRO DE PROMPT DE VÍDEO                  │
   │   (Analisa Roteiro + Câmera + Fogo + Dinâmica)         │
   └───────────────────────────┬────────────────────────────┘
                               │
                               ▼
   ┌────────────────────────────────────────────────────────┐
   │        MOTOR FIREFLY (GERENTE DE RENDER)               │
   │  (Start Frame + Prompt de Vídeo -> MP4 com Cache SHA)  │
   └────────────────────────────────────────────────────────┘
```

---

## 3. Subetapas Detalhadas de Implementação

### Subetapa 1: Atualização dos Contratos e Schemas Pydantic
- **Arquivos:** `contratos/plano.py`, `contratos/agentes.py`.
- **Implementação:**
  - Adicionar `prompt_imagem: Optional[str]` e `prompt_video: Optional[str]` em `Plano`.
  - Definir `PromptImagemItem`, `EngenheiroPromptImagemOutput`, `PromptVideoItem`, `EngenheiroPromptVideoOutput`.
- **Critério de Aceite:** 100% retrocompatível com instâncias existentes de `Plano`.

### Subetapa 2: Agente Especialista `Engenheiro de Prompt de Imagem`
- **Arquivo:** `grafo/direcao/engenheiro_prompt_imagem.py` e integração no nó.
- **Implementação:**
  - Agente LLM-R (`direcao.engenheiro_prompt_imagem`) com vocabulário cinematográfico de LUME:
    - Composição de sombras chinesas, proporção anamórfica 2.39 ou 16:9, lentes 35mm/50mm/85mm.
    - Iluminação em chiaroscuro: braseiro `#E85D04`, silhuetas `#16110D`, luz divina `#FDF0D5`.
    - Consistência de personagens e cenários.
- **Bateria de Testes (`testes/test_engenheiro_prompt_imagem.py`):**
  - *Unitário:* Geração de prompts ricos e conformes para cada plano do episódio.
  - *Estresse:* Processamento em lote de 20 planos sem degradação.
  - *Segurança:* Rejeição de injeção de prompt e sanitização de entradas.
  - *Caos:* Planos sem atributos de câmera/fogo recebem defaults cinemáticos seguros.

### Subetapa 3: Ferramenta e Agente `Gerador de Imagem via CLI`
- **Arquivo:** `grafo/ferramentas/gerador_imagem_cli.py`.
- **Implementação:**
  - `ImageCLIGenerator` com suporte a CLI Codex, Antigravity e StartFrameGenerator cinemático LUME.
  - Validação física de dimensões, formato PNG, integridade e armazenamento em `storage_local/frames/start_frames/`.
- **Bateria de Testes (`testes/test_gerador_imagem_cli.py`):**
  - *Unitário:* Geração de imagem PNG a partir do prompt do plano e gravação no `p["storyboard"]`.
  - *Estresse:* 10 planos gerados sem colisão de arquivo ou concorrência insegura.
  - *Segurança:* Prevenção absoluta de Path Traversal nos caminhos de arquivo.
  - *Caos:* Falha de subprocesso gerenciada com fallback determinístico sem travar o pipeline.

### Subetapa 4: Agente Especialista `Engenheiro de Prompt de Vídeo`
- **Arquivo:** `grafo/animacao/engenheiro_prompt_video.py`.
- **Implementação:**
  - Agente LLM-R (`animacao.engenheiro_prompt_video`):
    - Cruza `p["bloco_roteiro"]` com o texto correspondente em `roteiro["blocos"]`.
    - Modela prompts de movimento de vídeo para o Firefly: física de brasas e fumaça, movimento fluido de câmera, atuação da silhueta, ritmo de tensão.
- **Bateria de Testes (`testes/test_engenheiro_prompt_video.py`):**
  - *Unitário:* Geração de motion prompts específicos integrados à narrativa do roteiro.
  - *Estresse:* 15 planos com roteiro longo avaliados com tempos de resposta mínimos.
  - *Segurança:* Sanitização de strings para o motor de vídeo.
  - *Caos:* Roteiro sem bloco correspondente ativa inferência autônoma pela decupagem.

### Subetapa 5: Amarração no LangGraph e Teste de Integração Ponta a Ponta
- **Arquivos:** `grafo/direcao/subgrafo.py`, `grafo/animacao/subgrafo.py`, `grafo/showrunner/grafo.py`.
- **Implementação:**
  - Subgrafo de Direção orquestra decupagem -> elenco -> storyboarder -> engenheiro de imagem -> gerador CLI.
  - Subgrafo de Animação orquestra animador -> montador 3D -> engenheiro de vídeo -> gerente render Firefly com prompt real -> revisor -> VFX.
- **Bateria de Testes:**
  - `testes/test_pipeline_prompt_firefly.py` passando com louvor.
  - Execução da suíte completa de regressão (`pytest testes`) garantindo 100% de sucesso.
