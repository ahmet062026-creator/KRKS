import re
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add Settings button to header
html = html.replace('<!-- Profil Avatarı -->', '''
      <!-- Ayarlar Butonu -->
      <button id="openSettingsBtn" class="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-500/15 border border-slate-500/30 text-slate-300 hover:bg-slate-500/25 text-xs font-medium transition" title="Ayarlar (API Key)">
        <span>⚙️</span>
        <span>Ayarlar</span>
      </button>
      
      <!-- Profil Avatarı -->''')

# Add Settings Modal
settings_modal = '''
  <!-- Ayarlar Modalı (API Key) -->
  <div id="settingsModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
    <div class="bg-[#111827] border border-white/10 rounded-2xl p-6 max-w-md w-full shadow-2xl">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-xl font-bold text-white">⚙️ Ayarlar & API</h3>
        <button id="closeSettingsBtn" class="text-slate-400 hover:text-white font-bold">✕</button>
      </div>
      <div class="mb-4">
        <label class="block text-xs font-semibold text-slate-300 mb-1">Google Gemini API Anahtarı:</label>
        <input type="password" id="apiKeyInput" placeholder="AIzaSy..." class="w-full bg-[#0b0f19] border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-white outline-none focus:border-sky-400">
        <p class="text-[11px] text-slate-500 mt-1">MEBOT 0.1 gücünü kullanmak için API anahtarı zorunludur.</p>
      </div>
      <button id="saveSettingsBtn" class="w-full py-2.5 bg-sky-600 hover:bg-sky-500 text-white font-medium rounded-xl text-sm transition">
        Kaydet & Kapat
      </button>
    </div>
  </div>
'''

html = html.replace('<!-- Admin Modalı & Sohbet İnceleme -->', settings_modal + '\n  <!-- Admin Modalı & Sohbet İnceleme -->')

# Replace the fake submission with real fetch
fake_submit = '''    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = input.value.trim();
      if (!val || isPreviewGenerating) return;

      hero.classList.add('hidden');
      messages.classList.remove('hidden');

      // 1. Kullanıcı Mesajı - Sağda Kapsül Pill
      const userBubble = document.createElement('div');
      userBubble.className = 'self-end bg-[#1e1f20] text-white text-[15px] px-5 py-2.5 rounded-full border border-white/10 shadow max-w-[80%]';
      userBubble.textContent = val;
      messages.appendChild(userBubble);

      input.value = '';

      // 2. Durdur butonunu aktif et
      isPreviewGenerating = true;
      stopBtn.disabled = false;
      stopBtn.classList.remove('opacity-40');
      stopBtn.classList.add('opacity-100', 'text-red-500', 'bg-red-500/20', 'animate-pulse');

      // 3. Bot Yanıtı Alanı
      const botContainer = document.createElement('div');
      botContainer.className = 'self-start w-full text-slate-100 text-[15.5px] leading-relaxed';
      
      const botText = document.createElement('div');
      botText.className = 'bot-text-area';
      botContainer.appendChild(botText);

      // 5 İşlem Butonu
      const toolbar = document.createElement('div');
      toolbar.className = 'flex items-center gap-3 mt-3 text-[#8e918f]';
      toolbar.innerHTML = `
        <button class="hover:text-white p-1 rounded transition" title="İyi yanıt">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>
        </button>
        <button class="hover:text-white p-1 rounded transition" title="Kötü yanıt">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"></path></svg>
        </button>
        <button class="hover:text-white p-1 rounded transition" title="Yeniden dene">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
        </button>
        <button class="hover:text-white p-1 rounded transition" title="Kopyala">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
        </button>
        <button class="hover:text-white p-1 rounded transition" title="Daha fazla">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="1.5"></circle><circle cx="19" cy="12" r="1.5"></circle><circle cx="5" cy="12" r="1.5"></circle></svg>
        </button>
      `;
      botContainer.appendChild(toolbar);
      messages.appendChild(botContainer);

      const fullReply = `Merhaba ${currentName}! Ben MEBOT 0.1 süper modeliyim. "${val}" sorunuz analiz edildi ve akıcı şekilde yanıtlanıyor. İstediğiniz an gönderme butonunun yanındaki kırmızı kare durdurma butonuna basarak üretimi durdurabilirsiniz.`;
      const words = fullReply.split(' ');
      let currentIdx = 0;

      streamingTimer = setInterval(() => {
        if (currentIdx < words.length) {
          botText.textContent += (currentIdx > 0 ? ' ' : '') + words[currentIdx];
          currentIdx++;
        } else {
          clearInterval(streamingTimer);
          streamingTimer = null;
          isPreviewGenerating = false;
          stopBtn.disabled = true;
          stopBtn.classList.remove('opacity-100', 'text-red-500', 'bg-red-500/20', 'animate-pulse');
          stopBtn.classList.add('opacity-40');
        }
      }, 70);
    });'''

