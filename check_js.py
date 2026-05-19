import re

with open('C:\\Users\\CPXru\\Desktop\\thumb\\program\\分析\\dashboard\\index.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
js = match.group(1)
lines = js.split('\n')

in_single = False
in_double = False
in_backtick = False
depth = 0

for i, line in enumerate(lines, 1):
    j = 0
    while j < len(line):
        c = line[j]
        nc = line[j+1] if j+1 < len(line) else ''

        if c == "'" and not in_double and not in_backtick:
            in_single = not in_single
        elif c == '"' and not in_single and not in_backtick:
            in_double = not in_double
        elif c == '`' and not in_single and not in_double:
            in_backtick = not in_backtick
        elif c == '$' and nc == '{' and in_backtick:
            depth += 1
            j += 1
        elif c == '}' and in_backtick and depth > 0:
            depth -= 1

        if c == '<' and not in_single and not in_double and not in_backtick and depth == 0:
            ctx = line[max(0,j-15):j+15]
            print(f'Line {i}, col {j+1}: stray <: ...{ctx}...')

        j += 1

print('Scan complete')
