from pathlib import Path

overlays_path = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\firefly_bot\overlays.py")
content = overlays_path.read_text(encoding="utf-8")

idx = content.find("async def dismiss_overlays")
if idx != -1:
    header = content[:idx]
    new_func = """async def dismiss_overlays(
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
            const cd = document.querySelector('firefly-commerce-dialogs');
            if (cd) {
                cd.style.display = 'none';
                cd.style.pointerEvents = 'none';
            }
            function walk(root) {
                if (!root) return;
                const targets = root.querySelectorAll ? Array.from(root.querySelectorAll('sp-close-button, [aria-label*="Fechar" i], [aria-label*="Close" i]')) : [];
                for (const t of targets) {
                    try {
                        t.click();
                    } catch(e){}
                }
                const dialogs = root.querySelectorAll ? Array.from(root.querySelectorAll('firefly-commerce-dialogs, firefly-commerce-paywall-dialog, sp-dialog-base, susi-modal')) : [];
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
    overlays_path.write_text(header + new_func, encoding="utf-8")
    print("SUCCESS: overlays.py updated with perfect commerce overlay suppression!")
