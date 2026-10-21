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
        
        # Test dismiss script with firefly-commerce-dialogs included
        res = await page.evaluate('''() => {
            let clicked = 0;
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
                        clicked++;
                    } catch(e){}
                }
                const dialogs = root.querySelectorAll ? Array.from(root.querySelectorAll('firefly-commerce-dialogs, firefly-commerce-paywall-dialog, sp-dialog-base, susi-modal')) : [];
                for (const d of dialogs) {
                    if (d.shadowRoot) walk(d.shadowRoot);
                }
            }
            walk(document);
            return { clicked, hadCd: !!cd };
        }''')
        print("Dismiss result:", res)
        await asyncio.sleep(1)
        
        # Now click picker
        picker = page.get_by_test_id("firefly-picker-model")
        await picker.click(timeout=3000)
        print("Picker clicked successfully without any interception!")
        
        # Select Kling 2.5
        item = page.get_by_test_id("firefly-menu-item-ugs:video:kling@kling_v2_5_turbo_pro_i2v")
        await item.click(timeout=3000)
        print("Kling 2.5 selected successfully!")
        
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(test())
