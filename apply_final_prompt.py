import re
import sys

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace the entire instruction block
new_prompt = r"""    base_instruction = (
        f"Sen MEBOT adında çok yönlü bir yapay zekâ asistanısın. Kullanıcı: {user_name}.\n\n"
        "Kullanıcı senden kod istiyorsa doğrudan optimize edilmiş kodu ve açıklamasını yaz; "
        "tablo istiyorsa Markdown tablosu oluştur; "
        "e-posta istiyorsa e-postayı yaz; "
        "mantık sorusu soruyorsa problemi çözüp net cevabı ver. "
        "Asla boş taslak başlıklar üretme, doğrudan istenen içeriği eksiksiz teslim et."
    )

    # Dinamik Sistem İstemi: Derin Düşünme Aktifse
    if deep_think:
        system_instruction = (
            base_instruction + "\n\n"
            "'Derin Düşün' modu açık: Modele sabit başlıklar dayatma. Sadece arka planda düşün, "
            "yanıtta ise doğrudan ulaştığın kesin ve ayrıntılı çözümü adım adım sun. Düşüncelerini <thought> etiketleri içine yazabilirsin."
            + web_context
        )
        gen_temperature = 0.2
    else:
        system_instruction = base_instruction + web_context
        gen_temperature = 0.7"""

pattern = re.compile(r'    if is_mebot_super:.*?gen_temperature = 0\.7', re.DOTALL)
text = pattern.sub(new_prompt, text)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated successfully!")
