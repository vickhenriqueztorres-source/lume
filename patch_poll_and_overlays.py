from pathlib import Path

# 1. Patch worker.py to remove dismiss_overlays from the polling loop
worker_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\worker.py")
worker_text = worker_path.read_text(encoding="utf-8")

poll_target = """        while True:

            if hasattr(state_reader, "page") and self._human is not None:

                await dismiss_overlays(state_reader.page, self._human, self.logger, job.id)

            observation = await self._read_generation_state(job, state_reader)"""

poll_replacement = """        while True:

            observation = await self._read_generation_state(job, state_reader)"""

if poll_target in worker_text:
    worker_text = worker_text.replace(poll_target, poll_replacement)
    worker_path.write_text(worker_text, encoding="utf-8")
    print("SUCCESS: Removed dismiss_overlays from worker.py polling loop!")
else:
    # Try with single newlines
    w_norm = worker_text.replace("\r\n", "\n")
    p_norm = """        while True:
            if hasattr(state_reader, "page") and self._human is not None:
                await dismiss_overlays(state_reader.page, self._human, self.logger, job.id)
            observation = await self._read_generation_state(job, state_reader)"""
    r_norm = """        while True:
            observation = await self._read_generation_state(job, state_reader)"""
    if p_norm in w_norm:
        worker_path.write_text(w_norm.replace(p_norm, r_norm), encoding="utf-8")
        print("SUCCESS (norm): Removed dismiss_overlays from worker.py polling loop!")
    else:
        print("WARNING: poll target not found in worker.py")

# 2. Patch overlays.py to be fast, surgical, and never press Escape blindly
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
        modal_close = page.locator("sp-dialog-base, firefly-commerce-paywall-dialog, susi-modal").locator("sp-close-button, [aria-label*='Fechar' i], [aria-label*='Close' i]").first
        if await modal_close.count() > 0 and await modal_close.is_visible():
            await modal_close.click(timeout=1000)
            event(logger, logging.INFO, "promo_overlay_dismissed", job_id=job_id)
            if hasattr(page, "wait_for_timeout"):
                await page.wait_for_timeout(500)
            return
    except Exception:
        pass

    # Fallback via JavaScript direcionado (apenas se paywall estiver visível)
    try:
        dismissed = await page.evaluate('''() => {
            const paywall = document.querySelector('firefly-commerce-paywall-dialog, sp-dialog-base');
            if (!paywall) return false;
            let closeBtn = paywall.querySelector('sp-close-button, [aria-label*="Fechar" i], [aria-label*="Close" i]');
            if (!closeBtn && paywall.shadowRoot) {
                closeBtn = paywall.shadowRoot.querySelector('sp-close-button, [aria-label*="Fechar" i], [aria-label*="Close" i]');
            }
            if (closeBtn) {
                closeBtn.click();
                return true;
            }
            return false;
        }''')
        if dismissed:
            event(logger, logging.INFO, "promo_overlay_dismissed_js", job_id=job_id)
            if hasattr(page, "wait_for_timeout"):
                await page.wait_for_timeout(500)
    except Exception:
        pass
"""
    overlays_path.write_text(header + clean_overlays, encoding="utf-8")
    print("SUCCESS: overlays.py updated cleanly!")
