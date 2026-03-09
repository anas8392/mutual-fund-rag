import asyncio
import csv
from playwright.async_api import async_playwright

urls = [
    "https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth-option-3184",
    "https://www.indmoney.com/mutual-funds/sbi-elss-tax-saver-fund-direct-growth-2754",
    "https://www.indmoney.com/mutual-funds/hdfc-small-cap-fund-direct-growth-option-3580",
    "https://www.indmoney.com/mutual-funds/aditya-birla-sun-life-gold-fund-direct-plan-growth-3706",
    "https://www.indmoney.com/mutual-funds/hsbc-small-cap-fund-fund-direct-growth-3593"
]

def get_value_backwards(lines, key, exact=True):
    for i in range(len(lines)-1, -1, -1):
        l = lines[i]
        if exact:
            if l.lower() == key.lower() and i + 1 < len(lines):
                # Ensure the next line isn't a table header
                if "1y return" not in lines[i+1].lower() and "buy" not in lines[i+1].lower():
                    return lines[i+1]
        else:
            if key.lower() in l.lower() and i + 1 < len(lines):
                if "1y return" not in lines[i+1].lower() and "buy" not in lines[i+1].lower():
                    return lines[i+1]
    return "N/A"

def extract_statements_info(lines):
    for l in lines:
        if "statement" in l.lower() and len(l) > 20:
            return l
    return "Not explicitly mentioned on fund page. (Standard process: Use MFCentral, CAMS/KFintech, or Indmoney Portfolio reports)"

async def main():
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        for url in urls:
            try:
                print(f"Scraping: {url}")
                page = await context.new_page()
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                text = await page.evaluate("document.body.innerText")
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                
                fund_name = url.split('/')[-1].replace('-', ' ').title()
                
                expense_ratio = get_value_backwards(lines, "Expense ratio")
                exit_load = get_value_backwards(lines, "Exit Load")
                lumpsum_sip = get_value_backwards(lines, "Min Lumpsum/SIP")
                min_sip = lumpsum_sip.split('/')[-1] if '/' in lumpsum_sip else lumpsum_sip
                
                lock_in = get_value_backwards(lines, "Lock In")
                riskometer = get_value_backwards(lines, "Risk")
                benchmark = get_value_backwards(lines, "Benchmark")
                statements = extract_statements_info(lines)
                
                results.append({
                    "Fund Name": fund_name,
                    "Source URL": url,
                    "Expense Ratio": expense_ratio,
                    "Exit Load": exit_load,
                    "Minimum SIP": min_sip,
                    "Lock-in": lock_in,
                    "Riskometer": riskometer,
                    "Benchmark": benchmark,
                    "How to download statements": statements
                })
                
                await page.close()
            except Exception as e:
                print(f"Failed to scrape {url}: {e}")
                
        await browser.close()
        
    if results:
        csv_file = "mutual_fund_data.csv"
        keys = results[0].keys()
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            dict_writer = csv.DictWriter(f, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(results)
        print(f"Successfully saved {len(results)} records to {csv_file}")

if __name__ == "__main__":
    asyncio.run(main())
