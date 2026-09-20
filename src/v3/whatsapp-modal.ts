/**
 * Justor WhatsApp Legal Helpline & Client Case Status Simulator
 * Interactive mobile preview and production webhook deployment guide.
 */

interface WhatsAppMessage {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  time: string;
  isVoice?: boolean;
}

const DEFAULT_MESSAGES: WhatsAppMessage[] = [
  {
    id: 'm1',
    sender: 'bot',
    text: '*আসসালামু আলাইকুম! আমি জাসটর এআই (Justor AI) — ২৪/৭ স্মার্ট আইনি হেল্পলাইন।*\n\nআমি আপনাকে বাংলাদেশ আইনের ভিত্তিতে তথ্য, পরামর্শ ও মামলার বর্তমান অবস্থা জানাতে প্রস্তুত।\n\n- যে কোনো আইনি প্রশ্ন লিখে বা ভয়েস মেসেজ পাঠিয়ে দিন।\n- মামলার অবস্থা জানতে: `STATUS <রেফারেন্স>`\n- আইনজীবীর চেম্বার পরামর্শের জন্য লিখুন: `ADVOCATE`',
    time: '10:00 AM'
  }
];

const waSvg = (name: 'phone' | 'code' | 'scale' | 'refresh' | 'mic' | 'target' | 'flask' | 'check', size = 16): string => {
  const paths: Record<string, string> = {
    phone: '<rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><line x1="12" y1="18" x2="12.01" y2="18"/>',
    code: '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    scale: '<path d="M12 3v18M7 21h10M4 7h16M6 7 3 13h6L6 7Zm12 0-3 6h6l-3-6Z"/>',
    refresh: '<path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 21h5v-5"/>',
    mic: '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v3M8 22h8"/>',
    target: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    flask: '<path d="M10 2v7.527a2 2 0 0 1-.211.896L4.72 20.55a1 1 0 0 0 .9 1.45h12.76a1 1 0 0 0 .9-1.45l-5.069-10.127A2 2 0 0 1 14 9.527V2"/><path d="M8.5 2h7M7 16h10"/>',
    check: '<polyline points="20 6 9 17 4 12"/>',
  };
  return `<svg aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; display: inline-block;">${paths[name] || paths.phone}</svg>`;
};

export function openWhatsAppModal(): void {
  const existing = document.getElementById('justor-whatsapp-modal');
  if (existing) {
    existing.remove();
  }

  const modal = document.createElement('div');
  modal.id = 'justor-whatsapp-modal';
  modal.className = 'justor-modal-overlay active';

  let messages: WhatsAppMessage[] = [...DEFAULT_MESSAGES];
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
            <h3>Justor WhatsApp Helpline & Status Bot</h3>
            <p>24/7 Conversational Bangladesh Legal Guidance & Client Case Tracking</p>
          </div>
        </div>
        <button type="button" class="justor-modal-close" id="wa-modal-close-btn" aria-label="Close">✕</button>
      </header>

      <div class="whatsapp-tabs">
        <button type="button" class="whatsapp-tab active" data-tab="simulator">${waSvg('phone', 14)} <span>Interactive Simulator</span></button>
        <button type="button" class="whatsapp-tab" data-tab="integration">${waSvg('code', 14)} <span>Webhook & Deployment Guide</span></button>
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
                    <strong>Justor AI Legal Helpline</strong>
                    <span class="whatsapp-verified-badge" title="Verified Legal Assistant">✓</span>
                  </div>
                  <small>online • 24/7 Bangladesh Law Bot</small>
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
              <button type="button" class="wa-chip" data-query="চেক বাউন্স হলে কতদিনের মধ্যে নোটিশ দিতে হয়?">চেক বাউন্স নোটিশ</button>
              <button type="button" class="wa-chip" data-query="STATUS JUSTOR-2026-001">মামলার অবস্থা</button>
              <button type="button" class="wa-chip" data-query="জমি খারিজ বাতিলের উপায় কি?">জমি খারিজ বাতিল</button>
              <button type="button" class="wa-chip" data-query="ADVOCATE">আইনজীবীর পরামর্শ</button>
              <button type="button" class="wa-chip" data-query="HELP">HELP / মেনু</button>
            </div>

            <!-- WhatsApp Message Input Footer -->
            <div class="whatsapp-input-bar">
              <button type="button" class="wa-voice-btn" id="wa-voice-toggle-btn" title="Simulate Voice Message">
                <span id="wa-mic-icon">${waSvg('mic', 16)}</span>
              </button>
              <input type="text" id="whatsapp-message-input" placeholder="Type a message or case ID..." autocomplete="off" />
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
              <h4>${waSvg('target', 14)} <span>Chamber Helpline Standard</span></h4>
              <p>Justor delivers 24/7 client conversational experience to ordinary citizens and litigants with zero delay.</p>
              <ul>
                <li><strong>Statutory RAG:</strong> Grounded in 46,000+ provisions of Bangladesh Code (NI Act, Penal Code, CPC, CrPC).</li>
                <li><strong>Voice Reasoning:</strong> Accepts spoken voice notes in Bengali/English and answers with practical legal steps.</li>
                <li><strong>Case Status Tracker:</strong> Litigants check their next court date instantly without calling their advocate at night.</li>
                <li><strong>1,000 Free Chats / Mo:</strong> Powered directly via Meta WhatsApp Cloud API free tier.</li>
              </ul>
            </div>

            <div class="whatsapp-sim-card">
              <h4>${waSvg('flask', 14)} <span>Quick Test Scenarios</span></h4>
              <div class="wa-test-scenarios">
                <button type="button" class="wa-scenario-btn" data-query="বাদী হিসেবে চেক ডিজঅনারের মামলা করতে আমার কি কি কাগজপত্র লাগবে?">
                  <strong>1. Evidence Checklist</strong>
                  <span>Ask what documents are needed for NI Act 138</span>
                </button>
                <button type="button" class="wa-scenario-btn" data-query="STATUS JUSTOR-2026-001">
                  <strong>2. Live Matter Lookup</strong>
                  <span>Query case hearing dates & advocate details</span>
                </button>
                <button type="button" class="wa-scenario-btn" data-query="What is the limitation period for filing a suit for specific performance of contract in Bangladesh?">
                  <strong>3. English Legal Query</strong>
                  <span>Verify Limitation Act schedule rules</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 2: Webhook & Integration Guide -->
      <div class="whatsapp-tab-content" id="wa-content-integration">
        <div class="whatsapp-integration-guide">
          <div class="wa-guide-section">
            <h4>1. Meta WhatsApp Cloud API (Recommended — 1,000 Free Chats/Mo)</h4>
            <p>Connect your official Facebook Business & WhatsApp Business Account directly with zero middleman fees:</p>
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
            <h4>2. Twilio WhatsApp Sandbox / Production</h4>
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

          <div class="wa-guide-section">
            <h4>3. Environment Variables</h4>
            <p>Set these in Render or your production <code>.env</code> file:</p>
            <pre class="wa-env-block"><code>META_WA_PHONE_NUMBER_ID=your_phone_id
META_WA_ACCESS_TOKEN=your_meta_system_user_token
META_WA_VERIFY_TOKEN=justor_wa_verify_2026
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token</code></pre>
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
          sender: '+8801700000000'
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
    messages = [...DEFAULT_MESSAGES];
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
