/**
 * Justor AI — Matter Intelligence Workspace (Lawyer Chambers OS) Suite 2.0
 * Empowers advocates with:
 * 1. Lawyer Dictaphone: Quick voice notes -> Structured matter notes
 * 2. Consultation Audio: Ingest audio -> Transcript + Summary + Red Flags
 * 3. Case in 60 Seconds: Judgment summarizer & Ratio Decidendi
 * 4. Matter Chronology: Interactive timeline with statutory limitation alerts
 * 5. One-Click Hearing Preparation Pack: Bench objectives, evidence checklist, cross-exam questions, closing prayer
 * 6. Matter Consistency Checker & Evidence Matrix: Cross-document contradiction audit & proof gaps
 * 7. Source-Linked Legal Memo Generator: Formal advocate IRAC legal memorandum with Bangladesh Code & DLR citations
 * 8. Matter-Aware Legal Research Bridge: Pre-infuses active matter file into Justor AI RAG
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
  client_consent_verified?: boolean;
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

export interface HearingPreparationPack {
  hearing_title?: string;
  today_objective?: string;
  case_brief?: string;
  key_chronology_highlights?: string[];
  governing_statutes?: string[];
  precedents?: string[];
  evidence_in_hand?: string[];
  evidence_missing_or_risky?: string[];
  anticipated_opposing_arguments?: string[];
  effective_counter_arguments?: string[];
  witness_questions?: Array<{
    target?: string;
    question?: string;
    intended_admission?: string;
    caution?: string;
  }>;
  closing_prayer?: string;
  generatedAt?: string;
}

export interface ContradictionItem {
  category?: string;
  severity?: 'critical' | 'warning' | 'advisory';
  title?: string;
  source_a?: string;
  source_b?: string;
  impact?: string;
  remedy?: string;
}

export interface EvidenceMatrixRow {
  legal_issue?: string;
  supporting_evidence?: string;
  status?: 'proved' | 'partial' | 'vulnerable' | 'missing';
  evidence_gap?: string;
}

export interface ConsistencyAudit {
  audit_summary?: string;
  integrity_score?: string;
  contradictions?: ContradictionItem[];
  evidence_matrix?: EvidenceMatrixRow[];
  generatedAt?: string;
}

export interface LegalMemo {
  id: string;
  question_presented: string;
  memo_title?: string;
  short_answer?: string;
  facts_considered?: string[];
  applicable_statutes?: Array<{
    act?: string;
    section?: string;
    rule_of_law?: string;
    exact_passage?: string;
  }>;
  relevant_precedents?: Array<{
    case_citation?: string;
    principle_held?: string;
    exact_passage?: string;
  }>;
  irac_analysis?: {
    issue?: string;
    rule?: string;
    application?: string;
    conclusion?: string;
  };
  counterarguments_and_risks?: string[];
  final_recommendation?: string;
  source_citations?: Array<{
    title?: string;
    act?: string;
    section?: string;
    passage?: string;
    authority_type?: string;
  }>;
  createdAt: string;
}

export interface LegalMatter {
  id: string;
  title: string;
  clientName: string;
  clientPhone?: string;
  court?: string;
  caseNumber?: string;
  matterType: string;
  summary?: string;
  createdAt: string;
  updatedAt: string;
  notes: MatterNote[];
  consultations: MatterConsultation[];
  summaries: MatterDocumentSummary[];
  chronology?: MatterChronology;
  hearingPack?: HearingPreparationPack;
  consistencyAudit?: ConsistencyAudit;
  legalMemos?: LegalMemo[];
}

import { authService } from './services';

const STORAGE_KEY = 'justor_matters_v1';
const ACTIVE_MATTER_KEY = 'justor_active_matter_id';
const backendUrl = (import.meta.env.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com').replace(/\/$/, '');

async function getAuthHeaders(): Promise<HeadersInit> {
  const session = await authService.session();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }
  const guestId = localStorage.getItem('justor_guest_id');
  if (guestId) {
    headers['X-Guest-Id'] = guestId;
  }
  return headers;
}

export async function syncMatterToCloud(matter: LegalMatter): Promise<void> {
  try {
    const headers = await getAuthHeaders();
    await fetch(`${backendUrl}/api/matters`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ matter }),
    });
  } catch (err) {
    console.warn('Failed to sync matter to cloud:', err);
  }
}

export async function deleteMatterFromCloud(matterId: string): Promise<void> {
  try {
    const headers = await getAuthHeaders();
    await fetch(`${backendUrl}/api/matters/${encodeURIComponent(matterId)}`, {
      method: 'DELETE',
      headers,
    });
  } catch (err) {
    console.warn('Failed to delete matter from cloud:', err);
  }
}

export async function fetchRemoteMatters(): Promise<LegalMatter[]> {
  try {
    const headers = await getAuthHeaders();
    const resp = await fetch(`${backendUrl}/api/matters`, { headers });
    if (!resp.ok) return [];
    const data = await resp.json();
    return Array.isArray(data.matters) ? data.matters : [];
  } catch (err) {
    console.warn('Failed to fetch remote matters:', err);
    return [];
  }
}

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
    const active = getActiveMatter();
    if (active) {
      void syncMatterToCloud(active);
    }
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

/**
 * Builds an enriched matter-aware research prompt pre-infusing parties, facts,
 * chronology, and statutes into Justor AI's legal RAG chat composer.
 */
function buildMatterAwarePrompt(matter: LegalMatter, taskDescription: string): string {
  const sections: string[] = [];
  sections.push(`[CHAMBERS MATTER DOSSIER: ${matter.title}]`);
  sections.push(`Client: ${matter.clientName} | Case No: ${matter.caseNumber || 'Unassigned'} | Court: ${matter.court || 'Court of Bangladesh'} | Matter Type: ${matter.matterType}`);
  
  if (matter.summary) {
    sections.push(`Case Background: ${matter.summary}`);
  }

  // Facts from notes
  const notesFacts = matter.notes.map((n) => n.data.dispute_summary || n.rawText).filter(Boolean);
  if (notesFacts.length) {
    sections.push(`Advocate Notes & Facts:\n${notesFacts.map((f, i) => `(${i + 1}) ${f}`).join('\n')}`);
  }

  // Chronology
  if (matter.chronology?.timeline?.length) {
    const timelineSnippet = matter.chronology.timeline.slice(0, 6).map((t) => `• ${t.date_str}: ${t.title}`).join('\n');
    sections.push(`Key Chronology:\n${timelineSnippet}`);
  }

  sections.push(`\nLEGAL RESEARCH / DRAFTING INSTRUCTIONS:\n${taskDescription}\n(Ground your answer strictly under Bangladesh statutory law and Supreme Court precedents).`);
  return sections.join('\n\n');
}

