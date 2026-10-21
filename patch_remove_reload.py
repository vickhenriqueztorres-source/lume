from pathlib import Path

p = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\worker.py")
text = p.read_text(encoding="utf-8")

# Remove o bloco de reload na poll de geração
text_n = text.replace("\r\n", "\n")

target = """            # Se a renderização demorar mais de 120s, atualiza a página para destravar o evento de vídeo pronto
            if elapsed >= next_reload_after and hasattr(state_reader, "page") and state_reader.page is not None:
                event(
                    self.logger,
                    logging.INFO,
                    "generation_poll_refreshing_page",
                    job_id=job.id,
                    elapsed_seconds=round(elapsed, 1),
                )
                try:
                    await state_reader.page.reload(wait_until="domcontentloaded", timeout=self.config.nav_timeout_ms)
                    await asyncio.sleep(2.0)
                    if self._human is not None:
                        await dismiss_overlays(state_reader.page, self._human, self.logger, job.id)
                except Exception as reload_err:
                    event(self.logger, logging.WARNING, "generation_poll_refresh_failed", error=str(reload_err))
                next_reload_after = elapsed + 60.0  # Próximo reload a cada 60s"""

# Caso com quebras duplas
import re
pattern = r"[ \t]*# Se a renderiza.*?\n(?:[ \t]*\n)*[ \t]*if elapsed >= next_reload_after.*?(?=\n(?:[ \t]*\n)*[ \t]*if elapsed >= self\.config\.generation_budget_seconds)"
match = re.search(pattern, text_n, re.DOTALL)
if match:
    print("Encontrado bloco de reload:", match.group(0)[:100])
    text_n = text_n[:match.start()] + text_n[match.end():]
    p.write_text(text_n, encoding="utf-8")
    print("Bloco de reload removido com sucesso!")
else:
    print("Padrão de reload não encontrado via regex.")
