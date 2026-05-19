import requests
r = requests.get('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/js/warehouse.js', timeout=30)
js = r.text

# deptData starts at position 4994
# Find the content between deptData's new Array( and the next var/function
dept_start = js.find('new Array(', 4994) + len('new Array(')

# Find next var declaration after deptData or end of file
next_decl = len(js)
for i in range(dept_start, min(dept_start + 50000, len(js))):
    if js[i:i+4] == 'var ' or js[i:i+4] == 'func':
        print(f'Next declaration at position {i}: {repr(js[i:i+60])}')
        next_decl = i
        break

# Get the content between dept_start and next_decl
if next_decl == len(js):
    print('No next declaration found, using all remaining content')
content = js[dept_start:next_decl]
print(f'deptData content: {len(content)} bytes')
print(f'First 200 chars: {repr(content[:200])}')
print(f'Last 200 chars: {repr(content[-200:])}')

# Find the last ')' which closes new Array(
last_close = content.rfind(')')
print(f'\nLast closing paren at position {last_close}')
if last_close > 0:
    print(f'Around last paren: {repr(content[max(0,last_close-10):last_close+10])}')

# Check for 101001
print(f'\nContains "101001": {"101001" in content}')
idx = content.find('"101001"')
if idx < 0:
    idx = content.find("'101001'")
if idx >= 0:
    print(f'Found 101001 at {idx}')
    print(f'Context: {repr(content[max(0,idx-50):idx+200])}')
else:
    print('101001 not found in deptData content')
    
    # Check what deptData actually contains - look for known dept codes
    for code in ['101001', '102001', '104001']:
        idx = content.find(code)
        if idx >= 0:
            print(f'\n{code} found at {idx} (unquoted)')
            print(f'Context: {repr(content[max(0,idx-50):idx+300])}')
