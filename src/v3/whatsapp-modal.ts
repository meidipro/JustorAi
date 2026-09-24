import { getActiveMatter, getStoredMatters, saveStoredMatters, syncMatterToCloud, type LegalMatter } from './matter-workspace';

interface WhatsAppMessage {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  time: string;
  isVoice?: boolean;
}

const waSvg = (name: 'phone' | 'code' | 'scale' | 'refresh' | 'mic' | 'target' | 'flask' | 'check' | 'copy' | 'external' | 'folder' | 'briefcase', size = 16): string => {
  const paths: Record<string, string> = {
    phone: '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
    code: '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    scale: '<path d="M12 3v18M7 21h10M4 7h16M6 7 3 13h6L6 7Zm12 0-3 6h6l-3-6Z"/>',
    refresh: '<path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/>',
    mic: '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v3M8 22h8"/>',
    target: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    flask: '<path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><path d="M8.5 2h7M7 16h10"/>',
    check: '<polyline points="20 6 9 17 4 12"/>',
    copy: '<rect width="13" height="13" x="9" y="9" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
    external: '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14 21 3"/>',
    folder: '<path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/>',
    briefcase: '<rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>'
  };
  return `<svg aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; display: inline-block;">${paths[name] || paths.phone}</svg>`;
};

export function openWhatsAppModal(matterContext?: LegalMatter | null): void {
  const existing = document.getElementById('justor-whatsapp-modal');
  if (existing) {
    existing.remove();
  }

  const activeMatter = matterContext || getActiveMatter();
  const matterId = activeMatter?.id || 'JUSTOR-2026-001';
  const matterTitle = activeMatter?.title || 'করিম আহমেদ বনাম রহিম খান ও অন্যান্য';
  const clientName = activeMatter?.clientName || 'করিম আহমেদ';
  const chamberPhone = localStorage.getItem('justor_chamber_phone') || '+8801700000000';

  const defaultMessages: WhatsAppMessage[] = [
    {
      id: 'm1',
      sender: 'bot',
      text: `*আসসালামু আলাইকুম এডভোকেট সাহেব! আমি জাসটর চেম্বার হোয়াটসঅ্যাপ ব্রিজ (Chamber OS Gateway)।*\n\nআপনার চেম্বারের মক্কেলরা তাদের মামলার অবস্থা স্বয়ংক্রিয়ভাবে জানতে পারবে এবং আপনি কোর্ট চত্বর থেকে তাৎক্ষণিক ভয়েস বা টেক্সট নোট পাঠিয়ে ডকেটে ফাইল করতে পারবেন।\n\n- সক্রিয় মোকদ্দমার অবস্থা পরীক্ষা করতে লিখুন: \`STATUS ${matterId}\`\n- পরবর্তী শুনানির তারিখ জানতে: \`HEARING ${matterId}\`\n- প্রয়োজনীয় দলিলের চেকলিস্ট: \`DOCS ${matterId}\`\n- কোর্ট থেকে তাৎক্ষণিক ডিকটেশন: \`#${matterId} আদেশ: আসামি উপস্থিত, জামিন বহাল...\``,
      time: '10:00 AM'
    }
  ];

  const modal = document.createElement('div');
  modal.id = 'justor-whatsapp-modal';
  modal.className = 'justor-modal-overlay active';

  let messages: WhatsAppMessage[] = [...defaultMessages];
  let isSending = false;
  let isRecording = false;
  let recognition: any = null;

  modal.innerHTML = `
    <div class="justor-modal-card whatsapp-modal-card" role="dialog" aria-modal="true">
      <header class="whatsapp-modal-header">
        <div class="whatsapp-modal-title-group">
          <div class="whatsapp-badge-icon">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2z"/>
            </svg>
          </div>
          <div>
            <div style="display: flex; align-items: center; gap: 8px;">
              <h3>Justor Chamber OS · Advocate WhatsApp Live Gateway</h3>
              <span class="lawyer-only-badge" style="background: rgba(37, 211, 102, 0.15); color: #25D366; font-size: 11px; padding: 2px 8px; border-radius: 12px; font-weight: 700; border: 1px solid rgba(37, 211, 102, 0.3);">LAWYERS ONLY</span>
            </div>
            <p>২৪/৭ চেম্বার ক্লায়েন্ট অটো-আপডেট ও আদালত চত্বর থেকে সরাসরি মোবাইল ভয়েস ডিকটেশন ব্রিজ</p>
          </div>
        </div>
        <button type="button" class="justor-modal-close" id="wa-modal-close-btn" aria-label="Close">✕</button>
      </header>

      <div class="whatsapp-matter-context-strip" style="background: rgba(30, 41, 59, 0.85); padding: 8px 24px; border-bottom: 1px solid rgba(255, 255, 255, 0.08); display: flex; justify-content: space-between; align-items: center; font-size: 12.5px; color: #94A3B8;">
        <div style="display: flex; align-items: center; gap: 8px;">
          ${waSvg('briefcase', 14)}
          <span style="color: #E2E8F0; font-weight: 600;">সক্রিয় মোকদ্দমা:</span>
          <span style="color: #60A5FA; background: rgba(96, 165, 250, 0.12); padding: 1px 6px; border-radius: 4px; font-family: monospace;">${escapeHtml(matterId)}</span>
          <span style="color: #CBD5E1;">— ${escapeHtml(matterTitle)} (${escapeHtml(clientName)})</span>
        </div>
        <button type="button" id="wa-file-last-note-btn" class="button button-small" style="background: #1E293B; border: 1px solid rgba(255,255,255,0.15); color: #38BDF8; font-size: 11.5px; padding: 4px 10px; border-radius: 6px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px;">
          ${waSvg('folder', 13)}
          <span>📥 File Last Message to Matter Notes</span>
        </button>
      </div>

      <div class="whatsapp-tabs">
        <button type="button" class="whatsapp-tab active" data-tab="simulator">${waSvg('phone', 14)} <span>Chamber Simulator</span></button>
        <button type="button" class="whatsapp-tab" data-tab="integration">${waSvg('code', 14)} <span>Client Links & Setup</span></button>
      </div>

      <div class="whatsapp-tab-content active" id="wa-content-simulator">
        <div class="whatsapp-simulator-container">
          <!-- Smartphone Outer Frame -->
          <div class="whatsapp-phone-frame">
            <!-- WhatsApp App Bar -->
            <div class="whatsapp-app-bar">
              <div class="whatsapp-contact-info">
                <div class="whatsapp-avatar">
                  <span>${waSvg('scale', 14)}</span>
                  <span class="whatsapp-online-dot"></span>
                </div>
                <div class="whatsapp-contact-text">
                  <div class="whatsapp-name-row">
                    <strong>Justor Chamber Gateway</strong>
                    <span class="whatsapp-verified-badge" title="Verified Lawyer Gateway">✓</span>
                  </div>
                  <small>online • Chamber OS Docket Bot</small>
                </div>
              </div>
              <div class="whatsapp-app-bar-actions">
                <button type="button" class="wa-icon-btn" id="wa-clear-chat-btn" title="Clear Chat">${waSvg('refresh', 13)}</button>
              </div>
            </div>

            <!-- Chat Message Bubble Stream -->
            <div class="whatsapp-chat-stream" id="whatsapp-chat-stream"></div>

            <!-- Typing indicator -->
            <div class="whatsapp-typing-indicator" id="whatsapp-typing" style="display: none;">
              <span>Justor AI is typing...</span>
            </div>

            <!-- Quick Suggestions Row -->
            <div class="whatsapp-quick-chips">
              <button type="button" class="wa-chip" data-query="STATUS ${matterId}">STATUS ${matterId}</button>
              <button type="button" class="wa-chip" data-query="HEARING ${matterId}">শুনানির তারিখ</button>
              <button type="button" class="wa-chip" data-query="DOCS ${matterId}">প্রয়োজনীয় দলিল</button>
              <button type="button" class="wa-chip" data-query="#${matterId} কোর্টে শুনানি সম্পন্ন: আসামি হাজির, জামিন আগামী তারিখ পর্যন্ত বহাল।">কোর্ট ডিকটেশন (#)</button>
              <button type="button" class="wa-chip" data-query="চেক বাউন্স হলে কতদিনের মধ্যে নোটিশ দিতে হয়?">আইনি ধারা</button>
            </div>

            <!-- WhatsApp Message Input Footer -->
            <div class="whatsapp-input-bar">
              <button type="button" class="wa-voice-btn" id="wa-voice-toggle-btn" title="Simulate Voice Message">
                <span id="wa-mic-icon">${waSvg('mic', 16)}</span>
              </button>
              <input type="text" id="whatsapp-message-input" placeholder="Type or dictate a message or case ID..." autocomplete="off" />
              <button type="button" class="wa-send-btn" id="whatsapp-send-btn" aria-label="Send">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Simulator Control Panel & Feature Highlights -->
          <div class="whatsapp-sim-sidebar">
            <div class="whatsapp-sim-card">
              <h4>${waSvg('target', 14)} <span>Lawyer Chamber Benefits</span></h4>
              <p>Justor Chamber OS WhatsApp integration eliminates repetitive client phone calls and streamlines court corridor notes:</p>
              <ul>
                <li><strong>24/7 Client Case Tracker:</strong> Clients send <code>STATUS ${escapeHtml(matterId)}</code> and receive instant verified hearing dates without calling you late at night.</li>
                <li><strong>Court Corridor Dictation:</strong> Send a voice note or text starting with <code>#${escapeHtml(matterId)}</code> from High Court or District Court; it automatically files into your Chamber OS Vault.</li>
                <li><strong>Mandatory Evidence Checklists:</strong> Clients request <code>DOCS ${escapeHtml(matterId)}</code> to know exact originals and photocopies needed for court.</li>
                <li><strong>Meta WhatsApp Cloud API Free Tier:</strong> 1,000 conversations every month free directly through Meta.</li>
              </ul>
            </div>

            <div class="whatsapp-sim-card">
              <h4>${waSvg('flask', 14)} <span>Advocate Quick Actions</span></h4>
              <div class="wa-test-scenarios">
                <button type="button" class="wa-scenario-btn" data-query="STATUS ${matterId}">
                  <strong>1. Test Client Status Lookup</strong>
                  <span>Verify what your client sees for this active docket</span>
                </button>
                <button type="button" class="wa-scenario-btn" data-query="#${matterId} অন্তর্বর্তীকালীন স্থগিতাদেশ ৬ মাসের জন্য মঞ্জুর হয়েছে। মক্কেলকে ২৫% অর্থ জমা দিতে বলা হয়েছে।">
                  <strong>2. Test Mobile Dictation File</strong>
                  <span>Simulate filing court corridor note into matter vault</span>
                </button>
                <button type="button" class="wa-scenario-btn" data-query="DOCS ${matterId}">
                  <strong>3. Test Evidence Checklist</strong>
                  <span>Send client required original documents checklist</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 2: Webhook & Integration Guide -->
      <div class="whatsapp-tab-content" id="wa-content-integration">
        <div class="whatsapp-integration-guide">
          <!-- 1-Click Client Share Section -->
          <div class="wa-guide-section" style="background: rgba(30, 41, 59, 0.6); padding: 18px 20px; border-radius: 12px; border: 1px solid rgba(37, 211, 102, 0.25); margin-bottom: 20px;">
            <h4 style="color: #25D366; display: flex; align-items: center; gap: 8px;">
              ${waSvg('phone', 15)} <span>1. Share Case WhatsApp Link with Client</span>
            </h4>
            <p>Give this link to your client (${escapeHtml(clientName)}). When they tap it, WhatsApp opens with the pre-filled status query:</p>
            
            <div class="wa-code-snippet">
              <label>Client 1-Click WhatsApp Link</label>
              <div class="wa-copy-row">
                <code>https://wa.me/${chamberPhone.replace(/[^0-9]/g, '')}?text=STATUS%20${encodeURIComponent(matterId)}</code>
                <button type="button" class="wa-copy-btn" data-copy="https://wa.me/${chamberPhone.replace(/[^0-9]/g, '')}?text=STATUS%20${encodeURIComponent(matterId)}">Copy Link</button>
              </div>
            </div>

            <div style="display: flex; gap: 10px; margin-top: 12px;">
              <button type="button" class="button button-small" id="wa-open-web-btn" style="background: #25D366; color: #0F172A; font-weight: 700; border: none; border-radius: 6px; padding: 6px 14px; cursor: pointer; display: inline-flex; align-items: center; gap: 6px;">
                ${waSvg('external', 13)} <span>Open in WhatsApp Web</span>
              </button>
              <button type="button" class="button button-small wa-copy-btn" data-copy="সম্মানিত মক্কেল ${escapeHtml(clientName)}, আপনার মোকদ্দমা (${escapeHtml(matterTitle)})-এর পরবর্তী শুনানির তারিখ ও তথ্যের জন্য আমাদের চেম্বার হোয়াটসঅ্যাপে ক্লিক করুন অথবা STATUS ${matterId} লিখে পাঠান: https://wa.me/${chamberPhone.replace(/[^0-9]/g, '')}?text=STATUS%20${encodeURIComponent(matterId)}" style="background: #1E293B; border: 1px solid rgba(255,255,255,0.15); color: #F8FAFC; border-radius: 6px; padding: 6px 14px; cursor: pointer;">
                📋 Copy Bengali SMS for Client
              </button>
            </div>
          </div>

          <div class="wa-guide-section">
            <h4>2. Meta WhatsApp Cloud API (Recommended — 1,000 Free Chats/Mo)</h4>
            <p>Connect your official Chamber WhatsApp Business Number directly with zero middleman fees:</p>
            <div class="wa-code-snippet">
              <label>Callback URL (Webhook)</label>
              <div class="wa-copy-row">
                <code>https://api.justor.ai/api/whatsapp/meta</code>
                <button type="button" class="wa-copy-btn" data-copy="https://api.justor.ai/api/whatsapp/meta">Copy</button>
              </div>
            </div>
            <div class="wa-code-snippet">
              <label>Verify Token</label>
              <div class="wa-copy-row">
                <code>justor_wa_verify_2026</code>
                <button type="button" class="wa-copy-btn" data-copy="justor_wa_verify_2026">Copy</button>
              </div>
            </div>
            <p class="wa-tip">In Meta App Dashboard > WhatsApp > Configuration > Webhook, subscribe to <code>messages</code>.</p>
          </div>

          <div class="wa-guide-section">
            <h4>3. Twilio WhatsApp Sandbox / Production</h4>
            <p>For quick testing using Twilio's Developer Sandbox ($15.00 free credit):</p>
            <div class="wa-code-snippet">
              <label>Twilio Webhook URL (WHEN A MESSAGE COMES IN)</label>
              <div class="wa-copy-row">
                <code>https://api.justor.ai/api/whatsapp/twilio</code>
                <button type="button" class="wa-copy-btn" data-copy="https://api.justor.ai/api/whatsapp/twilio">Copy</button>
              </div>
            </div>
            <p class="wa-tip">Set HTTP POST on your Twilio Console WhatsApp Sandbox Settings.</p>
          </div>
        </div>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Bind close handlers
  const closeBtn = modal.querySelector('#wa-modal-close-btn');
  closeBtn?.addEventListener('click', () => modal.remove());
  modal.addEventListener('click', (e) => {
    if (e.target === modal) modal.remove();
  });

  // Open WhatsApp Web button
  modal.querySelector('#wa-open-web-btn')?.addEventListener('click', () => {
    const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(`STATUS ${matterId}`)}`;
    window.open(waUrl, '_blank');
  });

  // File Last Note to Chamber OS
  modal.querySelector('#wa-file-last-note-btn')?.addEventListener('click', () => {
    const lastUserMsg = [...messages].reverse().find(m => m.sender === 'user');
    const noteText = lastUserMsg ? lastUserMsg.text : messages[messages.length - 1]?.text;
    if (!noteText) {
      alert('ফাইল করার জন্য কোনো মেসেজ পাওয়া যায়নি। চ্যাটে মেসেজ বা ডিকটেশন পাঠান।');
      return;
    }

    const matters = getStoredMatters();
    const targetMatter = matters.find(m => m.id === matterId) || matters[0];
    if (targetMatter) {
      if (!targetMatter.notes) targetMatter.notes = [];
      targetMatter.notes.unshift({
        id: 'note_' + Date.now(),
        rawText: `[WhatsApp Chamber Dictation]\n${noteText}`,
        data: {
          matter_type: targetMatter.matterType,
          dispute_summary: noteText.slice(0, 150),
          next_actions: ['Review WhatsApp dictation in Chamber Vault']
        },
        createdAt: new Date().toISOString()
      });
      saveStoredMatters(matters);
      void syncMatterToCloud(targetMatter);
      alert(`নোটটি সফলভাবে "${targetMatter.title}" মোকদ্দমা ফাইলে সংরক্ষিত হয়েছে!`);
    } else {
      alert('সক্রিয় মোকদ্দমা খুঁজে পাওয়া যায়নি।');
    }
  });

  // Tab switching
  const tabs = modal.querySelectorAll('.whatsapp-tab');
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const tabTarget = tab.getAttribute('data-tab');
      modal.querySelectorAll('.whatsapp-tab-content').forEach(c => c.classList.remove('active'));
      const targetContent = modal.querySelector(`#wa-content-${tabTarget}`);
      if (targetContent) targetContent.classList.add('active');
    });
  });

  // Copy button handlers
  modal.querySelectorAll('.wa-copy-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const textToCopy = btn.getAttribute('data-copy') || '';
      navigator.clipboard.writeText(textToCopy).then(() => {
        const orig = btn.textContent;
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = orig; }, 1500);
      });
    });
  });

  // Render chat stream
  const chatStream = modal.querySelector('#whatsapp-chat-stream') as HTMLElement;
  const inputEl = modal.querySelector('#whatsapp-message-input') as HTMLInputElement;
  const sendBtn = modal.querySelector('#whatsapp-send-btn') as HTMLButtonElement;
  const typingIndicator = modal.querySelector('#whatsapp-typing') as HTMLElement;
  const voiceToggleBtn = modal.querySelector('#wa-voice-toggle-btn') as HTMLButtonElement;
  const micIcon = modal.querySelector('#wa-mic-icon') as HTMLElement;

  function renderMessages() {
    if (!chatStream) return;
    chatStream.innerHTML = messages.map(m => {
      const isUser = m.sender === 'user';
      const formattedBody = escapeHtml(m.text)
        .replace(/\*(.*?)\*/g, '<strong>$1</strong>')
        .replace(/_(.*?)_/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br/>');

      return `
        <div class="whatsapp-bubble-row ${isUser ? 'user-row' : 'bot-row'}">
          <div class="whatsapp-bubble ${isUser ? 'user-bubble' : 'bot-bubble'}">
            ${m.isVoice ? `<div class="wa-voice-tag">${waSvg('mic', 12)} <em>Spoken Voice Query</em></div>` : ''}
            <div class="wa-bubble-content">${formattedBody}</div>
            <div class="wa-bubble-meta">
              <span class="wa-bubble-time">${m.time}</span>
              ${isUser ? '<span class="wa-double-check">✓✓</span>' : ''}
            </div>
          </div>
        </div>
      `;
    }).join('');

    chatStream.scrollTop = chatStream.scrollHeight;
  }

  async function sendMessage(text: string, isVoice: boolean = false) {
    if (!text.trim() || isSending) return;
    isSending = true;

    const userMsg: WhatsAppMessage = {
      id: `u-${Date.now()}`,
      sender: 'user',
      text: text.trim(),
      time: getCurrentTime(),
      isVoice
    };
    messages.push(userMsg);
    renderMessages();
    inputEl.value = '';

    if (typingIndicator) typingIndicator.style.display = 'block';

    try {
      const resp = await fetch('/api/whatsapp/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text.trim(),
          sender: chamberPhone,
          matter_id: matterId
        })
      });

      if (!resp.ok) {
        throw new Error(`Server returned status ${resp.status}`);
      }

      const data = await resp.json();
      const botReply = data.reply || 'দুঃখিত, কোনো উত্তর তৈরি করা যায়নি।';

      messages.push({
        id: `b-${Date.now()}`,
        sender: 'bot',
        text: botReply,
        time: getCurrentTime()
      });
    } catch (err: any) {
      messages.push({
        id: `err-${Date.now()}`,
        sender: 'bot',
        text: `দুঃখিত, সংযোগে ত্রুটি দেখা দিয়েছে (${err.message || 'Error'})। অনুগ্রহ করে আবার চেষ্টা করুন।`,
        time: getCurrentTime()
      });
    } finally {
      isSending = false;
      if (typingIndicator) typingIndicator.style.display = 'none';
      renderMessages();
    }
  }

  // Bind input and send button
  sendBtn?.addEventListener('click', () => {
    sendMessage(inputEl.value);
  });

  inputEl?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(inputEl.value);
    }
  });

  // Clear chat
  modal.querySelector('#wa-clear-chat-btn')?.addEventListener('click', () => {
    messages = [...defaultMessages];
    renderMessages();
  });

  // Quick chips
  modal.querySelectorAll('.wa-chip, .wa-scenario-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const q = btn.getAttribute('data-query');
      if (q) sendMessage(q);
    });
  });

  // Web Speech Voice Simulation
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'bn-BD';

    recognition.onstart = () => {
      isRecording = true;
      voiceToggleBtn.classList.add('recording');
      micIcon.textContent = '⏹️';
      inputEl.placeholder = 'Listening in Bengali / English... Speak now';
    };

    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      if (transcript) {
        sendMessage(transcript, true);
      }
    };

    recognition.onerror = () => {
      stopRecording();
    };

    recognition.onend = () => {
      stopRecording();
    };
  }

  function stopRecording() {
    isRecording = false;
    voiceToggleBtn?.classList.remove('recording');
    if (micIcon) micIcon.textContent = '🎙️';
    if (inputEl) inputEl.placeholder = 'Type a message or case ID...';
  }

  voiceToggleBtn?.addEventListener('click', () => {
    if (!SpeechRecognition) {
      alert('Speech Recognition is not supported in this browser. Please type your message.');
      return;
    }
    if (isRecording) {
      recognition.stop();
    } else {
      recognition.start();
    }
  });

  // Initial render
  renderMessages();
}

function getCurrentTime(): string {
  const now = new Date();
  let hours = now.getHours();
  const minutes = now.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  hours = hours % 12;
  hours = hours ? hours : 12;
  const minStr = minutes < 10 ? '0' + minutes : minutes;
  return `${hours}:${minStr} ${ampm}`;
}

function escapeHtml(str: string): string {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}
