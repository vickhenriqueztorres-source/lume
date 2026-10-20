# Registro de Pendências Humanas (PENDENCIAS.md)

Formato: id · fase · o que falta · impacto · o que já está pronto para quando resolver.

---

- PEND-01 · Fase H · Credenciais do YouTube Data API (`YOUTUBE_CLIENT_SECRET`, `YOUTUBE_REFRESH_TOKEN`) · Upload real para o YouTube não é disparado (roda em modo fake simulado) · Ferramenta `YouTubePublisher` real pronta com interface e validação, chave de idempotência e modo privado garantido. Comando de teste: `pytest testes/test_publicacao.py -k test_real_youtube_integration`.
- PEND-02 · [RESOLVIDO VIA CLI LOCAL] · Inferência de modelos LLM-R, LLM-V e IMG sem necessidade de chaves de API pagas · Implementado adaptador `CodexCLIClient` em `grafo/ferramentas/cli_llm.py` acoplado ao `codex.cmd exec -m gpt-5.6-terra` e `StartFrameGenerator` em `grafo/ferramentas/start_frame.py`.
- PEND-03 · Fase B · Instância de PostgreSQL para checkpointer persistente em produção (`POSTGRES_URI`) · Grafo roda localmente com `MemorySaver` / `SqliteSaver` · Adaptador `PostgresSaver` e `PostgresStore` prontos e configuráveis. Comando de teste: `pytest testes/test_checkpointer.py -k test_postgres_saver`.
- PEND-04 · [RESOLVIDO VIA FIREFLY ENGINE] · Renderização de vídeo sem necessidade de binário Blender headless · Portado e integrado o motor `FireflyEngine` de `D:\LINHA DE FOGO EDITS` em `grafo/ferramentas/firefly.py` com lock serial estrito = 1, watchdog de timeout e Start Frames cinematográficos.
- PEND-05 · Fase E · Binário do Potrace (`POTRACE_BIN_PATH`) para vetorização de silhuetas · Vetorizador usa conversão fake determinística (SVG válido com curvas de silhueta) · Wrapper `PotraceRunner` pronto. Comando de teste: `pytest testes/test_ferramentas_potrace.py -k test_potrace_binary`.
