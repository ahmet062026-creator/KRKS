with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add a config block at the very top of the script
config_block = """
  <script>
    // ==========================================
    // AYARLAR: ARKA YÜZ (BACKEND) BAĞLANTI ADRESİ
    // ==========================================
    // Eğer projeyi Render, Railway gibi bir yere yüklediysen buraya o adresi yaz.
    // Örnek: const API_BASE_URL = "https://mebot-backend.onrender.com";
    // Eğer sadece kendi bilgisayarında çalıştırıyorsan boş bırak ("AQ.Ab8RN6LlRsapg1H4-iC_8bDoCv0lE1NguFRAQrOpRdlNbPg3Rw").
    const API_BASE_URL = ""; 
    
    const form = document.getElementById('previewForm');"""

html = html.replace("  <script>\n    const form = document.getElementById('previewForm');", config_block)

# Replace the fetch calls
html = html.replace("await fetch('/api/chat'", "await fetch(API_BASE_URL + '/api/chat'")
html = html.replace("await fetch('/api/admin/", "await fetch(API_BASE_URL + '/api/admin/")
html = html.replace("await fetch('/api/auth/", "await fetch(API_BASE_URL + '/api/auth/")
html = html.replace("await fetch('/api/search_users", "await fetch(API_BASE_URL + '/api/search_users")
html = html.replace("await fetch('/api/test_key", "await fetch(API_BASE_URL + '/api/test_key")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
