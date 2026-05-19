import requests, json, re

r = requests.get('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/js/warehouse.js', timeout=30)
js = r.text

# Find deptData start
start = js.find('new Array(') + len('new Array(')
last_semi = js.rfind(';')
raw = js[start:last_semi]

# Find first deptData entry (skip collegeData which comes first)
# Find "105" college code which is first dept entry
dept_start = raw.find("'105'")
bracket_start = raw.rfind('[', 0, dept_start)
first_bracket = bracket_start
depth = 0
in_str = False
end = first_bracket
for j in range(first_bracket, len(raw)):
    c = raw[j]
    if c == "'" and (j == 0 or raw[j-1] != '\\'):
        in_str = not in_str
    elif not in_str:
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                end = j + 1
                break

entry_str = raw[first_bracket:end]
print(f'Raw entry ({len(entry_str)} bytes):')
print(repr(entry_str[:300]))

# Try parsing approach 1: replace all ' with "
try1 = entry_str.replace("'", '"')
try1 = try1.replace('"True"', '"True"').replace('"False"', '"False"')
try1 = try1.replace('True', '"True"').replace('False', '"False"')
try1 = try1.replace('"True"', '"True"').replace('"False"', '"False"')
try1 = try1.replace('"True"', '"True"').replace('"False"', '"False"')
print(f'\nApproach 1 first 300: {try1[:300]}')
try:
    result = json.loads(try1)
    print(f'Approach 1 SUCCESS: {len(result)} fields')
    print(f'Fields 0-5: {result[:6]}')
except json.JSONDecodeError as e:
    print(f'Approach 1 FAILED: {e}')

# Approach 2: use ast.literal_eval
import ast
try:
    result = ast.literal_eval(entry_str)
    print(f'\nApproach 2 (ast) SUCCESS: {len(result)} fields')
    print(f'Fields 0-5: {result[:6]}')
except Exception as e:
    print(f'\nApproach 2 FAILED: {e}')

# Approach 3: parse manually
print('\nTrying manual field parsing...')
fields = []
i = 0
in_str = False
current = ''
while i < len(entry_str):
    c = entry_str[i]
    if c == "'":
        if in_str:
            # end of string
            fields.append(current)
            current = ''
            in_str = False
        else:
            in_str = True
            current = ''
    elif c == ',' and not in_str:
        pass  # skip commas between fields
    elif c in '[]' and not in_str:
        pass
    elif in_str:
        current += c
    i += 1
print(f'Manually parsed {len(fields)} fields')
print(f'Fields 0-5: {fields[:6]}')
