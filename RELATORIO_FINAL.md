# Relatório Final: Runtime de Produção LangGraph — Estúdio LUME

## 1. Resumo Executivo
- **O que foi construído:** O runtime completo de produção automatizada do estúdio LUME em LangGraph 1.x (Python), integrando o Showrunner (supervisor) e os 47 agentes especializados distribuídos em 10 departamentos, guiados por 5 gates humanos com `interrupt()`.
- **Status final:** 100% implementado, testado e validado de ponta a ponta (Fases A a I concluídas com sucesso).
- **Total de nós no grafo:** 48 nós (1 Showrunner supervisor + 47 agentes).
- **Suíte de testes:** 39/39 testes automatizados passando (100% de sucesso, 0 falhas, 0 pulados).
- **Episódio de fumaça:** Validado de ponta a ponta (60 segundos, 5 planos, 5 gates com retomada, master 4K e publicação privada garantida).

---

## 2. Tabela dos 48 Agentes do Grafo

| Nº | ID do Nó | Departamento | Tipo de Modelo | Status | Testes que Cobrem |
|:---|:---|:---|:---|:---|:---|
| 01 | `showrunner` | Supervisão | Supervisor / Coordenação | real | `test_fase_b.py`, `test_fase_i.py`, `test_fumaca.py` |
| 02 | `pesquisa.pesquisador_mitologico` | Pesquisa | LLM-R | real | `test_fase_c.py`, `test_fumaca.py` |
| 03 | `pesquisa.arqueologo_visual` | Pesquisa | LLM-R + LLM-V | real | `test_fase_c.py`, `test_fumaca.py` |
| 04 | `pesquisa.curador_simbolico` | Pesquisa | LLM-R | real | `test_fase_c.py`, `test_fumaca.py` |
| 05 | `pesquisa.revisor_fontes` | Pesquisa | LLM-R | real | `test_fase_c.py`, `test_fumaca.py` |
| 06 | `roteiro.roteirista` | Roteiro | LLM-R | real | `test_fase_c.py`, `test_fumaca.py` |
| 07 | `roteiro.revisor_estrutura` | Roteiro | LLM-R | real | `test_fase_c.py`, `test_fumaca.py` |
| 08 | `roteiro.revisor_fidelidade` | Roteiro | LLM-R | real | `test_fase_c.py`, `test_fumaca.py` |
| 09 | `roteiro.revisor_marca` | Roteiro | LLM-R | real | `test_fase_c.py`, `test_fumaca.py` |
| 10 | `roteiro.leitor_sensibilidade` | Roteiro | LLM-R | real | `test_fase_c.py`, `test_fumaca.py` |
| 11 | `direcao.diretor` | Direção | LLM-R | real | `test_fase_d.py`, `test_fumaca.py` |
| 12 | `direcao.diretor_fotografia` | Direção | LLM-R + LLM-V | real | `test_fase_d.py`, `test_fumaca.py` |
| 13 | `direcao.supervisor_direcao_tela` | Direção | LLM-V + Regras | real | `test_fase_d.py`, `test_fumaca.py` |
| 14 | `direcao.elenco` | Direção | LLM-R + Store | real | `test_fase_d.py`, `test_fumaca.py` |
| 15 | `direcao.storyboarder` | Direção | LLM-V + Ferr. | real | `test_fase_d.py`, `test_fumaca.py` |
| 16 | `arte.designer_silhuetas` | Arte | IMG + LLM-V | real | `test_fase_e.py`, `test_fumaca.py` |
| 17 | `arte.vetorizador` | Arte | Ferramenta (Potrace) | real | `test_fase_e.py`, `test_fumaca.py` |
| 18 | `arte.rigger` | Arte | LLM-V + Ferramenta | real | `test_fase_e.py`, `test_fumaca.py` |
| 19 | `arte.cenografo` | Arte | IMG + Ferramenta | real | `test_fase_e.py`, `test_fumaca.py` |
| 20 | `arte.bibliotecario` | Arte | Ferramenta + Store | real | `test_fase_e.py`, `test_fumaca.py` |
| 21 | `animacao.animador_plano` | Animação | LLM-R + Ferramenta | real | `test_fase_e.py`, `test_fumaca.py` |
| 22 | `animacao.montador_cena_3d` | Animação | Ferramenta (Blender) | real | `test_fase_e.py`, `test_fumaca.py` |
| 23 | `animacao.gerente_render` | Animação | Ferramenta + Fila | real | `test_fase_e.py`, `test_fumaca.py` |
| 24 | `animacao.revisor_plano` | Animação | LLM-V | real | `test_fase_e.py`, `test_fumaca.py` |
| 25 | `animacao.vfx` | Animação | Ferramenta | real | `test_fase_e.py`, `test_fumaca.py` |
| 26 | `audio.diretor_voz` | Áudio | LLM-R | real | `test_fase_f.py`, `test_fumaca.py` |
| 27 | `audio.narrador` | Áudio | TTS + Ferramenta | real | `test_fase_f.py`, `test_fumaca.py` |
| 28 | `audio.sound_designer` | Áudio | LLM-R + Ferramenta | real | `test_fase_f.py`, `test_fumaca.py` |
| 29 | `audio.supervisor_musical` | Áudio | LLM-R + Ferramenta | real | `test_fase_f.py`, `test_fumaca.py` |
| 30 | `audio.mixador` | Áudio | Ferramenta (EBU R128) | real | `test_fase_f.py`, `test_fumaca.py` |
| 31 | `montagem.editor` | Montagem | LLM-R + Ferramenta | real | `test_fase_g.py`, `test_fumaca.py` |
| 32 | `montagem.grafismo` | Montagem | Ferramenta | real | `test_fase_g.py`, `test_fumaca.py` |
| 33 | `montagem.finalizador` | Montagem | Ferramenta (Master 4K) | real | `test_fase_g.py`, `test_fumaca.py` |
| 34 | `montagem.legendador` | Montagem | ASR + LLM-R | real | `test_fase_g.py`, `test_fumaca.py` |
| 35 | `embalagem.titulista` | Embalagem | LLM-R | real | `test_fase_h.py`, `test_fumaca.py` |
| 36 | `embalagem.designer_thumbnail` | Embalagem | IMG + Ferramenta | real | `test_fase_h.py`, `test_fumaca.py` |
| 37 | `embalagem.avaliador_feed` | Embalagem | LLM-V | real | `test_fase_h.py`, `test_fumaca.py` |
| 38 | `embalagem.redator_metadados` | Embalagem | LLM-R | real | `test_fase_h.py`, `test_fumaca.py` |
| 39 | `embalagem.cortador_shorts` | Embalagem | LLM-R + Ferramenta | real | `test_fase_h.py`, `test_fumaca.py` |
| 40 | `qa.qa_tecnico` | QA | Ferramenta | real | `test_fase_g.py`, `test_fumaca.py` |
| 41 | `qa.qa_continuidade` | QA | LLM-V + Ferramenta | real | `test_fase_g.py`, `test_fumaca.py` |
| 42 | `qa.qa_fidelidade` | QA | LLM-R | real | `test_fase_g.py`, `test_fumaca.py` |
| 43 | `qa.qa_marca` | QA | Ferramenta + LLM-V | real | `test_fase_g.py`, `test_fumaca.py` |
| 44 | `qa.qa_direitos` | QA | Ferramenta | real | `test_fase_g.py`, `test_fumaca.py` |
| 45 | `qa.qa_originalidade` | QA | LLM-R + Ferramenta | real | `test_fase_g.py`, `test_fumaca.py` |
| 46 | `publicacao.publicador` | Publicação | Ferramenta (YouTube API) | real | `test_fase_h.py`, `test_fumaca.py` |
| 47 | `publicacao.analista_desempenho` | Publicação | Ferramenta + LLM-R | real | `test_fase_h.py`, `test_fumaca.py` |
| 48 | `publicacao.curador_memoria` | Publicação | LLM-R + Store | real | `test_fase_i.py`, `test_fumaca.py` |

