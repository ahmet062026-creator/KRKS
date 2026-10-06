import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Add File Input and Image Preview container
new_html = """
    <!-- Resim Önizleme (Mesaj alanının hemen üstünde) -->
    <div id="imagePreviewContainer" class="hidden w-full max-w-2xl mx-auto mb-2 px-4">
      <div class="relative inline-block border border-white/20 rounded-xl overflow-hidden shadow-lg bg-black/50">
        <img id="imagePreview" src="" class="max-h-32 object-contain" />
        <button type="button" id="removeImageBtn" class="absolute top-1 right-1 w-6 h-6 bg-red-500/80 hover:bg-red-500 text-white rounded-full flex items-center justify-center text-xs transition">X</button>
      </div>
    </div>
    
    <footer class="w-full max-w-2xl mx-auto pb-4 relative">
"""
html = html.replace('<footer class="w-full max-w-2xl mx-auto pb-4 relative">', new_html)

# Add EKLE option and hidden file input in optionsMenu
menu_old = """          <span class="text-sm text-slate-200 font-medium select-none">🧠 Daha Derin Düşünme</span>
        </label>
      </div>"""
menu_new = """          <span class="text-sm text-slate-200 font-medium select-none">🧠 Daha Derin Düşünme</span>
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

        <!-- Görsel Yoğun Düşünme (Sadece resim varken çıkar) -->
        <label id="visionThinkLabel" class="hidden flex items-center gap-3 p-2 rounded-xl hover:bg-white/5 cursor-pointer transition">
          <div class="relative">
            <input type="checkbox" id="toggleVisionThink" class="peer sr-only">
            <div class="w-9 h-5 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-amber-500"></div>
          </div>
          <span class="text-sm text-amber-200 font-medium select-none">Resim Üzerinden Yoğun Düşün</span>
        </label>
      </div>"""
html = html.replace(menu_old, menu_new)

# Add Base64 handling and JS logic
js_injection = """
    // Görsel Ekleme ve Önizleme
    const imageUpload = document.getElementById('imageUpload');
    const addImageBtn = document.getElementById('addImageBtn');
    const imagePreviewContainer = document.getElementById('imagePreviewContainer');
    const imagePreview = document.getElementById('imagePreview');
    const removeImageBtn = document.getElementById('removeImageBtn');
    const visionThinkLabel = document.getElementById('visionThinkLabel');
    const toggleVisionThink = document.getElementById('toggleVisionThink');
    
    let base64Image = null;

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
          optionsMenu.classList.add('hidden'); // Kapat
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
"""
# insert before clearChatBtn logic
html = html.replace('const clearChatBtn = document.getElementById(\'clearChatBtn\');', js_injection + '\n    const clearChatBtn = document.getElementById(\'clearChatBtn\');')

# Modify payload to include image and vision think
payload_old = """             webSearch: toggleWebSearch.checked,
             deepThink: toggleDeepThink.checked
          })"""
payload_new = """             webSearch: toggleWebSearch.checked,
             deepThink: toggleDeepThink.checked,
             image: base64Image,
             visionThink: toggleVisionThink.checked
          })"""
html = html.replace(payload_old, payload_new)

# Clear image after send
after_send_old = """        previewInput.value = '';
        const botText = document.createElement('div');"""
after_send_new = """        previewInput.value = '';
        
        // Resmi temizle
        if (base64Image) {
            removeImageBtn.click(); 
        }

        const botText = document.createElement('div');"""
html = html.replace(after_send_old, after_send_new)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("index.html image feature patched!")
