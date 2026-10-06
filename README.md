# MEBOT - Antigravity Yapay Zeka Sohbet Arayüzü

Bu proje, oluşturulan görsel maket (mockup) tasarımını tam donanımlı, canlı ve etkileşimli bir web uygulamasına dönüştürmektedir.

---

## 🚀 Mimari ve Teknik Bileşenler

Proje kullanıcının belirlediği 3 aşamalı teknik yol haritasına göre inşa edilmiştir:

1. **Ön Yüz Geliştirme (Frontend - HTML5 & CSS3):**
   - **`index.html`**: Görsel tasarımdaki tüm bileşenleri semantik olarak içerir (üst bar, 'Uygulamayı İndir' butonu, profil avatarı 'G', 'Hemen başlayalım [Kullanıcı Adı]' karşılama başlığı ve alt etkileşim çubuğu).
   - **`style.css`**: Tasarımdaki koyu lacivert radyal degrade arka plan, yumuşak ışıklandırma, 'DENEME 1' model rozeti, yuvarlak (pill) butonlar ve pürüzsüz animasyonlar pixel-perfect olarak kodlanmıştır.

2. **Etkileşim (JavaScript - `app.js`):**
   - **Kullanıcı Adı Entegrasyonu:** `[Kullanıcı Adı]` dinamiktir. Kullanıcı adını değiştirebilir; avatar harfi ve başlık otomatik güncellenir ve `localStorage`'da saklanır.
   - **Giriş ve Odaklanma:** Yazı çubuğuna tıklandığında imleç otomatik odaklanır.
   - **Enter ve Gönderim:** 'Enter' tuşu veya Gönder butonu mesajı tetikler, ekran pürüzsüzce sohbet akışı moduna geçer.
   - **Sesle Yazma (Mikrofon):** Web Speech API ile Türkçe sesli komut algılama mevcuttur.
   - **Model Seçimi:** 'DENEME 1', 'Gemini 2.5 Flash', 'Gemini 1.5 Pro' modelleri arasında geçiş yapılabilir.

3. **Yapay Zeka Entegrasyonu (Backend - `server.py`):**
   - Python HTTP sunucusu `/api/chat` uç noktası üzerinden mesajları alır.
   - **Gemini Entegrasyonu:** İster sistem ortam değişkenlerinden (`GEMINI_API_KEY`), ister arayüzdeki Ayarlar menüsünden sağlanan anahtarla Google Gemini modelleri ile gerçek zamanlı iletişim kurar.
   - **Çevrimdışı / Yerel Akıllı Motor:** API anahtarı olmasa bile kullanıcıyı yanıtsız bırakmayan, Türkçe dilinde akıllı yanıt üreten yerel mod desteği vardır.

---

## 🛠️ Nasıl Çalıştırılır?

### 1. Yöntem: Çift Tıklayarak (En Kolay)
Proje klasöründeki **`start.bat`** dosyasına çift tıklayın. Sunucu başlatılacak ve tarayıcınız otomatik olarak `http://127.0.0.1:8000` adresinde açılacaktır.

### 2. Yöntem: Terminalden Başlatma
Powershell veya Komut İstemi'nde:
```powershell
& "C:\Users\acer\AppData\Local\Python\bin\python.exe" server.py
```
Ardından tarayıcınızda `http://127.0.0.1:8000` adresine gidin.

### 3. Yöntem: Doğrudan Tarayıcıda Açma (Sunucusuz)
İnternet tarayıcınızla doğrudan `index.html` dosyasını açabilirsiniz. Yerel istemci tabanlı yapay zeka yanıtlayıcısı sayesinde sunucu olmadan da anında çalışır.