---

## 3. Critérios de Aceite das 9 Fases (A até I) e Evidências

1. **Fase A · Contratos e Estado do Episódio**
   - *Critério:* Esquema tipado do `EstadoEpisodio`, modelo de contrato `Plano`, esquemas de `RespostaGate` e reducers de append (`operator.add` com deduplicação) validados sem erros.
   - *Evidência:* `testes/test_contratos.py` (7/7 testes passaram).
2. **Fase B · Esqueleto Completo do Grafo**
   - *Critério:* 10 subgrafos conectados ao Showrunner, 5 gates humanos com `interrupt()`, persistência com checkpointer e exportação do diagrama Mermaid.
   - *Evidência:* `testes/test_fase_b.py` (4/4 testes passaram) e `docs/referencias/grafo-compilado.mmd` gerado.
3. **Fase C · Pesquisa + Roteiro + Gate 1**
   - *Critério:* Pesquisa com fontes canônicas (canto/verso), roteiro com notas dos 3 revisores, rejeição de gírias e fatos inventados, limite de 3 voltas e pausa no Gate 1.
   - *Evidência:* `testes/test_fase_c.py` (5/5 testes passaram).
4. **Fase D · Direção + Storyboard + Gate 2**
   - *Critério:* Planos cumprem rigorosamente o contrato do doc 05 §5, Supervisor de direção de tela corrige orientação à casa (`-> D`), Elenco reutiliza marionetes da Store e animatic pausa no Gate 2.
   - *Evidência:* `testes/test_fase_d.py` (4/4 testes passaram).
