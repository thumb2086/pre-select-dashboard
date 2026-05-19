import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/index.html')
    page.wait_for_load_state('networkidle')
    
    # Check what searchBtn does
    btn_info = page.evaluate('''() => {
        const btn = document.querySelector('input[name="searchBtn"]');
        if (!btn) return 'not found';
        return {
            type: btn.type,
            value: btn.value,
            onclick: btn.onclick ? btn.onclick.toString().substring(0, 500) : 'none',
            id: btn.id,
            className: btn.className,
        };
    }''')
    print(f'Search button: {btn_info}')
    
    # Also check the form's onsubmit
    form_info = page.evaluate('''() => {
        const form = document.querySelector('form');
        if (!form) return 'no form';
        return {
            action: form.action,
            method: form.method,
            onsubmit: form.onsubmit ? form.onsubmit.toString().substring(0, 500) : 'none',
            target: form.target,
        };
    }''')
    print(f'Form: {form_info}')
    
    # Look at all script tags for search function
    scripts = page.evaluate('''() => {
        const scripts = document.querySelectorAll('script');
        return Array.from(scripts).slice(0, 10).map(s => ({
            src: s.src,
            text: (s.text || '').substring(0, 300)
        }));
    }''')
    for s in scripts:
        if s['src']:
            print(f'Script src: {s["src"]}')
        elif s['text']:
            print(f'Script inline: {s["text"][:200]}')
    
    browser.close()
