import requests, json, re

r = requests.get('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/js/warehouse.js', timeout=30)
js = r.text

# Find deptData
idx = js.find('var deptData')
print(f'var deptData at position: {idx}')

# Find "new Array("
idx2 = js.find('new Array(', idx)
print(f'new Array( at position: {idx2}')

# Check what's between var deptData and new Array(
between = js[idx:idx2+20]
print(f'Between: ...{between[-30:]}...')

# Find matching close paren for new Array(
start = idx2 + len('new Array(')
print(f'Char at start position ({start}): "{js[start]}" (ord={ord(js[start])})')
print(f'Chars around start: {repr(js[start:start+50])}')

# Search for ALL "var" declarations
for m in re.finditer(r'var\s+(\w+)\s*=', js):
    pos = m.start()
    name = m.group(1)
    print(f'  var {name} at position {pos}: {repr(js[pos:pos+80])}')
    if pos > 100000:
        break  # stop after first few

print(f'Content from {start} to {end}')
raw = js[start:end]
print(f'Raw length: {len(raw)} bytes')

print(f'Array content from {start} to {end}')
print(f'Length: {end - start} bytes')

raw = js[start:end]
print(f'First 100 chars: {raw[:100]}')
print(f'Last 100 chars: {raw[-100:]}')

# Check if 101001 exists in the raw data
print(f'\nContains "101001": {"101001" in raw}')
print(f'Contains 102001: {"102001" in raw}')

# Try a simpler parsing approach - just find all dept entries by matching our codes
dept_codes = ['101001', '102001', '104001']
for code in dept_codes:
    pos = raw.find('"' + code + '"')
    print(f'\n{code} at position {pos} in raw')
    if pos >= 0:
        snippet = raw[max(0,pos-50):pos+200]
        print(f'Context: {snippet}')
