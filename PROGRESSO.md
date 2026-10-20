# Progresso da Construção: Runtime LangGraph LUME

## Status Geral
- **Fase Atual:** Concluído + Modernização CLI Codex / Antigravity e Motor Firefly Integrados
- **Status dos Testes:** 55/55 testes passando (100% de sucesso, 0 skipped, 0 falhas)
- **Fumaça:** `testes/test_fumaca.py` executado com sucesso de ponta a ponta (60s, 5 planos com Start Frames cinematográficos e clipes Firefly, 5 gates)
- **Diagrama Mermaid:** Salvo e sincronizado em `docs/referencias/grafo-compilado.mmd`
- **Subetapas Modernização:** Subetapas 1, 2, 3, 4 e 5 100% implementadas e testadas com baterias de estresse, segurança e caos.

---

## Avaliação Fase por Fase

### [x] Fase A · Contratos
- Esquemas do estado (`contratos/estado.py`): OK
- Contrato do plano com cálculo de hash SHA-256 (`contratos/plano.py`): OK
- Respostas estruturadas dos gates (`contratos/gates.py`): OK
- Esquemas de saída dos 48 agentes (`contratos/agentes.py`): OK
- Reducers de append para custos/erros/qa/aprovacoes: OK
- Tabela canônica agente → subcampo (`contratos/mapeamento.py`): OK
- Evidência: `testes/test_contratos.py` (7/7 passed)

### [x] Fase B · Esqueleto Completo
- Showrunner + 10 subgrafos + 48 nós: OK
- Gates com `interrupt` real e retomada via `Command(resume=...)`: OK
- Retomada num processo novo com checkpointer persistente SQLite: OK
- Retrabalho cirúrgico do QA: OK
- Diagrama Mermaid compilado: OK (`docs/referencias/grafo-compilado.mmd`)
- Evidência: `testes/test_fase_b.py` (4/4 passed)

### [x] Fase C · Pesquisa + Roteiro + Gate 1
- 4 agentes de Pesquisa com modelo determinístico e fontes Canto IX: OK
- 5 agentes de Roteiro com ciclo autor ↔ revisores (até 3 voltas): OK
- Checagem e reprovação de gírias pelo Revisor de Tom: OK
- Checagem e reprovação de fatos inventados pelo Revisor de Fidelidade: OK
- Checagem e reprovação de gancho inicial > 45s pelo Editor de Retenção: OK
- Evidência: `testes/test_fase_c.py` (5/5 passed)

### [x] Fase D · Direção + Storyboard + Gate 2
- 5 agentes de Direção cumprindo o contrato do Doc 05 §5: OK
- Color script com níveis de fogo 1 a 5 e proporções de tela: OK
- Supervisor de direção de tela corrigindo caso errado plantado (→ casa): OK
- Elenco distinguindo reaproveitadas de novas a criar via Store: OK
- Animatic e Storyboard no Gate 2: OK
- Evidência: `testes/test_fase_d.py` (4/4 passed)

### [x] Fase E · Arte + Animação
- 5 agentes de Arte e 5 de Animação: OK
- Template Blender headless montando cena .blend e renderizando MP4: OK
- Vetorização com Potrace em preto absoluto `#16110D`: OK
- Processamento em lote de 10 planos com controle de concorrência: OK
- Cache de render por hash visual (cache_hit=True): OK
- 3ª falha consecutiva escalada para a fila humana sem travar os outros planos: OK
- Evidência: `testes/test_fase_e.py` (4/4 passed)

### [x] Fase F · Áudio
- 5 agentes de Áudio com narração, SFX e trilha: OK
- Normalização de Loudness em exatamente -14.0 LUFS (±1.0 LUFS): OK
- Toda faixa com licença formal registrada no estado: OK
- Transcrição ASR com divergência ≤ 2% em relação ao roteiro: OK
- Diretor de voz com andamento entre 140 e 165 ppm: OK
- Evidência: `testes/test_fase_f.py` (4/4 passed)

### [x] Fase G · Montagem + QA
- 4 agentes de Montagem gerando Master 4K, capítulos e legendas SRT: OK
- 6 agentes de QA com checagens paralelas: OK
- Cada um dos 5 QAs bloqueantes reprova defeito e aponta departamento certo: OK
- QA de marca emite apenas aviso (bloqueia=False) sem travar o avanço: OK
- Evidência: `testes/test_fase_g.py` (4/4 passed)

