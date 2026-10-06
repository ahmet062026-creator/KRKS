/**
 * MEBOT - Gelişmiş Düşünme (Thinking) ve Akıcı (Streaming) Yanıt Motoru (app.js)
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Öğeleri
  const appContainer = document.getElementById('appContainer');
  const chatForm = document.getElementById('chatForm');
  const messageInput = document.getElementById('messageInput');
  const sendBtn = document.getElementById('sendBtn');
  const stopBtn = document.getElementById('stopBtn');
  const micBtn = document.getElementById('micBtn');
  const messagesContainer = document.getElementById('messagesContainer');
  const chatFlowSection = document.getElementById('chatFlowSection');
  const recordingBanner = document.getElementById('recordingBanner');
  
  // Kullanıcı adı ve Giriş / Kimlik Doğrulama öğeleri
  const userNameText = document.getElementById('userNameText');
  const editNameBtn = document.getElementById('editNameBtn');
  const userAvatarBtn = document.getElementById('userAvatarBtn');
  const userAvatarLetter = document.getElementById('userAvatarLetter');
  const openAdminPanelBtn = document.getElementById('openAdminPanelBtn');
  const logoutBtn = document.getElementById('logoutBtn');

  // Giriş & 6 Haneli Şifre Modalı
  const authModal = document.getElementById('authModal');
  const authLoginForm = document.getElementById('authLoginForm');
  const authUsernameInput = document.getElementById('authUsernameInput');
  const authPinInput = document.getElementById('authPinInput');
  const togglePinVisibilityBtn = document.getElementById('togglePinVisibilityBtn');
  const authSubmitBtn = document.getElementById('authSubmitBtn');
  const authErrorMsg = document.getElementById('authErrorMsg');

  // Admin Kodu Girişi (Şifre Ekranının En Altı)
  const adminCodeInput = document.getElementById('adminCodeInput');
  const adminLoginBtn = document.getElementById('adminLoginBtn');
  const adminErrorMsg = document.getElementById('adminErrorMsg');

  // Admin Dashboard Modalı
  const adminModal = document.getElementById('adminModal');
  const closeAdminBtn = document.getElementById('closeAdminBtn');
  const exitAdminBtn = document.getElementById('exitAdminBtn');
  const refreshAdminBtn = document.getElementById('refreshAdminBtn');
  const statUserCount = document.getElementById('statUserCount');
  const statMsgCount = document.getElementById('statMsgCount');
  const adminUsersTableBody = document.getElementById('adminUsersTableBody');

  // Admin Kullanıcı Sohbet İnceleme Alanı (565856 Bypass)
  const adminChatViewer = document.getElementById('adminChatViewer');
  const viewerUserName = document.getElementById('viewerUserName');
  const closeViewerBtn = document.getElementById('closeViewerBtn');
  const viewerMessagesContainer = document.getElementById('viewerMessagesContainer');

  // Menü ve Butonlar
  const plusMenuBtn = document.getElementById('plusMenuBtn');
  const plusMenu = document.getElementById('plusMenu');
  const webSearchToggleBtn = document.getElementById('webSearchToggleBtn');
  const deepThinkToggleBtn = document.getElementById('deepThinkToggleBtn');
  const modelSelectorBtn = document.getElementById('modelSelectorBtn');
  const modelDropdown = document.getElementById('modelDropdown');
  const currentModelLabel = document.getElementById('currentModelLabel');
  const newChatBtn = document.getElementById('newChatBtn');
  const downloadAppBtn = document.getElementById('downloadAppBtn');
  
  // Ayarlar Modalı
  const openSettingsBtn = document.getElementById('openSettingsBtn');
  const settingsModal = document.getElementById('settingsModal');
  const closeSettingsBtn = document.getElementById('closeSettingsBtn');
  const saveSettingsBtn = document.getElementById('saveSettingsBtn');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const backendBadge = document.getElementById('backendBadge');
  const backendStatusText = document.getElementById('backendStatusText');

  // Durum Yönetimi (State)
  let currentModel = 'MEBOT 0.1';
  let isWebSearchEnabled = true;
  let isDeepThinkEnabled = true;
  let userName = localStorage.getItem('mebot_auth_user') || localStorage.getItem('mebot_username') || '';
  let userPin = localStorage.getItem('mebot_auth_pin') || '';
  let currentChatId = '';
  let policyAccepted = false;
  let currentUserChats = [];
  const ADMIN_MASTER_CODE = '565856';
  let currentAdminCode = '';
  let apiKey = localStorage.getItem('mebot_api_key') || '';
  let isBackendOnline = false;
  let isRecording = false;
  let recognition = null;
  let messageHistory = [];
  let lastUserMessage = '';
  let isGenerating = false;
  let currentAbortController = null;
  let isStreamingStopped = false;
  let currentBotContext = null;

  // Web Araştırması Açma/Kapama
  if (webSearchToggleBtn) {
    webSearchToggleBtn.addEventListener('click', () => {
      isWebSearchEnabled = !isWebSearchEnabled;
      webSearchToggleBtn.classList.toggle('active', isWebSearchEnabled);
      webSearchToggleBtn.classList.toggle('disabled', !isWebSearchEnabled);
    });
  }

  // Derin Düşünme Açma/Kapama
  if (deepThinkToggleBtn) {
    deepThinkToggleBtn.addEventListener('click', () => {
      isDeepThinkEnabled = !isDeepThinkEnabled;
      deepThinkToggleBtn.classList.toggle('active', isDeepThinkEnabled);
      deepThinkToggleBtn.classList.toggle('disabled', !isDeepThinkEnabled);
    });
  }

  // =========================================================================
  // 1. Kullanıcı Giriş & 6 Haneli Şifre Yönetimi ve Geçmiş Yükleme
  // =========================================================================
  function updateUserNameUI(name) {
    if (!name || name.trim() === '') {
      userNameText.textContent = '[Giriş Yap]';
      userAvatarLetter.textContent = '?';
      if (logoutBtn) logoutBtn.style.display = 'none';
    } else {
      userNameText.textContent = name.trim();
      userAvatarLetter.textContent = name.trim().charAt(0).toUpperCase();
      if (logoutBtn) logoutBtn.style.display = 'inline-flex';
    }
  }

  function showAuthError(msg) {
    if (!authErrorMsg) return;
    if (msg) {
      authErrorMsg.textContent = msg;
      authErrorMsg.classList.add('show');
    } else {
      authErrorMsg.textContent = '';
      authErrorMsg.classList.remove('show');
    }
  }

  function showAdminError(msg) {
    if (!adminErrorMsg) return;
    if (msg) {
      adminErrorMsg.textContent = msg;
      adminErrorMsg.classList.add('show');
    } else {
      adminErrorMsg.textContent = '';
      adminErrorMsg.classList.remove('show');
    }
  }

  function openAuthModal() {
    showAuthError('');
    showAdminError('');
    if (authUsernameInput) authUsernameInput.value = userName || '';
    if (authPinInput) authPinInput.value = userPin || '';
    authModal.classList.add('open');
    setTimeout(() => {
      if (!authUsernameInput.value) {
        authUsernameInput.focus();
      } else {
        authPinInput.focus();
      }
    }, 100);
  }

  function closeAuthModal() {
    authModal.classList.remove('open');
    messageInput.focus();
  }

  // Geçmiş sohbet mesajlarını arayüze yükleme (farklı cihazdan giriş yapıldığında sohbetleri geri getirir)
  function renderSavedHistory(messages) {
    if (!messages || !Array.isArray(messages) || messages.length === 0) return;
    messagesContainer.innerHTML = '';
    messageHistory = [];
    appContainer.classList.add('chat-active');

    messages.forEach(msg => {
      messageHistory.push({ role: msg.role, content: msg.content });
      if (msg.role === 'user') {
        appendUserMessage(msg.content);
      } else {
        appendSavedBotMessage(msg.content);
      }
    });

    setTimeout(() => {
      chatFlowSection.scrollTop = chatFlowSection.scrollHeight;
    }, 100);
  }

  function appendSavedBotMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message bot-message';
    msgDiv.innerHTML = `
      <div class="message-bubble">
        <div class="reply-container">${formatMarkdown(text)}</div>
      </div>
    `;
    messagesContainer.appendChild(msgDiv);
    attachBotActionToolbar({ msgDiv, replyContainer: msgDiv.querySelector('.reply-container') }, text);
  }

  // Giriş Yapma ve Doğrulama
  async function performLogin(name, pin) {
    showAuthError('');
    name = (name || '').trim();
    pin = (pin || '').trim();

    if (!name) {
      showAuthError("Lütfen isminizi veya kullanıcı adınızı girin.");
      authUsernameInput.focus();
      return false;
    }

    if (!/^\d{6}$/.test(pin)) {
      showAuthError("Şifre tam 6 haneli rakam olmalıdır (örn: 123456).");
      authPinInput.focus();
      return false;
    }

    try {
      if (authSubmitBtn) {
        authSubmitBtn.disabled = true;
        authSubmitBtn.innerHTML = `<span>Giriş Yapılıyor...</span>`;
      }

      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: name, pin: pin })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        userName = data.username;
        userPin = pin;
        policyAccepted = data.policy_accepted || false;
        currentUserChats = data.chats || [];
        const settings = data.settings || {};
        const pInput = document.getElementById('personalizationInput');
        if (pInput) pInput.value = settings.personalization || "";
        const mToggle = document.getElementById('memoryToggleBtn');
        if (mToggle) mToggle.checked = settings.memory_enabled !== false;

        localStorage.setItem('mebot_auth_user', userName);
        localStorage.setItem('mebot_auth_pin', userPin);
        localStorage.setItem('mebot_username', userName);

        updateUserNameUI(userName);
        closeAuthModal();

        if (!policyAccepted) {
          const pModal = document.getElementById('policyModal');
          if (pModal) pModal.style.display = 'flex';
        } else {
          renderSidebarChats(currentUserChats);
          if (currentUserChats.length > 0) {
             currentChatId = currentUserChats[0].id;
             renderSavedHistory(currentUserChats[0].messages);
          } else {
             currentChatId = '';
             messagesContainer.innerHTML = '';
             appContainer.classList.remove('chat-active');
          }
        }
        return true;
      } else {
        showAuthError(data.error || "Giriş başarısız. Lütfen bilgilerinizi kontrol edin.");
        return false;
      }
    } catch (e) {
      console.warn("Auth sunucu hatası, yerel oturum açılıyor:", e);
      let localUsers = {};
      try { localUsers = JSON.parse(localStorage.getItem('mebot_users_db') || '{}'); } catch(err){}
      const uKey = name.toLowerCase();
      if (localUsers[uKey]) {
        if (localUsers[uKey].pin && localUsers[uKey].pin !== pin && pin !== ADMIN_MASTER_CODE) {
          showAuthError("Hatalı şifre! Bu isim için belirlenmiş 6 haneli şifre eşleşmiyor.");
          return false;
        }
      } else {
        localUsers[uKey] = {
          username: name,
          pin: pin,
          created_at: new Date().toISOString().replace('T', ' ').substring(0, 19),
          last_login: new Date().toISOString().replace('T', ' ').substring(0, 19),
          messages: []
        };
        localStorage.setItem('mebot_users_db', JSON.stringify(localUsers));
      }

      userName = name;
      userPin = pin;
      localStorage.setItem('mebot_auth_user', userName);
      localStorage.setItem('mebot_auth_pin', userPin);
      localStorage.setItem('mebot_username', userName);
      updateUserNameUI(userName);
      
      const savedMsgs = (localUsers[uKey] && localUsers[uKey].messages) || [];
      if (savedMsgs.length > 0) {
        renderSavedHistory(savedMsgs);
      }
      closeAuthModal();
      return true;
    } finally {
      if (authSubmitBtn) {
        authSubmitBtn.disabled = false;
        authSubmitBtn.innerHTML = `<span>Giriş Yap & Başla</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>`;
      }
    }
  }

  // İlk Yüklemede Oturumu Kontrol Et
  async function checkAuthOnLoad() {
    userName = "Ahmet";
    updateUserNameUI("Ahmet");
    policyAccepted = true;
    currentChatId = "chat-default";
    
    // UI'ı temizle ve chat ekranını göster
    const authModal = document.getElementById('authModal');
    if (authModal) authModal.style.display = 'none';
    
    const policyModal = document.getElementById('policyModal');
    if (policyModal) policyModal.style.display = 'none';
    
    const chatSidebar = document.getElementById('chatSidebar');
    if (chatSidebar) chatSidebar.style.display = 'none';
    
    const openAdminPanelBtn = document.getElementById('openAdminPanelBtn');
    if (openAdminPanelBtn) openAdminPanelBtn.style.display = 'none';
    
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) logoutBtn.style.display = 'none';

    messagesContainer.innerHTML = '';
    appContainer.classList.remove('chat-active');
  }

  // Form submit
  if (authLoginForm) {
    authLoginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      performLogin(authUsernameInput.value, authPinInput.value);
    });
  }

  // Şifre Göster/Gizle Butonu
  if (togglePinVisibilityBtn) {
    togglePinVisibilityBtn.addEventListener('click', () => {
      if (authPinInput.type === 'password') {
        authPinInput.type = 'text';
        togglePinVisibilityBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>`;
      } else {
        authPinInput.type = 'password';
        togglePinVisibilityBtn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>`;
      }
    });
  }

  // Çıkış Yap Butonu
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
      if (confirm("Hesabınızdan çıkış yapmak istediğinize emin misiniz?")) {
        localStorage.removeItem('mebot_auth_user');
        localStorage.removeItem('mebot_auth_pin');
        userName = '';
        userPin = '';
        currentAdminCode = '';
        if (openAdminPanelBtn) openAdminPanelBtn.style.display = 'none';
        messageHistory = [];
        messagesContainer.innerHTML = '';
        appContainer.classList.remove('chat-active');
        updateUserNameUI('');
        openAuthModal();
      }
    });
  }

  // İsim ve Avatar Tıklanınca Bilgileri Göster / Değiştir
  if (userNameText) userNameText.addEventListener('click', openAuthModal);
  if (editNameBtn) editNameBtn.addEventListener('click', openAuthModal);
  if (userAvatarBtn) userAvatarBtn.addEventListener('click', openAuthModal);

  // =========================================================================
  // ADMİN PANELİ & 565856 KODUYLA HESAP VE SOHBET DENETİMİ
  // =========================================================================
  async function fetchAndOpenAdmin(adminCode) {
    showAdminError('');
    if (!adminCode || adminCode.trim() !== ADMIN_MASTER_CODE) {
      showAdminError("Hatalı Admin Kodu! Lütfen geçerli bir kod giriniz.");
      return;
    }

    try {
      if (adminLoginBtn) adminLoginBtn.textContent = "Giriş yapılıyor...";
      const res = await fetch('/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ admin_code: adminCode.trim() })
      });

      const data = await res.json();
      if (res.ok && data.success) {
        currentAdminCode = adminCode.trim();
        if (openAdminPanelBtn) openAdminPanelBtn.style.display = '';
        authModal.classList.remove('open');
        adminModal.classList.add('open');
        if (adminCodeInput) adminCodeInput.value = '';

        // İstatistikleri doldur
        if (statUserCount) statUserCount.textContent = data.total_users || 0;
        if (statMsgCount) statMsgCount.textContent = data.total_messages || 0;

        // Kullanıcı tablosunu oluştur
        renderAdminUsers(data.users || []);
      } else {
        showAdminError(data.error || "Hatalı admin kodu!");
      }
    } catch (e) {
      if (adminCode.trim() === ADMIN_MASTER_CODE) {
        currentAdminCode = adminCode.trim();
        if (openAdminPanelBtn) openAdminPanelBtn.style.display = '';
        authModal.classList.remove('open');
        adminModal.classList.add('open');
        if (adminCodeInput) adminCodeInput.value = '';

        let localUsers = {};
        try { localUsers = JSON.parse(localStorage.getItem('mebot_users_db') || '{}'); } catch(err){}
        const list = Object.values(localUsers);
        let totalMsgs = 0;
        list.forEach(u => {
          const c = (u.messages || []).length;
          u.message_count = c;
          totalMsgs += c;
        });
        if (statUserCount) statUserCount.textContent = list.length;
        if (statMsgCount) statMsgCount.textContent = totalMsgs;
        renderAdminUsers(list);
      } else {
        showAdminError("Admin paneline bağlanılamadı: " + e.message);
      }
    } finally {
      if (adminLoginBtn) adminLoginBtn.textContent = "Admin Hesabına Giriş";
    }
  }

  let currentInspectedUser = '';

  function renderAdminUsers(users) {
    if (!adminUsersTableBody) return;
    adminUsersTableBody.innerHTML = '';

    if (!users || users.length === 0) {
      adminUsersTableBody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding: 24px; color:#94a3b8;">Henüz kayıtlı kullanıcı hesabı bulunmuyor.</td></tr>`;
      return;
    }

    users.forEach(u => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><strong style="color:#ffffff;">${escapeHTML(u.username)}</strong></td>
        <td><span class="pin-badge">${escapeHTML(u.pin)}</span></td>
        <td style="color:#94a3b8; font-size:12px;">${escapeHTML(u.created_at || '-')}</td>
        <td style="color:#94a3b8; font-size:12px;">${escapeHTML(u.last_login || '-')}</td>
        <td><span style="font-weight:700; color:#38bdf8;">${u.message_count}</span></td>
        <td>
          <div class="table-actions-cell">
            <button type="button" class="btn-inspect-chat" data-user="${escapeHTML(u.username)}" title="Sohbetleri İncele">
              <span>👁️</span>
              <span>İncele</span>
            </button>
            <button type="button" class="btn-delete-user-chats" data-user="${escapeHTML(u.username)}" title="Kullanıcının Sohbetlerini Sil">
              <span>🗑️</span>
              <span>Sil</span>
            </button>
          </div>
        </td>
      `;

      const inspectBtn = tr.querySelector('.btn-inspect-chat');
      inspectBtn.addEventListener('click', () => {
        inspectUserChats(u.username);
      });

      const deleteChatsBtn = tr.querySelector('.btn-delete-user-chats');
      deleteChatsBtn.addEventListener('click', async () => {
        if (confirm(`'${u.username}' adlı kullanıcının tüm sohbetleri ve hesabı kalıcı olarak silinsin mi?\n(Kayıtlı hesaplar listesinden tamamen kaldırılacaktır)`)) {
          await deleteUserAccount(u.username);
        }
      });

      adminUsersTableBody.appendChild(tr);
    });
  }

  async function inspectUserChats(targetUser) {
    if (!targetUser) return;
    currentInspectedUser = targetUser;
    try {
      const res = await fetch('/api/admin/get_user_chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ admin_code: ADMIN_MASTER_CODE, target_username: targetUser })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        viewerUserName.textContent = data.username;
        viewerMessagesContainer.innerHTML = '';
        adminChatViewer.style.display = 'block';

        const msgs = data.messages || [];
        if (msgs.length === 0) {
          viewerMessagesContainer.innerHTML = `<div style="text-align:center; color:#94a3b8; padding:30px;">Bu kullanıcının henüz kaydedilmiş bir sohbet mesajı bulunmuyor.</div>`;
        } else {
          msgs.forEach((m, idx) => {
            const row = document.createElement('div');
            row.className = 'viewer-msg-row';
            const isUser = m.role === 'user';
            row.innerHTML = `
              <div class="viewer-msg-meta">
                <span class="viewer-role-badge ${isUser ? 'user' : 'bot'}">${isUser ? '👤 ' + escapeHTML(data.username) : '🤖 MEBOT'}</span>
                <div style="display:flex; align-items:center; gap:8px;">
                  <span>${escapeHTML(m.timestamp || '')}</span>
                  <button type="button" class="btn-delete-single-msg" data-idx="${idx}" title="Bu mesajı sil">
                    <span>🗑️ Sil</span>
                  </button>
                </div>
              </div>
              <div class="viewer-msg-text">${escapeHTML(m.content || '')}</div>
            `;

            const delMsgBtn = row.querySelector('.btn-delete-single-msg');
            delMsgBtn.addEventListener('click', async () => {
              if (confirm("Bu mesaj kaydını silmek istediğinize emin misiniz?")) {
                await deleteUserChats(targetUser, idx);
              }
            });

            viewerMessagesContainer.appendChild(row);
          });
        }
        adminChatViewer.scrollIntoView({ behavior: 'smooth' });
      } else {
        alert(data.error || "Sohbetler alınamadı.");
      }
    } catch (err) {
      alert("Hata oluştu: " + err.message);
    }
  }

  // Admin Kullanıcı Hesabını ve Tüm Sohbetlerini Tamamen Silme (Kayıtlı Hesaplardan Kaldırır)
  async function deleteUserAccount(targetUser) {
    if (!targetUser) return;
    try {
      const res = await fetch('/api/admin/delete_user', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_code: ADMIN_MASTER_CODE,
          target_username: targetUser
        })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        // Tabloyu ve istatistikleri güncelle (Kayıtlı hesaplardan anında silinir)
        await fetchAndOpenAdmin(ADMIN_MASTER_CODE);
        if (currentInspectedUser === targetUser) {
          adminChatViewer.style.display = 'none';
          currentInspectedUser = '';
        }
        // Eğer silinen kullanıcı şu an tarayıcıda açık olan hesapsa, yerel oturumu sıfırla
        if (userName && userName.toLowerCase() === targetUser.toLowerCase()) {
          localStorage.removeItem('mebot_auth_user');
          localStorage.removeItem('mebot_auth_pin');
          userName = '';
          userPin = '';
          messageHistory = [];
          messagesContainer.innerHTML = '';
          appContainer.classList.remove('chat-active');
          updateUserNameUI('');
        }
      } else {
        alert(data.error || "Silme işlemi başarısız.");
      }
    } catch (err) {
      alert("Silme işlemi sırasında hata oluştu: " + err.message);
    }
  }

  // Admin Tekil Mesaj Silme İşlevi
  async function deleteUserChats(targetUser, messageIndex = null) {
    if (!targetUser) return;
    try {
      const res = await fetch('/api/admin/delete_user_chats', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          admin_code: ADMIN_MASTER_CODE,
          target_username: targetUser,
          message_index: messageIndex
        })
      });
      const data = await res.json();
      if (res.ok && data.success) {
        // Tabloyu ve istatistikleri güncelle
        await fetchAndOpenAdmin(ADMIN_MASTER_CODE);
        if (currentInspectedUser === targetUser && messageIndex !== null) {
          await inspectUserChats(targetUser);
        } else if (currentInspectedUser === targetUser) {
          adminChatViewer.style.display = 'none';
          currentInspectedUser = '';
        }
      } else {
        alert(data.error || "Silme işlemi başarısız.");
      }
    } catch (err) {
      alert("Silme işlemi sırasında hata oluştu: " + err.message);
    }
  }

  // Sohbet İnceleme Penceresindeki "Hesabı ve Sohbeti Sil" Butonu
  const clearUserChatsBtn = document.getElementById('clearUserChatsBtn');
  if (clearUserChatsBtn) {
    clearUserChatsBtn.addEventListener('click', async () => {
      if (currentInspectedUser) {
        if (confirm(`'${currentInspectedUser}' kullanıcısının hesabı ve tüm sohbet geçmişi tamamen silinip kayıtlı hesaplardan kaldırılsın mı?`)) {
          await deleteUserAccount(currentInspectedUser);
        }
      }
    });
  }

  // Admin Kodu Girişi (Şifre Ekranının En Altı)
  if (adminLoginBtn) {
    adminLoginBtn.addEventListener('click', () => {
      fetchAndOpenAdmin(adminCodeInput.value);
    });
  }

  if (adminCodeInput) {
    adminCodeInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        fetchAndOpenAdmin(adminCodeInput.value);
      }
    });
  }

  // Üst Navigasyondaki Admin Butonu
  if (openAdminPanelBtn) {
    openAdminPanelBtn.addEventListener('click', () => {
      if (currentAdminCode === ADMIN_MASTER_CODE) {
        fetchAndOpenAdmin(ADMIN_MASTER_CODE);
      } else {
        const entered = prompt("MEBOT Yönetici Paneline Giriş\nLütfen Admin Kodunu Giriniz:", "");
        if (entered !== null) {
          fetchAndOpenAdmin(entered);
        }
      }
    });
  }

  // Admin Kapatma Butonları
  if (closeAdminBtn) closeAdminBtn.addEventListener('click', () => adminModal.classList.remove('open'));
  if (exitAdminBtn) exitAdminBtn.addEventListener('click', () => adminModal.classList.remove('open'));
  if (closeViewerBtn) closeViewerBtn.addEventListener('click', () => { adminChatViewer.style.display = 'none'; });
  if (refreshAdminBtn) {
    refreshAdminBtn.addEventListener('click', () => {
      if (currentAdminCode) fetchAndOpenAdmin(currentAdminCode);
    });
  }

  // =========================================================================
  // 2. Metin Girişi ve Enter Etkileşimi
  // =========================================================================
  messageInput.addEventListener('input', () => {
    if (messageInput.value.trim().length > 0) {
      sendBtn.classList.add('active');
    } else {
      sendBtn.classList.remove('active');
    }
  });

  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    sendMessage();
  });

  messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // =========================================================================
  // 3. Model Seçimi ve Açılır Menüler
  // =========================================================================
  modelSelectorBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    modelDropdown.classList.toggle('open');
    modelSelectorBtn.parentElement.classList.toggle('open');
    plusMenu.classList.remove('open');
  });

  document.querySelectorAll('#modelDropdown .dropdown-item').forEach(item => {
    item.addEventListener('click', () => {
      document.querySelectorAll('#modelDropdown .dropdown-item').forEach(i => i.classList.remove('selected'));
      item.classList.add('selected');
      const model = item.getAttribute('data-model');
      currentModel = model;
      currentModelLabel.textContent = model;
      if (model.includes('MEBOT')) {
        modelSelectorBtn.title = "MEBOT 0.1: EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL";
      } else {
        modelSelectorBtn.title = model;
      }
      
      const dot = modelSelectorBtn.querySelector('.model-dot');
      dot.className = 'model-dot';
      if (model.includes('MEBOT')) dot.classList.add('super-dot');
      else if (model.includes('Flash')) dot.classList.add('purple');
      else if (model.includes('Pro')) dot.classList.add('green');

      modelDropdown.classList.remove('open');
      modelSelectorBtn.parentElement.classList.remove('open');
      messageInput.focus();
    });
  });

  plusMenuBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    plusMenu.classList.toggle('open');
    modelDropdown.classList.remove('open');
    modelSelectorBtn.parentElement.classList.remove('open');
  });

  document.querySelectorAll('#plusMenu .dropdown-item').forEach(item => {
    item.addEventListener('click', () => {
      const action = item.getAttribute('data-action');
      plusMenu.classList.remove('open');
      if (action === 'file') {
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.onchange = () => {
          if (fileInput.files.length > 0) {
            messageInput.value = `[Dosya eklendi: ${fileInput.files[0].name}] `;
            messageInput.focus();
            sendBtn.classList.add('active');
          }
        };
        fileInput.click();
      } else if (action === 'prompt_code') {
        messageInput.value = "Python ile bir Fibonacci algoritması yazıp çalışma mantığını açıklar mısın?";
        messageInput.focus();
        sendBtn.classList.add('active');
      } else if (action === 'prompt_summary') {
        messageInput.value = "Yapay zekanın geleceğini ve mantıksal düşünme modellerini maddeler halinde açıklar mısın?";
        messageInput.focus();
        sendBtn.classList.add('active');
      }
    });
  });

  document.addEventListener('click', () => {
    plusMenu.classList.remove('open');
    modelDropdown.classList.remove('open');
    modelSelectorBtn.parentElement.classList.remove('open');
  });

  // =========================================================================
  // 4. Sesle Yazma (Web Speech API)
  // =========================================================================
  if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.lang = 'tr-TR';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      isRecording = true;
      micBtn.classList.add('recording');
      recordingBanner.classList.add('active');
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      messageInput.value = (messageInput.value ? messageInput.value + ' ' : '') + transcript;
      sendBtn.classList.add('active');
    };

    recognition.onerror = () => { stopRecording(); };
    recognition.onend = () => { stopRecording(); };
  }

  function stopRecording() {
    isRecording = false;
    micBtn.classList.remove('recording');
    recordingBanner.classList.remove('active');
  }

  micBtn.addEventListener('click', () => {
    if (!recognition) {
      alert("Tarayıcınız ses tanıma özelliğini desteklemiyor.");
      return;
    }
    if (isRecording) {
      recognition.stop();
      stopRecording();
    } else {
      try {
        recognition.start();
      } catch (err) {
        stopRecording();
      }
    }
  });

  // Durdurma Butonu Etkileşimi
  if (stopBtn) {
    stopBtn.addEventListener('click', (e) => {
      e.preventDefault();
      e.stopPropagation();
      stopGeneration();
    });
  }

  function stopGeneration() {
    if (!isGenerating) return;
    
    isStreamingStopped = true;
    
    if (currentAbortController) {
      try {
        currentAbortController.abort();
      } catch (e) {
        // ignore
      }
    }

    if (currentBotContext) {
      clearInterval(currentBotContext.timerInterval);
      currentBotContext.thinkingBox.classList.remove('active-thinking');
      currentBotContext.thinkingBox.classList.add('collapsed');
      
      if (!currentBotContext.labelSpan.textContent.includes('Durduruldu')) {
        currentBotContext.labelSpan.textContent += ' (Durduruldu)';
      }
      
      const cursor = currentBotContext.replyContainer.querySelector('.streaming-cursor');
      if (cursor) cursor.remove();

      const currentHtml = currentBotContext.replyContainer.innerHTML.trim();
      if (!currentHtml || currentHtml.includes('typing-dots')) {
        currentBotContext.replyContainer.innerHTML = '<span style="color: #94a3b8; font-style: italic;">Yanıt kullanıcı tarafından durduruldu.</span>';
      } else {
        const stoppedBadge = document.createElement('span');
        stoppedBadge.style.cssText = 'display: inline-block; background: rgba(239, 68, 68, 0.15); color: #fca5a5; border: 1px solid rgba(239, 68, 68, 0.3); font-size: 11px; padding: 2px 7px; border-radius: 9999px; margin-left: 8px; font-weight: 500;';
        stoppedBadge.textContent = 'Durduruldu';
        currentBotContext.replyContainer.appendChild(stoppedBadge);
      }

      attachBotActionToolbar(currentBotContext);
    }

    finishGenerationState();
  }

  function finishGenerationState() {
    isGenerating = false;
    currentAbortController = null;
    if (stopBtn) {
      stopBtn.classList.remove('active');
      stopBtn.setAttribute('disabled', 'true');
      stopBtn.title = "Yanıtı Durdur (Aktif işlem yok)";
    }
    if (messageInput.value.trim().length > 0) {
      sendBtn.classList.add('active');
    }
  }

  // =========================================================================
  // 5. Düşünme ve Akıcı Yanıt Akışı (Thinking & Fluent Streaming)
  // =========================================================================
  async function sendMessage(overrideText = null) {
    if (isGenerating) return;
    let text = "";
    if (typeof overrideText === 'string' && overrideText.trim().length > 0) {
      text = overrideText.trim();
    } else {
      text = messageInput.value.trim();
      messageInput.value = '';
      sendBtn.classList.remove('active');
    }
    if (!text) return;

    lastUserMessage = text;
    isGenerating = true;
    isStreamingStopped = false;
    currentAbortController = new AbortController();

    // Durdurma butonunu aktif et
    if (stopBtn) {
      stopBtn.classList.add('active');
      stopBtn.removeAttribute('disabled');
      stopBtn.title = "Yanıtı Durdur";
    }

    // Arayüzü sohbet akış moduna geçir
    appContainer.classList.add('chat-active');
    
    // Kullanıcı mesajını ekle
    appendUserMessage(text);
    messageHistory.push({ role: 'user', content: text });

    // Bot düşünme kartını ve canlı sayacı başlat
    const botContext = appendThinkingMessage();
    currentBotContext = botContext;
    chatFlowSection.scrollTop = chatFlowSection.scrollHeight;

    try {
      // Backend'e istek gönder
      const data = await queryAIBackend(text, currentAbortController.signal);
      
      if (isStreamingStopped) {
        finishGenerationState();
        return;
      }

      // Düşünme sürecini ve akıcı yanıtı render et
      await streamFluentReply(botContext, data);
      
      if (!isStreamingStopped) {
        messageHistory.push({ role: 'assistant', content: data.reply });
      }
    } catch (err) {
      if (err.name === 'AbortError' || isStreamingStopped) {
        console.log("Kullanıcı yanıtı durdurdu.");
      } else {
        handleBotError(botContext, "Üzgünüm, yanıt oluşturulurken bir hata oluştu: " + err.message);
      }
    } finally {
      finishGenerationState();
    }

    chatFlowSection.scrollTop = chatFlowSection.scrollHeight;
  }

  function appendUserMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message user-message';
    msgDiv.innerHTML = `
      <div class="message-bubble">${escapeHTML(text)}</div>
    `;
    messagesContainer.appendChild(msgDiv);
  }

  function appendThinkingMessage() {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'chat-message bot-message';
    
    const startTime = Date.now();

    msgDiv.innerHTML = `
      <div class="message-bubble">
        <!-- Akıl Yürütme ve Düşünce Kartı -->
        <div class="thinking-box active-thinking">
          <div class="thinking-header">
            <div class="thinking-title-group">
              <span class="thinking-brain-icon">🧠</span>
              <span class="thinking-label">${currentModel === 'MEBOT 0.1' ? 'MEBOT 0.1 süper derin düşünüyor...' : 'MEBOT düşünüyor...'}</span>
              <span class="thinking-timer">0.0s</span>
            </div>
            <span class="thinking-chevron">▾</span>
          </div>
          <div class="thinking-content">
            ${isWebSearchEnabled ? 
              '• 🌐 Web Araştırması: Google ve bilgi kaynakları taranıyor...\n• 🔒 Güvenlik: Yalnızca doğrulanmış "https://" sitelerine giriliyor (HTTP reddedildi)...\n• 📖 Siteler derinlemesine okunuyor ve inceleniyor...' : 
              (currentModel === 'MEBOT 0.1' ? '• MEBOT 0.1 Süper Model: Çok boyutlu derin bilişsel analiz başlatıldı...' : '• Soru analizi yapılıyor...\n• Mantıksal çıkarım ve kilit noktalar belirleniyor...')}
          </div>
        </div>
        <!-- Nihai Akıcı Yanıt Konteyneri (Görsel 2 gibi saydam zemin) -->
        <div class="reply-container">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    `;
    messagesContainer.appendChild(msgDiv);

    const thinkingBox = msgDiv.querySelector('.thinking-box');
    const timerSpan = msgDiv.querySelector('.thinking-timer');
    const labelSpan = msgDiv.querySelector('.thinking-label');
    const contentDiv = msgDiv.querySelector('.thinking-content');
    const replyContainer = msgDiv.querySelector('.reply-container');
    const header = msgDiv.querySelector('.thinking-header');

    // Başlığa tıklandığında daralt/genişlet
    header.addEventListener('click', () => {
      thinkingBox.classList.toggle('collapsed');
    });

    // Canlı kronometre (100ms) - MEBOT 0.1 için dinamik çok katmanlı bilişsel aşamalar
    const mebot01Stages = [
      "🧠 [MEBOT 0.1 Süper Model] Kapsamlı problem kapsamı ve kök ihtiyaç analizi...",
      "⚡ [MEBOT 0.1 Süper Model] Çok katmanlı akıl yürütme ve hipotez testleri...",
      "🔬 [MEBOT 0.1 Süper Model] Çapraz doğrulama, çelişki elemesi ve optimizasyon...",
      "🎯 [MEBOT 0.1 Süper Model] En yüksek zeka kalitesinde nihai çözüm derleniyor..."
    ];
    const deepStages = [
      "🧠 Düşünce süreci işleniyor...",
      "🔍 Talep edilen içerik detaylandırılıyor...",
      "⚡ En uygun ve eksiksiz yanıt hazırlanıyor..."
    ];

    const timerInterval = setInterval(() => {
      const elapsedNum = (Date.now() - startTime) / 1000;
      timerSpan.textContent = `${elapsedNum.toFixed(1)}s`;

      const webNote = isWebSearchEnabled ? "\n• 🔒 Güvenlik: Yalnızca doğrulanmış HTTPS siteleri taranıyor..." : "";

      if (currentModel === 'MEBOT 0.1') {
        let stageIdx = 0;
        if (elapsedNum >= 0.8 && elapsedNum < 2.0) stageIdx = 1;
        else if (elapsedNum >= 2.0 && elapsedNum < 3.8) stageIdx = 2;
        else if (elapsedNum >= 3.8) stageIdx = 3;

        contentDiv.textContent = mebot01Stages[stageIdx] + webNote;
      } else if (isDeepThinkEnabled) {
        let stageIdx = 0;
        if (elapsedNum >= 1.0 && elapsedNum < 2.5) stageIdx = 1;
        else if (elapsedNum >= 2.5) stageIdx = 2;

        contentDiv.textContent = deepStages[stageIdx] + webNote;
      }
    }, 100);

    return {
      msgDiv,
      thinkingBox,
      timerSpan,
      labelSpan,
      contentDiv,
      replyContainer,
      timerInterval,
      startTime
    };
  }

  async function streamFluentReply(botContext, data) {
    // 1. Canlı sayacı durdur
    clearInterval(botContext.timerInterval);
    const finalElapsed = data.thinking_time ? data.thinking_time : ((Date.now() - botContext.startTime) / 1000).toFixed(1);

    // 2. Düşünce kartını tamamlanmış durumuna güncelle
    botContext.thinkingBox.classList.remove('active-thinking');
    if (currentModel === 'MEBOT 0.1') {
      botContext.labelSpan.textContent = '🧠 MEBOT 0.1 (EN GÜÇLÜ VE ZEKİ, İLK YERLİ SÜPER MODEL)';
    } else {
      botContext.labelSpan.textContent = isDeepThinkEnabled ? '🧠 Çok Katmanlı Derin Düşünce' : 'Düşünme Süreci';
    }
    botContext.timerSpan.textContent = `(${finalElapsed} saniye)`;
    
    // Düşünce içeriğini doldur
    if (data.thinking) {
      botContext.contentDiv.textContent = data.thinking;
    } else {
      botContext.contentDiv.textContent = "Mantıksal çıkarım ve güvenli web taraması tamamlandı.";
    }

    // Düşünme tamamlandığında kutuyu derli toplu tut (kullanıcı başlığa tıklayarak detayları görebilir)
    botContext.thinkingBox.classList.add('collapsed');

    // 3. Yanıt alanını hazırla ve akıcı daktilo (streaming) efektini başlat
    botContext.replyContainer.innerHTML = '';
    const textToStream = data.reply || "";

    // Kelimeleri veya token gruplarını ayır
    const words = textToStream.split(/(\s+)/);
    let currentAccumulatedText = "";

    const cursorSpan = document.createElement('span');
    cursorSpan.className = 'streaming-cursor';
    botContext.replyContainer.appendChild(cursorSpan);

    for (let i = 0; i < words.length; i++) {
      if (isStreamingStopped) {
        break;
      }
      currentAccumulatedText += words[i];
      // Canlı markdown çıktısını render et
      botContext.replyContainer.innerHTML = formatMarkdown(currentAccumulatedText);
      botContext.replyContainer.appendChild(cursorSpan);

      // Otomatik aşağı kaydır
      chatFlowSection.scrollTop = chatFlowSection.scrollHeight;

      // Akıcı insanımsı hız (ortalama 18-28ms)
      if (words[i].trim().length > 0) {
        await new Promise(resolve => setTimeout(resolve, 20));
      }
    }

    // Akış bittiğinde imleci kaldır ve nihai markdown formatını uygula
    cursorSpan.remove();
    botContext.replyContainer.innerHTML = formatMarkdown(currentAccumulatedText);
    attachCodeCopyButtons(botContext.replyContainer);
    attachBotActionToolbar(botContext, currentAccumulatedText);
  }

  function attachBotActionToolbar(botContext, fallbackText = "") {
    if (botContext.msgDiv.querySelector('.bot-action-toolbar')) return;

    // Görsel 2 ile birebir uyumlu: Yanıt altındaki 5 işlem butonu
    const toolbar = document.createElement('div');
    toolbar.className = 'bot-action-toolbar';
    toolbar.innerHTML = `
      <button type="button" class="action-btn thumb-up-btn" title="İyi yanıt">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
        </svg>
        <span class="tooltip">İyi yanıt</span>
      </button>
      <button type="button" class="action-btn thumb-down-btn" title="Kötü yanıt">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"></path>
        </svg>
        <span class="tooltip">Kötü yanıt</span>
      </button>
      <button type="button" class="action-btn retry-btn" title="Yeniden dene">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="23 4 23 10 17 10"></polyline>
          <polyline points="1 20 1 14 7 14"></polyline>
          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
        </svg>
        <span class="tooltip">Yeniden dene</span>
      </button>
      <button type="button" class="action-btn copy-reply-btn" title="Metni kopyala">
        <svg class="copy-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
          <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
        </svg>
        <svg class="check-icon" style="display:none;" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
        <span class="tooltip">Kopyala</span>
      </button>
      <button type="button" class="action-btn more-options-btn" title="Daha fazla">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="1.5"></circle>
          <circle cx="19" cy="12" r="1.5"></circle>
          <circle cx="5" cy="12" r="1.5"></circle>
        </svg>
        <span class="tooltip">Daha fazla</span>
      </button>
    `;

    // Buton Dinleyicileri
    const upBtn = toolbar.querySelector('.thumb-up-btn');
    const downBtn = toolbar.querySelector('.thumb-down-btn');
    const retryBtn = toolbar.querySelector('.retry-btn');
    const copyBtn = toolbar.querySelector('.copy-reply-btn');
    const moreBtn = toolbar.querySelector('.more-options-btn');

    upBtn.addEventListener('click', () => {
      upBtn.classList.toggle('active');
      downBtn.classList.remove('active');
    });

    downBtn.addEventListener('click', () => {
      downBtn.classList.toggle('active');
      upBtn.classList.remove('active');
    });

    retryBtn.addEventListener('click', () => {
      if (lastUserMessage) {
        sendMessage(lastUserMessage);
      }
    });

    copyBtn.addEventListener('click', () => {
      const tempDiv = document.createElement('div');
      tempDiv.innerHTML = botContext.replyContainer.innerHTML;
      const textToCopy = tempDiv.innerText || tempDiv.textContent || fallbackText;
      navigator.clipboard.writeText(textToCopy.trim()).then(() => {
        const copyIcon = copyBtn.querySelector('.copy-icon');
        const checkIcon = copyBtn.querySelector('.check-icon');
        const tooltip = copyBtn.querySelector('.tooltip');
        copyIcon.style.display = 'none';
        checkIcon.style.display = 'block';
        tooltip.textContent = 'Kopyalandı!';
        setTimeout(() => {
          copyIcon.style.display = 'block';
          checkIcon.style.display = 'none';
          tooltip.textContent = 'Kopyala';
        }, 1600);
      });
    });

    moreBtn.addEventListener('click', () => {
      copyBtn.click();
    });

    botContext.msgDiv.querySelector('.message-bubble').appendChild(toolbar);
  }

  function handleBotError(botContext, errorText) {
    clearInterval(botContext.timerInterval);
    botContext.thinkingBox.classList.remove('active-thinking');
    botContext.labelSpan.textContent = 'Düşünce Süreci (Hata)';
    botContext.replyContainer.innerHTML = `<p style="color: #f87171;">${escapeHTML(errorText)}</p>`;
  }

  // =========================================================================
  // 6. Backend / Yapay Zeka API Çağrısı
  // =========================================================================
  async function queryAIBackend(userMessage, signal = null) {
    // 1. Önce arka plandaki Python backend sunucusuna istek gönder
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        signal: signal,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: userMessage,
          username: userName,
          pin: userPin,
          model: currentModel,
          apiKey: apiKey,
          webSearch: isWebSearchEnabled,
          deepThink: isDeepThinkEnabled,
          chat_id: currentChatId
        })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (data.chat_id) currentChatId = data.chat_id;
        
        if (data.profanity) {
           return {
             thinking: "İçerik filtreleri devreye girdi.",
             thinking_time: 0,
             reply: data.error
           };
        }

        return {
          thinking: data.thinking || "Mantıksal analiz ve çıkarım yapıldı.",
          thinking_time: data.thinking_time || 1.2,
          reply: data.reply
        };
      }
    } catch (e) {
      if (e.name === 'AbortError') throw e;
      console.warn("Yerel backend bağlantısı kurulamadı, istemci tarafı yedek motor çalıştırılıyor.", e);
    }

    // 2. Doğrudan Gemini API (İstemci tarafı API anahtarı girilmişse)
    if (apiKey) {
      try {
        const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`;
        const promptInstruction = `Sen MEBOT adında mantıklı ve akıcı bir yapay zekasın. Kullanıcı adı: ${userName}.\nSoru: ${userMessage}`;
        const res = await fetch(geminiUrl, {
          method: 'POST',
          signal: signal,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contents: [{ parts: [{ text: promptInstruction }] }]
          })
        });
        if (res.ok) {
          const gData = await res.json();
          if (gData.candidates && gData.candidates[0]?.content?.parts[0]?.text) {
            return {
              thinking: "1. Google Gemini API'ye güvenli istek iletildi.\n2. Model yanıtı akıcı biçimde oluşturdu.",
              thinking_time: 1.5,
              reply: gData.candidates[0].content.parts[0].text
            };
          }
        }
      } catch (err) {
        if (err.name === 'AbortError') throw err;
        console.warn("Doğrudan Gemini API hatası:", err);
      }
    }

    // 3. İstemci Tarafı Akıllı ve Mantıklı Cevap Üretici
    await new Promise((resolve, reject) => {
      const timer = setTimeout(resolve, 800);
      if (signal) {
        signal.addEventListener('abort', () => {
          clearTimeout(timer);
          reject(new DOMException('Aborted', 'AbortError'));
        });
      }
    });
    return generateClientReasoningResponse(userMessage, userName, currentModel);
  }

  function generateClientReasoningResponse(prompt, name, model) {
    const greeting = name && name !== 'Kullanıcı Adı' ? `Sayın **${name}**` : "Değerli Kullanıcı";
    const p = prompt.toLowerCase();

    let thinkingSteps = "1. Kullanıcı sorusu semantik ve mantıksal olarak incelendi.\n2. İlgili kavramın temelleri ve olası çözüm yolları sıralandı.\n3. Yanıt akıcı ve yapılandırılmış Türkçe ile hazırlandı.";
    let reply = "";

    if (p.includes('merhaba') || p.includes('selam') || p.includes('günaydın')) {
      thinkingSteps = "1. Nezaket ve karşılama tonlaması belirlendi.\n2. Kullanıcının adı ve asistan kimliği doğrulandı.\n3. Diyaloğu başlatmaya yönelik açık uçlu yardım sorusu kurgulandı.";
      reply = `Merhaba ${greeting}! Ben **MEBOT** (${model}).\n\nArtık hem **derin düşünme (akıl yürütme)** hem de **akıcı ve mantıklı yanıt verme** yeteneğim devrede! Birlikte bir problem çözebilir, kod yazabilir veya merak ettiğiniz herhangi bir konuyu en ince detayına kadar inceleyebiliriz.\n\nBugün ne üzerinde çalışmak istersiniz?`;
    } else if (p.includes('kod') || p.includes('python') || p.includes('yazılım') || p.includes('algoritma')) {
      thinkingSteps = "1. Yazılım mimarisi ve algoritma verimliliği (Time/Space Complexity) gözetildi.\n2. Temiz kod (Clean Code) standartlarına uygun fonksiyon kurgulandı.\n3. Açıklayıcı notlar ve kullanım örneği eklendi.";
      reply = `${greeting}, talep ettiğiniz yazılım mantığını optimize edilmiş bir örnekle hazırladım:\n\n\`\`\`python
# MEBOT Mantıksal Çözüm Örneği
def akilli_veri_analizi(girdiler):
    \"\"\"
    Girdileri filtreleyip mantıksal sıralama ile sonuç üreten fonksiyon.
    \"\"\"
    if not girdiler:
        return "Veri bulunamadı."
    
    sonuc = [x for x in girdiler if isinstance(x, (int, float))]
    return {
        "islenen_adet": len(sonuc),
        "aritmetik_ortalama": sum(sonuc) / len(sonuc) if sonuc else 0
    }

# Test:
ornek = [10, 20, 30, 40]
print(akilli_veri_analizi(ornek))
\`\`\`\n\nBu kod parçasının amacı gereksiz bellek kullanımını önlemek ve doğrudan amaca yönelik çalışmaktır.`;
    } else if ((p.includes('kutu') || p.includes('kutular')) && (p.includes('meyve') || p.includes('elma') || p.includes('portakal') || p.includes('etiket') || p.includes('karışık') || p.includes('karisik'))) {
      thinkingSteps = "🧠 [Problem Tanımı ve Kısıtlar]:\n• 3 kutu var: Sadece Elma, Sadece Portakal, Karışık.\n• TÜM ETİKETLER YANLIŞTIR.\n• 'Karışık' etiketli kutudan 1 meyve çekildiğinde içi kesinleşir.\n🎯 [Kesin Çözüm]: 'Karışık' etiketli kutudan çekilmeli, çıkan meyveye göre diğer iki kutu eşleştirilmelidir.";
      reply = `Bu klasik mantık bulmacasının tek ve kesin çözümü, üzerinde **"Karışık"** yazan kutudan 1 adet meyve çekmektir.\n\n### 🎯 1. Hangi Kutudan Çekilmeli?\nKesinlikle **"Karışık"** etiketli kutudan 1 meyve çekilmelidir.\n\n**Gerekçesi:**\nSorunun en temel kuralı **"tüm etiketlerin yanlış"** olmasıdır. Bu kurala göre üzerinde "Karışık" yazan kutunun içinde kesinlikle karışık meyve bulunamaz! Dolayısıyla bu kutunun içi ya **tamamen Elma** ya da **tamamen Portakal** olmak zorundadır. Tek bir meyve çektiğinizde kutunun içeriği %100 kesinleşir.\n\n### 🔍 2. Kalan Kutular Nasıl Bulunur?\n- **🍏 Çekilen Meyve ELMA İse:**\n  1. "Karışık" etiketli kutu = **Sadece Elma**dır.\n  2. "Portakal" etiketli kutu kendi etiketi olamayacağından (ve elma zaten bulunduğundan) mecburen **Karışık**tır.\n  3. Geriye kalan "Elma" etiketli kutu kesinlikle **Sadece Portakal**dır.\n\n- **🍊 Çekilen Meyve PORTAKAL İse:**\n  1. "Karışık" etiketli kutu = **Sadece Portakal**dır.\n  2. "Elma" etiketli kutu kendi etiketi olamayacağından mecburen **Karışık**tır.\n  3. Geriye kalan "Portakal" etiketli kutu kesinlikle **Sadece Elma**dır.`;
    } else {
      thinkingSteps = `🧠 [Aşama 1/4 - Problem Tespiti]: "${prompt}" sorusu semantik olarak ayrıştırıldı.\n🔬 [Aşama 2/4 - Kavramsal Çerçeve]: İlgili konunun kök dinamikleri ve temel unsurları belirlendi.\n⚖️ [Aşama 3/4 - Çok Boyutlu İnceleme]: Neden-sonuç bağı ve pratik hayatla olan etkileşimi değerlendirildi.\n🎯 [Aşama 4/4 - Sentez]: Anlaşılır, yapıcı ve zengin bir yanıt kurgulandı.`;
      reply = `**"${prompt}"** konusunu çok boyutlu bir akıl süzgecinden geçirerek inceledim:\n\n### 1. 🔍 Kök Sebep ve Kavramsal Dinamik\nBu sorunun özünde, birbiriyle doğrudan bağlantılı neden-sonuç mekanizmaları yer almaktadır. Yüzeysel sonuçlara takılmak yerine, süreci başlatan temel etkenleri doğru kavramak en sağlıklı değerlendirmeyi sağlar.\n\n### 2. ⚖️ Dikkat Edilmesi Gereken Boyutlar\n- **Doğrudan Etkiler:** Bu durumun kısa vadede ortaya çıkardığı somut sonuçlar ve gereksinimler.\n- **Sistemik Denge:** Uzun vadede sürecin getirdiği sorumluluklar ve dikkat edilmesi gereken dengeler.\n\n### 🎯 3. Stratejik Çıkarım\nBu konuyu günlük hayatınızdaki somut bir senaryoya veya spesifik bir projeye uyarlamak isterseniz, merak ettiğiniz alt detayları iletebilirsiniz; birlikte adım adım derinleşebiliriz!`;
    }

    return {
      thinking: thinkingSteps,
      thinking_time: 1.4,
      reply: reply
    };
  }

  // =========================================================================
  // 7. Markdown ve Kod Blokları
  // =========================================================================
  function formatMarkdown(text) {
    if (!text) return "";
    let html = escapeHTML(text);

    // Tablolar | ... |
    html = html.replace(/((?:\|[^\n]+\|\r?\n)+)/g, (match) => {
      const rows = match.trim().split('\n').map(r => r.trim()).filter(Boolean);
      if (rows.length < 2) return match;
      let tableHtml = '<div style="overflow-x:auto; margin:12px 0;"><table style="width:100%; border-collapse:collapse; font-size:13px; text-align:left; background:rgba(30,41,59,0.5); border-radius:8px; overflow:hidden;">';
      let isHeader = true;
      for (let r = 0; r < rows.length; r++) {
        const row = rows[r];
        if (row.includes('---') || row.includes(':---')) {
          isHeader = false;
          continue;
        }
        const cells = row.split('|').filter((_, idx, arr) => idx > 0 && idx < arr.length - 1).map(c => c.trim());
        tableHtml += '<tr style="border-bottom: 1px solid rgba(255,255,255,0.08);">';
        for (const cell of cells) {
          if (isHeader) {
            tableHtml += `<th style="padding:8px 12px; background:rgba(255,255,255,0.06); color:#93c5fd; font-weight:600;">${cell}</th>`;
          } else {
            tableHtml += `<td style="padding:8px 12px; color:#e2e8f0;">${cell}</td>`;
          }
        }
        tableHtml += '</tr>';
      }
      tableHtml += '</table></div>';
      return tableHtml;
    });

    // Kod blokları ```...```
    html = html.replace(/```([a-zA-Z]*)\n([\s\S]*?)```/g, (match, lang, code) => {
      return `<div class="code-card">
        <div class="code-card-header">
          <span>${lang || 'kod'}</span>
          <button type="button" class="copy-code-btn" onclick="navigator.clipboard.writeText(this.closest('.code-card').querySelector('code').innerText); this.textContent='Kopyalandı!'; setTimeout(()=>this.textContent='Kopyala', 2000);">Kopyala</button>
        </div>
        <pre><code>${code.trim()}</code></pre>
      </div>`;
    });

    // Satır içi kod `...`
    html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

    // Başlıklar ### ...
    html = html.replace(/^### (.*$)/gim, '<h3 style="font-size:15px; font-weight:600; margin:10px 0 6px; color:#93c5fd;">$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2 style="font-size:16px; font-weight:700; margin:12px 0 8px; color:#ffffff;">$1</h2>');

    // Kalın yazı **...**
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // İtalik yazı *...*
    html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');

    // Güvenli Bağlantılar [Başlık](https://...)
    html = html.replace(/\[([^\]]+)\]\((https:\/\/[^\)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" style="color:#60a5fa; text-decoration:underline; font-weight:500;">$1 ↗</a>');

    // Listeler - ...
    html = html.replace(/^\s*-\s+(.*)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');

    // Paragraflar
    const paragraphs = html.split(/\n\n+/);
    return paragraphs.map(p => {
      if (p.startsWith('<div class="code-card">') || p.startsWith('<ul>') || p.startsWith('<h2') || p.startsWith('<h3')) return p;
      return `<p>${p.replace(/\n/g, '<br>')}</p>`;
    }).join('');
  }

  function escapeHTML(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        "'": '&#39;',
        '"': '&quot;'
      }[tag] || tag)
    );
  }

  function attachCodeCopyButtons(container) {
    // Buton dinleyicileri satır içi inline fonksiyonla yönetiliyor
  }

  // =========================================================================
  // 8. Hızlı Öneri ve Derin Soru Hapları (Suggestion Chips)
  // =========================================================================
  const suggestionChips = document.querySelectorAll('.suggestion-chip');
  suggestionChips.forEach(chip => {
    chip.addEventListener('click', (e) => {
      e.preventDefault();
      // KULLANICI KORUMASI: Kullanıcı input kutusuna bir metin yazmışsa, öneri hapı bu metni veya state'i EZEMEZ!
      if (messageInput.value && messageInput.value.trim().length > 0) {
        console.warn("Input kutusunda bekleyen kullanıcı metni korunuyor, öneri butonu metni ezemez.");
        messageInput.focus();
        return;
      }
      const prompt = chip.getAttribute('data-prompt');
      if (prompt) {
        sendMessage(prompt);
      }
    });
  });

  // =========================================================================
  // 9. Ayarlar & Backend Durum Kontrolü & Gemini API Entegrasyonu
  // =========================================================================
  const aiStatusBtn = document.getElementById('aiStatusBtn');
  const aiStatusText = document.getElementById('aiStatusText');
  const aiBadgeDot = document.getElementById('aiBadgeDot');

  async function checkBackendStatus() {
    try {
      const res = await fetch('/api/status', { method: 'GET' });
      if (res.ok) {
        const data = await res.json();
        isBackendOnline = true;
        backendBadge.className = 'status-badge live';
        backendBadge.textContent = 'ONLINE';
        
        const hasKey = Boolean(data.gemini_ready || data.has_api_key || apiKey);
        if (hasKey) {
          backendStatusText.textContent = '✨ Gemini AI Aktif (Google Bulut Zekası)';
          if (aiStatusText) aiStatusText.textContent = '✨ Gemini AI Aktif';
          if (aiBadgeDot) aiBadgeDot.className = 'badge-dot gemini-active';
        } else {
          backendStatusText.textContent = '⚡ Yerleşik Akıl Motoru (Gemini Anahtarı Ekle ↗)';
          if (aiStatusText) aiStatusText.textContent = '⚡ Yerleşik Akıl Motoru';
          if (aiBadgeDot) aiBadgeDot.className = 'badge-dot';
        }
        return;
      }
    } catch (e) {
      console.warn("Backend status kontrol hatası:", e);
    }

    isBackendOnline = false;
    backendBadge.className = 'status-badge offline';
    backendBadge.textContent = 'TARAYICI';
    backendStatusText.textContent = 'Statik Tarayıcı Modu (Yerel Bilişsel Motor)';
    if (aiStatusText) aiStatusText.textContent = 'Yerel Mod';
  }

  if (aiStatusBtn) {
    aiStatusBtn.addEventListener('click', () => {
      apiKeyInput.value = apiKey;
      settingsModal.classList.add('open');
      checkBackendStatus();
    });
  }

  openSettingsBtn.addEventListener('click', () => {
    apiKeyInput.value = apiKey;
    settingsModal.classList.add('open');
    checkBackendStatus();
  });

  closeSettingsBtn.addEventListener('click', () => {
    settingsModal.classList.remove('open');
  });

  saveSettingsBtn.addEventListener('click', async () => {
    const enteredKey = apiKeyInput.value.trim();
    apiKey = enteredKey;
    localStorage.setItem('mebot_api_key', apiKey);

    // Backend'e de kalıcı kaydet
    if (enteredKey) {
      try {
        saveSettingsBtn.textContent = "Kaydediliyor...";
        const saveRes = await fetch('/api/save_key', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ apiKey: enteredKey })
        });
        if (saveRes.ok) {
          console.log("API Anahtarı sunucuya kalıcı kaydedildi.");
        }
      } catch (err) {
        console.warn("Sunucuya anahtar kaydedilirken hata:", err);
      } finally {
        saveSettingsBtn.textContent = "Test Et ve Kaydet";
      }
    }

    await checkBackendStatus();
    settingsModal.classList.remove('open');
    alert(enteredKey ? "✨ Gemini API Anahtarı başarıyla kaydedildi! MEBOT artık Google Gemini bulut zekasıyla çalışıyor." : "Ayarlar güncellendi.");
  });

  newChatBtn.addEventListener('click', () => {
    messagesContainer.innerHTML = '';
    messageHistory = [];
    appContainer.classList.remove('chat-active');
    messageInput.value = '';
    messageInput.focus();
  });

  downloadAppBtn.addEventListener('click', () => {
    alert("MEBOT Web Uygulaması tarayıcınızda canlı olarak çalışıyor! İstediğiniz an masaüstünüzdeki start.bat dosyası ile başlatabilirsiniz.");
  });

  // SOHBETLERDE ARA & YAN MENU
  function renderSidebarChats(chats) {
    const list = document.getElementById('sidebarChatList');
    if (!list) return;
    list.innerHTML = '';
    chats.forEach(chat => {
      const div = document.createElement('div');
      div.className = 'sidebar-chat-item';
      div.style.padding = '10px';
      div.style.marginBottom = '5px';
      div.style.borderRadius = '8px';
      div.style.cursor = 'pointer';
      div.style.background = chat.id === currentChatId ? 'rgba(255,255,255,0.1)' : 'transparent';
      div.style.color = '#fff';
      div.style.fontSize = '13px';
      div.style.whiteSpace = 'nowrap';
      div.style.overflow = 'hidden';
      div.style.textOverflow = 'ellipsis';
      div.textContent = chat.title || 'Yeni Sohbet';
      div.onclick = () => {
         currentChatId = chat.id;
         renderSidebarChats(currentUserChats);
         renderSavedHistory(chat.messages || []);
      };
      list.appendChild(div);
    });
  }

  window.renderSidebarChats = renderSidebarChats;

  const newChatSidebarBtn = document.getElementById('newChatSidebarBtn');
  if (newChatSidebarBtn) {
    newChatSidebarBtn.addEventListener('click', () => {
      currentChatId = '';
      messagesContainer.innerHTML = '';
      appContainer.classList.remove('chat-active');
      renderSidebarChats(currentUserChats);
    });
  }

  // POLİTİKA KABUL
  const acceptPolicyCheck = document.getElementById('acceptPolicyCheck');
  const acceptPolicyBtn = document.getElementById('acceptPolicyBtn');
  const policyModal = document.getElementById('policyModal');

  if (acceptPolicyCheck && acceptPolicyBtn) {
    acceptPolicyCheck.addEventListener('change', () => {
      acceptPolicyBtn.disabled = !acceptPolicyCheck.checked;
    });

    acceptPolicyBtn.addEventListener('click', async () => {
      acceptPolicyBtn.innerText = 'İşleniyor...';
      try {
        const res = await fetch('/api/auth/accept_policy', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({username: userName, pin: userPin})
        });
        if (res.ok) {
           policyModal.style.display = 'none';
           policyAccepted = true;
           renderSidebarChats(currentUserChats);
           if (currentUserChats.length > 0) {
             currentChatId = currentUserChats[0].id;
             renderSavedHistory(currentUserChats[0].messages);
           }
        } else {
           alert("Politika onayı başarısız.");
           acceptPolicyBtn.innerText = 'Onayla ve Hesabı Aç';
        }
      } catch (e) {
         policyModal.style.display = 'none';
         policyAccepted = true;
         renderSidebarChats(currentUserChats);
      }
    });
  }

  // KİŞİSELLEŞTİRME & HAFIZA
  const personalizationBtn = document.getElementById('savePersonalizationBtn') || document.getElementById('saveSettingsBtn');
  if (personalizationBtn) {
    personalizationBtn.addEventListener('click', async () => {
      const pInput = document.getElementById('personalizationInput');
      const mToggle = document.getElementById('memoryToggleBtn');
      if(pInput && mToggle) {
        const personalization = pInput.value;
        const memory_enabled = mToggle.checked;
        
        try {
          await fetch('/api/auth/save_settings', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: userName, pin: userPin, personalization, memory_enabled})
          });
        } catch(e) {}
      }
    });
  }

  const searchChatsInput = document.getElementById('searchChatsInput');
  if (searchChatsInput) {
    searchChatsInput.addEventListener('input', (e) => {
      const term = e.target.value.toLowerCase();
      const filtered = currentUserChats.filter(c => (c.title || '').toLowerCase().includes(term));
      renderSidebarChats(filtered);
    });
  }

  // İlk yüklemede durum ve kimlik kontrolü
  checkBackendStatus();
  checkAuthOnLoad();
});