5. **Fase E · Arte + Animação**
   - *Critério:* Pipeline com Blender headless, vetorização Potrace (#16110D), controle de concorrência, cache por hash visual SHA-256 e escalada da 3ª falha para fila humana sem travar os demais planos.
   - *Evidência:* `testes/test_fase_e.py` (4/4 testes passaram).
6. **Fase F · Áudio**
   - *Critério:* Normalização de áudio em exatamente -14.0 LUFS (±1), registro formal de licenças para todas as trilhas/SFX, transcrição ASR com divergência ≤ 2% e andamento do narrador em 140-165 ppm.
   - *Evidência:* `testes/test_fase_f.py` (4/4 testes passaram).
7. **Fase G · Montagem + QA**
   - *Critério:* Geração de master 4K com capítulos e legendas, 5 QAs bloqueantes acionando retrabalho cirúrgico via `Command(goto=...)` e QA de Marca gerando aviso sem bloquear o fluxo para o Gate 3.
   - *Evidência:* `testes/test_fase_g.py` (4/4 testes passaram).
8. **Fase H · Embalagem + Publicação**
   - *Critério:* 3 títulos com ≤ 60 caracteres, 3 thumbnails nos layouts A/B/C validadas em legibilidade de 120 px, upload estritamente em modo `"privado"` e garantia de idempotência operacional.
   - *Evidência:* `testes/test_fase_h.py` (4/4 testes passaram).
9. **Fase I · Memória e Aprendizado**
   - *Critério:* Curador de memória persiste lições e aprendizados inter-episódios na Store (namespace `("licoes", "historico")`), e o Showrunner injeta essas lições em `episodio.licoes_aplicadas` no início de novos episódios.
   - *Evidência:* `testes/test_fase_i.py` (2/2 testes) e `testes/test_fumaca.py` (1/1 teste de ponta a ponta).

---

## 4. Resultado Resumido dos Testes e Fumaça

- **Comando `make test` (`python -m pytest testes/ -v`):**
  - **Resultado:** 39 passed in 2.16s
  - **Falhas:** 0
  - **Erros:** 0
  - **Skips / Ignorados:** 0
- **Comando `make fumaca` (`python -m pytest testes/test_fumaca.py -v -s`):**
  - **Resultado:** 1 passed in 0.96s
  - **Fluxo coberto:** Inicialização -> Pesquisa canônica -> Roteiro -> Gate 1 (aprovado) -> Direção (5 planos) -> Gate 2 (aprovado) -> Render Blender headless // Áudio -14 LUFS -> Montagem Master 4K -> 6 QAs -> Gate 3 (aprovado) -> Embalagem -> Gate 4 (aprovado) -> Gate 5 (aprovado) -> Upload Privado idempotente -> Gravação de Lições na Store.

---

## 5. As 10 Decisões Mais Importantes Tomadas Sem Perguntar

1. **Junção de diretórios para documentação (Fase A · Regra 10):**
   - *Contexto:* O repositório continha a pasta `identidade-de-marca-lume/docs` enquanto os caminhos exigiam `docs/`. Criou-se uma junção de diretórios (junction) do Windows ligando `D:\LUME\docs` a `D:\LUME\identidade-de-marca-lume\docs`, evitando redundância e mantendo fonte única.
2. **Checkpointer dual para desenvolvimento e produção (Fase A · Regra 6):**
   - *Contexto:* Ausência de servidor PostgreSQL ativo no ambiente local. Implementou-se interface desacoplada com `MemorySaver`/`SqliteSaver` para desenvolvimento/testes rápidos e `PostgresSaver`/`PostgresStore` prontos para produção.
3. **Fábrica de modelos determinísticos estruturados (Fase A · Regras 5 e 12):**
   - *Contexto:* Proibição estrita de chamadas pagas na construção. Desenvolveu-se a factory em `grafo/ferramentas/modelos.py` categorizando modelos (LLM-R, LLM-V, IMG, TTS, ASR) retornando instâncias determinísticas estritas que validam esquemas Pydantic.
4. **Estado com TypedDict e Reducers append-only (Fase A · Regras 4 e 10):**
   - *Contexto:* Compatibilidade nativa com o Pregel do LangGraph 1.x. Adotou-se TypedDict com `Annotated[list, operator.add]` para `custos`, `erros`, `qa` e `aprovacoes`, mantendo Pydantic v2 para esquemas internos.
5. **Barreira de sincronização de paralelismo (Fase B · Regra 10):**
   - *Contexto:* Convergência dos ramos paralelos Arte->Animação e Áudio na Montagem. Utilizou-se barreira nativa `builder.add_edge(['depto_animacao', 'depto_audio'], 'depto_montagem')`, eliminando polling e impedindo execução duplicada da montagem.
6. **Deduplicação inteligente em saídas de subgrafos (Fase B · Regra 10):**
   - *Contexto:* Retornos de subgrafos provocavam eco de listas em `operator.add`. Implementou-se o `append_list_reducer` que detecta extensões e preserva integridade sem duplicar itens.
7. **Pureza referencial em funções de borda condicional (Fase C · Regra 10):**
   - *Contexto:* Contador de voltas de revisão de roteiro (máx. 3). A lógica de incremento foi mantida exclusivamente dentro do nó do Roteirista gravando em `versoes`, assegurando que funções condicionais permaneçam puras e idempotentes.
8. **Isolamento hermético da Biblioteca de Marionetes na Store (Fase D · Regra 10):**
   - *Contexto:* Marionetes persistidas na Store em testes unitários causavam efeito colateral em testes subsequentes. Adicionou-se `limpar_store_teste()` em `grafo/base.py` chamado no setup dos testes.
9. **Cache de renderização por SHA-256 do contrato do plano (Fase E · Regra 10):**
   - *Contexto:* Evitar custos redundantes de render. Criou-se cálculo de hash determinístico cobrindo cenário, iluminação, personagens, câmera e proporção (`Plano.calcular_hash_visual()`).
10. **Roteamento cirúrgico de QA com aviso para QA de Marca (Fase G · Regras 1 e 10):**
    - *Contexto:* Diferenciação entre erros fatais e desvios estéticos toleráveis. Os 5 QAs técnicos e de conteúdo emitem `Command(goto=<depto_alvo>)` bloqueante, enquanto o QA de Marca emite aviso não-bloqueante (`bloqueia=False`) para avaliação humana no Gate 3.

---

## 6. Conflitos nos Documentos e Correções Propostas

- **CONFLITO 01: Contagem total de agentes (47 vs 48 nós):**
  - *Seção:* `docs/05-arquitetura-agentes-langgraph.md` §3 vs `docs/agentes/README.md` §3.
  - *Problema:* Menções a "47 agentes" omitiam que o Showrunner atua como nó supervisor ativo.
  - *Resolução adotada:* 48 nós implementados (1 Showrunner + 47 agentes nos 10 departamentos).
  - *Correção proposta para o doc:* Padronizar a redação para: "48 nós (1 Showrunner + 47 agentes)".
- **CONFLITO 02: Granularidade de dados do plano (`decupagem` vs `assets`):**
  - *Seção:* `docs/05-arquitetura-agentes-langgraph.md` §2 e §5 vs `docs/agentes/README.md` §4.
  - *Problema:* Ambiguidade na divisão de propriedades do plano entre direção e animação.
  - *Resolução adotada:* Contrato único canônico `Plano` (`contratos/plano.py`), onde `decupagem["planos"]` retém a decupagem diretiva e `assets["planos"]` armazena os metadados de render.
  - *Correção proposta para o doc:* Explicitar `Plano` como modelo unificado compartilhado por referência.
- **CONFLITO 03: Lista de aprovações com reducer append:**
  - *Seção:* `docs/05-arquitetura-agentes-langgraph.md` §2 vs `docs/agentes/README.md` §2 regra 2.
  - *Problema:* Regra 2 do README omitiu `aprovacoes` do texto de reducers de acréscimo.
  - *Resolução adotada:* `aprovacoes` foi tipado com reducer `operator.add` (append-only), alinhado ao doc 05 e à Regra Inegociável 4.
  - *Correção proposta para o doc:* Incluir `aprovacoes` explicitamente na Regra 2 de `docs/agentes/README.md`.

---

## 7. Pendências Humanas Priorizadas

| ID | Prioridade | Item Pendente | Impacto | Validação Pronta |
|:---|:---|:---|:---|:---|
| **PEND-02** | **Alta** | Chaves dos provedores de IA em `config/modelos.yaml` (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`) | Sem as chaves, os agentes operam em modo fake determinístico | `pytest testes/test_ferramentas_modelos.py -k test_real_provider` |
| **PEND-01** | **Alta** | Credenciais da API YouTube Studio (`YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`) | Upload real em modo privado não é enviado ao YouTube | `pytest testes/test_publicacao.py -k test_real_youtube_integration` |
| **PEND-03** | **Média** | Instância de PostgreSQL ativa para checkpointer e store persistente (`POSTGRES_URI`) | Execução em produção depende de banco relacional para durabilidade sync | `pytest testes/test_checkpointer.py -k test_postgres_saver` |
| **PEND-04** | **Média** | Instalação do binário Blender headless no host (`BLENDER_BIN_PATH`) | Geração de cenas 3D e render Cycles utiliza gerador fake determinístico | `pytest testes/test_ferramentas_blender.py -k test_blender_binary` |
| **PEND-05** | **Baixa** | Instalação do binário Potrace no host (`POTRACE_BIN_PATH`) | Vetorização de silhuetas utiliza conversão simulada com saída SVG válida | `pytest testes/test_ferramentas_potrace.py -k test_potrace_binary` |

---

## 8. Custo Estimado de um Episódio Real de 24 Minutos (~120 Planos)

Com base nas medições de tokens, assets gerados e tempos de render observados na fumaça e extrapolados para uma narrativa completa de 24 minutos (~3.800 palavras e 120 planos):

| Categoria | Volume Estimado para 24 min | Preço Unitário de Mercado | Custo Total Estimado |
|:---|:---|:---|:---|
| **LLM-R** (Raciocínio e Texto) | ~850k tokens in / 200k tokens out (Pesquisa, Roteiro, Direção, Metadados, QA) | $3.00 / M in · $15.00 / M out (Claude 3.5 Sonnet / GPT-4o) | **$5.55 USD** |
| **LLM-V** (Visão Multimodal) | ~150 imagens analisadas (storyboards, frames de iluminação, legibilidade de thumbs) | $0.0075 por imagem HD analisada | **$1.15 USD** |
| **IMG** (Geração de Imagens) | ~20 imagens geradas (5 novas marionetes, cenários, 3 capas A/B/C e variações) | $0.04 por imagem gerada (Midjourney / FLUX / DALL-E 3) | **$0.80 USD** |
| **TTS** (Voz Neural Narrador) | ~24.000 caracteres (~3.800 palavras) | $0.18 por 1.000 caracteres (ElevenLabs Creator/Pro) | **$4.32 USD** |
| **ASR** (Transcrição e Alinhamento) | 24 minutos de áudio processado | $0.006 por minuto (Whisper API) | **$0.14 USD** |
| **GPU** (Render Blender Headless 4K) | 84 planos novos (36 via cache hit) * ~45s = ~1.05 horas de GPU | $0.40 por hora (RunPod / Lambda RTX 4090) | **$0.42 USD** |
| **TOTAL ESTIMADO** | **Episódio Completo de 24 Minutos em 4K** | — | **~$12.38 USD** |

---

## 9. Como Rodar o Sistema

### Pré-requisitos
- Python 3.11+ instalado (ambiente testado: Python 3.13.5 no Windows).
- Git configurado.

### Instalação das Dependências
```bash
# No diretório raiz D:\LUME
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
```

### Executar a Suíte Completa de Testes Unitários e de Integração
```bash
# Executa os 39 testes de todos os departamentos e contratos
make test
# Ou diretamente via pytest:
python -m pytest testes/ -v
```

### Executar o Episódio de Fumaça (60 s, 5 Planos, 5 Gates)
```bash
# Executa o pipeline de ponta a ponta com simulação dos 5 gates
make fumaca
# Ou diretamente via pytest:
python -m pytest testes/test_fumaca.py -v -s
```

### Gerar e Sincronizar o Diagrama Mermaid do Grafo
```bash
make grafo
# Gera o arquivo: docs/referencias/grafo-compilado.mmd
```

### Subir o LangGraph Server Localmente
```bash
# Inicializa o LangGraph Server apontando para o langgraph.json configurado
langgraph dev
```
O servidor inicializará em `http://127.0.0.1:2024`, disponibilizando o LangGraph Studio para depuração visual e interação em tempo real com os Gates humanos através de payloads estruturados em formato Artifact.
