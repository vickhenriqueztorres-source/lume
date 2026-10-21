from pathlib import Path

# 1. Patch overlays.py
overlays_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\overlays.py")
overlays_text = overlays_path.read_text(encoding="utf-8")

idx = overlays_text.find("async def dismiss_overlays")
if idx != -1:
    header = overlays_text[:idx]
    clean_overlays = """async def dismiss_overlays(
    page: object, human_input: HumanInput, logger: logging.Logger, job_id: int
) -> None:
    \"\"\"Descarta overlays que possam cobrir a interface do Firefly.\"\"\"
    if await _dismiss_storage_warning(page, human_input, logger, job_id):
        return
    if await _dismiss_common_modals(page, human_input, logger, job_id):
        return

    # Descarta modais de promoção / paywall Spectrum especificamente
    try:
        js_dismiss = '''
        () => {
            function walk(root) {
                if (!root) return;
                const targets = root.querySelectorAll ? Array.from(root.querySelectorAll('sp-close-button, [aria-label*="Fechar" i], [aria-label*="Close" i]')) : [];
                for (const t of targets) {
                    try {
                        const rect = t.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) t.click();
                    } catch(e){}
                }
                const dialogs = root.querySelectorAll ? Array.from(root.querySelectorAll('firefly-commerce-paywall-dialog, sp-dialog-base, susi-modal')) : [];
                for (const d of dialogs) {
                    if (d.shadowRoot) walk(d.shadowRoot);
                }
            }
            walk(document);
        }
        '''
        await page.evaluate(js_dismiss)
    except Exception:
        pass
"""
    overlays_path.write_text(header + clean_overlays, encoding="utf-8")
    print("SUCCESS: overlays.py updated!")

# 2. Patch worker.py _configure_model
worker_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\worker.py")
worker_content = worker_path.read_text(encoding="utf-8")

m_idx = worker_content.find("async def _configure_model")
m_end = worker_content.find("async def _configure_resolution")

if m_idx != -1 and m_end != -1:
    before = worker_content[:m_idx]
    after = worker_content[m_end:]
    clean_model = """async def _configure_model(self, model: str) -> None:
        normalized = model.casefold()
        if normalized == "kling 3.0".casefold():
            await self._select_picker_option(
                picker_key="model_dropdown",
                trigger_key="model_dropdown_trigger",
                option_key="model_option_kling3",
                expected_values={"kling:firefly:colligo:v3direct"},
                description="modelo Kling 3.0",
            )
            return
        option = MODEL_PICKER_OPTIONS.get(normalized)
        if option is None:
            raise ValueError(f"modelo ainda não suportado: {model}")
        expected_value, display_name = option
        picker = self._page.get_by_test_id("firefly-picker-model")
        await picker.wait_for(state="attached", timeout=self.config.selector_timeout_ms)
        picker_value = (await picker.get_attribute("value") or "").casefold()
        if picker_value == expected_value.casefold():
            return
        await dismiss_overlays(self._page, self._human, self.logger, self._current_job_id)
        await picker.click(timeout=3000)
        await asyncio.sleep(0.5)
        option_locator = self._page.get_by_test_id(f"firefly-menu-item-{expected_value}")
        await option_locator.wait_for(state="visible", timeout=5000)
        await option_locator.click(timeout=3000)
        await asyncio.sleep(0.5)
        event(
            self.logger, logging.INFO, "model_selected", job_id=self._current_job_id,
            model=display_name, picker_value=expected_value,
        )

    """
    worker_path.write_text(before + clean_model + after, encoding="utf-8")
    print("SUCCESS: _configure_model updated cleanly in worker.py!")
else:
    print("ERROR: could not locate _configure_model markers")
