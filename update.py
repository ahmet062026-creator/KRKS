import sys, re
with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

replacement = '''    if not active_key:
        return {
            "thinking": "Sistem Uyarısı: API Anahtarı Gerekli",
            "reply": "MEBOT 0.1 (Süper Model) gücünü kullanabilmek için API anahtarına ihtiyaç duymaktadır. Lütfen sağ üstteki **Ayarlar** menüsüne girerek Google Gemini API anahtarınızı ekleyin.",
            "thinking_time": 0.5
        }

    return DeepCognitiveEngine.solve(prompt, user_name, model_name, web_research_data, deep_think)'''

text = re.sub(r'    # 3. Yerle.*?return DeepCognitiveEngine\.solve\(prompt, user_name, model_name, web_research_data, deep_think\)', replacement, text, flags=re.DOTALL)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done!')
