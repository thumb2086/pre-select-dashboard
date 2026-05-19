from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/index.html')
    page.wait_for_load_state('networkidle')

    info = page.evaluate('''() => {
        const forms = document.querySelectorAll('form');
        const result = { forms: [] };
        forms.forEach((f, i) => {
            const formData = { index: i, action: f.action, method: f.method, inputs: [] };
            f.querySelectorAll('input[name], select[name], button').forEach(inp => {
                formData.inputs.push({
                    tag: inp.tagName,
                    name: inp.name,
                    type: inp.type,
                    value: inp.value
                });
            });
            result.forms.push(formData);
        });

        result.links = [];
        document.querySelectorAll('a').forEach(l => {
            const href = l.href;
            const txt = l.innerText.trim().substring(0, 60);
            if (href && (href.includes('schoolQuery') || href.includes('advancedQuery') || href.includes('query'))) {
                result.links.push({ txt, href });
            }
        });

        result.selects = [];
        document.querySelectorAll('select[name]').forEach(sel => {
            const opts = Array.from(sel.options).filter(o => o.value).map(o => ({ v: o.value, t: o.text.trim().substring(0, 40) }));
            if (opts.length > 0) {
                result.selects.push({ name: sel.name, opts: opts.slice(0, 8) });
            }
        });

        return result;
    }''')

    print(f'Forms: {len(info["forms"])}')
    for f in info['forms']:
        print(f'  Form {f["index"]}: action={f["action"]}, method={f["method"]}')
        for inp in f['inputs'][:15]:
            print(f'    {inp["tag"]}: name={inp["name"]}, type={inp["type"]}, value={inp["value"]}')

    print(f'\nLinks:')
    for l in info['links']:
        print(f'  {l["txt"]} -> {l["href"]}')

    print(f'\nSelects:')
    for s in info['selects']:
        print(f'  {s["name"]}: {s["opts"]}')

    browser.close()
