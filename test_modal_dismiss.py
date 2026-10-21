import asyncio
from patchright.async_api import async_playwright
from pathlib import Path

profile_dir = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\data\chrome_profile")

async def test_close():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            channel="chrome",
            headless=True,
            viewport={"width": 1920, "height": 1080},
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://firefly.adobe.com/generate/video", wait_until="domcontentloaded")
        await asyncio.sleep(4)
        
        js_dismiss = """
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
        """
        res = await page.evaluate(js_dismiss)
        print("Dismissed items clicked:", res)
        await asyncio.sleep(2)
        
        # If modal is still present, try escape
        await page.keyboard.press("Escape")
        await asyncio.sleep(1)
        
        shot_path = r"C:\Users\brend\.gemini\antigravity\brain\3b5e0170-6ee3-479d-9a76-5894259c6e51\after_modal_dismiss.png"
        await page.screenshot(path=shot_path)
        print("Screenshot saved to", shot_path)
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(test_close())