export function openMatterWorkspaceModal(
  language: 'en' | 'bn' = 'en',
  onSendToChat?: (prompt: string) => void,
  onViewProvision?: (act: string, sectionRef: string) => void
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
      court: isBn ? 'মহানগর দায়রা জজ আদালত, ঢাকা' : 'Metropolitan Sessions Court, Dhaka',
      caseNumber: 'C.R. Case No. 1048 of 2023',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      notes: [],
      consultations: [],
      summaries: [],
      legalMemos: [],
    };
    matters = [defaultMatter];
    saveStoredMatters(matters);
    setActiveMatterId(defaultMatter.id);
  }

  let currentMatter = getActiveMatter() || matters[0];
  let currentTab: 'dictaphone' | 'consultation' | 'summarizer' | 'chronology' | 'hearing_pack' | 'consistency' | 'legal_memo' | 'overview' = 'dictaphone';

  const backdrop = document.createElement('div');
  backdrop.className = 'matter-modal-backdrop';

  // Asynchronous background cloud sync: merges any matters updated on other devices
  void fetchRemoteMatters().then((remoteMatters) => {
    if (remoteMatters && remoteMatters.length > 0) {
      const local = getStoredMatters();
      const localMap = new Map(local.map((m) => [m.id, m]));
      let changed = false;
      for (const rm of remoteMatters) {
        if (!localMap.has(rm.id)) {
          localMap.set(rm.id, rm);
          changed = true;
        } else {
          const lm = localMap.get(rm.id)!;
          if (new Date(rm.updatedAt || 0) > new Date(lm.updatedAt || 0)) {
            localMap.set(rm.id, rm);
            changed = true;
          }
        }
      }
      if (changed) {
        const merged = Array.from(localMap.values());
        localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
        renderModalContent();
      }
    }
  });

  const renderModalContent = () => {
    matters = getStoredMatters();
    currentMatter = getActiveMatter() || matters[0];

    backdrop.innerHTML = `
      <div class="matter-modal-drawer" role="dialog" aria-modal="true">
        <!-- Header -->
        <div class="matter-modal-header">
          <div class="matter-header-left">
            <span class="matter-badge-kicker">
              🧠 Justor Chamber Intelligence Suite 2.0 · Bangladesh
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

        <!-- Navigation Tabs Bar -->
        <div class="matter-tabs-bar">
          <button type="button" class="matter-tab-btn ${currentTab === 'dictaphone' ? 'active' : ''}" data-tab="dictaphone">
            🎙️ ${isBn ? 'ডিকটাফোন' : 'Dictaphone'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'consultation' ? 'active' : ''}" data-tab="consultation">
            🎧 ${isBn ? 'পরামর্শ অডিও' : 'Consultation Audio'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'summarizer' ? 'active' : ''}" data-tab="summarizer">
            📄 ${isBn ? 'কেস সামারি (৬০ সে.)' : 'Case in 60s'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'chronology' ? 'active' : ''}" data-tab="chronology">
            ⏳ ${isBn ? 'কালপঞ্জি ও তামাদি' : 'Chronology'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'hearing_pack' ? 'active' : ''}" data-tab="hearing_pack">
            🏛️ ${isBn ? 'হিয়ারিং প্যাক' : 'Hearing Pack'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'consistency' ? 'active' : ''}" data-tab="consistency">
            ⚖️ ${isBn ? 'সঙ্গতি ও এভিডেন্স' : 'Consistency & Proof'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'legal_memo' ? 'active' : ''}" data-tab="legal_memo">
            📝 ${isBn ? 'লিগ্যাল মেমো' : 'Legal Memo'}
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'overview' ? 'active' : ''}" data-tab="overview">
            📁 ${isBn ? 'ফাইল ভল্ট' : 'Matter Vault'}
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
    // ── 1. DICTAPHONE ──
    if (currentTab === 'dictaphone') {
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>🎙️ ${isBn ? 'আইনজীবীর ভয়েস ডিকটাফোন' : 'Lawyer Chambers Dictaphone'}</strong>
            <p>${isBn 
              ? 'ক্লায়েন্টের সাথে বৈঠকের পর বা আদালত থেকে বের হয়ে দ্রুত মুখে বলুন। Justor AI পক্ষগণের নাম, টাকার অংক, তারিখ, এনআই অ্যাক্ট বা প্যানেল কোডের ধারা ও পরবর্তী পদক্ষেপ সাজিয়ে দেবে।'
              : 'Dictate or speak quick notes after a client conference or hearing. Justor AI automatically extracts parties, claim amounts, dates, relevant Bangladesh statutes, and immediate next actions.'}
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
                  <button type="button" class="button button-small button-outline send-matter-prompt-btn" data-goal="${escapeHtml(n.data.dispute_summary || n.rawText)}">
                    ⚖️ ${isBn ? 'Justor AI-তে গবেষণা করুন' : 'Research Grounds in Justor AI'}
                  </button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    // ── 2. CONSULTATION AUDIO ──
    if (currentTab === 'consultation') {
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>🎧 ${isBn ? 'পরামর্শ অডিও রূপান্তর ও বিশ্লেষণ' : 'Client Consultation Audio Intelligence'}</strong>
            <p>${isBn 
              ? 'মক্কেলের সাথে ২০-৩০ মিনিটের আইনি পরামর্শের অডিও (MP3/M4A/WAV) আপলোড করুন। সম্পূর্ণ বাংলা-ইংরেজি ট্রান্সক্রিপ্ট, উল্লেখিত দলিলসমূহ এবং আইনি ঝুঁকি স্বয়ংক্রিয়ভাবে বের হয়ে আসবে।'
              : 'Upload a 15-30 min audio recording of your client interview or witness conference. Justor AI extracts verbatim transcript, mentioned documents, timeline, and missing evidentiary questions.'}
            </p>
          </div>

          <div class="audio-upload-zone" id="audio-dropzone">
            <input type="file" id="consultation-audio-file" accept=".mp3,.m4a,.wav,.webm,.ogg" style="display:none;" />
            <div class="audio-drop-icon">🎧</div>
            <strong>${isBn ? 'পরামর্শের অডিও ফাইল আপলোড করুন (MP3, M4A, WAV, WEBM)' : 'Drop Consultation Audio File (MP3, M4A, WAV, WEBM)'}</strong>
            <small>${isBn ? 'সর্বোচ্চ আকার: ২৫ মেগাবাইট' : 'Maximum file size: 25MB'}</small>
            <button type="button" class="button button-small button-primary" id="select-audio-btn">
              📁 ${isBn ? 'ফাইল নির্বাচন করুন' : 'Select Audio File'}
            </button>
            <span id="selected-audio-name" class="selected-filename"></span>
          </div>

          <div class="audio-ethics-consent-banner" style="margin: 14px 0; padding: 12px 14px; background: #FFFBEB; border: 1px solid #FCD34D; border-radius: 8px; font-size: 13px; color: #92400E;">
            <div style="display: flex; align-items: flex-start; gap: 8px;">
              <span style="font-size: 16px;">⚖️</span>
              <div>
                <strong>${isBn ? 'বার কাউন্সিল পেশাগত আচরণ ও মক্কেল গোপনীয়তা সম্মতি:' : 'Bar Council Professional Conduct & Confidentiality Compliance:'}</strong>
                <p style="margin: 4px 0 8px; font-size: 12px; line-height: 1.4; color: #78350F;">
                  ${isBn 
                    ? 'বাংলাদেশ বার কাউন্সিল ক্যাননস অফ প্রফেশনাল কনডাক্ট (অধ্যায় ২) অনুযায়ী আইনজীবী-মক্কেল কথোপকথন বিশেষ অধিকারপ্রাপ্ত (Privileged) ও গোপনীয়। অডিও রেকর্ড বা এআই বিশ্লেষণের পূর্বে মক্কেলের সুস্পষ্ট সম্মতি আবশ্যক।'
                    : 'Under Chapter II of the Bangladesh Bar Council Canons of Professional Conduct, advocate-client communications are legally privileged and confidential. Recording or AI processing requires express client informed consent.'}
                </p>
                <label style="display: inline-flex; align-items: center; gap: 8px; font-weight: 600; cursor: pointer; color: #1E293B; font-size: 12.5px;">
                  <input type="checkbox" id="consultation-consent-checkbox" style="width: 16px; height: 16px; accent-color: #1E38C8; cursor: pointer;" />
                  <span>${isBn ? 'আমি প্রত্যয়ন করছি যে মক্কেল এই পরামর্শের অডিও রেকর্ডিং ও এআই বিশ্লেষণে সুস্পষ্ট সম্মতি প্রদান করেছেন।' : 'I certify that the client has expressly consented to audio recording and AI analysis of this consultation.'}</span>
                </label>
              </div>
            </div>
          </div>

          <div class="dictate-actions" style="margin-top:12px;">
            <button type="button" class="button button-primary" id="consultation-process-btn" disabled>
              ⚡ ${isBn ? 'অডিও ট্রান্সক্রিপ্ট ও আইনি ব্রিফ তৈরি করুন' : 'Transcribe & Generate Legal Brief'}
            </button>
          </div>

          <div id="consultation-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'অডিও প্রক্রিয়া হচ্ছে এবং আইনি সারাংশ তৈরি হচ্ছে...' : 'Processing audio and synthesizing legal analysis...'}</span>
          </div>

          <div class="consultation-records-list">
            <h4>🎧 ${isBn ? 'বিশ্লেষিত আইনি পরামর্শসমূহ' : 'Analyzed Consultation Recordings'} (${currentMatter.consultations.length})</h4>
            ${currentMatter.consultations.length === 0 ? `<p class="empty-hint">${isBn ? 'এখনো কোনো অডিও পরামর্শ যোগ করা হয়নি।' : 'No consultation audios added yet.'}</p>` : ''}
            ${currentMatter.consultations.map((c, idx) => `
              <div class="consultation-card">
                <div class="note-card-header">
                  <strong>#${idx + 1} · ${escapeHtml(c.data.matter_title || c.filename)}</strong>
                  <span class="note-date">${new Date(c.createdAt).toLocaleDateString()}</span>
                </div>
                ${c.data.consultation_summary ? `<p class="consult-summary">${escapeHtml(c.data.consultation_summary)}</p>` : ''}
                ${c.data.client_facts?.length ? `
                  <div class="client-facts-block">
                    <strong>📌 ${isBn ? 'মক্কেলের বর্ণিত মূল তথ্য:' : 'Material Facts Alleged:'}</strong>
                    <ul>${c.data.client_facts.map((f) => `<li>${escapeHtml(f)}</li>`).join('')}</ul>
                  </div>
                ` : ''}
                ${c.data.documents_mentioned?.length ? `
                  <div class="docs-mentioned-block">
                    <strong>📑 ${isBn ? 'উল্লেখিত দলিল ও প্রমাণাদি:' : 'Documents Mentioned:'}</strong>
                    <div class="tag-row">${c.data.documents_mentioned.map((d) => `<span class="doc-tag">📄 ${escapeHtml(d)}</span>`).join('')}</div>
                  </div>
                ` : ''}
                ${c.data.red_flags_and_risks?.length ? `
                  <div class="red-flags-block">
                    <strong>⚠️ ${isBn ? 'মক্কেলের মামলার দুর্বলতা / আইনি ঝুঁকি:' : 'Evidentiary Vulnerabilities & Risks:'}</strong>
                    <ul>${c.data.red_flags_and_risks.map((r) => `<li>${escapeHtml(r)}</li>`).join('')}</ul>
                  </div>
                ` : ''}
                ${c.data.transcript ? `
                  <details class="transcript-details">
                    <summary>📜 ${isBn ? 'সম্পূর্ণ শ্রুতিলিপি (Verbatim Transcript)' : 'View Full Transcript'}</summary>
                    <pre class="transcript-pre">${escapeHtml(c.data.transcript)}</pre>
                  </details>
                ` : ''}
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    // ── 3. CASE IN 60 SECONDS ──
    if (currentTab === 'summarizer') {
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>📄 ${isBn ? '৬০ সেকেন্ডে রায় ও পিটিশন সারসংক্ষেপ' : 'Case in 60 Seconds: Ratio Decidendi & Briefing'}</strong>
            <p>${isBn 
              ? 'হাইকোর্ট বিভাগের দীর্ঘ রায়, আদেশের নকল বা প্রতিপক্ষের পিটিশন পেস্ট করুন। Justor AI এক নজরে মূল অনুসিদ্ধান্ত (Ratio Decidendi) ও পয়েন্ট অব ল বের করে দেবে।'
              : 'Paste Supreme Court judgments or petitions. Justor AI extracts the Ratio Decidendi, statutory provisions, bench ruling, and FIRAC analysis.'}
            </p>
          </div>

          <div class="summarizer-input-box">
            <textarea id="judgment-text" class="dictate-textarea" rows="5" placeholder="${isBn ? 'এখানে রায়, মামলার আরজি বা লিখিত জবাবের মূল পাঠ পেস্ট করুন...' : 'Paste judgment, plaint, or written statement text here...'}" style="min-height:130px;"></textarea>
            <div class="dictate-actions" style="margin-top:10px;">
              <button type="button" class="button button-primary" id="summarize-judgment-btn">
                ⚡ ${isBn ? '৬০ সেকেন্ডে বিশ্লেষণ করুন' : 'Generate 60s Briefing'}
              </button>
            </div>
          </div>

          <div id="summarizer-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'নথি বিশ্লেষণ এবং Ratio Decidendi নিষ্কাশন হচ্ছে...' : 'Synthesizing Ratio Decidendi and legal issues...'}</span>
          </div>

          <div class="matter-notes-list">
            <h4>📄 ${isBn ? 'সংরক্ষিত রায়ের সারসংক্ষেপসমূহ' : 'Saved Judgment Briefs'} (${currentMatter.summaries.length})</h4>
            ${currentMatter.summaries.length === 0 ? `<p class="empty-hint">${isBn ? 'এখনো কোনো রায় সংক্ষেপ করা হয়নি।' : 'No judgment briefs added yet.'}</p>` : ''}
            ${currentMatter.summaries.map((s, idx) => `
              <div class="judgment-brief-card">
                <div class="note-card-header">
                  <strong>#${idx + 1} · ${escapeHtml(s.data.case_title || s.filename)}</strong>
                  <span class="note-date">${new Date(s.createdAt).toLocaleDateString()}</span>
                </div>
                ${s.data.court ? `<div class="bench-badge">🏛️ ${escapeHtml(s.data.court)} ${s.data.bench ? `· ${escapeHtml(s.data.bench)}` : ''}</div>` : ''}
                ${s.data.ratio_decidendi ? `
                  <div class="ratio-box">
                    <span class="ratio-label">⚖️ ${isBn ? 'আইনি অনুসিদ্ধান্ত (Ratio Decidendi):' : 'Authoritative Ratio Decidendi:'}</span>
                    <p>${escapeHtml(s.data.ratio_decidendi)}</p>
                  </div>
                ` : ''}
                ${s.data.facts_brief ? `<p class="facts-brief"><strong>${isBn ? 'ঘটনা সংক্ষেপ:' : 'Factual Matrix:'}</strong> ${escapeHtml(s.data.facts_brief)}</p>` : ''}
                ${s.data.statutes_cited?.length ? `
                  <div class="note-sections">
                    <span>📜 ${isBn ? 'প্রযোজ্য আইন:' : 'Statutes Cited:'}</span>
                    ${s.data.statutes_cited.map((st) => `<span class="statute-badge">${escapeHtml(st)}</span>`).join('')}
                  </div>
                ` : ''}
                ${s.data.study_mode_firac?.analysis ? `
                  <details class="firac-details">
                    <summary>🎓 ${isBn ? 'FIRAC পদ্ধতি (আইন শিক্ষার্থীদের জন্য)' : 'FIRAC Framework Analysis'}</summary>
                    <div class="firac-grid">
                      <div><strong>Facts:</strong> ${escapeHtml(s.data.study_mode_firac.facts || '')}</div>
                      <div><strong>Issue:</strong> ${escapeHtml(s.data.study_mode_firac.issue || '')}</div>
                      <div><strong>Rule:</strong> ${escapeHtml(s.data.study_mode_firac.rule || '')}</div>
                      <div><strong>Analysis:</strong> ${escapeHtml(s.data.study_mode_firac.analysis || '')}</div>
                      <div><strong>Conclusion:</strong> ${escapeHtml(s.data.study_mode_firac.conclusion || '')}</div>
                    </div>
                  </details>
                ` : ''}
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    // ── 4. CHRONOLOGY & TIMELINE ──
    if (currentTab === 'chronology') {
      const chron = currentMatter.chronology;
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>⏳ ${isBn ? 'মামলার ইন্টারেক্টিভ কালপঞ্জি ও তামাদি সর্তকতা' : 'Interactive Matter Chronology & Limitation Alerts'}</strong>
            <p>${isBn 
              ? 'চুক্তি, নোটিশ, চেক ডিজঅনার বা এফআইআরের তারিখসমূহ পেস্ট করুন। Justor AI কালানুক্রমিক টাইমলাইন এবং তামাদি আইনের (Limitation Act) তামাদি ঝুঁকি নির্দেশ করবে।'
              : 'Paste pleadings, notices, or dispute events. Justor AI builds a date-sorted timeline with real-time statutory limitation alerts.'}
            </p>
          </div>

          <div class="chronology-input-card">
            <textarea id="chronology-input-text" class="dictate-textarea" rows="4" placeholder="${isBn ? 'ঘটনা এবং তারিখ পেস্ট করুন (যেমন: ১২/০৩/২০২৩ তারিখে চুক্তি সই, ১৫/০৪/২০২৩ তারিখে চেক ডিজঅনার, ১০/০৫/২০২৩ লিগ্যাল নোটিশ প্রাপ্তি...)' : 'Paste dates and dispute events here...'}" style="min-height:90px;"></textarea>
            <div class="dictate-actions" style="margin-top:8px;">
              <button type="button" class="button button-primary" id="generate-chronology-btn">
                ⚡ ${isBn ? 'কালপঞ্জি তৈরি করুন' : 'Generate Chronology & Alerts'}
              </button>
            </div>
          </div>

          <div id="chronology-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'তারিখসমূহ সাজানো হচ্ছে এবং তামাদি আইন বিশ্লেষণ করা হচ্ছে...' : 'Sorting events and checking Limitation Act schedules...'}</span>
          </div>

          ${chron ? `
            <div class="chronology-result-container">
              <!-- Limitation Alerts -->
              ${chron.limitation_alerts?.length ? `
                <div class="limitation-alerts-section">
                  <h4>🚨 ${isBn ? 'তামাদি আইন ও সংবিধিবদ্ধ সময়সীমার সতর্কতা' : 'Statutory Limitation Alerts'}</h4>
                  <div class="alerts-grid">
                    ${chron.limitation_alerts.map((al) => `
                      <div class="limitation-pill ${al.status}">
                        <div class="alert-top">
                          <span class="alert-status-tag ${al.status}">${al.status.toUpperCase()}</span>
                          <span class="alert-provision">${escapeHtml(al.provision)}</span>
                        </div>
                        <p class="alert-warning">${escapeHtml(al.warning)}</p>
                        <small class="alert-rule">⚖️ ${escapeHtml(al.rule)}</small>
                      </div>
                    `).join('')}
                  </div>
                </div>
              ` : ''}

              <!-- Visual Timeline -->
              <div class="timeline-tree">
                <h4>📅 ${isBn ? 'কালানুক্রমিক ঘটনার তালিকা' : 'Chronological Event Chain'} (${chron.timeline?.length || 0})</h4>
                <div class="timeline-nodes">
                  ${(chron.timeline || []).map((node, i) => `
                    <div class="timeline-node ${node.importance === 'critical' ? 'critical-node' : ''}">
                      <div class="node-marker">${i + 1}</div>
                      <div class="node-content">
                        <div class="node-header">
                          <span class="node-date">📅 ${escapeHtml(node.date_str)}</span>
                          ${node.importance === 'critical' ? `<span class="badge-critical">${isBn ? 'গুরুত্বপূর্ণ তারিখ' : 'Critical Date'}</span>` : ''}
                        </div>
                        <strong class="node-title">${escapeHtml(node.title)}</strong>
                        <p class="node-desc">${escapeHtml(node.description)}</p>
                        ${node.source_reference ? `<small class="node-source">📑 ${escapeHtml(node.source_reference)}</small>` : ''}
                      </div>
                    </div>
                  `).join('')}
                </div>
              </div>
            </div>
          ` : `
            <p class="empty-hint" style="margin-top:20px;">${isBn ? 'এখনো কোনো কালপঞ্জি তৈরি করা হয়নি।' : 'No chronology generated yet. Paste facts above to create one.'}</p>
          `}
        </div>
      `;
    }

    // ── 5. ONE-CLICK HEARING PREPARATION PACK ──
    if (currentTab === 'hearing_pack') {
      const pack = currentMatter.hearingPack;
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>🏛️ ${isBn ? 'এক ক্লিকে শুনানির প্রস্তুতি প্যাক (Courtroom Hearing Pack)' : 'One-Click Courtroom Hearing Preparation Pack'}</strong>
            <p>${isBn 
              ? 'দক্ষিণ-পূর্ব এশিয়ার শীর্ষ লিগ্যাল-টেক ধারণার আলোকে: বেঞ্চে দাঁড়িয়ে আজ কী অর্জন করতে হবে, কোন প্রমাণ সঙ্গে আছে আর কোনটি অনুপস্থিত, প্রতিপক্ষের সম্ভাব্য যুক্তি ও খণ্ডন, এবং জেরা করার ধারালো প্রশ্নমালা।'
              : 'Inspired by leading Singapore & SEA legal chambers AI: synthesizes today\'s prime bench objective, ready vs. missing evidence, counter-arguments, and witness cross-examination cards.'}
            </p>
          </div>

          <div class="hearing-pack-controls">
            <div class="hearing-type-select-row">
              <label for="hearing-type-select"><strong>${isBn ? 'শুনানির ধরন / স্তর:' : 'Hearing Focus:'}</strong></label>
              <select id="hearing-type-select" class="matter-select">
                <option value="general">${isBn ? 'সাধারণ শুনানি / আর্জি ও জবাব' : 'General Hearing / Case Management'}</option>
                <option value="bail">${isBn ? 'জামিন / আগাম জামিন শুনানি (s.498 CrPC)' : 'Bail / Anticipatory Bail Hearing (s.498 CrPC)'}</option>
                <option value="injunction">${isBn ? 'অস্থায়ী নিষেধাজ্ঞা শুনানি (Order 39 CPC)' : 'Ad-Interim Injunction Hearing (Order 39 CPC)'}</option>
                <option value="charge_hearing">${isBn ? 'চার্জ শুনানি ও অব্যাহতি (s.241A/265C CrPC)' : 'Framing of Charge / Discharge Hearing'}</option>
                <option value="cross_examination">${isBn ? 'সাক্ষ্য গ্রহণ ও জেরা (Deposition & Cross-Exam)' : 'Witness Examination & Cross-Examination'}</option>
                <option value="final_argument">${isBn ? 'চূড়ান্ত যুক্তি-তর্ক (Final Arguments)' : 'Final Submissions & Arguments'}</option>
              </select>
              <button type="button" class="button button-primary" id="generate-hearing-pack-btn">
                ⚡ ${isBn ? 'হিয়ারিং প্যাক তৈরি করুন' : 'Generate Hearing Pack'}
              </button>
            </div>
          </div>

          <div id="hearing-pack-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'মোকদ্দমার নথি থেকে আজ আদালতের শুনানির কৌশল ও প্রশ্নমালা প্রস্তুত হচ্ছে...' : 'Synthesizing tactical courtroom objectives, evidence gaps, and cross questions...'}</span>
          </div>

          ${pack ? `
            <div class="hearing-pack-display">
              <!-- Top Objective Banner -->
              <div class="hearing-objective-banner">
                <div class="objective-header">
                  <span class="tactical-badge">🎯 ${isBn ? 'আজকের মূল বেঞ্চ লক্ষ্য' : 'Today\'s Core Tactical Objective'}</span>
                  ${pack.generatedAt ? `<span class="pack-timestamp">Generated: ${new Date(pack.generatedAt).toLocaleDateString()}</span>` : ''}
                </div>
                <h3 class="objective-title">${escapeHtml(pack.today_objective || 'Achieve favorable order')}</h3>
                ${pack.case_brief ? `<p class="brief-lead"><strong>${isBn ? 'বেঞ্চের সামনে সংক্ষেপ:' : 'Bench Briefing:'}</strong> ${escapeHtml(pack.case_brief)}</p>` : ''}
              </div>

              <!-- Statutes & Precedents Quick Pills -->
              ${pack.governing_statutes?.length || pack.precedents?.length ? `
                <div class="hearing-authorities-row">
                  ${pack.governing_statutes?.length ? `
                    <div class="auth-col">
                      <span class="auth-title">📜 ${isBn ? 'প্রযোজ্য ধারা:' : 'Controlling Sections:'}</span>
                      <div class="tag-row">${pack.governing_statutes.map((s) => `<span class="statute-badge">${escapeHtml(s)}</span>`).join('')}</div>
                    </div>
                  ` : ''}
                  ${pack.precedents?.length ? `
                    <div class="auth-col">
                      <span class="auth-title">⚖️ ${isBn ? 'সুপ্রিম কোর্টের নজির:' : 'Leading Precedents:'}</span>
                      <div class="tag-row">${pack.precedents.map((p) => `<span class="precedent-badge">📖 ${escapeHtml(p)}</span>`).join('')}</div>
                    </div>
                  ` : ''}
                </div>
              ` : ''}

              <!-- Evidence Battle Board: In-Hand vs Missing/Risky -->
              <div class="evidence-dual-grid">
                <div class="evidence-box in-hand">
                  <h4>✅ ${isBn ? 'হাতে প্রস্তুত প্রমাণাদি ও প্রদর্শনী' : 'Evidence in Hand (Ready for Bench)'}</h4>
                  ${pack.evidence_in_hand?.length ? `
                    <ul>${pack.evidence_in_hand.map((e) => `<li>${escapeHtml(e)}</li>`).join('')}</ul>
                  ` : `<p class="empty-hint">${isBn ? 'কোনো তালিকা নেই।' : 'None noted.'}</p>`}
                </div>
                <div class="evidence-box risky">
                  <h4>⚠️ ${isBn ? 'অনুপস্থিত বা ঝুঁকিপূর্ণ নথি (প্রতিপক্ষ আক্রমণ করতে পারে)' : 'Missing Proofs / Opponent Targets'}</h4>
                  ${pack.evidence_missing_or_risky?.length ? `
                    <ul>${pack.evidence_missing_or_risky.map((e) => `<li>${escapeHtml(e)}</li>`).join('')}</ul>
                  ` : `<p class="empty-hint">${isBn ? 'কোনো তালিকা নেই।' : 'None noted.'}</p>`}
                </div>
              </div>

              <!-- Tactical Arguments Matrix -->
              <div class="tactics-arguments-grid">
                <div class="tactic-card opposing">
                  <h4>🛡️ ${isBn ? 'প্রতিপক্ষের সম্ভাব্য যুক্তি' : 'Anticipated Opposing Arguments'}</h4>
                  ${pack.anticipated_opposing_arguments?.length ? `
                    <ul>${pack.anticipated_opposing_arguments.map((a) => `<li>${escapeHtml(a)}</li>`).join('')}</ul>
                  ` : `<p class="empty-hint">${isBn ? 'কোনো তথ্য নেই।' : 'None noted.'}</p>`}
                </div>
                <div class="tactic-card rebuttal">
                  <h4>⚔️ ${isBn ? 'আপনার তাৎক্ষণিক খণ্ডন ও জবাব' : 'Effective Statutory Rebuttals'}</h4>
                  ${pack.effective_counter_arguments?.length ? `
                    <ul>${pack.effective_counter_arguments.map((c) => `<li>${escapeHtml(c)}</li>`).join('')}</ul>
                  ` : `<p class="empty-hint">${isBn ? 'কোনো তথ্য নেই।' : 'None noted.'}</p>`}
                </div>
              </div>

              <!-- Witness Cross-Examination Deck -->
              ${pack.witness_questions?.length ? `
                <div class="witness-deck-section">
                  <h4>🎯 ${isBn ? 'জেরা ও সাক্ষ্য গ্রহণের প্রশ্নমালা' : 'Witness Cross-Examination & Trial Deck'}</h4>
                  <div class="witness-cards-grid">
                    ${pack.witness_questions.map((w, idx) => `
                      <div class="witness-question-card">
                        <div class="witness-target-tag">Target: <strong>${escapeHtml(w.target || 'Witness')}</strong> (#${idx + 1})</div>
                        <div class="witness-q-text">"${escapeHtml(w.question || '')}"</div>
                        <div class="witness-admission"><strong>🎯 ${isBn ? 'লক্ষ্য:' : 'Goal:'}</strong> ${escapeHtml(w.intended_admission || '')}</div>
                        ${w.caution ? `<div class="witness-caution"><strong>⚠️ ${isBn ? 'সতর্কতা:' : 'Caution:'}</strong> ${escapeHtml(w.caution)}</div>` : ''}
                      </div>
                    `).join('')}
                  </div>
                </div>
              ` : ''}

              <!-- Closing Standing Prayer -->
              ${pack.closing_prayer ? `
                <div class="closing-prayer-card">
                  <div class="prayer-header">
                    <h4>🗣️ ${isBn ? 'বেঞ্চের সামনে সমাপনী মৌখিক প্রার্থনা (Verbal Submission)' : 'Stand-up Closing Submission & Prayer'}</h4>
                    <button type="button" class="button button-small button-outline" id="copy-prayer-btn" data-text="${escapeHtml(pack.closing_prayer)}">
                      📋 ${isBn ? 'প্রার্থনা কপি করুন' : 'Copy Prayer'}
                    </button>
                  </div>
                  <blockquote class="prayer-quote">${escapeHtml(pack.closing_prayer)}</blockquote>
                </div>
              ` : ''}

              <!-- Footer Bridge Action -->
              <div class="pack-footer-actions">
                <button type="button" class="button button-secondary send-matter-prompt-btn" data-goal="${isBn ? 'এই হিয়ারিং প্যাকের তথ্যের আলোকে আজকের শুনানির জন্য একটি পূর্ণাঙ্গ লিখিত সাবমিশন বা পিটিশন ড্রাফট করুন।' : 'Draft a comprehensive written submission for court based on this hearing pack.'}">
                  ⚖️ ${isBn ? 'Justor AI-তে ড্রাফট তৈরি করুন' : 'Draft Full Written Submission in Justor'}
                </button>
              </div>
            </div>
          ` : `
            <p class="empty-hint" style="margin-top:24px;">${isBn ? 'এই মোকদ্দমার জন্য এখনো কোনো হিয়ারিং প্যাক তৈরি করা হয়নি। উপরের বোতামে ক্লিক করুন।' : 'No hearing pack generated yet. Select a hearing focus above and click Generate.'}</p>
          `}
        </div>
      `;
    }

    // ── 6. CONSISTENCY CHECKER & EVIDENCE MATRIX ──
    if (currentTab === 'consistency') {
      const audit = currentMatter.consistencyAudit;
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>⚖️ ${isBn ? 'মোকদ্দমা সঙ্গতি ও এভিডেন্স ম্যাট্রিক্স (Consistency & Proof Audit)' : 'Matter Consistency Checker & Evidence Matrix'}</strong>
            <p>${isBn 
              ? 'ফাইলের আরজি, নোটিশ, রশিদ ও ডিকটেশনের মধ্যে তারিখের অমিল, টাকার গরমিল বা দাগ নম্বরের অসঙ্গতি স্বয়ংক্রিয়ভাবে চিহ্নিত করুন এবং মামলায় প্রতিটি দাবি প্রমাণের জন্য প্রয়োজনীয় দলিলের শূন্যতা যাচাই করুন।'
              : 'Cross-audits all documents, pleadings, and notes for factual contradictions (dates, claim sums, CS/SA/RS Dag & Khatian numbers) and builds an evidentiary proof matrix.'}
            </p>
          </div>

          <div class="audit-controls-bar">
            <button type="button" class="button button-primary" id="run-consistency-btn">
              🔍 ${isBn ? 'ফাইলের সঙ্গতি ও প্রমাণাদি অডিট চালান' : 'Run Consistency & Evidence Audit'}
            </button>
          </div>

          <div id="consistency-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'সকল নথি ও ডিকটেশনের মধ্যে তথ্যগত বৈপরীত্য ও প্রমাণের ঘাটতি খতিয়ে দেখা হচ্ছে...' : 'Auditing dates, sums, plot numbers, and evidentiary proof elements...'}</span>
          </div>

          ${audit ? `
            <div class="consistency-results-display">
              <!-- Integrity Score & Summary -->
              <div class="integrity-summary-card">
                <div class="score-badge-circle">
                  <span class="score-num">${escapeHtml(audit.integrity_score || '80%')}</span>
                  <span class="score-lbl">${isBn ? 'রেকর্ডের দৃঢ়তা' : 'Record Integrity'}</span>
                </div>
                <div class="integrity-details">
                  <h4>📋 ${isBn ? 'আইনি অডিট ফলাফল' : 'Litigation Record Audit Verdict'}</h4>
                  <p>${escapeHtml(audit.audit_summary || 'Audit complete.')}</p>
                </div>
              </div>

              <!-- Factual Contradictions Section -->
              <div class="contradictions-section">
                <h4>⚠️ ${isBn ? 'চিহ্নিত তথ্যগত বৈপরীত্য ও অসঙ্গতি' : 'Detected Factual Contradictions'} (${audit.contradictions?.length || 0})</h4>
                ${audit.contradictions?.length ? `
                  <div class="contradictions-list">
                    ${audit.contradictions.map((c) => `
                      <div class="contradiction-card ${c.severity || 'warning'}">
                        <div class="contra-top">
                          <span class="contra-pill ${c.severity}">${(c.severity || 'WARNING').toUpperCase()}</span>
                          <span class="contra-category">${escapeHtml(c.category || 'General Discrepancy')}</span>
                        </div>
                        <h5 class="contra-title">${escapeHtml(c.title || 'Inconsistent Statements')}</h5>
                        <div class="contra-sources-grid">
                          <div class="contra-source a">
                            <span class="source-lbl">📌 Source A:</span>
                            <p>${escapeHtml(c.source_a || '')}</p>
                          </div>
                          <div class="contra-source b">
                            <span class="source-lbl">📌 Source B:</span>
                            <p>${escapeHtml(c.source_b || '')}</p>
                          </div>
                        </div>
                        ${c.impact ? `<div class="contra-impact"><strong>⚠️ ${isBn ? 'আইনি প্রভাব:' : 'Courtroom Impact:'}</strong> ${escapeHtml(c.impact)}</div>` : ''}
                        ${c.remedy ? `<div class="contra-remedy"><strong>💡 ${isBn ? 'আইনজীবীর করণীয় প্রতিকার:' : 'Recommended Cure:'}</strong> ${escapeHtml(c.remedy)}</div>` : ''}
                      </div>
                    `).join('')}
                  </div>
                ` : `
                  <div class="no-contradictions-box">
                    <span>✅ ${isBn ? 'নথি ও তথ্যের মধ্যে কোনো স্পষ্ট বৈপরীত্য পাওয়া যায়নি।' : 'No material factual contradictions detected across current matter entries.'}</span>
                  </div>
                `}
              </div>

              <!-- Evidentiary Proof Matrix Section -->
              <div class="evidence-matrix-section">
                <h4>📊 ${isBn ? 'দাবির উপাদান ও প্রমাণের ম্যাট্রিক্স (Evidence Matrix)' : 'Evidentiary Proof Matrix'}</h4>
                ${audit.evidence_matrix?.length ? `
                  <div class="table-responsive">
                    <table class="evidence-matrix-table">
                      <thead>
                        <tr>
                          <th>${isBn ? 'দাবির আইনি উপাদান / ইস্যু' : 'Essential Legal Issue'}</th>
                          <th>${isBn ? 'ফাইলে থাকা সমর্থক প্রমাণ' : 'Supporting Evidence'}</th>
                          <th>${isBn ? 'অবস্থা' : 'Status'}</th>
                          <th>${isBn ? 'ঘাটতি ও সংগ্রহের করণীয়' : 'Evidence Gap & Action'}</th>
                        </tr>
                      </thead>
                      <tbody>
                        ${audit.evidence_matrix.map((row) => `
                          <tr>
                            <td class="issue-cell"><strong>${escapeHtml(row.legal_issue || '')}</strong></td>
                            <td class="evidence-cell">${escapeHtml(row.supporting_evidence || 'None')}</td>
                            <td class="status-cell">
                              <span class="matrix-status-pill ${row.status || 'missing'}">${(row.status || 'missing').toUpperCase()}</span>
                            </td>
                            <td class="gap-cell">${escapeHtml(row.evidence_gap || 'Ready')}</td>
                          </tr>
                        `).join('')}
                      </tbody>
                    </table>
                  </div>
                ` : `<p class="empty-hint">${isBn ? 'কোনো ম্যাট্রিক্স উপলব্ধ নেই।' : 'No proof rows generated.'}</p>`}
              </div>

              <!-- Chat Bridge -->
              <div class="pack-footer-actions">
                <button type="button" class="button button-secondary send-matter-prompt-btn" data-goal="${isBn ? 'এই মোকদ্দমার প্রমাণের ঘাটতি এবং অসঙ্গতিগুলো কীভাবে আইনি পদ্ধতিতে আদালতে সমাধান করা যায় তার স্ট্র্যাটেজি তৈরি করুন।' : 'Formulate a litigation strategy to resolve the detected evidence gaps and contradictions under Bangladesh procedural law.'}">
                  ⚖️ ${isBn ? 'Justor AI-তে সমাধানের কৌশল খুঁজুন' : 'Research Solutions in Justor AI'}
                </button>
              </div>
            </div>
          ` : `
            <p class="empty-hint" style="margin-top:24px;">${isBn ? 'এই মোকদ্দমার এখনো কোনো অডিট রেকর্ড নেই। অডিট শুরু করতে উপরের বোতামে চাপুন।' : 'No consistency audit run yet. Click the button above to cross-audit your matter file.'}</p>
          `}
        </div>
      `;
    }

    // ── 7. SOURCE-LINKED LEGAL MEMO GENERATOR ──
    if (currentTab === 'legal_memo') {
      const memos = currentMatter.legalMemos || [];
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <strong>📝 ${isBn ? 'উৎস-সংযুক্ত লিগ্যাল মেমোরেন্ডাম জেনারেটর (IRAC Method)' : 'Source-Linked Legal Memorandum Generator'}</strong>
            <p>${isBn 
              ? 'ইন্দোনেশিয়ার Hukumonline AIlex ও সিঙ্গাপুরের Pair-a-Legal আদলে: মোকদ্দমার যেকোনো প্রশ্ন উপস্থাপন করুন। Justor AI বাংলাদেশ কোড, সুপ্রিম কোর্টের নজির (DLR/BLD) ও IRAC মেথডে প্রফেশনাল লিগ্যাল মেমো প্রস্তুত করবে।'
              : 'Drafts formal IRAC advocate legal memoranda grounded strictly in matter facts with direct statutory sections and Supreme Court (DLR/BLD) authorities.'}
            </p>
          </div>

          <div class="memo-composer-card">
            <label for="memo-question-input"><strong>${isBn ? 'উপস্থাপিত আইনি প্রশ্ন (Question Presented):' : 'Question Presented (Legal Issue to Analyze):'}</strong></label>
            <textarea id="memo-question-input" class="dictate-textarea" rows="2" placeholder="${isBn ? 'উদাহরণ: তামাদি আইনের অনুচ্ছেদ ১১৩ অনুযায়ী বায়নাপত্র সম্পাদনের কত দিনের মধ্যে চুক্তি প্রবলের মামলা দায়ের করতে হবে?' : 'Example: Whether the suit is barred by limitation under Article 113 of the Limitation Act, 1908 in light of part-performance under Section 53A TPA?'}" style="min-height:70px;"></textarea>
            
            <div class="memo-quick-prompts">
              <span>${isBn ? 'দ্রুত পরামর্শ:' : 'Quick Issues:'}</span>
              <button type="button" class="memo-tag-btn" data-q="${isBn ? 'এনআই অ্যাক্টের ১৩৮ ধারা অনুযায়ী সিকিউরিটি চেক ডিজঅনার হলে মামলা চলবে কি না?' : 'Whether dishonour of a cheque issued as security attracts Section 138 of NI Act?'}">
                🏷️ ${isBn ? 'এনআই অ্যাক্ট সিকিউরিটি চেক' : 'NI Act Security Cheque'}
              </button>
              <button type="button" class="memo-tag-btn" data-q="${isBn ? 'অস্থায়ী নিষেধাজ্ঞার ৩টি মূল শর্ত (Prima Facie Case, Balance of Convenience, Irreparable Loss) কীভাবে পূরণ হবে?' : 'Whether the requirements of prima facie case and irreparable loss are satisfied for temporary injunction under Order 39 CPC?'}">
                🏷️ ${isBn ? 'অস্থায়ী নিষেধাজ্ঞার শর্ত' : 'Temporary Injunction Order 39'}
              </button>
            </div>

            <div class="dictate-actions" style="margin-top:10px;">
              <button type="button" class="button button-primary" id="generate-memo-btn">
                ⚡ ${isBn ? 'আনুষ্ঠানিক লিগ্যাল মেমো তৈরি করুন' : 'Generate Formal Legal Memo'}
              </button>
            </div>
          </div>

          <div id="memo-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'আইনগত প্রশ্ন, বাংলাদেশ কোড ও সুপ্রিম কোর্টের নজির গবেষণা করে মেমোরেন্ডাম তৈরি হচ্ছে...' : 'Researching statutory provisions, DLR/BLD precedents, and drafting IRAC analysis...'}</span>
          </div>

          <!-- Existing Legal Memos -->
          <div class="legal-memos-list">
            <h4>📑 ${isBn ? 'সংরক্ষিত আইনি মেমোরেন্ডামসমূহ' : 'Drafted Legal Memoranda'} (${memos.length})</h4>
            ${memos.length === 0 ? `<p class="empty-hint">${isBn ? 'এখনো কোনো মেমো তৈরি করা হয়নি।' : 'No legal memos drafted yet.'}</p>` : ''}
            ${memos.map((memo, idx) => `
              <div class="legal-memo-document">
                <div class="memo-doc-header">
                  <div class="memo-badge">JUSTOR LEGAL MEMORANDUM #${idx + 1}</div>
                  <span class="memo-date">${new Date(memo.createdAt).toLocaleDateString()}</span>
                </div>

                <div class="memo-meta-table">
                  <div><strong>TO:</strong> Senior Advocates & Chambers Briefing Counsel</div>
                  <div><strong>FROM:</strong> Justor AI Chamber Intelligence</div>
                  <div><strong>MATTER:</strong> ${escapeHtml(currentMatter.title)} (${escapeHtml(currentMatter.court || 'Court of Bangladesh')})</div>
                  <div><strong>RE:</strong> ${escapeHtml(memo.question_presented)}</div>
                </div>

                <div class="memo-section">
                  <h5>📌 I. QUESTION PRESENTED</h5>
                  <p class="memo-text highlight">${escapeHtml(memo.question_presented)}</p>
                </div>

                ${memo.short_answer ? `
                  <div class="memo-section">
                    <h5>⚡ II. SHORT ANSWER</h5>
                    <p class="memo-text font-medium">${escapeHtml(memo.short_answer)}</p>
                  </div>
                ` : ''}

                ${memo.facts_considered?.length ? `
                  <div class="memo-section">
                    <h5>📋 III. MATERIAL FACTS CONSIDERED</h5>
                    <ul>${memo.facts_considered.map((f) => `<li>${escapeHtml(f)}</li>`).join('')}</ul>
                  </div>
                ` : ''}

                ${memo.applicable_statutes?.length ? `
                  <div class="memo-section">
                    <h5>📜 IV. CONTROLLING STATUTORY PROVISIONS</h5>
                    <div class="statutes-callouts">
                      ${memo.applicable_statutes.map((st) => `
                        <div class="statute-callout interactive-citation" data-act="${escapeHtml(st.act || '')}" data-sec="${escapeHtml(st.section || '')}">
                          <div class="statute-callout-header">
                            <strong>${escapeHtml(st.act || 'Act')} — ${escapeHtml(st.section || 'Section')}</strong>
                            <button type="button" class="btn-jump-provision" data-act="${escapeHtml(st.act || '')}" data-sec="${escapeHtml(st.section || '')}" data-passage="${escapeHtml(st.exact_passage || st.rule_of_law || '')}" title="View verified statutory provision">
                              🔍 ${isBn ? 'ধারা দেখুন ↗' : 'Inspect Provision ↗'}
                            </button>
                          </div>
                          <p>${escapeHtml(st.rule_of_law || '')}</p>
                        </div>
                      `).join('')}
                    </div>
                  </div>
                ` : ''}

                ${memo.relevant_precedents?.length ? `
                  <div class="memo-section">
                    <h5>⚖️ V. AUTHORITATIVE PRECEDENTS (DLR / BLD / BLC)</h5>
                    <div class="precedents-callouts">
                      ${memo.relevant_precedents.map((pr) => `
                        <div class="precedent-callout interactive-citation" data-act="Supreme Court of Bangladesh" data-sec="${escapeHtml(pr.case_citation || '')}">
                          <div class="precedent-callout-header">
                            <strong>📖 ${escapeHtml(pr.case_citation || 'Case Law')}</strong>
                            <button type="button" class="btn-jump-provision" data-act="Supreme Court of Bangladesh" data-sec="${escapeHtml(pr.case_citation || '')}" data-passage="${escapeHtml(pr.exact_passage || pr.principle_held || '')}" title="View precedent holding">
                              ⚖️ ${isBn ? 'নজির দেখুন ↗' : 'Inspect Case ↗'}
                            </button>
                          </div>
                          <p>${escapeHtml(pr.principle_held || '')}</p>
                        </div>
                      `).join('')}
                    </div>
                  </div>
                ` : ''}

                ${memo.irac_analysis?.application ? `
                  <div class="memo-section">
                    <h5>🧠 VI. IRAC LEGAL ANALYSIS</h5>
                    <div class="irac-card">
                      ${memo.irac_analysis.issue ? `<div><strong>Issue:</strong> ${escapeHtml(memo.irac_analysis.issue)}</div>` : ''}
                      ${memo.irac_analysis.rule ? `<div><strong>Rule of Law:</strong> ${escapeHtml(memo.irac_analysis.rule)}</div>` : ''}
                      ${memo.irac_analysis.application ? `<div><strong>Application to Matter Facts:</strong> ${escapeHtml(memo.irac_analysis.application)}</div>` : ''}
                      ${memo.irac_analysis.conclusion ? `<div><strong>Legal Conclusion:</strong> ${escapeHtml(memo.irac_analysis.conclusion)}</div>` : ''}
                    </div>
                  </div>
                ` : ''}

                ${memo.counterarguments_and_risks?.length ? `
                  <div class="memo-section">
                    <h5>🛡️ VII. COUNTERARGUMENTS & PROCEDURAL RISKS</h5>
                    <ul>${memo.counterarguments_and_risks.map((cr) => `<li>${escapeHtml(cr)}</li>`).join('')}</ul>
                  </div>
                ` : ''}

                ${memo.final_recommendation ? `
                  <div class="memo-section recommendation">
                    <h5>💡 VIII. PRACTICAL LITIGATION RECOMMENDATION</h5>
                    <p class="memo-text">${escapeHtml(memo.final_recommendation)}</p>
                  </div>
                ` : ''}

                ${memo.source_citations?.length ? `
                  <div class="memo-section sources">
                    <h5>🔗 IX. EXACT SOURCE PASSAGES & CITATIONS</h5>
                    <div class="sources-snippets">
                      ${memo.source_citations.map((src) => {
                        const actName = src.act || src.title || 'Statute';
                        const secRef = src.section || src.title || '';
                        return `
                        <div class="source-snippet-card interactive-citation" data-act="${escapeHtml(actName)}" data-sec="${escapeHtml(secRef)}">
                          <div class="source-snippet-header">
                            <span class="src-title">📖 ${escapeHtml(src.title || 'Citation')}</span>
                            <button type="button" class="btn-jump-provision" data-act="${escapeHtml(actName)}" data-sec="${escapeHtml(secRef)}" data-passage="${escapeHtml(src.passage || '')}" title="Open canonical source passage">
                              ${isBn ? 'মূল ধারা/উদ্ধৃতি দেখুন ↗' : 'View Source Authority ↗'}
                            </button>
                          </div>
                          <blockquote class="src-passage">${escapeHtml(src.passage || '')}</blockquote>
                        </div>
                      `}).join('')}
                    </div>
                  </div>
                ` : ''}

                <!-- Memo Actions -->
                <div class="memo-action-bar">
                  <button type="button" class="button button-small button-outline copy-memo-btn" data-id="${memo.id}">
                    📋 ${isBn ? 'মেমো কপি করুন' : 'Copy Memorandum'}
                  </button>
                  <button type="button" class="button button-small button-secondary send-matter-prompt-btn" data-goal="${isBn ? `এই লিগ্যাল মেমোরেন্ডামের সুনির্দিষ্ট আইনি ভিত্তি ও নজিরের আলোকে আদালতের জন্য একটি আনুষ্ঠানিক আরজি বা পিটিশন ড্রাফট করুন:\n\nবিষয়: ${escapeHtml(memo.question_presented)}\n\nসিদ্ধান্ত: ${escapeHtml(memo.short_answer || '')}\n\nআইনি বিশ্লেষণ: ${escapeHtml(memo.irac_analysis?.application || '')}` : `Draft formal court pleading/petition strictly grounded in this legal memo:\n\nQuestion: ${escapeHtml(memo.question_presented)}\n\nShort Answer: ${escapeHtml(memo.short_answer || '')}\n\nIRAC Analysis: ${escapeHtml(memo.irac_analysis?.application || '')}`}">
                    ✍️ ${isBn ? 'Justor AI-তে ড্রাফট করুন' : 'Draft Pleading in Justor'}
                  </button>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    // ── 8. MATTER VAULT OVERVIEW ──
    if (currentTab === 'overview') {
      return `
        <div class="matter-tab-content">
          <div class="matter-vault-container">
            <div class="vault-header">
              <div>
                <h3>📁 ${escapeHtml(currentMatter.title)}</h3>
                <span class="vault-client">👤 ${isBn ? 'মক্কেল:' : 'Client:'} <strong>${escapeHtml(currentMatter.clientName || 'Unspecified')}</strong></span>
                <span class="vault-type">⚖️ ${isBn ? 'মোকদ্দমার ধরন:' : 'Matter Type:'} <strong>${escapeHtml(currentMatter.matterType || 'General Litigation')}</strong></span>
                ${currentMatter.court ? `<span class="vault-court">🏛️ ${escapeHtml(currentMatter.court)}</span>` : ''}
              </div>
              <button type="button" class="button button-secondary button-small" id="edit-matter-title-btn">
                ✏️ ${isBn ? 'বিবরণ সম্পাদনা' : 'Edit Details'}
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
                <span class="stat-num">${currentMatter.chronology?.timeline?.length || 0}</span>
                <span class="stat-lbl">⏳ ${isBn ? 'কালপঞ্জি ঘটনা' : 'Timeline Events'}</span>
              </div>
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.hearingPack ? '1' : '0'}</span>
                <span class="stat-lbl">🏛️ ${isBn ? 'হিয়ারিং প্যাক' : 'Hearing Pack'}</span>
              </div>
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.legalMemos?.length || 0}</span>
                <span class="stat-lbl">📝 ${isBn ? 'লিগ্যাল মেমো' : 'Legal Memos'}</span>
              </div>
            </div>

            <div class="vault-rag-bridge">
              <h4>🚀 ${isBn ? 'Justor AI দিয়ে মোকদ্দমার খসড়া ও আইনি গবেষণা' : 'Matter-Aware Legal RAG Bridge'}</h4>
              <p>${isBn 
                ? 'এই মোকদ্দমার সকল তথ্য, কালপঞ্জি ও প্রমাণ সরাসরি Justor AI-এর আরএজি সার্চে যুক্ত করে নোটিশ, জামিন পিটিশন বা সিভিল রিভিশন ড্রাফট করুন।' 
                : 'Pre-infuses this matter\'s entire facts, chronology, and evidence matrix directly into Justor AI\'s Bangladesh legal RAG engine.'}
              </p>
              <div class="bridge-actions">
                <button type="button" class="button button-primary send-matter-prompt-btn" data-goal="${isBn ? 'এই মোকদ্দমার তথ্যের ভিত্তিতে একটি আনুষ্ঠানিক লিগ্যাল নোটিশ বা আরজি ড্রাফট করুন।' : 'Draft a formal legal notice or plaint based on this matter file.'}">
                  ✍️ ${isBn ? 'লিগ্যাল নোটিশ ড্রাফট করুন' : 'Draft Legal Demand Notice'}
                </button>
                <button type="button" class="button button-secondary send-matter-prompt-btn" data-goal="${isBn ? 'দেওয়ানি কার্যবিধির অর্ডার ৩৯ বা ফৌজদারি কার্যবিধির ৪৯৮ ধারায় সুপ্রিম কোর্টের নজিরসহ প্রার্থনার গ্রাউন্ডস বের করুন।' : 'Research strongest grounds and Supreme Court of Bangladesh precedents for bail or injunction.'}">
                  ⚖️ ${isBn ? 'জামিন / নিষেধাজ্ঞার নজির খুঁজুন' : 'Research Grounds & Case Law'}
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
          court: isBn ? 'জজ কোর্ট / হাইকোর্ট বিভাগ' : 'District Court / High Court Division',
          caseNumber: '',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          notes: [],
          consultations: [],
          summaries: [],
          legalMemos: [],
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

    // Global Matter-Aware Chat Bridge Button Handler
    backdrop.querySelectorAll<HTMLButtonElement>('.send-matter-prompt-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        const goal = btn.getAttribute('data-goal') || 'Research this matter';
        const enrichedPrompt = buildMatterAwarePrompt(currentMatter, goal);
        if (onSendToChat) {
          backdrop.remove();
          onSendToChat(enrichedPrompt);
        }
      });
    });

    // Global Citation / Provision Inspector Handler
    backdrop.querySelectorAll<HTMLButtonElement>('.btn-jump-provision').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const act = btn.getAttribute('data-act') || '';
        const sec = btn.getAttribute('data-sec') || '';
        const passage = btn.getAttribute('data-passage') || '';
        if (onViewProvision && (act || sec)) {
          onViewProvision(act, sec);
        } else if (passage) {
          alert(`${act ? act + ' — ' : ''}${sec}\n\n${passage}`);
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
          alert(isBn ? 'অনুগ্রহ করে কিছু বলুন বা টাইপ করুন।' : 'Please dictate or type notes first.');
          return;
        }

        dictateLoading.style.display = 'flex';
        try {
          const resp = await fetch(`${backendUrl}/api/matter/voice-note`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text, language: isBn ? 'bn' : 'en' }),
          });
          const res = await resp.json();
          if (resp.ok && res.status === 'ok' && res.data) {
            currentMatter.notes.unshift({
              id: 'note_' + Date.now(),
              rawText: text,
              data: res.data,
              createdAt: new Date().toISOString(),
            });
            saveStoredMatters(matters);
            renderModalContent();
          } else {
            alert(res.detail || 'Failed to process voice note.');
          }
        } catch {
          alert('Network error connecting to backend.');
        } finally {
          dictateLoading.style.display = 'none';
        }
      });
    }

    // ── Tab 2: Consultation Audio Handlers ──
    if (currentTab === 'consultation') {
      const dropzone = backdrop.querySelector('#audio-dropzone') as HTMLElement;
      const fileInput = backdrop.querySelector('#consultation-audio-file') as HTMLInputElement;
      const selectBtn = backdrop.querySelector('#select-audio-btn') as HTMLButtonElement;
      const processBtn = backdrop.querySelector('#consultation-process-btn') as HTMLButtonElement;
      const consentCheckbox = backdrop.querySelector('#consultation-consent-checkbox') as HTMLInputElement;
      const filenameSpan = backdrop.querySelector('#selected-audio-name') as HTMLElement;
      const loading = backdrop.querySelector('#consultation-loading') as HTMLElement;

      let selectedFile: File | null = null;

      const updateBtnState = () => {
        const hasFile = Boolean(selectedFile);
        const hasConsent = Boolean(consentCheckbox?.checked);
        if (hasFile && hasConsent) {
          processBtn.removeAttribute('disabled');
        } else {
          processBtn.setAttribute('disabled', 'true');
        }
      };

      consentCheckbox?.addEventListener('change', updateBtnState);

      selectBtn?.addEventListener('click', () => fileInput?.click());
      dropzone?.addEventListener('click', (e) => {
        if (e.target !== selectBtn) fileInput?.click();
      });

      fileInput?.addEventListener('change', () => {
        if (fileInput.files && fileInput.files[0]) {
          selectedFile = fileInput.files[0];
          filenameSpan.textContent = `📎 ${selectedFile.name} (${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB)`;
          updateBtnState();
        }
      });

      processBtn?.addEventListener('click', async () => {
        if (!selectedFile) return;
        if (!consentCheckbox?.checked) {
          alert(isBn ? 'অনুগ্রহ করে মক্কেলের অডিও রেকর্ডিং সম্মতির বক্সে টিক দিন।' : 'Please certify client consent before processing consultation audio.');
          return;
        }
        loading.style.display = 'flex';
        processBtn.setAttribute('disabled', 'true');

        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('language', isBn ? 'bn' : 'en');

        try {
          const resp = await fetch(`${backendUrl}/api/matter/audio-consultation`, {
            method: 'POST',
            body: formData,
          });
          const res = await resp.json();
          if (resp.ok && res.status === 'ok' && res.data) {
            currentMatter.consultations.unshift({
              id: 'consult_' + Date.now(),
              filename: selectedFile.name,
              client_consent_verified: true,
              data: res.data,
              createdAt: new Date().toISOString(),
            });
            saveStoredMatters(matters);
            renderModalContent();
          } else {
            alert(res.detail || 'Failed to analyze consultation recording.');
          }
        } catch {
          alert('Error uploading or analyzing audio.');
        } finally {
          loading.style.display = 'none';
        }
      });
    }

    // ── Tab 3: Case in 60 Seconds Handlers ──
    if (currentTab === 'summarizer') {
      const judgmentText = backdrop.querySelector('#judgment-text') as HTMLTextAreaElement;
      const summarizeBtn = backdrop.querySelector('#summarize-judgment-btn') as HTMLButtonElement;
      const loading = backdrop.querySelector('#summarizer-loading') as HTMLElement;

      summarizeBtn?.addEventListener('click', async () => {
        const text = judgmentText?.value.trim();
        if (!text || text.length < 15) {
          alert(isBn ? 'অনুগ্রহ করে রায় বা আদেশের পাঠ্য পেস্ট করুন।' : 'Please paste sufficient judgment text (min 15 chars).');
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
              filename: 'Pasted Judgment Brief',
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

    // ── Tab 5: Hearing Preparation Pack Handlers ──
    if (currentTab === 'hearing_pack') {
      const typeSelect = backdrop.querySelector('#hearing-type-select') as HTMLSelectElement;
      const generateBtn = backdrop.querySelector('#generate-hearing-pack-btn') as HTMLButtonElement;
      const loading = backdrop.querySelector('#hearing-pack-loading') as HTMLElement;

      generateBtn?.addEventListener('click', async () => {
        const hearingType = typeSelect?.value || 'general';
        loading.style.display = 'flex';

        try {
          const resp = await fetch(`${backendUrl}/api/matter/hearing-pack`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              matter: currentMatter,
              hearing_type: hearingType,
              language: isBn ? 'bn' : 'en',
            }),
          });
          const res = await resp.json();
          if (resp.ok && res.status === 'ok' && res.data) {
            currentMatter.hearingPack = {
              ...res.data,
              generatedAt: new Date().toISOString(),
            };
            saveStoredMatters(matters);
            renderModalContent();
          } else {
            alert(res.detail || 'Failed to generate hearing pack.');
          }
        } catch {
          alert('Network error communicating with Justor Chamber server.');
        } finally {
          loading.style.display = 'none';
        }
      });

      // Copy Prayer Button
      backdrop.querySelector('#copy-prayer-btn')?.addEventListener('click', (e) => {
        const btn = e.currentTarget as HTMLButtonElement;
        const text = btn.getAttribute('data-text') || '';
        if (text) {
          navigator.clipboard.writeText(text);
          btn.textContent = isBn ? '✅ কপি করা হয়েছে' : '✅ Copied!';
          setTimeout(() => {
            btn.textContent = isBn ? '📋 প্রার্থনা কপি করুন' : 'Copy Prayer';
          }, 2000);
        }
      });
    }

    // ── Tab 6: Consistency & Evidence Matrix Handlers ──
    if (currentTab === 'consistency') {
      const runBtn = backdrop.querySelector('#run-consistency-btn') as HTMLButtonElement;
      const loading = backdrop.querySelector('#consistency-loading') as HTMLElement;

      runBtn?.addEventListener('click', async () => {
        loading.style.display = 'flex';

        try {
          const resp = await fetch(`${backendUrl}/api/matter/consistency-check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              matter: currentMatter,
              language: isBn ? 'bn' : 'en',
            }),
          });
          const res = await resp.json();
          if (resp.ok && res.status === 'ok' && res.data) {
            currentMatter.consistencyAudit = {
              ...res.data,
              generatedAt: new Date().toISOString(),
            };
            saveStoredMatters(matters);
            renderModalContent();
          } else {
            alert(res.detail || 'Failed to run consistency check.');
          }
        } catch {
          alert('Network error connecting to Justor server.');
        } finally {
          loading.style.display = 'none';
        }
      });
    }

    // ── Tab 7: Source-Linked Legal Memo Handlers ──
    if (currentTab === 'legal_memo') {
      const memoInput = backdrop.querySelector('#memo-question-input') as HTMLTextAreaElement;
      const generateBtn = backdrop.querySelector('#generate-memo-btn') as HTMLButtonElement;
      const loading = backdrop.querySelector('#memo-loading') as HTMLElement;

      // Quick prompt buttons
      backdrop.querySelectorAll<HTMLButtonElement>('.memo-tag-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
          const q = btn.getAttribute('data-q') || '';
          if (memoInput) memoInput.value = q;
        });
      });

      generateBtn?.addEventListener('click', async () => {
        const question = memoInput?.value.trim();
        if (!question || question.length < 5) {
          alert(isBn ? 'অনুগ্রহ করে বিশ্লেষণের জন্য একটি আইনি প্রশ্ন লিখুন।' : 'Please provide a legal question to analyze (min 5 chars).');
          return;
        }

        loading.style.display = 'flex';
        try {
          const resp = await fetch(`${backendUrl}/api/matter/legal-memo`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              matter: currentMatter,
              question_presented: question,
              language: isBn ? 'bn' : 'en',
            }),
          });
          const res = await resp.json();
          if (resp.ok && res.status === 'ok' && res.data) {
            const raw = res.data;
            const applicable_statutes = (raw.applicable_statutes || raw.statutory_authorities || []).map((s: any) => ({
              act: s.act || s.statute || '',
              section: s.section || s.provision || '',
              rule_of_law: s.rule_of_law || s.rule || s.application || '',
              exact_passage: s.exact_passage || '',
            }));
            const relevant_precedents = (raw.relevant_precedents || raw.judicial_precedents || []).map((p: any) => ({
              case_citation: p.case_citation || p.citation || (p.parties ? `${p.parties} (${p.citation || ''})` : ''),
              principle_held: p.principle_held || p.ratio || p.application || '',
              exact_passage: p.exact_passage || '',
            }));
            const facts_considered = Array.isArray(raw.facts_considered)
              ? raw.facts_considered
              : (Array.isArray(raw.statement_of_facts) ? raw.statement_of_facts : (raw.statement_of_facts ? [raw.statement_of_facts] : []));
            const irac_analysis = raw.irac_analysis || (typeof raw.legal_analysis === 'object' ? raw.legal_analysis : {
              application: typeof raw.legal_analysis === 'string' ? raw.legal_analysis : '',
            });
            const counterarguments_and_risks = Array.isArray(raw.counterarguments_and_risks)
              ? raw.counterarguments_and_risks
              : (Array.isArray(raw.counterarguments_and_rebuttals) ? raw.counterarguments_and_rebuttals : (raw.counterarguments_and_rebuttals ? [raw.counterarguments_and_rebuttals] : []));
            const final_recommendation = raw.final_recommendation || raw.conclusion_and_recommendations || '';
            const source_citations = Array.isArray(raw.source_citations) && raw.source_citations.length > 0
              ? raw.source_citations
              : [
                  ...applicable_statutes.map((s: any) => ({
                    title: `${s.act}${s.section ? ' — ' + s.section : ''}`,
                    act: s.act,
                    section: s.section,
                    passage: s.exact_passage || s.rule_of_law,
                    authority_type: 'statute',
                  })),
                  ...relevant_precedents.map((p: any) => ({
                    title: p.case_citation,
                    act: 'Supreme Court of Bangladesh',
                    section: p.case_citation,
                    passage: p.exact_passage || p.principle_held,
                    authority_type: 'precedent',
                  })),
                ];

            if (!currentMatter.legalMemos) currentMatter.legalMemos = [];
            currentMatter.legalMemos.unshift({
              id: 'memo_' + Date.now(),
              question_presented: question,
              memo_title: raw.memo_title || `LEGAL MEMORANDUM: ${question.slice(0, 45)}`,
              short_answer: raw.short_answer || '',
              facts_considered,
              applicable_statutes,
              relevant_precedents,
              irac_analysis,
              counterarguments_and_risks,
              final_recommendation,
              source_citations,
              createdAt: new Date().toISOString(),
            });
            saveStoredMatters(matters);
            renderModalContent();
          } else {
            alert(res.detail || 'Failed to generate legal memo.');
          }
        } catch {
          alert('Network error generating legal memorandum.');
        } finally {
          loading.style.display = 'none';
        }
      });

      // Copy Memo Button
      backdrop.querySelectorAll<HTMLButtonElement>('.copy-memo-btn').forEach((btn) => {
        btn.addEventListener('click', () => {
          const memoId = btn.getAttribute('data-id');
          const memo = (currentMatter.legalMemos || []).find((m) => m.id === memoId);
          if (memo) {
            const memoText = [
              `LEGAL MEMORANDUM`,
              `MATTER: ${currentMatter.title}`,
              `DATE: ${new Date(memo.createdAt).toLocaleDateString()}`,
              `\nQUESTION PRESENTED:\n${memo.question_presented}`,
              `\nSHORT ANSWER:\n${memo.short_answer || 'N/A'}`,
              memo.irac_analysis?.application ? `\nLEGAL ANALYSIS:\n${memo.irac_analysis.application}` : '',
              memo.final_recommendation ? `\nRECOMMENDATION:\n${memo.final_recommendation}` : '',
            ].filter(Boolean).join('\n\n');

            navigator.clipboard.writeText(memoText);
            btn.textContent = isBn ? '✅ কপি হয়েছে' : '✅ Copied!';
            setTimeout(() => {
              btn.textContent = isBn ? '📋 মেমো কপি করুন' : 'Copy Memorandum';
            }, 2000);
          }
        });
      });
    }

    // ── Tab 8: Vault Overview Handlers ──
    if (currentTab === 'overview') {
      backdrop.querySelector('#edit-matter-title-btn')?.addEventListener('click', () => {
        const newTitle = prompt(isBn ? 'মোকদ্দমার নতুন নাম:' : 'New matter title:', currentMatter.title);
        if (newTitle && newTitle.trim()) {
          const newCourt = prompt(isBn ? 'আদালতের নাম (যেমন: ১ম যুগ্ম জেলা জজ আদালত, ঢাকা):' : 'Court jurisdiction:', currentMatter.court || '');
          currentMatter.title = newTitle.trim();
          if (newCourt !== null) currentMatter.court = newCourt.trim();
          saveStoredMatters(matters);
          renderModalContent();
        }
      });
    }
  };

  renderModalContent();
  document.body.appendChild(backdrop);
}
