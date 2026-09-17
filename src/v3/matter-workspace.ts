/**
 * Justor AI — Matter Intelligence Workspace (Lawyer Chambers OS)
 * Empowers advocates with:
 * 1. Lawyer Dictaphone: Quick voice notes -> Structured matter notes
 * 2. Consultation Audio: Ingest audio -> Transcript + Summary + Red Flags
 * 3. Case in 60 Seconds: Judgment summarizer & Ratio Decidendi
 * 4. Matter Chronology: Interactive timeline with statutory limitation alerts
 * 5. Integrated Matter Vault & Justor RAG Bridge
 */

export interface MatterNote {
  id: string;
  rawText: string;
  data: {
    client_name?: string;
    opponent_name?: string;
    matter_type?: string;
    dispute_summary?: string;
    claim_amount?: string;
    property_details?: string;
    key_dates?: Array<{ date?: string; event?: string; note?: string }>;
    statutory_provisions?: string[];
    missing_questions?: string[];
    next_actions?: string[];
  };
  createdAt: string;
}

export interface MatterConsultation {
  id: string;
  filename: string;
  data: {
    matter_title?: string;
    transcript?: string;
    consultation_summary?: string;
    client_facts?: string[];
    documents_mentioned?: string[];
    crucial_dates?: Array<{ date?: string; event?: string }>;
    statutory_provisions?: string[];
    red_flags_and_risks?: string[];
    questions_to_ask_client?: string[];
  };
  createdAt: string;
}

export interface MatterDocumentSummary {
  id: string;
  filename: string;
  data: {
    case_title?: string;
    court?: string;
    bench?: string;
    case_number?: string;
    decision_date?: string;
    facts_brief?: string;
    legal_issues?: string[];
    petitioner_arguments?: string[];
    respondent_arguments?: string[];
    statutes_cited?: string[];
    precedents_cited?: string[];
    ratio_decidendi?: string;
    operative_order?: string;
    study_mode_firac?: {
      facts?: string;
      issue?: string;
      rule?: string;
      analysis?: string;
      conclusion?: string;
    };
  };
  createdAt: string;
}

export interface MatterChronology {
  timeline: Array<{
    date_str: string;
    standard_date?: string;
    title: string;
    description: string;
    importance: 'critical' | 'standard';
    source_reference?: string;
  }>;
  limitation_alerts: Array<{
    provision: string;
    rule: string;
    status: 'expired' | 'urgent' | 'active' | 'compliant';
    warning: string;
  }>;
  summary: string;
}

export interface LegalMatter {
  id: string;
  title: string;
  clientName: string;
  matterType: string;
  createdAt: string;
  updatedAt: string;
  notes: MatterNote[];
  consultations: MatterConsultation[];
  summaries: MatterDocumentSummary[];
  chronology?: MatterChronology;
}

const STORAGE_KEY = 'justor_matters_v1';
const ACTIVE_MATTER_KEY = 'justor_active_matter_id';

export function getStoredMatters(): LegalMatter[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

export function saveStoredMatters(matters: LegalMatter[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(matters));
  } catch (e) {
    console.warn('Failed to save matters to storage:', e);
  }
}

export function getActiveMatter(): LegalMatter | null {
  const matters = getStoredMatters();
  const activeId = localStorage.getItem(ACTIVE_MATTER_KEY);
  return matters.find((m) => m.id === activeId) || matters[0] || null;
}

export function setActiveMatterId(id: string): void {
  localStorage.setItem(ACTIVE_MATTER_KEY, id);
}

