import requests, re

r = requests.get('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/js/warehouse.js', timeout=30)
text = r.text

# Search for variable definitions in first 100KB
vars_found = re.findall(r'(var|let|const)\s+(\w+)\s*=', text[:100000])
print('Variables found (first 100KB):')
for v in vars_found:
    print(f'  {v[0]} {v[1]}')

# Find the deptData var and check its start
dept_idx = text.find('var deptData')
print(f'\ndeptData found at position: {dept_idx}')
if dept_idx >= 0:
    print(text[dept_idx:dept_idx+200])
    
    # Find the = sign
    eq_idx = text.find('=', dept_idx)
    if eq_idx >= 0:
        # Extract the array content (find matching brackets)
        start_arr = text.find('[', eq_idx)
        if start_arr >= 0:
            depth = 0
            end_arr = start_arr
            for i in range(start_arr, min(start_arr + 500000, len(text))):
                if text[i] == '[': depth += 1
                elif text[i] == ']': 
                    depth -= 1
                    if depth == 0:
                        end_arr = i + 1
                        break
            print(f'\nArray from {start_arr} to {end_arr} ({end_arr - start_arr} bytes)')
            snippet = text[start_arr:min(start_arr + 500, end_arr)]
            print(f'Preview: {snippet[:500]}')

# Search for specific dept code to understand format
for code in ['101001', '102001', '104001']:
    idx = text.find('"' + code + '"')
    if idx >= 0:
        start = max(0, idx - 50)
        end = min(len(text), idx + 300)
        snippet = text[start:end]
        print(f'\nFound {code} at position {idx}:')
        print(snippet[:400])
