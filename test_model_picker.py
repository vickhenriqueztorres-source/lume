import asyncio
from patchright.async_api import async_playwright
from pathlib import Path

profile_dir = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\data\chrome_profile")

async def test_picker():
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
        
        # Dismiss modals
        from firefly_bot.overlays import dismiss_overlays
        import logging
        logger = logging.getLogger("test")
        await dismiss_overlays(page, None, logger, 999)
        await asyncio.sleep(1)
        
        # Open model dropdown
        trigger = page.get_by_test_id("firefly-picker-model").locator("button, [role='button'], sp-picker").first
        if not await trigger.is_visible():
            trigger = page.locator("[data-testid='firefly-picker-model']").first
        print("Clicking trigger...")
        await trigger.click()
        await asyncio.sleep(1)
        
        # Scan for menu items
        items = await page.evaluate('''() => {
            const list = [];
            function scan(root) {
                if (!root) return;
                const els = root.querySelectorAll ? Array.from(root.querySelectorAll('sp-menu-item, [role=\"option\"], [data-testid*=\"menu-item\"]')) : [];
                for (const el of els) {
                    list.push({
                        tag: el.tagName.toLowerCase(),
                        testid: el.getAttribute('data-testid') || '',
                        value: el.getAttribute('value') || '',
                        text: (el.innerText || el.textContent || '').trim()
                    });
                }
                const all = root.querySelectorAll ? Array.from(root.querySelectorAll('*')) : [];
                for (const el of all) {
                    if (el.shadowRoot) scan(el.shadowRoot);
                }
            }
            scan(document);
            return list;
        }''')
        print(f"Found {len(items)} menu items:")
        for it in items:
            print(it)
            
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(test_picker())
