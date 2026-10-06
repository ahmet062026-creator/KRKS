import re
with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix literal newlines inside strings
def remove_newlines_in_strings(match):
    return match.group(0).replace('\n', '\\n')

# Find string literals and replace literal newlines with \n
text = re.sub(r'f"Sen MEBOT.*?Kullanıcı: \{user_name\}\.\n\n"', r'f"Sen MEBOT 0.1\'sin: EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL\'sin. Kullanıcı: {user_name}.\\n\\n"', text, flags=re.DOTALL)
text = text.replace('YER ALMAMALIDIR.\n"', 'YER ALMAMALIDIR.\\n"')
text = text.replace('akıl yürütme ile çöz.\n"', 'akıl yürütme ile çöz.\\n"')
text = text.replace('açıkça yaz.\n"', 'açıkça yaz.\\n"')
text = text.replace('tablo yap.\n"', 'tablo yap.\\n"')
text = re.sub(r'f"Sen MEBOT adında.*?Kullanıcı: \{user_name\}\.\n\n"', r'f"Sen MEBOT adında çok yönlü bir yapay zekâ asistanısın. Kullanıcı: {user_name}.\\n\\n"', text, flags=re.DOTALL)
text = text.replace('açıkça yaz.\n"', 'açıkça yaz.\\n"')

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Fixed!")
