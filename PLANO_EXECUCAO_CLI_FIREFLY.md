# Plano de Execução Cirúrgica: Integração CLI Codex/Antigravity & Motor Firefly

## 1. Análise Cirúrgica dos Pontos de Acoplamento e Erro

Identificamos com precisão cirúrgica os pontos do sistema LUME onde ocorrem acoplamentos com provedores externos de API ou dependências de ambiente faltantes:

1. **Inferência LLM (LLM-R e LLM-V):**
   - **Localização:** `grafo/ferramentas/modelos.py` e `config/modelos.yaml`.
   - **Diagnóstico:** Atualmente configurado como `fake-deterministic` para desenvolvimento, mas a arquitetura real esperava variáveis de ambiente (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) listadas em `PENDENCIAS.md` (PEND-02).
   - **Solução Cirúrgica:** Criar o adaptador `CodexAgyLLMClient` que executa inferência através do CLI local autenticado (`codex.cmd exec -m gpt-5.6-terra` ou `agy`), com suporte a schema Pydantic/JSON estruturado, eliminando a necessidade de chaves de API pagas externas.

2. **Geração e Validação de Imagens (IMG / Start Frames):**
   - **Localização:** `grafo/ferramentas/modelos.py` (categoria `IMG`), `grafo/arte/subgrafo.py` e `grafo/embalagem/subgrafo.py`.
   - **Diagnóstico:** Atualmente utilizava simulação ou dependia de provedor comercial de imagem externo.
   - **Solução Cirúrgica:** Implementar gerador e adaptador visual via CLI Codex/Antigravity e gerador de start frames compatível com o look cinematográfico de LUME (paleta `#16110D`, `#E85D04`, `#FDF0D5`, vinhetas e silhuetas).

3. **Geração de Vídeo e Renderização:**
   - **Localização:** `grafo/ferramentas/blender.py` e `grafo/animacao/subgrafo.py`.
   - **Diagnóstico:** Dependência de binário do Blender headless (`BLENDER_BIN_PATH`), ausente no host (PEND-04).
   - **Solução Cirúrgica:** Portar o `FireflyEngine` de `D:\LINHA DE FOGO EDITS\services\video\firefly_engine.py` para `grafo/ferramentas/firefly.py`, mantendo concorrência serial estrita (`_lock`), watchdog com retry, geração atômica de MP4, e integrar os comandos LangGraph de controle de start frames e animação serial Firefly (portados de `D:\LINHA DE FOGO EDITS\apps\orchestrator\sonar\nodes\animator.py` e `visual_production.py`).

4. **Integridade de Escopo (Regra Inegociável):**
   - O contrato do plano (`contratos/plano.py`), o estado do episódio (`contratos/estado.py`) e os 39 testes existentes em `testes/` **NÃO SERÃO QUEBRADOS**.

---

## 2. Plano Geral Cirúrgico

```
   ┌────────────────────────────────────────────────────────┐
   │                LUME RUNTIME (LangGraph)                │
   └───────────────────────────┬────────────────────────────┘
                               │
       ┌───────────────────────┼───────────────────────┐
       ▼                       ▼                       ▼
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  CLI Codex / │       │   Geração    │       │   Firefly    │
│ Antigravity  │       │ Start Frames │       │ Video Engine │
│ (LLM-R/LLM-V)│       │ (IMG / Look) │       │ (Linha Fogo) │
└──────┬───────┘       └──────┬───────┘       └──────┬───────┘
       │                       │                       │
       ▼                       ▼                       ▼
  Pesquisa,              Storyboards,            Animação e
   Roteiro,               Silhuetas,              Render MP4
  Decupagem,               Capas e                 dos 120
      QA                 Start Frames               Planos
```

---

## 3. Subetapas Detalhadas de Implementação

### Subetapa 1: Adaptador CLI Codex / Antigravity para LLM (LLM-R e LLM-V)
- **Arquivo a criar/modificar:** `grafo/ferramentas/cli_llm.py`, `grafo/ferramentas/modelos.py`, `config/modelos.yaml`.
- **Implementação:**
  - Classe `CodexCLIClient` com timeout, captura de JSON estruturado, suporte a schema Pydantic e modelo `gpt-5.6-terra`.
  - Fallback gracioso para simulação determinística quando o CLI não estiver acessível.
