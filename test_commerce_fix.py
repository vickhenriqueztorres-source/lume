import asyncio
from patchright.async_api import async_playwright
from pathlib import Path

profile_dir = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\data\chrome_profile")

async def test():
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
        
        # Test dismiss script
        res = await page.evaluate('''() => {
            let dismissed = false;
            const cd = document.querySelector('firefly-commerce-dialogs');
            if (cd) {
                cd.style.pointerEvents = 'none';
                if (cd.shadowRoot) {
                    const pd = cd.shadowRoot.querySelector('firefly-commerce-paywall-dialog');
                    if (pd && pd.shadowRoot) {
                        const btn = pd.shadowRoot.querySelector('sp-close-button, [aria-label*="Fechar" i], [aria-label*="Close" i]');
                        if (btn) { btn.click(); dismissed = true; }
                        const base = pd.shadowRoot.querySelector('sp-dialog-base');
                        if (base && base.shadowRoot) {
                            const btn2 = base.shadowRoot.querySelector('sp-close-button');
                            if (btn2) { btn2.click(); dismissed = true; }
                        }
                    }
                }
            }
            return { dismissed };
        }''')
        print("Dismiss result:", res)
        await asyncio.sleep(1)
        
        # Now click picker
        picker = page.get_by_test_id("firefly-picker-model")
        await picker.click(timeout=3000)
        print("Picker clicked successfully without any interception!")
        
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(test())
