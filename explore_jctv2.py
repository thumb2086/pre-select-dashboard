from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/index.html')
    page.wait_for_load_state('networkidle')
    
    # Find all the search-related links/buttons
    all_links = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('a')).filter(a => a.href).map(a => ({
            text: a.innerText.trim().substring(0, 50),
            href: a.href
        }));
    }''')
    
    for l in all_links:
        print(f'Link: {l["text"]} -> {l["href"]}')
    
    # Try to navigate to schoolQuery directly
    page.goto('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/schoolQuery.php')
    page.wait_for_load_state('networkidle')
    print(f'\nDirect schoolQuery URL: {page.url}')
    
    # Check for form elements
    form_info = page.evaluate('''() => {
        const forms = document.querySelectorAll('form');
        return Array.from(forms).map((f, i) => ({
            action: f.action,
            method: f.method,
            inputs: Array.from(f.querySelectorAll('input, select, button')).slice(0, 30).map(el => ({
                tag: el.tagName,
                name: el.name || el.id,
                type: el.type,
                value: el.value,
                placeholder: el.placeholder || ''
            }))
        }));
    }''')
    
    for f in form_info:
        print(f'\nForm action={f["action"]}, method={f["method"]}')
        for inp in f['inputs']:
            print(f'  {inp["tag"]}: name={inp["name"]}, type={inp["type"]} value={inp["value"]} placeholder={inp["placeholder"]}')
    
    # Check for select options
    selects = page.evaluate('''() => {
        return Array.from(document.querySelectorAll('select[name]')).map(sel => ({
            name: sel.name,
            options: Array.from(sel.options).map(o => ({ v: o.value, t: o.text.trim().substring(0, 50) }))
        }));
    }''')
    
    for s in selects:
        print(f'\nSelect: {s["name"]} ({len(s["options"])} options)')
        for o in s['options'][:10]:
            print(f'  {o["v"]}: {o["t"]}')
    
    browser.close()
