import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Try direct query with parameters
    params = '?schoolId=102001'
    page.goto(f'https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/schoolQuery.php{params}')
    page.wait_for_load_state('networkidle')
    print(f'URL: {page.url}')
    
    content = page.content()
    # Check what we got
    if '機械' in content or '102001' in content:
        print(f'Found 102001 in page ({len(content)} bytes)')
        # Save for inspection
        with open('school_query.html', 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        print(f'No 102001 found. Trying search form...')
        # Go back to index and try to search
        page.goto('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/index.html')
        page.wait_for_load_state('networkidle')
        
        # Fill in keyword and submit
        # Look for the keyword input
        kw = page.query_selector('input[name="keyword"]')
        if kw:
            kw.fill('機械')
            page.query_selector('input[type="submit"]').click()
            page.wait_for_load_state('networkidle')
            print(f'Search URL: {page.url}')
            with open('search_result.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
        else:
            print('No keyword input found')
            # Dump all inputs
            inputs = page.evaluate('''() => {
                return Array.from(document.querySelectorAll('input, select')).map(el => ({
                    tag: el.tagName,
                    name: el.name || el.id,
                    type: el.type,
                    placeholder: el.placeholder || ''
                }));
            }''')
            for inp in inputs:
                print(f'  {inp}')
    
    browser.close()
