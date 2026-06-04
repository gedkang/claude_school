import asyncio
from playwright.async_api import async_playwright

async def take_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1400, "height": 900})
        await page.goto("http://localhost:8501", wait_until="networkidle")
        await page.screenshot(path="c:\\biyam_work\\dashboard_screenshot.png")
        print("스크린샷 저장됨: c:\\biyam_work\\dashboard_screenshot.png")
        await browser.close()

asyncio.run(take_screenshot())
