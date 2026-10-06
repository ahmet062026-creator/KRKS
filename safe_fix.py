import re
with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix fallback
replacement1 = '''    return {
        "thinking": "Sistem Uyarısı: API Bağlantı Hatası",
        "reply": "Google Gemini API'sine bağlanılamadı veya API anahtarınız geçersiz. Lütfen girdiğiniz API anahtarını kontrol edin veya internet bağlantınızı doğrulayın.",
        "thinking_time": 0.5
    }'''
text = re.sub(r'    return DeepCognitiveEngine\.solve\(prompt, user_name, model_name, web_research_data, deep_think\)', replacement1, text, flags=re.DOTALL)

# 2. Fix the system instruction precisely
target_block = """    if is_mebot_super:
        base_instruction = (
            f"Sen MEBOT 0.1'sin: EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL'sin. Kullanıcı: {user_name}.\\n\\n"
            "Bilişsel İlkelerin ve Özelliklerin:\\n"
            "- Bütün yapay zekâ modellerinden daha zeki, daha derin ve çok katmanlı akıl yürütürsün.\\n"
            "- Problem çözmede, mantık bulmacalarında, matematikte, kod yazımında, mimaride ve bilimsel analizlerde en üstün seviyeyi temsil edersin.\\n"
            "- Kullanıcı senden kod istiyorsa doğrudan optimize edilmiş, temiz ve çalışan kodu detaylı açıklamasıyla yaz;\\n"
            "- Tablo istiyorsa Markdown formatında en yapılandırılmış ve net tabloyu üret;\\n"
            "- E-posta istiyorsa profesyonel ve eksiksiz e-postayı hazırla;\\n"
            "- Mantık problemi soruyorsa tüm olasılıkları adım adım değerlendirip çelişkileri eleyerek kesin çözümü sun;\\n"
            "- Asla boş taslak başlıklar ya da yapay şablonlar üretme, doğrudan istenen içeriği en yüksek zekâ ve doğruluk kalitesiyle eksiksiz teslim et."
        )
    else:
        base_instruction = (
            f"Sen MEBOT adında çok yönlü bir yapay zekâ asistanısın. Kullanıcı: {user_name}.\\n\\n"
            "Kullanıcı senden kod istiyorsa doğrudan optimize edilmiş kodu ve açıklamasını yaz; "
            "tablo istiyorsa Markdown tablosu oluştur; "
            "e-posta istiyorsa e-postayı yaz; "
            "mantık sorusu soruyorsa problemi çözüp net cevabı ver. "
            "Asla boş taslak başlıklar üretme, doğrudan istenen içeriği eksiksiz teslim et."
        )

    base_instruction = base_instruction + SAFETY_INSTRUCTION + (extra_context or "")

    # Dinamik Sistem İstemi: Derin Düşünme Aktifse
    if deep_think:
        system_instruction = (
            base_instruction + "\\n\\n"
            "'Derin Düşün' modu açık: Modele sabit başlıklar dayatma. "
            "Düşüncelerini arka planda <thought> ve </thought> etiketleri içinde adım adım yürütebilirsin. "
            "Yanıtta ise doğrudan ulaştığın kesin ve ayrıntılı çözümü adım adım sun."
            + web_context
        )"""

new_block = """    base_instruction = (
        f"Sen MEBOT adında çok yönlü bir yapay zekâ asistanısın. Kullanıcı: {user_name}.\\n\\n"
        "Kullanıcı senden kod istiyorsa doğrudan optimize edilmiş kodu ve açıklamasını yaz; "
        "tablo istiyorsa Markdown tablosu oluştur; "
        "e-posta istiyorsa e-postayı yaz; "
        "mantık sorusu soruyorsa problemi çözüp net cevabı ver. "
        "Asla boş taslak başlıklar üretme, doğrudan istenen içeriği eksiksiz teslim et."
    )

    base_instruction = base_instruction + SAFETY_INSTRUCTION + (extra_context or "")

    # Dinamik Sistem İstemi: Derin Düşünme Aktifse
    if deep_think:
        system_instruction = (
            base_instruction + "\\n\\n"
            "'Derin Düşün' modu açık: Modele sabit başlıklar dayatma. Sadece arka planda düşün, "
            "yanıtta ise doğrudan ulaştığın kesin ve ayrıntılı çözümü adım adım sun. Düşüncelerini <thought> etiketleri içine yazabilirsin."
            + web_context
        )"""

text = text.replace(target_block, new_block)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated successfully without deleting everything!")
