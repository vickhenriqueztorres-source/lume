# Registro de Pendências Humanas (PENDENCIAS.md)

Formato: id · fase · o que falta · impacto · o que já está pronto para quando resolver.

---

- PEND-01 · Fase H · Credenciais do YouTube Data API (`YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`) · Upload real para o YouTube não é disparado (roda em modo fake simulado) · Ferramenta `YouTubePublisher` real pronta com interface e validação, chave de idempotência e modo privado garantido. Comando de teste: `pytest testes/test_publicacao.py -k test_real_youtube_integration`.
- PEND-02 · Fase C-H · Chaves de provedores de modelos LLM-R, LLM-V, IMG, TTS, ASR em `config/modelos.yaml` (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`, etc.) · Sistema roda com mock/fake determinístico estruturado · Factory de modelos configurável e prompts versionados prontos. Comando de teste: `pytest testes/test_ferramentas_modelos.py -k test_real_provider`.
- PEND-03 · Fase B · Instância de PostgreSQL para checkpointer persistente em produção (`POSTGRES_URI`) · Grafo roda localmente com `MemorySaver` / `SqliteSaver` · Adaptador `PostgresSaver` e `PostgresStore` prontos e configuráveis. Comando de teste: `pytest testes/test_checkpointer.py -k test_postgres_saver`.
- PEND-04 · Fase E · Binários do Blender headless (`BLENDER_BIN_PATH`) instalados no ambiente host · Renders 3D executam em modo fake determinístico (geram assets de placeholder com hash válido) · Wrapper `BlenderRunner` pronto com parâmetros de cena. Comando de teste: `pytest testes/test_ferramentas_blender.py -k test_blender_binary`.
- PEND-05 · Fase E · Binário do Potrace (`POTRACE_BIN_PATH`) para vetorização de silhuetas · Vetorizador usa conversão fake determinística (SVG válido com curvas de silhueta) · Wrapper `PotraceRunner` pronto. Comando de teste: `pytest testes/test_ferramentas_potrace.py -k test_potrace_binary`.
