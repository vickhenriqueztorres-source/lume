# Progresso da Construção: Runtime LangGraph LUME

## Status Geral
- **Fase Atual:** Fase F · Áudio
- **Fase Anterior Concluída:** Fase E · Arte + Animação (4/4 testes passaram, total 24/24)
- **Próximo Passo Exato:** Implementar os 5 agentes de Áudio (diretor de voz, narração por bloco com TTS/gravação humana, sound designer com SFX licenciados, supervisor musical com trilha e leitmotivs, mixador em -14 LUFS rigoroso).

---

## Avaliação Fase E · Arte + Animação
- [x] Os 5 agentes de Arte e 5 de Animação com ferramentas e cache: OK
- [x] 1 plano renderizado no template Blender headless (mock determinístico): OK (`test_render_um_plano_blender`)
- [x] Vetorização de silhuetas com Potrace (preto absoluto #16110D): OK (`test_vetorizacao_potrace`)
- [x] 10 planos renderizados em lote com concorrência limitada: OK (`test_dez_planos_concorrencia_e_cache_por_hash`)
- [x] Cache por hash visual do contrato do plano (cache_hit=True): OK (`test_dez_planos_concorrencia_e_cache_por_hash`)
- [x] Terceira falha de plano escalada sem bloquear outros: OK (`test_terceira_falha_de_plano_escala_sem_travar_outros`)

---

## Avaliação Fase D · Direção + Storyboard + Gate 2
- [x] Os 5 agentes de Direção com prompts e ferramentas: OK
- [x] Todo plano cumpre o contrato do doc 05 §5: OK (`test_planos_cumprem_contrato_doc05_paragrafo_5`)
- [x] Supervisor de direção de tela corrige caso errado plantado no teste: OK (`test_supervisor_direcao_tela_corrige_caso_errado_plantado`)
- [x] Elenco distingue novas marionetes de reaproveitadas via Store: OK (`test_elenco_marca_novas_e_reaproveitadas`)
- [x] Storyboarder e animatic no Gate 2: OK (`test_direcao_chega_ao_gate_2_com_animatic`)

---

## Avaliação Fase C · Pesquisa + Roteiro + Gate 1
- [x] Os 4 agentes de Pesquisa com prompts e modelo determinístico: OK
- [x] Os 5 agentes de Roteiro com ciclo autor ↔ revisores: OK
- [x] Roteiro chega ao Gate 1 com fontes por bloco (canto/verso): OK (`test_pesquisa_e_roteiro_chegam_ao_gate_1_com_fontes_e_fatos`)
- [x] Notas dos 3 revisores (retenção, fidelidade, tom): OK
- [x] Nenhuma frase sem fato correspondente: OK
- [x] Casos de reprovação da ficha (gíria, fato inventado, gancho > 45s): OK
- [x] Limite máximo de 3 voltas respeitado: OK (`test_ciclo_revisao_refaz_roteiro_e_limita_3_voltas`)

---

## Avaliação Fase B · Esqueleto Completo
- [x] Showrunner + 10 subgrafos + os 48 nós como stubs válidos: OK
- [x] Gates com `interrupt` real e retomada via `Command(resume=...)`: OK (`test_execucao_ponta_a_ponta_com_gates_simulados`)
- [x] Retomada num processo novo com checkpointer persistente SQLite: OK (`test_retomada_processo_novo_com_sqlite_e_idempotencia`)
- [x] Retrabalho cirúrgico do QA: OK (`test_qa_reprovado_volta_para_departamento_exato`)
- [x] Diagrama Mermaid compilado: OK (`docs/referencias/grafo-compilado.mmd`, `test_diagrama_mermaid_compilado_existe`)

---

## Avaliação Fase A · Contratos
- [x] Esquemas do estado (doc 05 §2 + README §4): OK (`contratos/estado.py`)
- [x] Contrato do plano com cálculo de hash SHA-256 (doc 05 §5): OK (`contratos/plano.py`, `test_contrato_plano_e_hash_cache`)
- [x] Respostas estruturadas dos gates (doc 05 §7): OK (`contratos/gates.py`, `test_contratos_gates_validacao`)
- [x] Esquemas de saída dos 48 agentes: OK (`contratos/agentes.py`)
- [x] Reducers de append para custos/erros/qa/aprovacoes: OK (`test_reducers_append_only_nunca_sobrescrevem`)
- [x] Tabela canônica agente → subcampo: OK (`contratos/mapeamento.py`, `test_tabela_mapeamento_48_agentes`, `test_validar_escrita_agente_impede_invasao_de_departamento`)

---

## Tabela Geral dos 48 Agentes (Nós do Grafo)

| # | Id do Nó | Departamento | Tipo | Subcampo que Escreve | Status | Testes |
|---|---|---|---|---|---|---|
| 0 | `showrunner` | supervisor | LLM-R + regras | `episodio.status, episodio.rota, episodio.orcamento, episodio.fila_humana, episodio.licoes_aplicadas` | contratos ok | fase A ok |
| 1 | `pesquisa.pesquisador_fontes` | pesquisa | LLM-R | `pesquisa.fontes, pesquisa.nomes_canonicos` | contratos ok | fase A ok |
| 2 | `pesquisa.verificador_fatos` | pesquisa | LLM-R | `pesquisa.fatos, pesquisa.controversias` | contratos ok | fase A ok |
| 3 | `pesquisa.analista_referencia` | pesquisa | Ferr. + LLM-V | `pesquisa.referencia` | contratos ok | fase A ok |
| 4 | `pesquisa.analista_demanda` | pesquisa | LLM-R | `pesquisa.angulos` | contratos ok | fase A ok |
| 5 | `roteiro.arquiteto_estrutura` | roteiro | LLM-R | `roteiro.esqueleto` | contratos ok | fase A ok |
| 6 | `roteiro.roteirista` | roteiro | LLM-R | `roteiro.blocos, roteiro.versoes` | contratos ok | fase A ok |
| 7 | `roteiro.editor_retencao` | roteiro | LLM-R | `roteiro.notas.retencao` | contratos ok | fase A ok |
| 8 | `roteiro.revisor_fidelidade` | roteiro | LLM-R | `roteiro.notas.fidelidade` | contratos ok | fase A ok |
| 9 | `roteiro.revisor_tom` | roteiro | LLM-R | `roteiro.notas.tom` | contratos ok | fase A ok |
| 10 | `direcao.diretor_decupagem` | direcao | LLM-R | `decupagem.planos` | contratos ok | fase A ok |
| 11 | `direcao.diretor_fotografia` | direcao | LLM-R | `color_script`, enriquece `decupagem.planos[].fogo/luz_deus/proporcao` | contratos ok | fase A ok |
| 12 | `direcao.supervisor_direcao_tela` | direcao | LLM-R (regras) | `decupagem.correcoes_direcao` | contratos ok | fase A ok |
| 13 | `direcao.diretor_arte` | direcao | LLM-R + Store | `elenco` | contratos ok | fase A ok |
| 14 | `direcao.storyboarder` | direcao | IMG + Ferr. | `decupagem.animatic`, enriquece `decupagem.planos[].storyboard` | contratos ok | fase A ok |
| 15 | `arte.designer_silhuetas` | arte | IMG + LLM-V | `assets.marionetes` | contratos ok | fase A ok |
| 16 | `arte.vetorizador` | arte | Ferr. | `assets.marionetes[].svg` | contratos ok | fase A ok |
| 17 | `arte.rigger` | arte | LLM-V + Ferr. | `assets.marionetes[].rig` | contratos ok | fase A ok |
| 18 | `arte.cenografo` | arte | IMG + Ferr. | `assets.cenarios` | contratos ok | fase A ok |
| 19 | `arte.bibliotecario` | arte | Ferr. + Store | `assets.indice` | contratos ok | fase A ok |
| 20 | `animacao.animador_plano` | animacao | LLM-R + Ferr. | `assets.planos[].cena` | contratos ok | fase A ok |
| 21 | `animacao.montador_cena_3d` | animacao | Ferr. | `assets.planos[].blend` | contratos ok | fase A ok |
| 22 | `animacao.gerente_render` | animacao | Ferr. | `assets.planos[].render` | contratos ok | fase A ok |
| 23 | `animacao.revisor_plano` | animacao | LLM-V | `assets.planos[].revisao` | contratos ok | fase A ok |
| 24 | `animacao.vfx` | animacao | Ferr. | `assets.planos[].vfx` | contratos ok | fase A ok |
| 25 | `audio.diretor_voz` | audio | LLM-R | `audio.roteiro_anotado` | contratos ok | fase A ok |
| 26 | `audio.narrador` | audio | TTS / Ferr. | `audio.narracao` | contratos ok | fase A ok |
| 27 | `audio.sound_designer` | audio | LLM-R + Ferr. | `audio.sfx` | contratos ok | fase A ok |
| 28 | `audio.supervisor_musical` | audio | LLM-R + Ferr. | `audio.trilha` | contratos ok | fase A ok |
| 29 | `audio.mixador` | audio | Ferr. | `audio.mix, audio.lufs` | contratos ok | fase A ok |
| 30 | `montagem.editor` | montagem | LLM-R + Ferr. | `timeline` | contratos ok | fase A ok |
| 31 | `montagem.grafismo` | montagem | Ferr. | `timeline.camadas_motion` | contratos ok | fase A ok |
| 32 | `montagem.finalizador` | montagem | Ferr. | `master.arquivo, master.capitulos` | contratos ok | fase A ok |
| 33 | `montagem.legendador` | montagem | ASR + LLM-R | `master.legendas` | contratos ok | fase A ok |
| 34 | `embalagem.titulista` | embalagem | LLM-R | `embalagem.titulos` | contratos ok | fase A ok |
| 35 | `embalagem.designer_thumbnail` | embalagem | IMG + Ferr. | `embalagem.thumbs` | contratos ok | fase A ok |
| 36 | `embalagem.avaliador_feed` | embalagem | LLM-V | `embalagem.ranking` | contratos ok | fase A ok |
| 37 | `embalagem.redator_metadados` | embalagem | LLM-R | `embalagem.metadados` | contratos ok | fase A ok |
| 38 | `embalagem.cortador_shorts` | embalagem | LLM-R + Ferr. | `embalagem.shorts` | contratos ok | fase A ok |
| 39 | `qa.qa_tecnico` | qa | Ferr. | `qa` (append) | contratos ok | fase A ok |
| 40 | `qa.qa_continuidade` | qa | LLM-V + Ferr. | `qa` (append) | contratos ok | fase A ok |
| 41 | `qa.qa_fidelidade` | qa | LLM-R | `qa` (append) | contratos ok | fase A ok |
| 42 | `qa.qa_marca` | qa | Ferr. + LLM-V | `qa` (append, aviso) | contratos ok | fase A ok |
| 43 | `qa.qa_direitos` | qa | Ferr. | `qa` (append) | contratos ok | fase A ok |
| 44 | `qa.qa_originalidade` | qa | LLM-R + Ferr. | `qa` (append) | contratos ok | fase A ok |
| 45 | `publicacao.publicador` | publicacao | Ferr. | `episodio.publicacao` | contratos ok | fase A ok |
| 46 | `publicacao.analista_desempenho` | publicacao | Ferr. + LLM-R | `episodio.desempenho` | contratos ok | fase A ok |
| 47 | `publicacao.curador_memoria` | publicacao | LLM-R + Store | `episodio.licoes_gravadas` | contratos ok | fase A ok |

---

## Fases do Projeto

- [x] **Fase A · Contratos**
- [ ] **Fase B · Esqueleto Completo**
- [ ] **Fase C · Pesquisa + Roteiro + Gate 1**
- [ ] **Fase D · Direção + Storyboard + Gate 2**
- [ ] **Fase E · Arte + Animação**
- [ ] **Fase F · Áudio**
- [ ] **Fase G · Montagem + QA**
- [ ] **Fase H · Embalagem + Publicação**
- [ ] **Fase I · Memória e Aprendizado**
