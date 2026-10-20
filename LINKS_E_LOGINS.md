# Guia Local: Links, Logins e Comandos de Operação — Estúdio LUME

Arquivo de referência local permanente para acesso, credenciais, autenticação de CLIs e operação do pipeline de produção.

---

## 1. Links de Acesso e Serviços Web

| Serviço | URL | Finalidade no Projeto |
|:---|:---|:---|
| **Adobe Firefly** | [https://firefly.adobe.com](https://firefly.adobe.com) | Motor de animação e geração de vídeo dos planos a partir de Start Frames |
| **OpenAI / ChatGPT** | [https://chatgpt.com](https://chatgpt.com) | Conta vinculada à autenticação local do Codex CLI |
| **YouTube Studio** | [https://studio.youtube.com](https://studio.youtube.com) | Painel para envio e monitoramento dos episódios em modo privado |
| **Google Antigravity Docs** | [https://antigravity.google/docs](https://antigravity.google/docs) | Documentação oficial da CLI (`agy`), SDK e extensões |
| **Perseus Digital Library** | [https://www.perseus.tufts.edu/hopper/](https://www.perseus.tufts.edu/hopper/) | Fonte primária de validação de cantos e versos canônicos da Odisseia |

---

## 2. Comandos de Autenticação das CLIs Locais

### 2.1. Codex CLI (`codex`)
A CLI já está configurada para operar com `gpt-5.6-terra` sem custo de API avulsa, com redundância multi-conta ativa:
- **Conta 1 (Principal):** Armazenada em `~/.codex` (Ativa).
- **Conta 2 (Backup / Failover):** Armazenada em `~/.codex_secundaria` (Ativa).
- *Se a Conta 1 atingir limites de cota ou taxa (HTTP 429), o runtime alterna automaticamente para a Conta 2.*

- **Conferir status da conta principal:**
  ```bash
  codex login status
  ```
- **Conferir status da conta secundária:**
  ```powershell
  $env:CODEX_HOME="C:\Users\brend\.codex_secundaria"; codex login status
  ```
- **Login via Navegador (Padrão ChatGPT):**
  ```bash
  codex login
  ```
- **Login via Código no Terminal (Device Auth):**
  ```bash
  codex login --device-auth
  ```
- **Login direto com API Key OpenAI (PowerShell):**
  ```powershell
  'sk-proj-SUA_CHAVE_AQUI' | codex login --with-api-key
  ```
- **Desconectar / Trocar de conta:**
  ```bash
  codex logout
  ```

### 2.2. Google Antigravity CLI (`agy`)
Utiliza as credenciais da conta Google ativa no ambiente local.

- **Iniciar interface interativa / login:**
  ```bash
  agy
  ```
- **Reconfigurar caminhos, ambiente e permissões:**
  ```bash
  agy install
  ```

---

## 3. Comandos de Operação do Runtime LUME

Todos os comandos devem ser executados na raiz do projeto (`D:\LUME`):

- **Executar Suíte Completa de Testes (55 testes):**
  ```bash
  python -m pytest testes/ -v
  ```
  *Ou:*
  ```bash
  make test
  ```

- **Executar Episódio de Fumaça de Ponta a Ponta (60s, 5 Planos, 5 Gates):**
  ```bash
  python -m pytest testes/test_fumaca.py -v -s
  ```
  *Ou:*
  ```bash
  make fumaca
  ```

- **Gerar / Atualizar Diagrama Mermaid do Grafo:**
  ```bash
  python -m grafo.gerar_diagrama
  ```
  *Ou:*
  ```bash
  make grafo
  ```

- **Iniciar Servidor Local do LangGraph Studio:**
  ```bash
  langgraph dev
  ```
  *Interface visual disponível em:* `http://127.0.0.1:2024`

---

## 4. Documentos de Controle e Relatórios no Repositório

- **[RELATORIO_FINAL.md](file:///D:/LUME/RELATORIO_FINAL.md):** Relatório completo de construção das 9 fases (A a I), tabela dos 48 nós, evidências e custos extrapolados.
- **[PLANO_EXECUCAO_CLI_FIREFLY.md](file:///D:/LUME/PLANO_EXECUCAO_CLI_FIREFLY.md):** Especificação técnica da modernização com CLI Codex e motor Adobe Firefly.
- **[PROGRESSO.md](file:///D:/LUME/PROGRESSO.md):** Status atualizado das fases e suíte de testes (55/55 ok).
- **[PENDENCIAS.md](file:///D:/LUME/PENDENCIAS.md):** Controle de pendências humanas (YouTube API e Postgres).
- **[DECISOES.md](file:///D:/LUME/DECISOES.md):** Registro de todas as decisões arquiteturais tomadas no projeto.
- **[CONFLITOS-DOCS.md](file:///D:/LUME/CONFLITOS-DOCS.md):** Registro de conflitos entre documentos e soluções adotadas.
- **Projeto Fonte Firefly:** `D:\LINHA DE FOGO EDITS` (motor `services/video/firefly_engine.py` e testes de subgrafo).
