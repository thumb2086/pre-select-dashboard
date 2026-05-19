import requests, json, re, os, ast

DATA_DIR = r'C:\Users\CPXru\Desktop\thumb\program\分析'

print('Downloading warehouse.js...')
r = requests.get('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/js/warehouse.js', timeout=30)
js = r.text
print(f'Downloaded: {len(js)} bytes')

# Get our departments' codes
dept_codes = set()
for f in os.listdir(DATA_DIR):
    m = re.match(r'scores_(\d+)\.csv', f)
    if m:
        dept_codes.add(m.group(1))
print(f'Looking for {len(dept_codes)} departments')

# Find deptData content
idx = js.find('var deptData = new Array(')
if idx < 0:
    print('Could not find deptData')
    exit()

start = idx + len('var deptData = new Array(')
# Find the final ); that closes new Array()
# Search for ); followed by var/function or end of file
end = js.rfind(';')
if end <= start:
    print('Could not find end')
    exit()

raw = js[start:end]
print(f'Raw deptData: {len(raw)} bytes')

all_depts = []

# Parse by finding each entry [...]
i = 0
while i < len(raw):
    si = raw.find('[', i)
    if si < 0:
        break
    # Find matching ] respecting strings
    depth = 0
    in_str = False
    ei = si
    for j in range(si, len(raw)):
        c = raw[j]
        if c == "'":
            in_str = not in_str
        elif not in_str:
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    ei = j + 1
                    break
    if depth != 0:
        break
    
    entry_str = raw[si:ei]
    i = ei
    
    # Use ast.literal_eval to parse (it handles single-quoted strings)
    try:
        entry = ast.literal_eval(entry_str)
        if isinstance(entry, list) and len(entry) > 30:  # dept entries have ~82 fields
            all_depts.append(entry)
    except (ValueError, SyntaxError):
        pass

print(f'Parsed {len(all_depts)} total department entries')

# Build lookup
dept_lookup = {}
for d in all_depts:
    if len(d) > 2:
        dept_lookup[d[1]] = d

matched = [c for c in dept_codes if c in dept_lookup]
print(f'Found {len(matched)} matching our departments')
if matched:
    print(f'Examples: {matched[:5]}')

# Extract relevant info
results = {}
for code in sorted(dept_codes):
    if code not in dept_lookup:
        continue
    d = dept_lookup[code]
    
    assign_items = []
    for i2 in range(5):
        base = 33 + i2 * 4
        if base < len(d):
            name = d[base]
            if name and name != '--' and name != '':
                assign_items.append({
                    'name': name,
                    'min_score': d[base + 1] if base + 1 < len(d) else '',
                    'rate': d[base + 3] if base + 3 < len(d) else '',
                })
    
    item = {
        'depid': code,
        'name': d[2] if len(d) > 2 else '',
        'college_name': d[4] if len(d) > 4 else '',
        'category_code': d[3] if len(d) > 3 else '',
        'quota_general': d[5] if len(d) > 5 else 0,
        'expected_interviews': d[6] if len(d) > 6 else 0,
        'filter_ratios': {
            'chinese': d[17] if len(d) > 17 and d[17] else '--',
            'english': d[18] if len(d) > 18 and d[18] else '--',
            'math': d[19] if len(d) > 19 and d[19] else '--',
            'pro1': d[20] if len(d) > 20 and d[20] else '--',
            'pro2': d[21] if len(d) > 21 and d[21] else '--',
        },
        'weight_multipliers': {
            'chinese': d[27] if len(d) > 27 else 0,
            'english': d[28] if len(d) > 28 else 0,
            'math': d[29] if len(d) > 29 else 0,
            'pro1': d[30] if len(d) > 30 else 0,
            'pro2': d[31] if len(d) > 31 else 0,
        },
        'tcte_score_rate': d[32] if len(d) > 32 else 0,
        'assign_items': assign_items,
        'cert_bonus': d[48] if len(d) > 48 else 0,
        'ref_order': [d[i2] for i2 in range(49, 55) if i2 < len(d)],
        'interview_fee': d[55] if len(d) > 55 else '',
        'portfolio_deadline': d[56] if len(d) > 56 else '',
        'interview_date': d[58] if len(d) > 58 else '',
        'result_announce_date': d[57] if len(d) > 57 else '',
        'upload_limits': {
            'A': d[64] if len(d) > 64 else 0,
            'B1': d[65] if len(d) > 65 else 0,
            'B2': d[66] if len(d) > 66 else 0,
            'C': d[67] if len(d) > 67 else 0,
            'D1': d[76] if len(d) > 76 else 0,
            'D2': d[77] if len(d) > 77 else 0,
            'D3': d[78] if len(d) > 78 else 0,
        },
        'notes': d[81] if len(d) > 81 else '',
    }
    results[code] = item

# Save
out_path = os.path.join(DATA_DIR, 'dashboard', 'data', 'dept_details.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f'\nSaved {len(results)} departments to dept_details.json')

# Sample
if results:
    sample = list(results.values())[0]
    print(f'\nSample: {sample["depid"]} {sample["name"]}')
    print(f'  College: {sample["college_name"]}')
    print(f'  Filter ratios: {sample["filter_ratios"]}')
    print(f'  Weights: {sample["weight_multipliers"]}')
    print(f'  TCTE rate: {sample["tcte_score_rate"]}%')
    print(f'  Interview fee: {sample["interview_fee"]}')
    print(f'  Assign items: {len(sample["assign_items"])}')
    for a in sample['assign_items']:
        print(f'    - {a["name"]}: {a["rate"]}')
print('Done!')
