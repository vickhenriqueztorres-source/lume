import asyncio
from patchright.async_api import async_playwright
from pathlib import Path

profile_dir = Path(r"D:\agents 3.0 brecha - antigravity\canalbrecha\firefly-automation\data\chrome_profile")

async def check():
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
        
        shot_path = r"C:\Users\brend\.gemini\antigravity\brain\3b5e0170-6ee3-479d-9a76-5894259c6e51\check_current_generation.png"
        await page.screenshot(path=shot_path)
        print("Screenshot saved to", shot_path)
        
        # Check download button
        btn = page.get_by_test_id("generate-video-download-button")
        has_dl = await btn.count() > 0 and await btn.is_visible()
        print("Download button visible:", has_dl)
        
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(check())
