import json
import base64
import urllib.request
import os

key = os.getenv("GEMINI_API_KEY")
print("Key exists:", bool(key))

img_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="

payload = {
    "contents": [
        {
            "parts": [
                {"text": "bu görselde ne var?"},
                {"inlineData": {"mimeType": "image/png", "data": img_b64}}
            ]
        }
    ]
}

if key:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    req = urllib.request.Request(url, method="POST", headers={"Content-Type": "application/json"}, data=json.dumps(payload).encode("utf-8"))
    try:
        with urllib.request.urlopen(req) as resp:
            print("SUCCESS:", resp.read().decode())
    except Exception as e:
        print("ERROR:", e.read().decode())
