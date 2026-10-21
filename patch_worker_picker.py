from pathlib import Path

p = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\worker.py")
text = p.read_text(encoding="utf-8")

# 1. Chamar dismiss_overlays logo apos _open_video_generation
target_1 = """        await self._open_video_generation()
        # Aguarda a montagem dos Web Components do Firefly
        await page.get_by_test_id("firefly-picker-model").wait_for(state="attached", timeout=30000)"""

replacement_1 = """        await self._open_video_generation()
        await dismiss_overlays(page, human_input, self.logger, job.id)
        # Aguarda a montagem dos Web Components do Firefly
        await page.get_by_test_id("firefly-picker-model").wait_for(state="attached", timeout=30000)
        await dismiss_overlays(page, human_input, self.logger, job.id)"""

# 2. Tornar a abertura e clique do picker mais resiliente
target_2 = """        await trigger.press("Enter")
        option_locator = self._page.get_by_test_id(f"firefly-menu-item-{expected_value}")
        await option_locator.wait_for(state="visible", timeout=self.config.selector_timeout_ms)
        await option_locator.click()"""

replacement_2 = """        await dismiss_overlays(self._page, self._human, self.logger, self._current_job_id)
        try:
            await trigger.click(timeout=1500)
        except Exception:
            await trigger.press("Enter")
        option_locator = self._page.get_by_test_id(f"firefly-menu-item-{expected_value}")
        try:
            await option_locator.wait_for(state="visible", timeout=3000)
            await option_locator.click(timeout=2000)
        except Exception:
            # Fallback direto: aciona o evento de clique no componente
            await option_locator.evaluate("el => el.click()")"""

text_n = text.replace("\r\n", "\n")
t1_n = target_1.replace("\r\n", "\n")
t2_n = target_2.replace("\r\n", "\n")

if t1_n in text_n and t2_n in text_n:
    text_n = text_n.replace(t1_n, replacement_1.replace("\r\n", "\n"))
    text_n = text_n.replace(t2_n, replacement_2.replace("\r\n", "\n"))
    p.write_text(text_n.replace("\n", "\r\n"), encoding="utf-8")
    print("worker.py atualizado com sucesso!")
else:
    print(f"Falha ao localizar alvos: t1 in text = {t1_n in text_n}, t2 in text = {t2_n in text_n}")