### [x] Fase H · Embalagem + Publicação
- 5 agentes de Embalagem e Publicador: OK
- 3 títulos com ≤ 60 caracteres: OK
- 3 thumbnails nos layouts A, B e C respeitando regras de marca: OK
- Avaliador de feed medindo legibilidade em 120 px: OK
- Publicador com upload estritamente privado: OK
- Idempotência garantida (reexecução evitada): OK
- Evidência: `testes/test_fase_h.py` (4/4 passed)

### [x] Fase I · Memória e Aprendizado
- Curador de memória gravando lições na Store no término do episódio: OK
- Showrunner recuperando e injetando lições no episódio subsequente: OK
- Registro formal em `episodio.licoes_aplicadas`: OK
- Evidência: `testes/test_fase_i.py` (2/2 passed)

---

## Tabela Geral dos 48 Agentes (Nós do Grafo)

| # | Id do Nó | Departamento | Tipo | Subcampo que Escreve | Status | Testes |
|---|---|---|---|---|---|---|
| 0 | `showrunner` | supervisor | LLM-R + regras | `episodio.status, episodio.rota, episodio.orcamento, episodio.fila_humana, episodio.licoes_aplicadas` | real | ok (fase B, I, fumaca) |
| 1 | `pesquisa.pesquisador_fontes` | pesquisa | LLM-R | `pesquisa.fontes, pesquisa.nomes_canonicos` | real | ok (fase C, fumaca) |
| 2 | `pesquisa.verificador_fatos` | pesquisa | LLM-R | `pesquisa.fatos, pesquisa.controversias` | real | ok (fase C, fumaca) |
| 3 | `pesquisa.analista_referencia` | pesquisa | Ferr. + LLM-V | `pesquisa.referencia` | real | ok (fase C, fumaca) |
| 4 | `pesquisa.analista_demanda` | pesquisa | LLM-R | `pesquisa.angulos` | real | ok (fase C, fumaca) |
| 5 | `roteiro.arquiteto_estrutura` | roteiro | LLM-R | `roteiro.esqueleto` | real | ok (fase C, fumaca) |
| 6 | `roteiro.roteirista` | roteiro | LLM-R | `roteiro.blocos, roteiro.versoes` | real | ok (fase C, fumaca) |
| 7 | `roteiro.editor_retencao` | roteiro | LLM-R | `roteiro.notas.retencao` | real | ok (fase C, fumaca) |
| 8 | `roteiro.revisor_fidelidade` | roteiro | LLM-R | `roteiro.notas.fidelidade` | real | ok (fase C, fumaca) |
| 9 | `roteiro.revisor_tom` | roteiro | LLM-R | `roteiro.notas.tom` | real | ok (fase C, fumaca) |
| 10 | `direcao.diretor_decupagem` | direcao | LLM-R | `decupagem.planos` | real | ok (fase D, fumaca) |
| 11 | `direcao.diretor_fotografia` | direcao | LLM-R | `color_script`, enriquece `decupagem.planos[].fogo/luz_deus/proporcao` | real | ok (fase D, fumaca) |
| 12 | `direcao.supervisor_direcao_tela` | direcao | LLM-R (regras) | `decupagem.correcoes_direcao` | real | ok (fase D, fumaca) |
| 13 | `direcao.diretor_arte` | direcao | LLM-R + Store | `elenco` | real | ok (fase D, fumaca) |
| 14 | `direcao.storyboarder` | direcao | IMG + Ferr. | `decupagem.animatic`, enriquece `decupagem.planos[].storyboard` | real | ok (fase D, fumaca) |
| 15 | `arte.designer_silhuetas` | arte | IMG + LLM-V | `assets.marionetes` | real | ok (fase E, fumaca) |
| 16 | `arte.vetorizador` | arte | Ferr. | `assets.marionetes[].svg` | real | ok (fase E, fumaca) |
| 17 | `arte.rigger` | arte | LLM-V + Ferr. | `assets.marionetes[].rig` | real | ok (fase E, fumaca) |
| 18 | `arte.cenografo` | arte | IMG + Ferr. | `assets.cenarios` | real | ok (fase E, fumaca) |
| 19 | `arte.bibliotecario` | arte | Ferr. + Store | `assets.indice` | real | ok (fase E, fumaca) |
| 20 | `animacao.animador_plano` | animacao | LLM-R + Ferr. | `assets.planos[].cena` | real | ok (fase E, fumaca) |
| 21 | `animacao.montador_cena_3d` | animacao | Ferr. | `assets.planos[].blend` | real | ok (fase E, fumaca) |
| 22 | `animacao.gerente_render` | animacao | Ferr. | `assets.planos[].render` | real | ok (fase E, fumaca) |
| 23 | `animacao.revisor_plano` | animacao | LLM-V | `assets.planos[].revisao` | real | ok (fase E, fumaca) |
| 24 | `animacao.vfx` | animacao | Ferr. | `assets.planos[].vfx` | real | ok (fase E, fumaca) |
| 25 | `audio.diretor_voz` | audio | LLM-R | `audio.roteiro_anotado` | real | ok (fase F, fumaca) |
| 26 | `audio.narrador` | audio | TTS / Ferr. | `audio.narracao` | real | ok (fase F, fumaca) |
| 27 | `audio.sound_designer` | audio | LLM-R + Ferr. | `audio.sfx` | real | ok (fase F, fumaca) |
| 28 | `audio.supervisor_musical` | audio | LLM-R + Ferr. | `audio.trilha` | real | ok (fase F, fumaca) |
| 29 | `audio.mixador` | audio | Ferr. | `audio.mix, audio.lufs` | real | ok (fase F, fumaca) |
| 30 | `montagem.editor` | montagem | LLM-R + Ferr. | `timeline` | real | ok (fase G, fumaca) |
| 31 | `montagem.grafismo` | montagem | Ferr. | `timeline.camadas_motion` | real | ok (fase G, fumaca) |
| 32 | `montagem.finalizador` | montagem | Ferr. | `master.arquivo, master.capitulos` | real | ok (fase G, fumaca) |
| 33 | `montagem.legendador` | montagem | ASR + LLM-R | `master.legendas` | real | ok (fase G, fumaca) |
| 34 | `embalagem.titulista` | embalagem | LLM-R | `embalagem.titulos` | real | ok (fase H, fumaca) |
| 35 | `embalagem.designer_thumbnail` | embalagem | IMG + Ferr. | `embalagem.thumbs` | real | ok (fase H, fumaca) |
| 36 | `embalagem.avaliador_feed` | embalagem | LLM-V | `embalagem.ranking` | real | ok (fase H, fumaca) |
| 37 | `embalagem.redator_metadados` | embalagem | LLM-R | `embalagem.metadados` | real | ok (fase H, fumaca) |
| 38 | `embalagem.cortador_shorts` | embalagem | LLM-R + Ferr. | `embalagem.shorts` | real | ok (fase H, fumaca) |
| 39 | `qa.qa_tecnico` | qa | Ferr. | `qa` (append) | real | ok (fase G, fumaca) |
| 40 | `qa.qa_continuidade` | qa | LLM-V + Ferr. | `qa` (append) | real | ok (fase G, fumaca) |
| 41 | `qa.qa_fidelidade` | qa | LLM-R | `qa` (append) | real | ok (fase G, fumaca) |
| 42 | `qa.qa_marca` | qa | Ferr. + LLM-V | `qa` (append, aviso) | real | ok (fase G, fumaca) |
| 43 | `qa.qa_direitos` | qa | Ferr. | `qa` (append) | real | ok (fase G, fumaca) |
| 44 | `qa.qa_originalidade` | qa | LLM-R + Ferr. | `qa` (append) | real | ok (fase G, fumaca) |
| 45 | `publicacao.publicador` | publicacao | Ferr. | `episodio.publicacao` | real | ok (fase H, fumaca) |
| 46 | `publicacao.analista_desempenho` | publicacao | Ferr. + LLM-R | `episodio.desempenho` | real | ok (fase H, fumaca) |
| 47 | `publicacao.curador_memoria` | publicacao | LLM-R + Store | `episodio.licoes_gravadas` | real | ok (fase I, fumaca) |

---

## Fases do Projeto

- [x] **Fase A · Contratos**
- [x] **Fase B · Esqueleto Completo**
- [x] **Fase C · Pesquisa + Roteiro + Gate 1**
- [x] **Fase D · Direção + Storyboard + Gate 2**
- [x] **Fase E · Arte + Animação**
- [x] **Fase F · Áudio**
- [x] **Fase G · Montagem + QA**
- [x] **Fase H · Embalagem + Publicação**
- [x] **Fase I · Memória e Aprendizado**
