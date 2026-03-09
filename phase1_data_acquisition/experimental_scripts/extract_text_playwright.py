import asyncio
from playwright.async_api import async_playwright
import re

async def main():
    url = "https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth-option-3184"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        # Wait until network is idle to ensure all API calls for data are done
        await page.goto(url, wait_until="networkidle")
        
        # Get visible text
        text = await page.evaluate("document.body.innerText")
        with open("visible_text.txt", "w", encoding="utf-8") as f:
             f.write(text)
             
        # Find our targets in the text
        targets = ["Expense Ratio", "Exit Load", "Minimum SIP", "Lock-in", "Riskometer", "Benchmark", "statement"]
        
        print("--- EXTRACTED TARGETS ---")
        lines = text.split('\n')
        # Clean up empty lines
        lines = [l.strip() for l in lines if l.strip()]
        
        for idx, line in enumerate(lines):
            for t in targets:
                if t.lower() in line.lower():
                    # Print context (1 line before, the line, 3 lines after)
                    start = max(0, idx - 1)
                    end = min(len(lines), idx + 4)
                    print(f"\nTarget Match: {t}")
                    for i in range(start, end):
                        prefix = ">> " if i == idx else "   "
                        print(f"{prefix}{lines[i]}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
