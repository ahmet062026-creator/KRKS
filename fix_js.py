import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add the Yeni Sohbet button HTML if it's missing
if 'id="clearChatBtn"' not in html:
    header_old = """    <div class="flex items-center gap-3">
      <!-- Ayarlar Butonu -->"""
    header_new = """    <div class="flex items-center gap-3">
      <!-- Yeni Sohbet -->
      <button id="clearChatBtn" class="text-xs font-medium text-slate-300 hover:text-white bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-full transition">Yeni Sohbet</button>
      <!-- Ayarlar Butonu -->"""
    html = html.replace(header_old, header_new)

# 2. Add the JS logic for BOTH New Chat and Image Upload
missing_js = """

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

if 'addImageBtn.addEventListener' not in html:
    html = html.replace('// Ayarlar modalini ac', missing_js + '\n    // Ayarlar modalini ac')
    
    # Just in case 'Ayarlar modalini ac' is not found, append before </script>
    if 'addImageBtn.addEventListener' not in html:
        html = html.replace('</script>', missing_js + '\n  </script>')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("JS properly patched!")
