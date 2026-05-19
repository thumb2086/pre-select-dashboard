import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/index.html')
    page.wait_for_load_state('networkidle')
    
    # Fill keyword and search
    page.fill('input[name="keywordInput"]', '102001')
    page.click('input[name="searchBtn"]')
    page.wait_for_load_state('networkidle')
    print(f'Search URL: {page.url}')
    
    content = page.content()
    with open('search_102001.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    if '102001' in content:
        print(f'Found 102001 in results! Page size: {len(content)} bytes')
        
        # Extract the table data
        data = page.evaluate('''() => {
            const tables = document.querySelectorAll('table');
            const results = [];
            tables.forEach((table, ti) => {
                const rows = table.querySelectorAll('tr');
                rows.forEach((row, ri) => {
                    const cells = row.querySelectorAll('td, th');
                    if (cells.length > 0) {
                        results.push({
                            table: ti,
                            row: ri,
                            cells: Array.from(cells).map(c => c.innerText.trim())
                        });
                    }
                });
            });
            return results;
        }''')
        
        for d in data[:50]:
            print(f'T{table[d["table"]]} R{d["row"]}: {d["cells"]}')
    else:
        print(f'102001 not found. Page title: {page.title()}')
        links = page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a[href]')).map(a => a.href).filter(h => h.includes('schoolQuery'));
        }''')
        print(f'School query links: {links}')
    
    browser.close()