- **Bateria de Testes (`testes/test_cli_llm.py`):**
  1. *Unitário:* Geração de JSON estruturado válido com schema Pydantic via CLI.
  2. *Estresse:* 5 invocações seriais rápidas garantindo liberação de processos subprocess.
  3. *Segurança:* Sanitização rigorosa de argumentos, rejeição de injeção de comandos de shell (`&`, `|`, `;`).
  4. *Caos:* Resiliência a timeout de subprocesso e saída JSON malformada com recuperação sem travar o grafo.

### Subetapa 2: Gerador de Start Frames e Imagens (IMG) via CLI/Visual LUME
- **Arquivo a criar:** `grafo/ferramentas/start_frame.py`.
- **Implementação:**
  - Gerador de Start Frames cinematográficos para teatro de sombras e braseiro: silhuetas pretas absolutas (`#16110D`), iluminação de fogo/luz divina (`#E85D04`, `#FDF0D5`), proporção 16:9 (1920x1080) e 9:16 (1080x1920), sem texto ou artefatos.
  - Integração com `grafo/ferramentas/modelos.py` para a categoria `IMG`.
- **Bateria de Testes (`testes/test_start_frame.py`):**
  1. *Unitário:* Geração de arquivo PNG válido de Start Frame com dimensões corretas e paleta LUME.
  2. *Estresse:* Geração em lote de 10 start frames sem vazamento de descritores de arquivo.
  3. *Segurança:* Validação estrita de nomes de arquivos, prevenindo Path Traversal (`..`, caminhos absolutos forjados).
  4. *Caos:* Resiliência contra diretório de destino somente leitura ou espaço em disco restrito com erro tipado.

### Subetapa 3: Portabilidade do FireflyEngine (`services/video` -> `grafo/ferramentas`)
- **Arquivo a criar:** `grafo/ferramentas/firefly.py`.
- **Implementação:**
  - Portar `FireflyEngine` diretamente de `D:\LINHA DE FOGO EDITS\services\video\firefly_engine.py`:
    - Concorrência serial estrita (`threading.Lock`).
    - Watchdog com retries (`max_retries=3`) e timeout (`timeout_seconds=240.0`).
    - Geração atômica de MP4 ISO padrão (`ftyp isom/mp42` + bloco `mdat`).
    - Modo `simulate=True` para testes offline instantâneos sem queimar GPU ou CPU.
- **Bateria de Testes (`testes/test_firefly_engine.py`):**
  1. *Unitário:* Animação de um start frame gerando arquivo MP4 com tamanho > 100 bytes e metadados corretos.
  2. *Estresse:* Lock serial estrito: duas threads tentando animar em paralelo devem ser serializadas sem corrupção.
  3. *Segurança:* Sanitização de caminhos de clipes e validação de existência prévia do start frame.
  4. *Caos:* Tratamento gracioso quando o arquivo de start frame for deletado antes do render, disparando `FileNotFoundError` sem corromper a fila.

### Subetapa 4: Integração dos Comandos LangGraph de Start Frame e Firefly
- **Arquivos a modificar:** `grafo/animacao/subgrafo.py`, `grafo/direcao/subgrafo.py`.
- **Implementação:**
  - No subgrafo de animação: atualizar `montador_cena_3d` e `gerente_render` para orquestrar a geração de clipes via `FireflyEngine`, alimentados pelos storyboards/start frames da decupagem.
  - Manter rigorosamente o cache de render por hash visual SHA-256 (`calcular_hash_plano`).
  - Preservar a compatibilidade total com o contrato `Plano` e `EstadoEpisodio`.
- **Bateria de Testes (`testes/test_animacao_firefly.py`):**
  1. *Unitário:* Subgrafo de animação completo executando com `FireflyEngine` e gerando clipes MP4 para todos os planos.
  2. *Estresse:* 10 planos animados com cache hit verificado na reexecução.
  3. *Segurança:* Verificação de integridade dos caminhos gravados no estado (`storage_local/renders/`).
  4. *Caos:* Injeção de falha simulada no Firefly com verificação da escalada para `fila_humana` na 3ª falha.

### Subetapa 5: Validação de Regressão Geral e Episódio de Fumaça
- **Execução:**
  - Rodar `python -m pytest testes/ -v` (garantir que todos os 39 testes legados + todos os novos testes passem).
  - Rodar `python -m pytest testes/test_fumaca.py -v -s` de ponta a ponta.
  - Atualizar documentação de controle (`PROGRESSO.md`, `DECISOES.md`, `PENDENCIAS.md`).
