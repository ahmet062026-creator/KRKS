import sys, re
with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''    return {
        "thinking": "Sistem Uyarısı: API Bağlantı Hatası",
        "reply": "Google Gemini API'sine bağlanılamadı veya API anahtarınız geçersiz. Lütfen girdiğiniz API anahtarını kontrol edin veya internet bağlantınızı doğrulayın.",
        "thinking_time": 0.5
    }'''

text = re.sub(r'    return DeepCognitiveEngine\.solve\(prompt, user_name, model_name, web_research_data, deep_think\)', replacement, text, flags=re.DOTALL)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
