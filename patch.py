import io

with io.open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re

pattern = re.compile(r"async function checkAuthOnLoad\(\) \{.*?setTimeout\(openAuthModal, 350\);\s*\}", re.DOTALL)
replacement = r"""async function checkAuthOnLoad() {
    if (userName && userPin && /^\d{6}$/.test(userPin)) {
      updateUserNameUI(userName);
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: userName, pin: userPin })
        });
        if (res.ok) {
          const data = await res.json();
          if (data.success) {
            policyAccepted = data.policy_accepted || false;
            currentUserChats = data.chats || [];
            const settings = data.settings || {};
            
            const pInput = document.getElementById('personalizationInput');
            if (pInput) pInput.value = settings.personalization || "";
            const mToggle = document.getElementById('memoryToggleBtn');
            if (mToggle) mToggle.checked = settings.memory_enabled !== false;

            if (!policyAccepted) {
              const pModal = document.getElementById('policyModal');
              if (pModal) pModal.style.display = 'flex';
            } else {
              if (typeof renderSidebarChats === 'function') renderSidebarChats(currentUserChats);
              if (currentUserChats.length > 0) {
                 currentChatId = currentUserChats[0].id;
                 renderSavedHistory(currentUserChats[0].messages);
              }
            }
            return;
          }
        }
      } catch (err) {
        console.log("Sunucu kontrolü beklemede, yerel oturum devam ediyor.");
        let localUsers = {};
        try { localUsers = JSON.parse(localStorage.getItem('mebot_users_db') || '{}'); } catch(e){}
        const uKey = userName.toLowerCase();
        if (localUsers[uKey]) {
           const savedMsgs = localUsers[uKey].messages;
           if (savedMsgs && savedMsgs.length > 0) {
             renderSavedHistory(savedMsgs);
           }
        }
        return;
      }
    }
    setTimeout(openAuthModal, 350);
  }"""

new_content = pattern.sub(replacement, content)

with io.open('app.js', 'w', encoding='utf-8') as f:
    f.write(new_content)
    
print("Updated successfully")
