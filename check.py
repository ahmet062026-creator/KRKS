import re

with open('app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

ids_in_js = re.findall(r"getElementById\('([^']+)'\)", js_content)
missing = []
for el_id in set(ids_in_js):
    if f'id="{el_id}"' not in html_content:
        missing.append(el_id)

print("Missing IDs:", missing)

try:
    import js2py
    js2py.parse_js(js_content)
    print("JS Parsed successfully!")
except Exception as e:
    print("JS Syntax Error:", str(e))
