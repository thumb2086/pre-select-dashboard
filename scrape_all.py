from playwright.sync_api import sync_playwright
import json, os, time

BASE = 'https://photo.taivs.tp.edu.tw/enter42/preSelect'
OUTPUT_DIR = r'C:\Users\CPXru\Desktop\thumb\program\分析'

def login(page):
    page.goto(f'{BASE}/departmentList/studentsList.php')
    page.fill('#examId', '52010375')
    page.fill('#pw', '8138@daan')
    page.click('button[type=submit]')
    page.wait_for_load_state('networkidle')
    print(f'登入成功: {page.url}')

def scrape_students(page, depid, depname):
    page.goto(f'{BASE}/departmentList/')
    page.wait_for_load_state('networkidle')
    page.evaluate(f'studentsList("{depid}")')
    page.wait_for_load_state('networkidle')
    time.sleep(0.5)
    
    data = page.evaluate('''() => {
        if (typeof studentArray === 'undefined') return null;
        return studentArray.map((s, i) => ({
            no: i + 1,
            examId: s.examId,
            chinese: s.chinese,
            english: s.english,
            math: s.math,
            pro1: s.pro1,
            pro2: s.pro2,
            total: s.total
        }));
    }''')
    
    if data and len(data) > 0:
        filename = f'scores_{depid}.csv'
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('校系代碼,序號,准考證號,國文,英文,數學,專一,專二,總分\n')
            for s in data:
                f.write(f'{depid},{s["no"]},{s["examId"]},{s["chinese"]},{s["english"]},{s["math"]},{s["pro1"]},{s["pro2"]},{s["total"]}\n')
        print(f'  {depid} {depname}: {len(data)} 筆 -> {filename}')
        return len(data)
    else:
        print(f'  {depid} {depname}: 無資料')
        return 0

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        login(page)
        
        page.goto(f'{BASE}/departmentList/')
        page.wait_for_load_state('networkidle')
        
        depts = page.evaluate('''() => {
            const rows = document.querySelectorAll('table tr');
            const result = [];
            for (const row of rows) {
                const btn = row.querySelector('button.btn-info');
                if (!btn) continue;
                const onclick = btn.getAttribute('onclick');
                if (!onclick) continue;
                const match = onclick.match(/studentsList\('(\d+)'\)/);
                if (!match) continue;
                const depid = match[1];
                const link = row.querySelector('a');
                const name = link ? link.innerText.trim() : depid;
                result.push({ depid, name, count: btn.innerText.trim() });
            }
            return result;
        }''')
        
        print(f'\n找到 {len(depts)} 個有預選人數的校系\n')
        
        total = 0
        for d in depts:
            count = d['count']
            if count == '無人選' or count == '0':
                continue
            n = scrape_students(page, d['depid'], d['name'])
            total += n
        
        print(f'\n完成！共匯入 {total} 筆成績資料')
        browser.close()

if __name__ == '__main__':
    main()
