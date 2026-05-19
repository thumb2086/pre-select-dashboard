import requests, json, re, os

DATA_DIR = r'C:\Users\CPXru\Desktop\thumb\program\分析'

# Download warehouse.js
url = 'https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/js/warehouse.js'
print('Downloading warehouse.js...')
r = requests.get(url, timeout=30)
js = r.text
print(f'Downloaded: {len(js)} bytes')

# Get our departments' codes
dept_codes = set()
for f in os.listdir(DATA_DIR):
    m = re.match(r'scores_(\d+)\.csv', f)
    if m:
        dept_codes.add(m.group(1))
print(f'Looking for {len(dept_codes)} departments')

# Parse deptData from JS
# deptData format: [colCode, deptCode, deptName, categoryCode, ...lots of fields...]
# Fields of interest (0-indexed):
# 0: college code
# 1: dept code (our depid)
# 2: dept name
# 3: category code
# 5: general quota (招生名額-一般)
# 6: general expected interviews (預計甄試人數)
# 17: chinese filter ratio (國文篩選倍率)
# 18: english filter ratio
# 19: math filter ratio
# 20: pro1 filter ratio
# 21: pro2 filter ratio
# 22-26: 同級分超額篩選 flags
# 27-31: score weight multipliers (加權倍數)
# 32: 統測成績占總成績比率
# 33-47: 第二階段指定項目 (5个项目, each has name, low score, high score, rate)
# 48: 證照或得獎加分
# 49-54: 同分參酌順序
# 55: 指定項目甄試費
# 56: 學習歷程上傳截止時間
# 57: 公告第二階段甄試名單日期
# 58: 甄試日期
# 59-63: various dates
# 64-67: 上傳文件件數上限 (A,B-1,B-2,C)
# 68-75: 多元表現C1-C8 flags
# 76-78: D-1,D-2,D-3 件數
# 79: 學習歷程備審資料上傳說明
# 80: 指定項目甄試說明
# 81: 備註

# Extract deptData array - uses new Array(...) syntax
match = re.search(r'var deptData\s*=\s*new Array\(', js)
if not match:
    print('Could not find deptData in JS')
    exit()

start = match.end()
# Find last semicolon (end of this var statement)
last_semi = js.rfind(';')
if last_semi <= start:
    print('Could not find end of deptData')
    exit()
end = last_semi

raw = js[start:end]
print(f'Raw deptData length: {len(raw)} bytes')

all_depts = []

# Parse entry by entry using regex
# Each entry: ['field1','field2',...] or ['field1','field2',...],
# Fields can be quoted strings '' or unquoted numbers
# Use bracket matching
i = 0
while i < len(raw):
    # Find next '['
    start_idx = raw.find('[', i)
    if start_idx < 0:
        break
    # Find matching ']'
    depth = 0
    in_string = False
    end_idx = start_idx
    for j in range(start_idx, len(raw)):
        c = raw[j]
        if c == "'" and (j == 0 or raw[j-1] != '\\'):
            in_string = not in_string
        elif not in_string:
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    end_idx = j + 1
                    break
    if depth != 0:
        break
    
    entry_str = raw[start_idx:end_idx]
    i = end_idx
    
    # Clean up the entry for JSON parsing
    # Replace JS True/False
    entry_str = entry_str.replace("'True'", '"True"').replace("'False'", '"False"')
    entry_str = entry_str.replace("True", '"True"').replace("False", '"False"')
    # Replace single quotes with double quotes
    entry_str = entry_str.replace("'", '"')
    
    try:
        entry = json.loads(entry_str)
        if len(entry) > 2:  # basic sanity check
            all_depts.append(entry)
    except json.JSONDecodeError:
        pass  # skip malformed entries

print(f'Parsed {len(all_depts)} total departments')

# Build lookup by dept code
dept_lookup = {}
for d in all_depts:
    code = d[1]
    dept_lookup[code] = d
    
print(f'Parsed {len(all_depts)} total departments')
print(f'Found {len([c for c in dept_codes if c in dept_lookup])} matching our departments')

# Extract relevant info for our departments
results = {}
for code in sorted(dept_codes):
    if code not in dept_lookup:
        continue
    d = dept_lookup[code]
    
    # Fields
    item = {
        'depid': code,
        'name': d[2],
        'college_name': '',  # will fill from collegeData
        'category_code': d[3],
        'quota_general': d[5],
        'quota_low_income': d[7],
        'quota_indigenous': d[9],
        'quota_outlying': d[11],
        'expected_interviews': d[6],  # 預計甄試人數
        'filter_ratios': {
            'chinese': d[17] or '--',
            'english': d[18] or '--',
            'math': d[19] or '--',
            'pro1': d[20] or '--',
            'pro2': d[21] or '--',
        },
        'weight_multipliers': {
            'chinese': d[27],
            'english': d[28],
            'math': d[29],
            'pro1': d[30],
            'pro2': d[31],
        },
        'tcte_score_rate': d[32],  # 統測成績占總成績比率
        'assign_items': [],
        'cert_bonus': d[48],  # 證照或得獎加分
        'ref_order': [d[49], d[50], d[51], d[52], d[53], d[54]],
        'interview_fee': d[55],
        'portfolio_deadline': d[56],
        'interview_date': d[58],
        'result_announce_date': d[57],
        'upload_limits': {
            'A': d[64],
            'B1': d[65],
            'B2': d[66],
            'C': d[67],
            'D1': d[76],
            'D2': d[77],
            'D3': d[78],
        },
        'notes': d[81],
    }
    
    # Second stage items (up to 5)
    for i in range(5):
        base = 33 + i * 4
        name = d[base]
        if name and name != '--':
            item['assign_items'].append({
                'name': name,
                'min_score': d[base + 1] or '--',
                'max_score': '100',
                'rate': d[base + 3] or '--',
            })
    
    results[code] = item

# Save
out_path = os.path.join(DATA_DIR, 'dashboard', 'data', 'dept_details.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f'Saved {len(results)} departments to {out_path}')

# Also extract category data for reference
cat_match = re.search(r'tcategoryData\s*=\s*new Array\(', js)
if not cat_match:
    cat_match = re.search(r'categoryData\s*=\s*new Array\(', js)
if cat_match:
    cat_start = cat_match.end()
    # Find end - the next var declaration or end of statement
    cat_end_search = js.find('\nvar ', cat_start)
    if cat_end_search < 0:
        cat_end_search = js.find(';', cat_start)
    if cat_end_search > cat_start:
        cat_raw = js[cat_start:cat_end_search]
        cats = []
        i = 0
        while i < len(cat_raw):
            si = cat_raw.find('[', i)
            if si < 0: break
            depth = 0
            in_str = False
            ei = si
            for j in range(si, len(cat_raw)):
                c2 = cat_raw[j]
                if c2 == "'" and (j == 0 or cat_raw[j-1] != '\\'):
                    in_str = not in_str
                elif not in_str:
                    if c2 == '[': depth += 1
                    elif c2 == ']':
                        depth -= 1
                        if depth == 0: ei = j + 1; break
            if depth != 0: break
            try:
                entry = json.loads(cat_raw[si:ei].replace("'", '"'))
                cats.append(entry)
            except: pass
            i = ei
    
    if cats:
        cat_lookup = {c[0]: c for c in cats}
        for code in results:
            cat_code = results[code]['category_code']
            if cat_code in cat_lookup:
                results[code]['category'] = f'{cat_lookup[cat_code][1]} {cat_lookup[cat_code][2]}'
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f'Added category info')
    else:
        print('No category data found')

print('Done!')