real_submit = '''
    const openSettingsBtn = document.getElementById('openSettingsBtn');
    const closeSettingsBtn = document.getElementById('closeSettingsBtn');
    const settingsModal = document.getElementById('settingsModal');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const saveSettingsBtn = document.getElementById('saveSettingsBtn');
    
    let currentApiKey = localStorage.getItem('mebot_api_key') || '';
    apiKeyInput.value = currentApiKey;
    
    openSettingsBtn.addEventListener('click', () => { settingsModal.classList.remove('hidden'); });
    closeSettingsBtn.addEventListener('click', () => { settingsModal.classList.add('hidden'); });
    saveSettingsBtn.addEventListener('click', () => {
      currentApiKey = apiKeyInput.value.trim();
      localStorage.setItem('mebot_api_key', currentApiKey);
      settingsModal.classList.add('hidden');
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const val = input.value.trim();
      if (!val || isPreviewGenerating) return;

      hero.classList.add('hidden');
      messages.classList.remove('hidden');

      // Kullanıcı Mesajı
      const userBubble = document.createElement('div');
      userBubble.className = 'self-end bg-[#1e1f20] text-white text-[15px] px-5 py-2.5 rounded-full border border-white/10 shadow max-w-[80%]';
      userBubble.textContent = val;
      messages.appendChild(userBubble);
      input.value = '';

      isPreviewGenerating = true;
      stopBtn.disabled = false;
      stopBtn.classList.remove('opacity-40');
      stopBtn.classList.add('opacity-100', 'text-red-500', 'bg-red-500/20', 'animate-pulse');

      const botContainer = document.createElement('div');
      botContainer.className = 'self-start w-full text-slate-100 text-[15.5px] leading-relaxed';
      const botText = document.createElement('div');
      botText.className = 'bot-text-area';
      botText.innerHTML = '<span class="text-sky-400 animate-pulse">MEBOT düşünüyor...</span>';
      botContainer.appendChild(botText);
      messages.appendChild(botContainer);
      
      messages.scrollTop = messages.scrollHeight;

      try {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
             message: val,
             apiKey: currentApiKey,
             model: "MEBOT 0.1",
             username: currentName,
             pin: currentPin
          })
        });
        
        const data = await response.json();
        
        botText.innerHTML = '';
        if (data.thinking) {
          const thinkDiv = document.createElement('div');
          thinkDiv.className = 'text-xs text-sky-300 bg-sky-900/20 p-2 rounded-md mb-2 border border-sky-500/30';
          thinkDiv.innerText = data.thinking + "\\n(Süre: " + data.thinking_time + " sn)";
          botText.appendChild(thinkDiv);
        }
        
        const replyDiv = document.createElement('div');
        botText.appendChild(replyDiv);
        
        // basit kelime kelime akış
        const words = (data.reply || "").split(' ');
        let currentIdx = 0;
        
        streamingTimer = setInterval(() => {
          if (currentIdx < words.length) {
            replyDiv.textContent += (currentIdx > 0 ? ' ' : '') + words[currentIdx];
            currentIdx++;
            messages.scrollTop = messages.scrollHeight;
          } else {
            clearInterval(streamingTimer);
            streamingTimer = null;
            isPreviewGenerating = false;
            stopBtn.disabled = true;
            stopBtn.classList.remove('opacity-100', 'text-red-500', 'bg-red-500/20', 'animate-pulse');
            stopBtn.classList.add('opacity-40');
          }
        }, 30);
      } catch (err) {
        botText.textContent = "Bağlantı hatası: Sunucu yanıt vermiyor.";
        isPreviewGenerating = false;
        stopBtn.disabled = true;
        stopBtn.classList.remove('opacity-100', 'text-red-500', 'bg-red-500/20', 'animate-pulse');
        stopBtn.classList.add('opacity-40');
      }
    });
'''

html = html.replace(fake_submit, real_submit)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Done index update')
