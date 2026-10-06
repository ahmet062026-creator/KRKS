with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace physical newlines followed by quote
text = text.replace('{user_name}.\n\n"', '{user_name}.\\n\\n"')

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