function escapeHtml(str: string): string {
  return (str || '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function openMatterWorkspaceModal(
  language: 'en' | 'bn' = 'en',
  onSendToChat?: (prompt: string) => void
): void {
  // Remove existing modal if any
  const existing = document.querySelector('.matter-modal-backdrop');
  if (existing) existing.remove();

  const isBn = language === 'bn';
  let matters = getStoredMatters();

  // Create default sample matter if empty
  if (matters.length === 0) {
    const defaultMatter: LegalMatter = {
      id: 'matter_' + Date.now(),
      title: isBn ? 'রহিম বনাম করিম — চেক ডিজঅনার ও ক্ষতিপূরণ' : 'Rahim v. Karim — NI Act Cheque Dishonour',
      clientName: isBn ? 'মো: রহিম উদ্দিন' : 'Md. Rahim Uddin',
      matterType: isBn ? 'চেক ডিজঅনার (NI Act s.138)' : 'Cheque Dishonour (NI Act s.138)',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      notes: [],
      consultations: [],
      summaries: [],
    };
    matters = [defaultMatter];
    saveStoredMatters(matters);
    setActiveMatterId(defaultMatter.id);
  }

  let currentMatter = getActiveMatter() || matters[0];
  let currentTab: 'dictaphone' | 'consultation' | 'summarizer' | 'chronology' | 'overview' = 'dictaphone';

  const backendUrl = (import.meta.env.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com').replace(/\/$/, '');

  const backdrop = document.createElement('div');
  backdrop.className = 'matter-modal-backdrop';

  const renderModalContent = () => {
    matters = getStoredMatters();
    currentMatter = getActiveMatter() || matters[0];

    backdrop.innerHTML = `
      <div class="matter-modal-drawer" role="dialog" aria-modal="true">
        <!-- Header -->
        <div class="matter-modal-header">
          <div class="matter-header-left">
            <span class="matter-badge-kicker">
              🧠 Justor Matter Intelligence · Lawyer Chambers OS
            </span>
            <div class="matter-selector-row">
              <select id="matter-select" class="matter-select">
                ${matters.map((m) => `
                  <option value="${m.id}" ${m.id === currentMatter.id ? 'selected' : ''}>
                    📁 ${escapeHtml(m.title)} (${escapeHtml(m.clientName || 'General')})
                  </option>
                `).join('')}
              </select>
              <button type="button" class="button button-small button-outline" id="new-matter-btn">
                ➕ ${isBn ? 'নতুন মোকদ্দমা' : 'New Matter'}
              </button>
            </div>
          </div>
          <button class="modal-close-btn" type="button" data-action="close-matter-modal" aria-label="Close">✕</button>
        </div>

        <!-- Navigation Tabs -->
        <div class="matter-tabs-bar">
          <button type="button" class="matter-tab-btn ${currentTab === 'dictaphone' ? 'active' : ''}" data-tab="dictaphone">
            🎙️ ${isBn ? 'ডিকটাফোন / ভয়েস নোট' : 'Lawyer Dictaphone'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'consultation' ? 'active' : ''}" data-tab="consultation">
            🎧 ${isBn ? 'পরামর্শ অডিও বিশ্লেষণ' : 'Consultation Audio'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'summarizer' ? 'active' : ''}" data-tab="summarizer">
            📄 ${isBn ? 'রায় ও নথি সংক্ষেপ (৬০ সে.)' : 'Case in 60s'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'chronology' ? 'active' : ''}" data-tab="chronology">
            ⏳ ${isBn ? 'কালপঞ্জি ও তামাদি' : 'Matter Chronology'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'overview' ? 'active' : ''}" data-tab="overview">
            ⚖️ ${isBn ? 'মোকদ্দমা ফাইল ভল্ট' : 'Matter Vault'}
          </button>
        </div>

        <!-- Tab Body -->
        <div class="matter-modal-body">
          ${renderTabBody()}
        </div>
      </div>
    `;

    attachEventListeners();
  };

  const renderTabBody = (): string => {
    if (currentTab === 'dictaphone') {
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>🎙️ ${isBn ? 'আইনজীবীর ভয়েস ডিকটাফোন' : 'Lawyer Chambers Dictaphone'}</strong>
            <p>${isBn 
              ? 'ক্লায়েন্টের সাথে বৈঠকের পর বা আদালত থেকে বের হয়ে দ্রুত মুখে বলুন। Justor AI স্বয়ংক্রিয়ভাবে পক্ষগণের নাম, টাকার অংক, তারিখ, এনআই অ্যাক্ট বা প্যানেল কোডের প্রাসঙ্গিক ধারা এবং করণীয় পদক্ষেপ বের করে দেবে।'
              : 'Dictate or speak quick notes after a client conference or court hearing. Justor AI automatically structures parties, claim amounts, limitation dates, relevant BD statutes, and next actions.'}
            </p>
          </div>

          <div class="dictaphone-composer-card">
            <div class="dictaphone-input-header">
              <span class="composer-label">📝 ${isBn ? 'আপনার মুখে বলা বিবরণ বা নোট:' : 'Dictated or Typed Facts:'}</span>
              <button type="button" class="dictate-mic-btn" id="dictate-mic-toggle">
                🎤 <span>${isBn ? 'ভয়েস টাইপিং' : 'Start Speaking'}</span>
              </button>
            </div>
            <textarea id="dictate-text" class="dictate-textarea" rows="4" placeholder="${isBn ? 'উদাহরণ: মক্কেল রহিম উদ্দিন আজ এসেছিলেন। পূবালী ব্যাংকের ৫ লাখ টাকার চেক বাউন্স করেছে। গত ১২ আগস্ট লিগ্যাল নোটিশ পাঠিয়েছিলেন...' : 'Example: Client Rahim came today regarding a cheque dishonour matter. Cheque amount 5 lakh taka, Pubali bank, notice served on 12 August...'}"></textarea>
            <div class="dictate-actions">
              <button type="button" class="button button-primary" id="dictate-submit-btn">
                ⚡ ${isBn ? 'স্ট্রাকচার্ড নোট তৈরি করুন' : 'Structure into Matter Note'}
              </button>
            </div>
          </div>

          <div id="dictate-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'আইনি তথ্য, পক্ষগণ ও প্রযোজ্য ধারা বিশ্লেষণ করা হচ্ছে...' : 'Analyzing facts, parties, and applicable Bangladesh statutes...'}</span>
          </div>

          <!-- Existing Notes List -->
          <div class="matter-notes-list">
            <h4>📋 ${isBn ? 'সংরক্ষিত ডিকটেশন ও নোটসমূহ' : 'Saved Dictation Notes'} (${currentMatter.notes.length})</h4>
            ${currentMatter.notes.length === 0 ? `<p class="empty-hint">${isBn ? 'এখনো কোনো নোট সংরক্ষণ করা হয়নি।' : 'No dictation notes saved yet.'}</p>` : ''}
            ${currentMatter.notes.map((n, idx) => `
              <div class="matter-note-card">
                <div class="note-card-header">
                  <strong>#${idx + 1} · ${escapeHtml(n.data.client_name || currentMatter.clientName || 'Note')} — ${escapeHtml(n.data.matter_type || 'General')}</strong>
                  <span class="note-date">${new Date(n.createdAt).toLocaleDateString()}</span>
                </div>
                <p class="note-summary"><strong>${isBn ? 'সারসংক্ষেপ:' : 'Dispute Summary:'}</strong> ${escapeHtml(n.data.dispute_summary || n.rawText)}</p>
                ${n.data.claim_amount ? `<p class="note-pill">💰 ${isBn ? 'দাবীকৃত অংক:' : 'Claim Amount:'} <strong>${escapeHtml(n.data.claim_amount)}</strong></p>` : ''}
                ${n.data.statutory_provisions?.length ? `
                  <div class="note-sections">
                    <span>⚖️ ${isBn ? 'প্রাসঙ্গিক আইন:' : 'Relevant Laws:'}</span>
                    ${n.data.statutory_provisions.map((s) => `<span class="statute-badge">${escapeHtml(s)}</span>`).join('')}
                  </div>
                ` : ''}
                ${n.data.missing_questions?.length ? `
                  <div class="note-red-flags">
                    <strong>❓ ${isBn ? 'ক্লায়েন্টকে যে প্রশ্নগুলো করতে হবে:' : 'Questions Still to Ask Client:'}</strong>
                    <ul>${n.data.missing_questions.map((q) => `<li>${escapeHtml(q)}</li>`).join('')}</ul>
                  </div>
                ` : ''}
                <div class="note-actions">
                  <button type="button" class="button button-small button-outline send-to-chat-btn" data-text="${escapeHtml(n.data.dispute_summary || n.rawText)}">
                    ⚖️ ${isBn ? 'Justor AI-তে গবেষণা করুন' : 'Research Grounds in Justor AI'}
                  </button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    if (currentTab === 'consultation') {
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>🎧 ${isBn ? 'পরামর্শ অডিও রূপান্তর ও বিশ্লেষণ' : 'Client Consultation Audio Intelligence'}</strong>
            <p>${isBn 
              ? 'মক্কেলের সাথে ২০-৩০ মিনিটের আইনি পরামর্শ বা সাক্ষীর জবানবন্দির অডিও (MP3/M4A/WAV) আপলোড করুন। সম্পূর্ণ বাংলা-ইংরেজি ট্রান্সক্রিপ্ট, উল্লেখিত দলিলসমূহ এবং আইনের ফাঁকফোকর স্বয়ংক্রিয়ভাবে চিহ্নিত হবে।'
              : 'Upload a 15-30 min audio recording of your client interview or witness conference. Justor AI extracts verbatim transcript, mentioned documents, timeline, and missing evidentiary questions.'}
            </p>
          </div>

          <div class="audio-upload-zone" id="audio-dropzone">
            <input type="file" id="consultation-audio-file" accept=".mp3,.m4a,.wav,.webm,.ogg" style="display:none;" />
            <div class="audio-drop-icon">🎧</div>
            <strong>${isBn ? 'পরামর্শের অডিও ফাইল আপলোড করুন (MP3, M4A, WAV, WEBM)' : 'Drop Consultation Audio File (MP3, M4A, WAV, WEBM)'}</strong>
            <small>${isBn ? 'সর্বোচ্চ আকার: ২৫ মেগাবাইট' : 'Maximum file size: 25MB'}</small>
            <button type="button" class="button button-outline" id="browse-audio-btn">
              ${isBn ? 'ফাইল নির্বাচন করুন' : 'Select Audio File'}
            </button>
          </div>

          <div id="audio-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'অডিও ট্রান্সক্রিপশন ও আইনি বিশ্লেষণ চলছে (১-২ মিনিট সময় লাগতে পারে)...' : 'Transcribing audio & synthesizing legal consultation intelligence...'}</span>
          </div>

          <div class="matter-notes-list">
            <h4>🎧 ${isBn ? 'বিশ্লেষিত পরামর্শসমূহ' : 'Processed Consultations'} (${currentMatter.consultations.length})</h4>
            ${currentMatter.consultations.length === 0 ? `<p class="empty-hint">${isBn ? 'এখনো কোনো পরামর্শ অডিও বিশ্লেষণ করা হয়নি।' : 'No consultations processed yet.'}</p>` : ''}
            ${currentMatter.consultations.map((c) => `
              <div class="matter-note-card consultation-card">
                <div class="note-card-header">
                  <strong>🎙️ ${escapeHtml(c.data.matter_title || c.filename)}</strong>
                  <span class="note-date">${new Date(c.createdAt).toLocaleDateString()}</span>
                </div>
                <p><strong>${isBn ? 'সারসংক্ষেপ:' : 'Summary:'}</strong> ${escapeHtml(c.data.consultation_summary || '')}</p>
                ${c.data.documents_mentioned?.length ? `
                  <div class="note-sections">
                    <span>📑 ${isBn ? 'উল্লেখিত নথিপত্র:' : 'Documents Mentioned:'}</span>
                    ${c.data.documents_mentioned.map((d) => `<span class="statute-badge">${escapeHtml(d)}</span>`).join('')}
                  </div>
                ` : ''}
                ${c.data.red_flags_and_risks?.length ? `
                  <div class="note-red-flags" style="margin-top: 10px;">
                    <strong>⚠️ ${isBn ? 'আইনি ঝুঁকি ও অসংগতি:' : 'Red Flags & Inconsistencies:'}</strong>
                    <ul>${c.data.red_flags_and_risks.map((r) => `<li>${escapeHtml(r)}</li>`).join('')}</ul>
                  </div>
                ` : ''}
                ${c.data.transcript ? `
                  <details class="transcript-details" style="margin-top: 12px;">
                    <summary style="cursor: pointer; color: #1E38C8; font-weight: 600;">📜 ${isBn ? 'সম্পূর্ণ ট্রান্সক্রিপ্ট দেখুন' : 'View Full Transcript'}</summary>
                    <pre class="transcript-box">${escapeHtml(c.data.transcript)}</pre>
                  </details>
                ` : ''}
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    if (currentTab === 'summarizer') {
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>📄 ${isBn ? 'রায় ও নথি সংক্ষেপ (৬০ সেকেন্ডে কেস)' : 'Legal Document & Judgment 60-Second Summarizer'}</strong>
            <p>${isBn 
              ? '৪০-৫০ পৃষ্ঠার উচ্চ আদালতের রায় বা আদেশনামা আপলোড করুন। Justor AI স্বয়ংক্রিয়ভাবে বেঞ্চ, মূল আইনি প্রশ্ন, উভয় পক্ষের যুক্তি, Ratio Decidendi (আইনি নীতি) এবং চূড়ান্ত রায় সংক্ষেপ করে দেবে।'
              : 'Upload lengthy High Court or trial court judgments. Justor AI extracts Bench, Legal Issues, Ratio Decidendi, and Operative Orders in 60 seconds.'}
            </p>
          </div>

          <div class="summarizer-input-box">
            <div class="summarizer-drop-row">
              <input type="file" id="judgment-file-input" accept=".pdf,.txt" style="display:none;" />
              <button type="button" class="button button-outline" id="upload-judgment-btn">
                📎 ${isBn ? 'রায়ের পিডিএফ ফাইল আপলোড করুন' : 'Upload Judgment PDF'}
              </button>
              <span>${isBn ? 'অথবা নিচে রায়ের বয়ান পেস্ট করুন:' : 'or paste judgment text below:'}</span>
            </div>
            <textarea id="judgment-text-input" class="dictate-textarea" rows="4" placeholder="${isBn ? 'রায়ের মূল অংশ বা প্যারাগ্রাফ এখানে পেস্ট করুন...' : 'Paste judgment text or paragraphs here...'}"></textarea>
            <div class="dictate-actions">
              <button type="button" class="button button-primary" id="summarize-btn">
                ⚡ ${isBn ? '৬০ সেকেন্ডে বিশ্লেষণ করুন' : 'Summarize Case in 60s'}
              </button>
            </div>
          </div>

          <div id="summarize-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'রায় বিশ্লেষণ ও Ratio Decidendi নিষ্কাশন করা হচ্ছে...' : 'Analyzing judicial holding & Ratio Decidendi...'}</span>
          </div>

          <div class="matter-notes-list">
            <h4>📄 ${isBn ? 'সংরক্ষিত রায়ের সারসংক্ষেপ' : 'Saved Judgment Briefs'} (${currentMatter.summaries.length})</h4>
            ${currentMatter.summaries.length === 0 ? `<p class="empty-hint">${isBn ? 'এখনো কোনো রায় সংক্ষেপ করা হয়নি।' : 'No judgment briefs saved yet.'}</p>` : ''}
            ${currentMatter.summaries.map((s) => `
              <div class="matter-note-card judgment-card">
                <div class="note-card-header">
                  <strong>⚖️ ${escapeHtml(s.data.case_title || s.filename)}</strong>
                  <span class="note-date">${escapeHtml(s.data.court || 'Supreme Court')}</span>
                </div>
                ${s.data.case_number ? `<p class="case-number-tag">📌 ${escapeHtml(s.data.case_number)} ${s.data.bench ? `· Bench: ${escapeHtml(s.data.bench)}` : ''}</p>` : ''}
                <div class="ratio-box">
                  <strong>💡 ${isBn ? 'Ratio Decidendi (মূল আইনি নীতি):' : 'Ratio Decidendi (Core Ruling):'}</strong>
                  <p>${escapeHtml(s.data.ratio_decidendi || '')}</p>
                </div>
                <div class="operative-box" style="margin-top: 8px;">
                  <strong>🏛️ ${isBn ? 'চূড়ান্ত সিদ্ধান্ত / Operative Order:' : 'Operative Order:'}</strong>
                  <p>${escapeHtml(s.data.operative_order || '')}</p>
                </div>
                ${s.data.legal_issues?.length ? `
                  <div class="issues-list" style="margin-top: 8px;">
                    <strong>🔍 ${isBn ? 'বিচার্য বিষয়সমূহ:' : 'Framed Legal Issues:'}</strong>
                    <ul>${s.data.legal_issues.map((i) => `<li>${escapeHtml(i)}</li>`).join('')}</ul>
                  </div>
                ` : ''}
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    if (currentTab === 'chronology') {
      const chronology = currentMatter.chronology;
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>⏳ ${isBn ? 'মোকদ্দমা কালপঞ্জি ও তামাদি সতর্কতা' : 'Matter Chronology & Statutory Limitation Engine'}</strong>
            <p>${isBn 
              ? 'আরজি, জবাব, বায়নাপত্র বা নোটিশের ঘটনাগুলো পেস্ট করুন। Justor AI নিখুঁত সময়রেখা তৈরি করবে এবং তামাদি আইন বা এনআই অ্যাক্টের নির্দিষ্ট সময়সীমা পার হয়ে গেছে কি না তা সতর্ক করবে।'
              : 'Paste pleadings, notices, and dispute facts. Justor AI builds an interactive date-ordered timeline and alerts you to statutory limitation expiry risks under Bangladesh law.'}
            </p>
          </div>

          <div class="chronology-composer">
            <textarea id="chronology-input-text" class="dictate-textarea" rows="4" placeholder="${isBn ? 'মোকদ্দমার ঘটনাবলী ও তারিখ পেস্ট করুন (যেমন: ১২ জানুয়ারি চুক্তি executed হয়, ১৫ জুলাই টাকা প্রদানের কথা ছিল, ২ আগস্ট নোটিশ পাঠানো হয়...)' : 'Paste matter facts and dates (e.g., 12 Jan 2021 agreement executed, 15 Jul payment due, 2 Aug notice sent...)'}"></textarea>
            <div class="dictate-actions">
              <button type="button" class="button button-primary" id="generate-chronology-btn">
                📅 ${isBn ? 'কালপঞ্জি ও তামাদি তৈরি করুন' : 'Generate Interactive Timeline'}
              </button>
            </div>
          </div>

          <div id="chronology-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'তারিখ ও তামাদি সময়সীমা বিশ্লেষণ করা হচ্ছে...' : 'Sorting chronological events & verifying statutory limitation...'}</span>
          </div>

          ${chronology ? `
            <div class="chronology-display-card">
              ${chronology.limitation_alerts?.length ? `
                <div class="limitation-alerts-container">
                  <h4>⚠️ ${isBn ? 'তামাদি ও সময়সীমা সতর্কতা' : 'Statutory Limitation Alerts'}</h4>
                  ${chronology.limitation_alerts.map((al) => `
                    <div class="limitation-alert-pill alert-${al.status || 'urgent'}">
                      <span class="alert-status-tag">${escapeHtml(al.status?.toUpperCase() || 'ALERT')}</span>
                      <strong>${escapeHtml(al.provision)}:</strong>
                      <span>${escapeHtml(al.warning || al.rule)}</span>
                    </div>
                  `).join('')}
                </div>
              ` : ''}

              <div class="timeline-v-container">
                <h4>📅 ${isBn ? 'ঘটনাপ্রবাহ সময়রেখা' : 'Event Timeline'}</h4>
                <div class="timeline-v-track">
                  ${(chronology.timeline || []).map((ev) => `
                    <div class="timeline-v-item ${ev.importance === 'critical' ? 'is-critical' : ''}">
                      <div class="timeline-v-marker"></div>
                      <div class="timeline-v-body">
                        <div class="timeline-v-date">
                          <span>${escapeHtml(ev.date_str)}</span>
                          ${ev.importance === 'critical' ? `<span class="critical-tag">${isBn ? 'গুরুত্বপূর্ণ' : 'Critical'}</span>` : ''}
                        </div>
                        <strong class="timeline-v-title">${escapeHtml(ev.title)}</strong>
                        <p class="timeline-v-desc">${escapeHtml(ev.description)}</p>
                      </div>
                    </div>
                  `).join('')}
                </div>
              </div>
            </div>
          ` : `
            <p class="empty-hint" style="margin-top: 20px;">${isBn ? 'উপরে ঘটনাবলী পেস্ট করে কালপঞ্জি তৈরি করুন।' : 'Generate a chronology above to see the timeline.'}</p>
          `}
        </div>
      `;
    }

    if (currentTab === 'overview') {
      return `
        <div class="matter-tab-content">
          <div class="matter-vault-card">
            <div class="vault-header">
              <div>
                <h3>📁 ${escapeHtml(currentMatter.title)}</h3>
                <span class="vault-client">👤 ${isBn ? 'মক্কেল:' : 'Client:'} <strong>${escapeHtml(currentMatter.clientName || 'Unspecified')}</strong></span>
                <span class="vault-type">⚖️ ${isBn ? 'মোকদ্দমার ধরন:' : 'Matter Type:'} <strong>${escapeHtml(currentMatter.matterType || 'General Litigation')}</strong></span>
              </div>
              <button type="button" class="button button-secondary button-small" id="edit-matter-title-btn">
                ✏️ ${isBn ? 'নাম পরিবর্তন' : 'Edit Title'}
              </button>
            </div>

            <div class="vault-stats-grid">
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.notes.length}</span>
                <span class="stat-lbl">🎙️ ${isBn ? 'ডিকটেশন নোট' : 'Dictation Notes'}</span>
              </div>
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.consultations.length}</span>
                <span class="stat-lbl">🎧 ${isBn ? 'পরামর্শ অডিও' : 'Consultations'}</span>
              </div>
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.summaries.length}</span>
                <span class="stat-lbl">📄 ${isBn ? 'রায়ের সারসংক্ষেপ' : 'Judgment Briefs'}</span>
              </div>
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.chronology?.timeline.length || 0}</span>
                <span class="stat-lbl">⏳ ${isBn ? 'কালপঞ্জি ঘটনা' : 'Timeline Events'}</span>
              </div>
            </div>

            <div class="vault-rag-bridge">
              <h4>🚀 ${isBn ? 'Justor AI দিয়ে মোকদ্দমার খসড়া ও আইনি গবেষণা' : 'Research & Draft with Justor AI'}</h4>
              <p>${isBn 
                ? 'এই মোকদ্দমার সকল নোট, তারিখ এবং দলিল সরাসরি Justor AI-এর লিগ্যাল ইঞ্জিনে পাঠিয়ে জামিন আবেদন বা লিগ্যাল নোটিশ ড্রাফট করুন।' 
                : 'Send this matter\'s facts, dates, and documents directly to Justor AI\'s Bangladesh legal RAG engine to draft petitions or research case law.'}
              </p>
              <div class="bridge-actions">
                <button type="button" class="button button-primary" id="vault-draft-notice-btn">
                  ✍️ ${isBn ? 'লিগ্যাল নোটিশ ড্রাফট করুন' : 'Draft Legal Demand Notice'}
                </button>
                <button type="button" class="button button-secondary" id="vault-research-bail-btn">
                  ⚖️ ${isBn ? 'জামিন বা নিষেধাজ্ঞার গ্রাউন্ডস খুঁজুন' : 'Research Grounds for Bail / Injunction'}
                </button>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    return '';
  };

  const attachEventListeners = () => {
    // Close modal
    backdrop.querySelector('[data-action="close-matter-modal"]')?.addEventListener('click', () => backdrop.remove());
    backdrop.addEventListener('click', (e) => {
      if (e.target === backdrop) backdrop.remove();
    });

    // Matter switcher
    const matterSelect = backdrop.querySelector('#matter-select') as HTMLSelectElement;
    matterSelect?.addEventListener('change', () => {
      setActiveMatterId(matterSelect.value);
      renderModalContent();
    });

    // New Matter button
    backdrop.querySelector('#new-matter-btn')?.addEventListener('click', () => {
      const title = prompt(isBn ? 'নতুন মোকদ্দমার শিরোনাম লিখুন (যেমন: রহমান বনাম করিম):' : 'Enter new matter title (e.g. Rahman v. Karim):');
      if (title && title.trim()) {
        const clientName = prompt(isBn ? 'মক্কেলের নাম:' : 'Client name:') || 'Client';
        const newMatter: LegalMatter = {
          id: 'matter_' + Date.now(),
          title: title.trim(),
          clientName: clientName.trim(),
          matterType: isBn ? 'দেওয়ানি / ফৌজদারি' : 'Civil / Criminal',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          notes: [],
          consultations: [],
          summaries: [],
        };
        matters.push(newMatter);
        saveStoredMatters(matters);
        setActiveMatterId(newMatter.id);
        renderModalContent();
      }
    });

    // Tab buttons
    backdrop.querySelectorAll<HTMLButtonElement>('.matter-tab-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        currentTab = btn.getAttribute('data-tab') as any;
        renderModalContent();
      });
    });

    // Send note to chat buttons
    backdrop.querySelectorAll<HTMLButtonElement>('.send-to-chat-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const txt = btn.getAttribute('data-text') || '';
        if (onSendToChat && txt) {
          backdrop.remove();
          onSendToChat(txt);
        }
      });
    });

    // ── Tab 1: Dictaphone Handlers ──
    if (currentTab === 'dictaphone') {
      const dictateText = backdrop.querySelector('#dictate-text') as HTMLTextAreaElement;
      const dictateSubmit = backdrop.querySelector('#dictate-submit-btn') as HTMLButtonElement;
      const dictateLoading = backdrop.querySelector('#dictate-loading') as HTMLElement;
      const dictateMicToggle = backdrop.querySelector('#dictate-mic-toggle') as HTMLButtonElement;

      // Web Speech recognition toggle
      const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (SpeechRecognition && dictateMicToggle) {
        let recognition: any = null;
        let isRec = false;

        dictateMicToggle.addEventListener('click', () => {
          if (!isRec) {
            try {
              recognition = new SpeechRecognition();
              recognition.continuous = true;
              recognition.interimResults = true;
              recognition.lang = isBn ? 'bn-BD' : 'en-US';

              recognition.onresult = (e: any) => {
                for (let i = e.resultIndex; i < e.results.length; ++i) {
                  if (e.results[i].isFinal) {
                    dictateText.value += (dictateText.value ? ' ' : '') + e.results[i][0].transcript;
                  }
                }
              };

              recognition.start();
              isRec = true;
              dictateMicToggle.classList.add('is-recording');
              dictateMicToggle.innerHTML = `🔴 <span>${isBn ? 'রেকর্ড হচ্ছে...' : 'Recording...'}</span>`;
            } catch (err) {
              console.warn('Speech start error:', err);
            }
          } else {
            if (recognition) recognition.stop();
            isRec = false;
            dictateMicToggle.classList.remove('is-recording');
            dictateMicToggle.innerHTML = `🎤 <span>${isBn ? 'ভয়েস টাইপিং' : 'Start Speaking'}</span>`;
          }
        });
      }

      dictateSubmit?.addEventListener('click', async () => {
        const text = dictateText?.value.trim();
        if (!text) {
          alert(isBn ? 'অনুগ্রহ করে কিছু বিবরণ লিখুন বা মুখে বলুন।' : 'Please type or dictate some notes first.');
          return;
        }

        dictateLoading.style.display = 'flex';
        dictateSubmit.disabled = true;

        try {
          const resp = await fetch(`${backendUrl}/api/matter/voice-note`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, language: isBn ? 'bn' : 'en' }),
          });
          const res = await resp.json();
          if (resp.ok && res.status === 'ok' && res.data) {
            const newNote: MatterNote = {
              id: 'note_' + Date.now(),
              rawText: text,
              data: res.data,
              createdAt: new Date().toISOString(),
            };
            currentMatter.notes.unshift(newNote);
            currentMatter.updatedAt = new Date().toISOString();
            if (res.data.client_name && res.data.client_name !== 'Unknown') {
              currentMatter.clientName = res.data.client_name;
            }
            saveStoredMatters(matters);
            renderModalContent();
          } else {
            alert(res.detail || 'Failed to process note.');
          }
        } catch (err) {
          alert('Network error connecting to Matter Service.');
        } finally {
          dictateLoading.style.display = 'none';
          dictateSubmit.disabled = false;
        }
      });
    }

    // ── Tab 2: Consultation Audio Handlers ──
    if (currentTab === 'consultation') {
      const fileInput = backdrop.querySelector('#consultation-audio-file') as HTMLInputElement;
      const browseBtn = backdrop.querySelector('#browse-audio-btn') as HTMLButtonElement;
      const audioLoading = backdrop.querySelector('#audio-loading') as HTMLElement;

      browseBtn?.addEventListener('click', () => fileInput?.click());

      fileInput?.addEventListener('change', async () => {
        if (!fileInput.files || fileInput.files.length === 0) return;
        const file = fileInput.files[0];
        audioLoading.style.display = 'flex';

        const formData = new FormData();
        formData.append('file', file);
        formData.append('language', isBn ? 'bn' : 'en');

        try {
          const resp = await fetch(`${backendUrl}/api/matter/audio-consultation`, {
            method: 'POST',
            body: formData,
          });
          const res = await resp.json();
          if (resp.ok && res.status === 'ok' && res.data) {
            const newConsultation: MatterConsultation = {
              id: 'cons_' + Date.now(),
              filename: file.name,
              data: res.data,
              createdAt: new Date().toISOString(),
            };
            currentMatter.consultations.unshift(newConsultation);
            currentMatter.updatedAt = new Date().toISOString();
            saveStoredMatters(matters);
            renderModalContent();
          } else {
            alert(res.detail || 'Failed to process consultation audio.');
          }
        } catch (err) {
          alert('Error uploading consultation audio.');
        } finally {
          audioLoading.style.display = 'none';
        }
      });
    }

    // ── Tab 3: Judgment Summarizer Handlers ──
    if (currentTab === 'summarizer') {
      const judgmentFileInput = backdrop.querySelector('#judgment-file-input') as HTMLInputElement;
      const uploadBtn = backdrop.querySelector('#upload-judgment-btn') as HTMLButtonElement;
      const textInput = backdrop.querySelector('#judgment-text-input') as HTMLTextAreaElement;
      const summarizeBtn = backdrop.querySelector('#summarize-btn') as HTMLButtonElement;
      const loading = backdrop.querySelector('#summarize-loading') as HTMLElement;

      uploadBtn?.addEventListener('click', () => judgmentFileInput?.click());

      judgmentFileInput?.addEventListener('change', async () => {
        if (!judgmentFileInput.files || judgmentFileInput.files.length === 0) return;
        const file = judgmentFileInput.files[0];
        loading.style.display = 'flex';

        const formData = new FormData();
        formData.append('file', file);
        formData.append('language', isBn ? 'bn' : 'en');

        try {
          const resp = await fetch(`${backendUrl}/api/matter/document-summary`, {
            method: 'POST',
            body: formData,
          });
          const res = await resp.json();
          if (resp.ok && res.status === 'ok' && res.data) {
            currentMatter.summaries.unshift({
              id: 'sum_' + Date.now(),
              filename: file.name,
              data: res.data,
              createdAt: new Date().toISOString(),
            });
            saveStoredMatters(matters);
            renderModalContent();
          } else {
            alert(res.detail || 'Failed to summarize document.');
          }
        } catch {
          alert('Error summarizing document file.');
        } finally {
          loading.style.display = 'none';
        }
      });

      summarizeBtn?.addEventListener('click', async () => {
        const text = textInput?.value.trim();
        if (!text) {
          alert(isBn ? 'অনুগ্রহ করে রায়ের কোনো অংশ পেস্ট করুন।' : 'Please paste some judgment text first.');
          return;
        }
        loading.style.display = 'flex';

        const formData = new FormData();
        formData.append('text', text);
        formData.append('language', isBn ? 'bn' : 'en');

        try {
          const resp = await fetch(`${backendUrl}/api/matter/document-summary`, {
            method: 'POST',
            body: formData,
          });
          const res = await resp.json();
          if (resp.ok && res.status === 'ok' && res.data) {
            currentMatter.summaries.unshift({
              id: 'sum_' + Date.now(),
              filename: 'Pasted Judgment',
              data: res.data,
              createdAt: new Date().toISOString(),
            });
            saveStoredMatters(matters);
            renderModalContent();
          } else {
            alert(res.detail || 'Failed to summarize text.');
          }
        } catch {
          alert('Error summarizing text.');
        } finally {
          loading.style.display = 'none';
        }
      });
    }

    // ── Tab 4: Chronology Handlers ──
    if (currentTab === 'chronology') {
      const chronologyInput = backdrop.querySelector('#chronology-input-text') as HTMLTextAreaElement;
      const generateBtn = backdrop.querySelector('#generate-chronology-btn') as HTMLButtonElement;
      const loading = backdrop.querySelector('#chronology-loading') as HTMLElement;

      generateBtn?.addEventListener('click', async () => {
        const text = chronologyInput?.value.trim();
        if (!text) {
          alert(isBn ? 'অনুগ্রহ করে ঘটনাবলী ও তারিখ পেস্ট করুন।' : 'Please paste dispute facts or dates first.');
          return;
        }
        loading.style.display = 'flex';

        try {
          const resp = await fetch(`${backendUrl}/api/matter/chronology`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, language: isBn ? 'bn' : 'en' }),
          });
          const res = await resp.json();
          if (resp.ok && res.status === 'ok' && res.data) {
            currentMatter.chronology = res.data;
            saveStoredMatters(matters);
            renderModalContent();
          } else {
            alert(res.detail || 'Failed to generate chronology.');
          }
        } catch {
          alert('Network error generating chronology.');
        } finally {
          loading.style.display = 'none';
        }
      });
    }

    // ── Tab 5: Vault Handlers ──
    if (currentTab === 'overview') {
      backdrop.querySelector('#edit-matter-title-btn')?.addEventListener('click', () => {
        const newTitle = prompt(isBn ? 'মোকদ্দমার নতুন নাম:' : 'New matter title:', currentMatter.title);
        if (newTitle && newTitle.trim()) {
          currentMatter.title = newTitle.trim();
          saveStoredMatters(matters);
          renderModalContent();
        }
      });

      backdrop.querySelector('#vault-draft-notice-btn')?.addEventListener('click', () => {
        const factsText = currentMatter.notes.map((n) => n.data.dispute_summary || n.rawText).join('\n') || currentMatter.title;
        const prompt = isBn 
          ? `নিচের মোকদ্দমার তথ্যের আলোকে নেগোশিয়েবল ইনস্ট্রুমেন্টস অ্যাক্ট, ১৮৮১-এর ধারা ১৩৮ অনুযায়ী একটি আনুষ্ঠানিক লিগ্যাল ডিমান্ড নোটিশ (Statutory Legal Demand Notice) ড্রাফট করুন:\n${factsText}`
          : `Draft a formal Statutory Legal Demand Notice under Section 138 of the Negotiable Instruments Act, 1881 based on these matter facts:\n${factsText}`;
        if (onSendToChat) {
          backdrop.remove();
          onSendToChat(prompt);
        }
      });

      backdrop.querySelector('#vault-research-bail-btn')?.addEventListener('click', () => {
        const factsText = currentMatter.notes.map((n) => n.data.dispute_summary || n.rawText).join('\n') || currentMatter.title;
        const prompt = isBn 
          ? `নিচের ঘটনা এবং সংশ্লিষ্ট ধারাসমূহের ভিত্তিতে দেওয়ানি কার্যবিধির অর্ডার ৩৯ অথবা ফৌজদারি কার্যবিধির ধারা ৪৯৮ অনুযায়ী আদালতে প্রার্থনার জন্য শক্তিশালী আইনি গ্রাউন্ডস (Legal Grounds) ও সুপ্রিম কোর্টের নজির বিশ্লেষণ করুন:\n${factsText}`
          : `Analyze strongest legal grounds and Supreme Court of Bangladesh precedents for bail under Section 498 CrPC or temporary injunction under Order 39 CPC based on these facts:\n${factsText}`;
        if (onSendToChat) {
          backdrop.remove();
          onSendToChat(prompt);
        }
      });
    }
  };

  renderModalContent();
  document.body.appendChild(backdrop);
}
