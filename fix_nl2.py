with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('base_instruction + "\n\n"', 'base_instruction + "\\n\\n"')

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
