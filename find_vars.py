import requests
r = requests.get('https://www.jctv.ntut.edu.tw/downloads/115/apply/ugcdrom/js/warehouse.js', timeout=30)
js = r.text

# Find all "var name =" patterns in first 100KB
for i in range(0, 100000):
    if js[i:i+4] == 'var ':
        end = js.find('=', i)
        if end > 0 and end - i < 50:
            name = js[i+4:end].strip()
            print(f'Position {i}: var {name}')
            i = end
