import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add the popup HTML above the footer
popup_html = """
    <!-- Options Popup -->
    <div id="optionsMenu" class="hidden absolute bottom-[80px] left-4 bg-[#1e1f20] border border-white/10 rounded-2xl p-3 shadow-2xl w-64 z-50">
      <div class="flex flex-col gap-2">
        <label class="flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 cursor-pointer transition">
          <div class="relative">
            <input type="checkbox" id="toggleWebSearch" class="peer sr-only">
            <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-sky-500"></div>
          </div>
          <span class="text-sm text-slate-200 font-medium select-none">🌐 Web Araştırması</span>
        </label>
        
        <label class="flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 cursor-pointer transition">
          <div class="relative">
            <input type="checkbox" id="toggleDeepThink" class="peer sr-only" checked>
            <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-fuchsia-500"></div>
          </div>
          <span class="text-sm text-slate-200 font-medium select-none">🧠 Daha Derin Düşünme</span>
        </label>
      </div>
    </div>
    
    <footer class="w-full max-w-2xl mx-auto pb-4 relative">
"""
html = html.replace('<footer class="w-full max-w-2xl mx-auto pb-4">', popup_html)

# Replace the title of newChatBtn to "Seçenekler"
html = html.replace('title="Yeni Sohbet"', 'title="Seçenekler"')

# 2. Add the JS logic for the menu
old_js = """    const newChatBtn = document.getElementById('newChatBtn');
    newChatBtn.addEventListener('click', () => {
      messages.innerHTML = '';
      messages.classList.add('hidden');
      hero.classList.remove('hidden');
      if (streamingTimer) {
        clearInterval(streamingTimer);
        streamingTimer = null;
        isPreviewGenerating = false;
        stopBtn.disabled = true;
        stopBtn.classList.remove('opacity-100', 'text-red-500', 'bg-red-500/20', 'animate-pulse');
        stopBtn.classList.add('opacity-40');
      }
    });"""

new_js = """    const newChatBtn = document.getElementById('newChatBtn');
    const optionsMenu = document.getElementById('optionsMenu');
    const toggleWebSearch = document.getElementById('toggleWebSearch');
    const toggleDeepThink = document.getElementById('toggleDeepThink');
    
    // Toggle Menu
    newChatBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      optionsMenu.classList.toggle('hidden');
    });

    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!optionsMenu.contains(e.target) && e.target !== newChatBtn) {
        optionsMenu.classList.add('hidden');
      }
    });"""

html = html.replace(old_js, new_js)

# 3. Add to the payload
payload_old = """          body: JSON.stringify({
             message: val,
             apiKey: currentApiKey,
             model: "MEBOT 0.1",
             username: currentName,
             pin: currentPin
          })"""
payload_new = """          body: JSON.stringify({
             message: val,
             apiKey: currentApiKey,
             model: "MEBOT 0.1",
             username: currentName,
             pin: currentPin,
             webSearch: toggleWebSearch.checked,
             deepThink: toggleDeepThink.checked
          })"""
html = html.replace(payload_old, payload_new)

# 4. We should add a New Chat button somewhere since we overwrote the + button.
# Let's put it next to the settings gear.
header_old = """    <div class="flex items-center gap-3">
      <!-- Ayarlar İkonu -->"""
header_new = """    <div class="flex items-center gap-3">
      <!-- Yeni Sohbet -->
      <button id="clearChatBtn" class="text-xs font-medium text-slate-300 hover:text-white bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-full transition">Yeni Sohbet</button>
      <!-- Ayarlar İkonu -->"""
html = html.replace(header_old, header_new)

# 5. JS logic for clearChatBtn
clear_chat_js = """
    const clearChatBtn = document.getElementById('clearChatBtn');
    if (clearChatBtn) {
      clearChatBtn.addEventListener('click', () => {
        messages.innerHTML = '';
        messages.classList.add('hidden');
        hero.classList.remove('hidden');
        if (streamingTimer) {
          clearInterval(streamingTimer);
          streamingTimer = null;
          isPreviewGenerating = false;
          stopBtn.disabled = true;
          stopBtn.classList.remove('opacity-100', 'text-red-500', 'bg-red-500/20', 'animate-pulse');
          stopBtn.classList.add('opacity-40');
        }
      });
    }
"""
html = html.replace('// Ayarlar modalı', clear_chat_js + '\n    // Ayarlar modalı')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html patched!")
