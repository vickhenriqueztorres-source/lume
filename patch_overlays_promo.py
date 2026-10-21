from pathlib import Path

p = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\overlays.py")
text = p.read_text(encoding="utf-8")

old_snippet = """    if not SELECTORS["overlay_close_buttons"].confirmed:
        return
    try:
        locator = locator_for(page, "overlay_close_buttons")
        if await locator.is_visible(timeout=500):
            await human_input.click(locator)
            event(logger, logging.INFO, "overlay_dismissed", job_id=job_id)
    except (PatchrightTimeoutError, PatchrightError) as exc:
        event(
            logger,
            logging.WARNING,
            "overlay_dismiss_failed",
            job_id=job_id,
            error=type(exc).__name__,
        )"""

new_snippet = """    # Descarta modais de promoção / marketing / upgrade (ex: Firefly Pro Plus)
    promo_selectors = [
        'button[aria-label="Fechar"]',
        'button[aria-label="Close"]',
        'button[aria-label*="Fechar" i]',
        'button[aria-label*="Close" i]',
        '[data-testid*="close" i]',
        'sp-dialog button[slot="button"]',
        'sp-dialog [aria-label="Close"]',
        'sp-dialog [aria-label="Fechar"]',
        '.spectrum-Dialog button[aria-label="Close"]',
    ]
    for sel in promo_selectors:
        try:
            loc = page.locator(sel)
            if await loc.count() > 0 and await loc.first.is_visible(timeout=300):
                await loc.first.click(timeout=1000)
                event(logger, logging.INFO, "promo_overlay_dismissed", job_id=job_id, selector=sel)
                if hasattr(page, "wait_for_timeout"):
                    await page.wait_for_timeout(500)
                return
        except Exception:
            pass

    # Pressiona Escape para fechar qualquer diálogo Spectrum aberto em primeiro plano
    try:
        dialog = page.locator('dialog, [role="dialog"], sp-dialog, sp-underlay')
        if await dialog.count() > 0 and await dialog.first.is_visible(timeout=300):
            await page.keyboard.press("Escape")
            event(logger, logging.INFO, "overlay_escape_pressed", job_id=job_id)
            if hasattr(page, "wait_for_timeout"):
                await page.wait_for_timeout(500)
    except Exception:
        pass"""

old_n = old_snippet.replace("\r\n", "\n")
text_n = text.replace("\r\n", "\n")

if old_n in text_n:
    updated = text_n.replace(old_n, new_snippet.replace("\r\n", "\n"))
    p.write_text(updated.replace("\n", "\r\n"), encoding="utf-8")
    print("overlays.py corrigido com sucesso!")
else:
    print("Snippet não encontrado!")
