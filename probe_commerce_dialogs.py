import asyncio
from patchright.async_api import async_playwright
from pathlib import Path

profile_dir = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\data\chrome_profile")

async def probe():
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
        
        info = await page.evaluate('''() => {
            const cd = document.querySelector('firefly-commerce-dialogs');
            if (!cd) return { found: false };
            const res = {
                tag: cd.tagName,
                hasShadow: !!cd.shadowRoot,
                children: []
            };
            if (cd.shadowRoot) {
                const els = Array.from(cd.shadowRoot.querySelectorAll('*'));
                res.children = els.map(e => ({
                    tag: e.tagName,
                    aria: e.getAttribute('aria-label'),
                    testid: e.getAttribute('data-testid'),
                    hasShadow: !!e.shadowRoot
                })).slice(0, 20);
            }
            return res;
        }''')
        print("COMMERCE DIALOGS INFO:")
        print(info)
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(probe())
