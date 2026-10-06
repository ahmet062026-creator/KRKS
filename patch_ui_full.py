import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Image Preview Container
preview_html = """
    <!-- Resim Önizleme (Mesaj alanının hemen üstünde) -->
    <div id="imagePreviewContainer" class="hidden w-full max-w-2xl mx-auto mb-2 px-4">
      <div class="relative inline-block border border-white/20 rounded-xl overflow-hidden shadow-lg bg-black/50">
        <img id="imagePreview" src="" class="max-h-32 object-contain" />
        <button type="button" id="removeImageBtn" class="absolute top-1 right-1 w-6 h-6 bg-red-500/80 hover:bg-red-500 text-white rounded-full flex items-center justify-center text-xs transition">X</button>
      </div>
    </div>
    
    <footer class="w-full max-w-2xl mx-auto pb-4">
"""
html = html.replace('<footer class="w-full max-w-2xl mx-auto pb-4">', preview_html)

# 2. Add Options Menu (replaces the old footer opening partially, so we put it right before footer)
options_menu = """
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
        
        <div class="h-px bg-white/10 my-1"></div>
        
        <!-- Dosya Yükleme (EKLE) -->
        <input type="file" id="imageUpload" accept="image/*" class="hidden">
        <button type="button" id="addImageBtn" class="flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 transition w-full text-left">
          <div class="w-9 h-5 flex items-center justify-center bg-slate-700 rounded-full">
            <span class="text-white text-xs">📷</span>
          </div>
          <span class="text-sm text-slate-200 font-medium select-none">Görsel Ekle</span>
        </button>

        <!-- Görsel Yoğun Düşünme -->
        <label id="visionThinkLabel" class="hidden flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 cursor-pointer transition">
          <div class="relative">
            <input type="checkbox" id="toggleVisionThink" class="peer sr-only">
            <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-amber-500"></div>
          </div>
          <span class="text-sm text-amber-200 font-medium select-none">Resim Üzerinden Yoğun Düşün</span>
        </label>
      </div>
    </div>
"""
# We must insert it before the `<footer` which is now `<footer class="w-full max-w-2xl mx-auto pb-4">`
html = html.replace('<footer class="w-full max-w-2xl mx-auto pb-4">', options_menu + '\n    <footer class="w-full max-w-2xl mx-auto pb-4 relative">')

# Replace title of + button
html = html.replace('title="Yeni Sohbet"', 'title="Seçenekler"')

# Replace the payload JS
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
             webSearch: typeof toggleWebSearch !== 'undefined' ? toggleWebSearch.checked : false,
             deepThink: typeof toggleDeepThink !== 'undefined' ? toggleDeepThink.checked : true,
             image: typeof base64Image !== 'undefined' ? base64Image : null,
             visionThink: typeof toggleVisionThink !== 'undefined' ? toggleVisionThink.checked : false
          })"""
html = html.replace(payload_old, payload_new)

# Add "Yeni Sohbet" button to header
header_old = """    <div class="flex items-center gap-3">
      <!-- Ayarlar Butonu -->"""
header_new = """    <div class="flex items-center gap-3">
      <!-- Yeni Sohbet -->
      <button id="clearChatBtn" class="text-xs font-medium text-slate-300 hover:text-white bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-full transition">Yeni Sohbet</button>
      <!-- Ayarlar Butonu -->"""
html = html.replace(header_old, header_new)

# Replace newChatBtn event listener with Options Menu and Add logic
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
    });
    
    // --- Yeni Sohbet Butonu ---
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

    // --- Görsel Ekleme ve Önizleme ---
    const imageUpload = document.getElementById('imageUpload');
    const addImageBtn = document.getElementById('addImageBtn');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const removeImageBtn = document.getElementById('removeImageBtn');
    const visionThinkLabel = document.getElementById('visionThinkLabel');
    const toggleVisionThink = document.getElementById('toggleVisionThink');
    
    let base64Image = null;

    if (addImageBtn && imageUpload) {
        addImageBtn.addEventListener('click', () => {
          imageUpload.click();
        });

        imageUpload.addEventListener('change', (e) => {
          const file = e.target.files[0];
          if (file) {
            const reader = new FileReader();
            reader.onload = (evt) => {
              base64Image = evt.target.result;
              imagePreview.src = base64Image;
              imagePreviewContainer.classList.remove('hidden');
              visionThinkLabel.classList.remove('hidden');
              optionsMenu.classList.add('hidden'); // Menüyü kapat
            };
            reader.readAsDataURL(file);
          }
        });

        removeImageBtn.addEventListener('click', () => {
          base64Image = null;
          imagePreview.src = "";
          imageUpload.value = "";
          imagePreviewContainer.classList.add('hidden');
          visionThinkLabel.classList.add('hidden');
          toggleVisionThink.checked = false;
        });
    }
"""
html = html.replace(old_js, new_js)

# Clear image after send
after_send_old = """        previewInput.value = '';
        const botText = document.createElement('div');"""
after_send_new = """        previewInput.value = '';
        
        if (typeof removeImageBtn !== 'undefined' && base64Image) {
            removeImageBtn.click(); 
        }

        const botText = document.createElement('div');"""
html = html.replace(after_send_old, after_send_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Complete UI patch applied successfully!")
