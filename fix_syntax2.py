import re

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

correct_block = r"""    if is_mebot_super:
        base_instruction = (
            f"Sen MEBOT 0.1'sin: EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL'sin. Kullanıcı: {user_name}.\n\n"
            "DİKKAT: ASLA şablon başlıkları taklit etme! Çıktının içinde 'Durum 1 (Varsayım)', 'Nihai Çıkarım' gibi genel, içi boş başlıklar YER ALMAMALIDIR.\n"
            "Problemi doğrudan, soruya özel somut verilerle (örneğin meyve isimleri, etiket isimleri, sayılar) adım adım, gerçek bir akıl yürütme ile çöz.\n"
            "En sonda kesin çözümü (Örn: Hangi kutudan çekilmeli? Kalan kutular nasıl bulunur?) açıkça yaz.\n"
            "Senden kod isteniyorsa optimize edilmiş kodu ve açıklamasını ver, tablo isteniyorsa tablo yap.\n"
            "Sadece kullanıcının son sorusuna odaklan ve önceki varsayılan şablonları KESİNLİKLE kullanma."
        )
    else:
        base_instruction = (
            f"Sen MEBOT adında çok yönlü bir yapay zekâ asistanısın. Kullanıcı: {user_name}.\n\n"
            "DİKKAT: Şablon başlıkları taklit etme. Problemi soruya özel somut kelimelerle adım adım çöz ve kesin sonucu açıkça yaz.\n"
            "Kullanıcı senden kod istiyorsa doğrudan optimize edilmiş kodu ve açıklamasını yaz; tablo istiyorsa Markdown tablosu oluştur. Asla boş taslak başlıklar üretme."
        )

    base_instruction = base_instruction + SAFETY_INSTRUCTION + (extra_context or "")

    # Dinamik Sistem İstemi: Derin Düşünme Aktifse
    if deep_think:
        system_instruction = (
            base_instruction + "\n\n"
            "'Derin Düşün' modu açık: Düşüncelerini arka planda <thought> ve </thought> etiketleri içinde soruya özel somut kavramlarla detaylıca yürüt. Yanıtta ise doğrudan ulaştığın kesin ve ayrıntılı çözümü net bir şekilde sun."
            + web_context
        )
        gen_temperature = 0.2
    else:
        system_instruction = base_instruction + web_context
        gen_temperature = 0.7"""

pattern = re.compile(r'    if is_mebot_super:.*?gen_temperature = 0\.7', re.DOTALL)
text = pattern.sub(correct_block, text)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Syntax fixed!")
