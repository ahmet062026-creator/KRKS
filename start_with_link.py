# -*- coding: utf-8 -*-
"""
MEBOT 0.1 - GİZLİ VE ÖZEL LİNK İLE BAŞLATICI
Bu betik:
1. MEBOT yerel sunucusunu (server.py) başlatır.
2. Cloudflare gizli tünelini (cloudflared.exe) başlatarak arama motorlarında ve
   mağazalarda ÇIKMAYAN, sadece bu linki bilenlerin girebileceği özel bir HTTPS linki üretir.
3. Linki 'mebot_link.txt' dosyasına kaydeder ve ekranda gösterip tarayıcıda açar.
"""

import os
import sys
import time
import re
import socket
import subprocess
import webbrowser
import signal

# UTF-8 Konsol Desteği
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CLOUDFLARED_BIN = os.path.join(BASE_DIR, "cloudflared.exe")
SERVER_PY = os.path.join(BASE_DIR, "server.py")
LINK_FILE = os.path.join(BASE_DIR, "mebot_link.txt")

# Python yorumlayıcısını bul
PYTHON_CANDIDATES = [
    r"C:\Users\acer\AppData\Local\Python\bin\python.exe",
    sys.executable,
    "python",
    "py"
]

def find_python():
    for p in PYTHON_CANDIDATES:
        if os.path.isfile(p):
            return p
    return sys.executable

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0

def main():
    python_exe = find_python()
    local_ip = get_local_ip()

    print("=" * 66)
    print("  MEBOT 0.1 - EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL")
    print("  Gizli Link & Arama Motoru İndeksleme Korumalı Başlatıcı")
    print("=" * 66)

    # 1. server.py zaten çalışıyor mu kontrol et, çalışmıyorsa başlat
    server_proc = None
    if not is_port_in_use(8000):
        print("\n[1/3] MEBOT Yerel Sunucusu Başlatılıyor (Port 8000)...")
        server_proc = subprocess.Popen(
            [python_exe, SERVER_PY],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        time.sleep(2)
    else:
        print("\n[1/3] MEBOT Yerel Sunucusu Zaten Aktif (Port 8000).")

    # 2. cloudflared kontrolü
    if not os.path.exists(CLOUDFLARED_BIN):
        print(f"\n[UYARI] {CLOUDFLARED_BIN} bulunamadı!")
        print(f"Yerel Ağ Bağlantısı: http://{local_ip}:8000")
        print(f"Bilgisayar Bağlantısı: http://127.0.0.1:8000")
        webbrowser.open("http://127.0.0.1:8000")
        return

    print("\n[2/3] Güvenli & Gizli HTTPS Linki Üretiliyor...")
    tunnel_proc = subprocess.Popen(
        [CLOUDFLARED_BIN, "tunnel", "--url", "http://127.0.0.1:8000", "--no-autoupdate"],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding="utf-8",
        errors="replace"
    )

    public_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    # Çıktıdan URL'yi yakala (maksimum 25 saniye bekle)
    start_time = time.time()
    while time.time() - start_time < 25:
        line = tunnel_proc.stdout.readline()
        if not line:
            if tunnel_proc.poll() is not None:
                break
            time.sleep(0.1)
            continue

        match = url_pattern.search(line)
        if match:
            public_url = match.group(0)
            break

    # 3. Sonuçları hazırla ve göster
    link_content = f"""==================================================================
           MEBOT 0.1 - GİZLİ & ÖZEL ERİŞİM BİLGİLERİ
==================================================================

1) GİZLİ DIŞ İNTERNET LİNKİ (Telefon, tablet, başka PC'ler için):
   {public_url if public_url else 'Üretilemedi'}

   * Bu link Google'da veya arama motorlarında ASLA ÇIKMAZ.
   * noindex, nofollow, noarchive ve robots.txt ile tamamen gizlenmiştir.
   * Google Play / App Store gibi mağazalarda YOKTUR.
   * Yalnızca bu linki gönderdiğiniz kişiler açabilir!

2) EV / AYNI Wİ-Fİ AĞI LİNKİ (Aynı modeme bağlı telefonlar için):
   http://{local_ip}:8000

3) BİLGİSAYAR İÇİN YEREL LİNK:
   http://127.0.0.1:8000

------------------------------------------------------------------
* ADMİN PANELİ KODU: 565856
  (Giriş ekranında şifre kutusuna "565856" yazarak veya sayfa altındaki
   Admin Kodu butonuna tıklayarak açabilirsiniz)
* Şifreli hesaplar users_db.json dosyasında güvenle saklanır.
==================================================================
"""

    with open(LINK_FILE, "w", encoding="utf-8") as f:
        f.write(link_content)

    print("\n" + "=" * 66)
    if public_url:
        print("  TEBRİKLER! GİZLİ VE ÖZEL LİNKİNİZ OLUŞTURULDU:")
        print(f"  --> {public_url} <--")
    else:
        print("  Dış link oluşturulamadı, yerel link aktif:")
        print(f"  --> http://{local_ip}:8000 <--")
    print("=" * 66)
    print(f"• Google / Arama motoru indeksleme: ENGELLENDİ (noindex)")
    print(f"• Uygulama mağazalarında: YOKTUR (Sadece doğrudan linkle girilir)")
    print(f"• Ev / Wi-Fi Linki: http://{local_ip}:8000")
    print(f"• Link ve bilgiler 'mebot_link.txt' dosyasına kaydedildi!")
    print("=" * 66)
    print("\nTarayıcınızda açılıyor...")

    target_url = public_url if public_url else f"http://{local_ip}:8000"
    try:
        webbrowser.open(target_url)
    except Exception:
        pass

    print("\n[BİLGİ] Sunucu ve gizli tünel arka planda çalışıyor.")
    print("Kapatmak için bu pencereyi kapatabilir veya klavyeden CTRL + C basabilirsiniz.\n")

    # Süreci açık tut
    try:
        while True:
            time.sleep(1)
            # Eğer tünel veya sunucu beklenmedik şekilde kapandıysa kontrol et
            if tunnel_proc and tunnel_proc.poll() is not None:
                print("\n[UYARI] Tünel bağlantısı kapandı.")
                break
    except KeyboardInterrupt:
        print("\nMEBOT kapatılıyor...")
    finally:
        if tunnel_proc:
            try:
                tunnel_proc.terminate()
            except Exception:
                pass
        if server_proc:
            try:
                server_proc.terminate()
            except Exception:
                pass

if __name__ == "__main__":
    main()
