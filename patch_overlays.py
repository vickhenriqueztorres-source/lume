from pathlib import Path

path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\overlays.py")
content = path.read_text(encoding="utf-8")

idx = content.find("async def dismiss_overlays")
if idx == -1:
    print("Could not find dismiss_overlays")
    exit(1)

header = content[:idx]

new_func = """async def dismiss_overlays(
    page: object, human_input: HumanInput, logger: logging.Logger, job_id: int
) -> None:
    \"\"\"Overlay ausente é normal; erros são logados sem mascarar o fluxo principal.\"\"\"
    if await _dismiss_storage_warning(page, human_input, logger, job_id):
        return
    if await _dismiss_common_modals(page, human_input, logger, job_id):
        return

    # 1. Dismiss via Shadow-DOM traversal for Spectrum components (sp-close-button, SusI modals, etc)
    try:
        js_dismiss = '''
        () => {
            let clicked = 0;
            function walk(root) {
                if (!root) return;
                const targets = root.querySelectorAll ? Array.from(root.querySelectorAll('sp-close-button, [aria-label*="Fechar" i], [aria-label*="Close" i]')) : [];
                for (const t of targets) {
                    try {
                        const rect = t.getBoundingClientRect();
                        if (rect.width > 0 && rect.height > 0) {
                            t.click();
                            clicked++;
                        }
                    } catch(e){}
                }
                const all = root.querySelectorAll ? Array.from(root.querySelectorAll('*')) : [];
                for (const el of all) {
                    if (el.shadowRoot) walk(el.shadowRoot);
                }
            }
            walk(document);
            return clicked;
        }
        '''
        dismissed_count = await page.evaluate(js_dismiss)
        if dismissed_count > 0:
            event(logger, logging.INFO, "promo_overlay_dismissed_js", job_id=job_id, count=dismissed_count)
            if hasattr(page, "wait_for_timeout"):
                await page.wait_for_timeout(500)
    except Exception:
        pass

    # 2. Descarta modais de promoção / marketing / upgrade (ex: Firefly Pro Plus)
    promo_selectors = [
        'sp-close-button',
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

    # 3. Pressiona Escape para fechar qualquer diálogo Spectrum aberto em primeiro plano
    try:
        dialog = page.locator('dialog, [role="dialog"], sp-dialog, sp-underlay, firefly-commerce-paywall-dialog')
        if await dialog.count() > 0 and await dialog.first.is_visible(timeout=300):
            await page.keyboard.press("Escape")
            event(logger, logging.INFO, "overlay_escape_pressed", job_id=job_id)
            if hasattr(page, "wait_for_timeout"):
                await page.wait_for_timeout(500)
    except Exception:
        pass
"""

path.write_text(header + new_func, encoding="utf-8")
print("SUCCESSFULLY REPLACED dismiss_overlays in overlays.py!")
