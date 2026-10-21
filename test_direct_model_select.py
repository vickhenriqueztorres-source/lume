import asyncio
from patchright.async_api import async_playwright
from pathlib import Path

profile_dir = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\data\chrome_profile")

async def test_set_model():
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
        
        # 1. Dismiss promo via JS
        js_dismiss = """
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
        """
        await page.evaluate(js_dismiss)
        await asyncio.sleep(1)
        
        # 2. Select Kling 2.5 Turbo via JS dispatch or trigger click
        picker = page.get_by_test_id("firefly-picker-model")
        print("Picker count:", await picker.count())
        
        # Open picker
        await picker.click()
        await asyncio.sleep(1)
        
        # Click Kling 2.5 item
        item = page.get_by_test_id("firefly-menu-item-ugs:video:kling@kling_v2_5_turbo_pro_i2v")
        print("Item count:", await item.count(), "visible:", await item.is_visible())
        if await item.count() > 0:
            await item.click()
            print("Clicked item successfully!")
        
        await asyncio.sleep(2)
        shot_path = r"C:\Users\brend\.gemini\antigravity\brain\3b5e0170-6ee3-479d-9a76-5894259c6e51\test_model_direct_select.png"
        await page.screenshot(path=shot_path)
        print("Screenshot saved to", shot_path)
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(test_set_model())
