import asyncio
from playwright.async_api import async_playwright

async def main():
    url = "https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth-option-3184"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using a typical user agent
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        # Navigate and wait for network idle to ensure JS loads content if any
        await page.goto(url, wait_until="networkidle")
        
        content = await page.content()
        with open("sample.html", "w", encoding="utf-8") as f:
            f.write(content)
        
        print("Dom saved to sample.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
