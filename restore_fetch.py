with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
text = re.sub(r'const API_BASE_URL = .*?const response = await fetch\(API_BASE_URL \+ \'/api/chat\'', 'const response = await fetch(\'/api/chat\'', text, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(text)
