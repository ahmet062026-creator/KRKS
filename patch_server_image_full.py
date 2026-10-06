import re

with open('server.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update signature
sig_old = 'def get_gemini_reply(api_key: str, model_name: str, prompt: str, user_name: str, force_web_search: bool = False, deep_think: bool = True, extra_context: str = "") -> dict:'
sig_new = 'def get_gemini_reply(api_key: str, model_name: str, prompt: str, user_name: str, force_web_search: bool = False, deep_think: bool = True, extra_context: str = "", base64_image: str = None, vision_think: bool = False) -> dict:'
text = text.replace(sig_old, sig_new)

# 2. Add vision think to system prompt
sys_old = '    gen_temperature = 0.7'
sys_new = """    gen_temperature = 0.7

    if vision_think and base64_image:
        system_instruction += "\\n\\n'Resim Üzerinden Yoğun Düşünme' aktif: Kullanıcının yüklediği görseldeki her bir pikseli, detayı, metni milimetrik olarak incele. Görsel veriyi en derin seviyede analiz ederek doğrudan çözüme veya sonuca ulaş."
"""
text = text.replace(sys_old, sys_new)

# 3. Update the call to generate_content for SDK
gen_old = '                    response = model.generate_content(prompt)'
gen_new = """                    content_parts = [prompt]
                    if base64_image:
                        import base64
                        mime_type = "image/jpeg"
                        encoded = base64_image
                        if "data:" in base64_image and ";base64," in base64_image:
                            header, encoded = base64_image.split(";base64,", 1)
                            mime_type = header.split(":")[1]
                        
                        # Use inline_data structure!
                        # Some versions of google-generativeai require this:
                        img_data = base64.b64decode(encoded)
                        content_parts.append({"mime_type": mime_type, "data": img_data})
                        
                    response = model.generate_content(content_parts)"""
text = text.replace(gen_old, gen_new)

# 4. Update the REST API call to support image
rest_old = """                    payload = {
                        "systemInstruction": {
                            "parts": [{"text": system_instruction}]
                        },
                        "contents": [
                            {"parts": [{"text": prompt}]}
                        ],
                        "generationConfig": {
                            "temperature": gen_temperature
                        }
                    }"""
rest_new = """                    parts_list = [{"text": prompt}]
                    if base64_image:
                        mime_type = "image/jpeg"
                        encoded = base64_image
                        if "data:" in base64_image and ";base64," in base64_image:
                            header, encoded = base64_image.split(";base64,", 1)
                            mime_type = header.split(":")[1]
                        parts_list.append({
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": encoded
                            }
                        })
                        
                    payload = {
                        "systemInstruction": {
                            "parts": [{"text": system_instruction}]
                        },
                        "contents": [
                            {"parts": parts_list}
                        ],
                        "generationConfig": {
                            "temperature": gen_temperature
                        }
                    }"""
text = text.replace(rest_old, rest_new)

# 5. Update the endpoint to pass image and visionThink
endpoint_old = '                deep_think = bool(data.get("deepThink", True))'
endpoint_new = """                deep_think = bool(data.get("deepThink", True))
                base64_img = data.get("image", None)
                v_think = bool(data.get("visionThink", False))"""
text = text.replace(endpoint_old, endpoint_new)

call_old = '                result = get_gemini_reply(client_api_key, model_name, user_msg, user_name, force_web_search, deep_think)'
call_new = '                result = get_gemini_reply(client_api_key, model_name, user_msg, user_name, force_web_search, deep_think, "", base64_img, v_think)'
text = text.replace(call_old, call_new)

with open('server.py', 'w', encoding='utf-8') as f:
    f.write(text)
print("server.py patched for images with REST API!")
