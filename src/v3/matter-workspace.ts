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

function cIcon(name: string, size = 16, className = ''): string {
  const cls = className ? ` class="${className}"` : '';
  const paths: Record<string, string> = {
    scales: '<path d="M12 3v18M7 21h10M4 7h16M6 7 3 13h6L6 7Zm12 0-3 6h6l-3-6Z"/>',
    gavel: '<path d="m14 13 5 5M7 6l4 4M3 10l7-7 4 4-7 7zM14 17l3-3M2 21h8M14 21h8"/>',
    memo: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2zM9 7h6M9 11h6"/>',
    mic: '<path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v3M8 22h8"/>',
    headphones: '<path d="M3 18v-6a9 9 0 0 1 18 0v6"/><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    doc: '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8M16 17H8M10 9H8"/>',
    vault: '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>',
    shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
    sparkle: '<path d="m12 3 1.912 5.885L20 10.8l-5.088 3.915L16.824 21 12 16.915 7.176 21l1.912-6.285L4 10.8l6.088-1.915z"/>',
    copy: '<rect width="13" height="13" x="9" y="9" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>',
    external: '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14 21 3"/>',
    check: '<path d="M20 6 9 17l-5-5"/>',
    alert: '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    pen: '<path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>',
    book: '<path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10M6 10h10"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    target: '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>',
    zap: '<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>',
    upload: '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>',
    folder: '<path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"/>',
    calendar: '<rect width="18" height="18" x="3" y="4" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>',
    fileText: '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><line x1="10" y1="9" x2="8" y2="9"/>',
    quote: '<path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/>',
    whatsapp: '<path d="M3 21l1.65-3.8a9 9 0 1 1 3.4 2.9L3 21"/><path d="M9 10a.5.5 0 0 0 1 0V9a.5.5 0 0 0-1 0v1a5 5 0 0 0 5 5h1a.5.5 0 0 0 0-1h-1a.5.5 0 0 0 0 1"/>',
  };
  return `<svg aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"${cls}>${paths[name] || paths.doc}</svg>`;
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
  let currentTab: 'dictaphone' | 'consultation' | 'summarizer' | 'chronology' | 'hearing_pack' | 'consistency' | 'legal_memo' | 'overview' | 'whatsapp' = 'dictaphone';

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
            <div class="matter-brand-badge-row">
              <span class="matter-badge-kicker">
                ${cIcon('scales', 13)}
                <span>JUSTOR CHAMBER OS</span>
              </span>
              <span class="matter-security-pill">
                ${cIcon('shield', 11)}
                <span>CHAPTER II ETHICS COMPLIANT</span>
              </span>
            </div>
            <div class="matter-selector-row">
              <div class="matter-select-container">
                <select id="matter-select" class="matter-select">
                  ${matters.map((m) => `
                    <option value="${m.id}" ${m.id === currentMatter.id ? 'selected' : ''}>
                      ${escapeHtml(m.title)} · ${escapeHtml(m.clientName || 'General Client')}
                    </option>
                  `).join('')}
                </select>
              </div>
              <button type="button" class="button button-small button-outline new-docket-btn" id="new-matter-btn">
                ${cIcon('plus', 13)}
                <span>${isBn ? 'নতুন মোকদ্দমা' : 'New Docket'}</span>
              </button>
            </div>
          </div>
          <button class="modal-close-btn" type="button" data-action="close-matter-modal" aria-label="Close">✕</button>
        </div>

        <!-- Navigation Tabs Bar -->
        <div class="matter-tabs-bar">
          <button type="button" class="matter-tab-btn ${currentTab === 'dictaphone' ? 'active' : ''}" data-tab="dictaphone">
            ${cIcon('mic', 15)} <span>${isBn ? 'ডিকটাফোন' : 'Dictaphone'}</span>
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'consultation' ? 'active' : ''}" data-tab="consultation">
            ${cIcon('headphones', 15)} <span>${isBn ? 'পরামর্শ অডিও' : 'Consultations'}</span>
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'summarizer' ? 'active' : ''}" data-tab="summarizer">
            ${cIcon('doc', 15)} <span>${isBn ? 'কেস সামারি' : 'Case in 60s'}</span>
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'chronology' ? 'active' : ''}" data-tab="chronology">
            ${cIcon('clock', 15)} <span>${isBn ? 'কালপঞ্জি ও তামাদি' : 'Chronology'}</span>
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'hearing_pack' ? 'active' : ''}" data-tab="hearing_pack">
            ${cIcon('gavel', 15)} <span>${isBn ? 'হিয়ারিং স্ট্র্যাটেজি' : 'Hearing Strategy'}</span>
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'consistency' ? 'active' : ''}" data-tab="consistency">
            ${cIcon('scales', 15)} <span>${isBn ? 'সঙ্গতি ও প্রুফ' : 'Proof Audit'}</span>
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'legal_memo' ? 'active' : ''}" data-tab="legal_memo">
            ${cIcon('memo', 15)} <span>${isBn ? 'লিগ্যাল মেমো' : 'Legal Memo'}</span>
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'overview' ? 'active' : ''}" data-tab="overview">
            ${cIcon('vault', 15)} <span>${isBn ? 'চেম্বার ভল্ট' : 'Chamber Vault'}</span>
          </button>
          <button type="button" class="matter-tab-btn ${currentTab === 'whatsapp' ? 'active' : ''}" data-tab="whatsapp">
            ${cIcon('whatsapp', 15)} <span>${isBn ? 'হোয়াটসঅ্যাপ ব্রিজ' : 'WhatsApp Bridge'}</span>
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
    // ── 1. DICTAPHONE & QUICK VOICE NOTES ──
    if (currentTab === 'dictaphone') {
      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <div class="intro-callout-badge">
              ${cIcon('mic', 12)}
              <span>CHAMBERS AUDIO & NOTE INTELLIGENCE</span>
            </div>
            <strong>${isBn ? 'আইনজীবীর ভয়েস ডিকটাফোন' : 'Lawyer Chambers Dictaphone & Brief Builder'}</strong>
            <p>${isBn 
              ? 'ক্লায়েন্টের সাথে বৈঠকের পর বা আদালত থেকে বের হয়ে দ্রুত মুখে বলুন। Justor AI পক্ষগণের নাম, টাকার অংক, তারিখ, এনআই অ্যাক্ট বা প্যানেল কোডের ধারা ও পরবর্তী পদক্ষেপ সাজিয়ে দেবে।'
              : 'Dictate or speak quick notes after a client conference or hearing. Justor AI automatically extracts parties, claim amounts, dates, relevant Bangladesh statutes, and immediate next actions.'}
            </p>
          </div>

          <div class="dictaphone-composer-card">
            <div class="dictaphone-input-header">
              <span class="composer-label">
                ${cIcon('pen', 13)}
                <span>${isBn ? 'আপনার মুখে বলা বিবরণ বা নোট:' : 'Dictated or Typed Facts:'}</span>
              </span>
              <button type="button" class="dictate-mic-btn" id="dictate-mic-toggle">
                ${cIcon('mic', 13)}
                <span>${isBn ? 'ভয়েস টাইপিং' : 'Start Speaking'}</span>
              </button>
            </div>
            <textarea id="dictate-text" class="dictate-textarea" rows="4" placeholder="${isBn ? 'উদাহরণ: মক্কেল রহিম উদ্দিন আজ এসেছিলেন। পূবালী ব্যাংকের ৫ লাখ টাকার চেক বাউন্স করেছে। গত ১২ আগস্ট লিগ্যাল নোটিশ পাঠিয়েছিলেন...' : 'Example: Client Rahim came today regarding a cheque dishonour matter. Cheque amount 5 lakh taka, Pubali bank, notice served on 12 August...'}"></textarea>
            <div class="dictate-actions">
              <button type="button" class="button button-primary" id="dictate-submit-btn">
                ${cIcon('sparkle', 13)}
                <span>${isBn ? 'স্ট্রাকচার্ড নোট তৈরি করুন' : 'Structure Matter Record'}</span>
              </button>
            </div>
          </div>

          <div id="dictate-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'আইনি তথ্য, পক্ষগণ ও প্রযোজ্য ধারা বিশ্লেষণ করা হচ্ছে...' : 'Analyzing facts, parties, and applicable Bangladesh statutes...'}</span>
          </div>

          <!-- Existing Notes List -->
          <div class="matter-notes-list">
            <div class="section-badge-header">
              <span class="sec-num">${currentMatter.notes.length}</span>
              <h5 class="sec-title">${isBn ? 'সংরক্ষিত ডিকটেশন ও নোটসমূহ' : 'Saved Dictation Records'}</h5>
            </div>
            ${currentMatter.notes.length === 0 ? `<p class="empty-hint">${isBn ? 'এখনো কোনো নোট সংরক্ষণ করা হয়নি।' : 'No dictation notes saved yet.'}</p>` : ''}
            ${currentMatter.notes.map((n, idx) => `
              <div class="matter-note-card">
                <div class="note-card-header">
                  <div class="note-title-wrap">
                    <span class="note-idx-pill">#${idx + 1}</span>
                    <strong class="note-client-title">${escapeHtml(n.data.client_name || currentMatter.clientName || 'Note')} — ${escapeHtml(n.data.matter_type || 'General')}</strong>
                  </div>
                  <span class="note-date">${new Date(n.createdAt).toLocaleDateString()}</span>
                </div>
                <p class="note-summary"><strong>${isBn ? 'সারসংক্ষেপ:' : 'Dispute Summary:'}</strong> ${escapeHtml(n.data.dispute_summary || n.rawText)}</p>
                ${n.data.claim_amount ? `
                  <div class="note-financial-row">
                    <span class="financial-chip">
                      ${cIcon('scales', 12)}
                      <span>${isBn ? 'দাবীকৃত অংক:' : 'Claim Amount:'} <strong>${escapeHtml(n.data.claim_amount)}</strong></span>
                    </span>
                  </div>
                ` : ''}
                ${n.data.statutory_provisions?.length ? `
                  <div class="note-sections">
                    <span class="note-sections-lbl">${cIcon('book', 12)} ${isBn ? 'প্রাসঙ্গিক আইন:' : 'Relevant Laws:'}</span>
                    <div class="tag-row">${n.data.statutory_provisions.map((s) => `<span class="statute-badge">${escapeHtml(s)}</span>`).join('')}</div>
                  </div>
                ` : ''}
                ${n.data.missing_questions?.length ? `
                  <div class="note-red-flags">
                    <div class="inquiry-title">
                      ${cIcon('alert', 12)}
                      <span>${isBn ? 'ক্লায়েন্টকে যে প্রশ্নগুলো করতে হবে:' : 'Unresolved Client Inquiries & Evidence Needed:'}</span>
                    </div>
                    <ul>${n.data.missing_questions.map((q) => `<li>${escapeHtml(q)}</li>`).join('')}</ul>
                  </div>
                ` : ''}
                <div class="note-actions">
                  <button type="button" class="button button-small button-outline send-matter-prompt-btn" data-goal="${escapeHtml(n.data.dispute_summary || n.rawText)}">
                    ${cIcon('search', 12)}
                    <span>${isBn ? 'Justor AI-তে গবেষণা করুন' : 'Research Grounds in Justor AI'}</span>
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
            <div class="intro-callout-badge">
              ${cIcon('headphones', 12)}
              <span>AUDIO FORENSICS & TRANSCRIPTION</span>
            </div>
            <strong>${isBn ? 'পরামর্শ অডিও রূপান্তর ও বিশ্লেষণ' : 'Client Consultation Audio Intelligence'}</strong>
            <p>${isBn 
              ? 'মক্কেলের সাথে ২০-৩০ মিনিটের আইনি পরামর্শের অডিও (MP3/M4A/WAV) আপলোড করুন। সম্পূর্ণ বাংলা-ইংরেজি ট্রান্সক্রিপ্ট, উল্লেখিত দলিলসমূহ এবং আইনি ঝুঁকি স্বয়ংক্রিয়ভাবে বের হয়ে আসবে।'
              : 'Upload a 15-30 min audio recording of your client interview or witness conference. Justor AI extracts verbatim transcript, mentioned documents, timeline, and missing evidentiary questions.'}
            </p>
          </div>

          <div class="audio-upload-zone" id="audio-dropzone">
            <input type="file" id="consultation-audio-file" accept=".mp3,.m4a,.wav,.webm,.ogg" style="display:none;" />
            <div class="audio-drop-icon">${cIcon('headphones', 32)}</div>
            <strong class="audio-drop-title">${isBn ? 'পরামর্শের অডিও ফাইল আপলোড করুন (MP3, M4A, WAV, WEBM)' : 'Drop Consultation Audio File (MP3, M4A, WAV, WEBM)'}</strong>
            <small class="audio-drop-sub">${isBn ? 'সর্বোচ্চ আকার: ২৫ মেগাবাইট · আইনজীবী-মক্কেল কথোপকথন এনক্রিপ্টেড' : 'Maximum file size: 25MB · Advocate-Client Privilege Protected'}</small>
            <button type="button" class="button button-small button-primary" id="select-audio-btn">
              ${cIcon('upload', 13)}
              <span>${isBn ? 'ফাইল নির্বাচন করুন' : 'Select Audio File'}</span>
            </button>
            <span id="selected-audio-name" class="selected-filename"></span>
          </div>

          <div class="audio-ethics-card">
            <div class="ethics-card-header">
              ${cIcon('shield', 14)}
              <strong>${isBn ? 'বার কাউন্সিল পেশাগত আচরণ ও মক্কেল গোপনীয়তা সম্মতি:' : 'Bar Council Professional Conduct & Confidentiality Compliance:'}</strong>
            </div>
            <p class="ethics-card-body">
              ${isBn 
                ? 'বাংলাদেশ বার কাউন্সিল ক্যাননস অফ প্রফেশনাল কনডাক্ট (অধ্যায় ২) অনুযায়ী আইনজীবী-মক্কেল কথোপকথন বিশেষ অধিকারপ্রাপ্ত (Privileged) ও গোপনীয়। অডিও রেকর্ড বা এআই বিশ্লেষণের পূর্বে মক্কেলের সুস্পষ্ট সম্মতি আবশ্যক।'
                : 'Under Chapter II of the Bangladesh Bar Council Canons of Professional Conduct, advocate-client communications are legally privileged and confidential. Recording or AI processing requires express client informed consent.'}
            </p>
            <label class="ethics-consent-label">
              <input type="checkbox" id="consultation-consent-checkbox" />
              <span>${isBn ? 'আমি প্রত্যয়ন করছি যে মক্কেল এই পরামর্শের অডিও রেকর্ডিং ও এআই বিশ্লেষণে সুস্পষ্ট সম্মতি প্রদান করেছেন।' : 'I certify that the client has expressly consented to audio recording and AI analysis of this consultation.'}</span>
            </label>
          </div>

          <div class="dictate-actions" style="margin-top:14px;">
            <button type="button" class="button button-primary" id="consultation-process-btn" disabled>
              ${cIcon('sparkle', 13)}
              <span>${isBn ? 'অডিও ট্রান্সক্রিপ্ট ও আইনি ব্রিফ তৈরি করুন' : 'Transcribe & Generate Legal Brief'}</span>
            </button>
          </div>

          <div id="consultation-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'অডিও প্রক্রিয়া হচ্ছে এবং আইনি সারাংশ তৈরি হচ্ছে...' : 'Processing audio and synthesizing legal analysis...'}</span>
          </div>

          <div class="consultation-records-list">
            <div class="section-badge-header">
              <span class="sec-num">${currentMatter.consultations.length}</span>
              <h5 class="sec-title">${isBn ? 'বিশ্লেষিত আইনি পরামর্শসমূহ' : 'Analyzed Consultation Recordings'}</h5>
            </div>
            ${currentMatter.consultations.length === 0 ? `<p class="empty-hint">${isBn ? 'এখনো কোনো অডিও পরামর্শ যোগ করা হয়নি।' : 'No consultation audios added yet.'}</p>` : ''}
            ${currentMatter.consultations.map((c, idx) => `
              <div class="consultation-card">
                <div class="note-card-header">
                  <div class="note-title-wrap">
                    <span class="note-idx-pill">#${idx + 1}</span>
                    <strong class="note-client-title">${escapeHtml(c.data.matter_title || c.filename)}</strong>
                  </div>
                  <span class="note-date">${new Date(c.createdAt).toLocaleDateString()}</span>
                </div>
                ${c.data.consultation_summary ? `<p class="consult-summary">${escapeHtml(c.data.consultation_summary)}</p>` : ''}
                ${c.data.client_facts?.length ? `
                  <div class="client-facts-block">
                    <div class="block-subtitle">${cIcon('doc', 12)} <span>${isBn ? 'মক্কেলের বর্ণিত মূল তথ্য:' : 'Material Facts Alleged:'}</span></div>
                    <ul class="clean-bullet-list">${c.data.client_facts.map((f) => `<li><span class="bullet-dot"></span><span>${escapeHtml(f)}</span></li>`).join('')}</ul>
                  </div>
                ` : ''}
                ${c.data.documents_mentioned?.length ? `
                  <div class="docs-mentioned-block">
                    <div class="block-subtitle">${cIcon('folder', 12)} <span>${isBn ? 'উল্লেখিত দলিল ও প্রমাণাদি:' : 'Documents Mentioned:'}</span></div>
                    <div class="tag-row">${c.data.documents_mentioned.map((d) => `<span class="doc-tag">${cIcon('doc', 11)} ${escapeHtml(d)}</span>`).join('')}</div>
                  </div>
                ` : ''}
                ${c.data.red_flags_and_risks?.length ? `
                  <div class="red-flags-block">
                    <div class="inquiry-title">${cIcon('alert', 12)} <span>${isBn ? 'মক্কেলের মামলার দুর্বলতা / আইনি ঝুঁকি:' : 'Evidentiary Vulnerabilities & Risks:'}</span></div>
                    <ul>${c.data.red_flags_and_risks.map((r) => `<li>${escapeHtml(r)}</li>`).join('')}</ul>
                  </div>
                ` : ''}
                ${c.data.transcript ? `
                  <details class="transcript-details">
                    <summary>${cIcon('fileText', 12)} <span>${isBn ? 'সম্পূর্ণ শ্রুতিলিপি (Verbatim Transcript)' : 'View Full Transcript'}</span></summary>
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
            <div class="intro-callout-badge">
              ${cIcon('gavel', 12)}
              <span>EXECUTIVE JUDGMENT BRIEFING</span>
            </div>
            <strong>${isBn ? '৬০ সেকেন্ডে রায় ও পিটিশন সারসংক্ষেপ' : 'Case in 60 Seconds: Ratio Decidendi & Briefing'}</strong>
            <p>${isBn 
              ? 'হাইকোর্ট বিভাগের দীর্ঘ রায়, আদেশের নকল বা প্রতিপক্ষের পিটিশন পেস্ট করুন। Justor AI এক নজরে মূল অনুসিদ্ধান্ত (Ratio Decidendi) ও পয়েন্ট অব ল বের করে দেবে।'
              : 'Paste Supreme Court judgments or petitions. Justor AI extracts the Ratio Decidendi, statutory provisions, bench ruling, and FIRAC analysis.'}
            </p>
          </div>

          <div class="summarizer-input-box">
            <textarea id="judgment-text" class="dictate-textarea" rows="5" placeholder="${isBn ? 'এখানে রায়, মামলার আরজি বা লিখিত জবাবের মূল পাঠ পেস্ট করুন...' : 'Paste judgment, plaint, or written statement text here...'}" style="min-height:130px;"></textarea>
            <div class="dictate-actions" style="margin-top:10px;">
              <button type="button" class="button button-primary" id="summarize-judgment-btn">
                ${cIcon('sparkle', 13)}
                <span>${isBn ? '৬০ সেকেন্ডে বিশ্লেষণ করুন' : 'Generate 60s Briefing'}</span>
              </button>
            </div>
          </div>

          <div id="summarizer-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'নথি বিশ্লেষণ এবং Ratio Decidendi নিষ্কাশন হচ্ছে...' : 'Synthesizing Ratio Decidendi and legal issues...'}</span>
          </div>

          <div class="matter-notes-list">
            <div class="section-badge-header">
              <span class="sec-num">${currentMatter.summaries.length}</span>
              <h5 class="sec-title">${isBn ? 'সংরক্ষিত রায়ের সারসংক্ষেপসমূহ' : 'Saved Judgment Briefs'}</h5>
            </div>
            ${currentMatter.summaries.length === 0 ? `<p class="empty-hint">${isBn ? 'এখনো কোনো রায় সংক্ষেপ করা হয়নি।' : 'No judgment briefs added yet.'}</p>` : ''}
            ${currentMatter.summaries.map((s, idx) => `
              <div class="judgment-brief-card">
                <div class="note-card-header">
                  <div class="note-title-wrap">
                    <span class="note-idx-pill">#${idx + 1}</span>
                    <strong class="note-client-title">${escapeHtml(s.data.case_title || s.filename)}</strong>
                  </div>
                  <span class="note-date">${new Date(s.createdAt).toLocaleDateString()}</span>
                </div>
                ${s.data.court ? `<div class="bench-badge">${cIcon('gavel', 12)} <span>${escapeHtml(s.data.court)} ${s.data.bench ? `· ${escapeHtml(s.data.bench)}` : ''}</span></div>` : ''}
                ${s.data.ratio_decidendi ? `
                  <div class="ratio-box">
                    <div class="ratio-label">${cIcon('quote', 13)} <span>${isBn ? 'আইনি অনুসিদ্ধান্ত (Ratio Decidendi):' : 'Authoritative Ratio Decidendi:'}</span></div>
                    <p class="ratio-p">${escapeHtml(s.data.ratio_decidendi)}</p>
                  </div>
                ` : ''}
                ${s.data.facts_brief ? `<p class="facts-brief"><strong>${isBn ? 'ঘটনা সংক্ষেপ:' : 'Factual Matrix:'}</strong> ${escapeHtml(s.data.facts_brief)}</p>` : ''}
                ${s.data.statutes_cited?.length ? `
                  <div class="note-sections">
                    <span class="note-sections-lbl">${cIcon('book', 12)} ${isBn ? 'প্রযোজ্য আইন:' : 'Statutes Cited:'}</span>
                    <div class="tag-row">${s.data.statutes_cited.map((st) => `<span class="statute-badge">${escapeHtml(st)}</span>`).join('')}</div>
                  </div>
                ` : ''}
                ${s.data.study_mode_firac?.analysis ? `
                  <details class="firac-details">
                    <summary>${cIcon('book', 12)} <span>${isBn ? 'FIRAC পদ্ধতি (আইন শিক্ষার্থীদের জন্য)' : 'FIRAC Framework Analysis'}</span></summary>
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
            <div class="intro-callout-badge">
              ${cIcon('calendar', 12)}
              <span>PROCEDURAL TIME LIMITS & SCHEDULES</span>
            </div>
            <strong>${isBn ? 'মামলার ইন্টারেক্টিভ কালপঞ্জি ও তামাদি সর্তকতা' : 'Interactive Matter Chronology & Limitation Alerts'}</strong>
            <p>${isBn 
              ? 'চুক্তি, নোটিশ, চেক ডিজঅনার বা এফআইআরের তারিখসমূহ পেস্ট করুন। Justor AI কালানুক্রমিক টাইমলাইন এবং তামাদি আইনের (Limitation Act) তামাদি ঝুঁকি নির্দেশ করবে।'
              : 'Paste pleadings, notices, or dispute events. Justor AI builds a date-sorted timeline with real-time statutory limitation alerts.'}
            </p>
          </div>

          <div class="chronology-input-card">
            <textarea id="chronology-input-text" class="dictate-textarea" rows="4" placeholder="${isBn ? 'ঘটনা এবং তারিখ পেস্ট করুন (যেমন: ১২/০৩/২০২৩ তারিখে চুক্তি সই, ১৫/০৪/২০২৩ তারিখে চেক ডিজঅনার, ১০/০৫/২০২৩ লিগ্যাল নোটিশ প্রাপ্তি...)' : 'Paste dates and dispute events here...'}" style="min-height:90px;"></textarea>
            <div class="dictate-actions" style="margin-top:8px;">
              <button type="button" class="button button-primary" id="generate-chronology-btn">
                ${cIcon('sparkle', 13)}
                <span>${isBn ? 'কালপঞ্জি তৈরি করুন' : 'Generate Chronology & Alerts'}</span>
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
                  <div class="section-badge-header">
                    <span class="sec-num">${chron.limitation_alerts.length}</span>
                    <h5 class="sec-title">${isBn ? 'তামাদি আইন ও সংবিধিবদ্ধ সময়সীমার সতর্কতা' : 'Statutory Limitation & Filing Alerts'}</h5>
                  </div>
                  <div class="alerts-grid">
                    ${chron.limitation_alerts.map((al) => `
                      <div class="limitation-pill ${al.status}">
                        <div class="alert-top">
                          <span class="alert-status-tag ${al.status}">${al.status.toUpperCase()}</span>
                          <span class="alert-provision">${escapeHtml(al.provision)}</span>
                        </div>
                        <p class="alert-warning">${escapeHtml(al.warning)}</p>
                        <small class="alert-rule">${cIcon('scales', 11)} ${escapeHtml(al.rule)}</small>
                      </div>
                    `).join('')}
                  </div>
                </div>
              ` : ''}

              <!-- Visual Timeline -->
              <div class="timeline-tree">
                <div class="section-badge-header">
                  <span class="sec-num">${chron.timeline?.length || 0}</span>
                  <h5 class="sec-title">${isBn ? 'কালানুক্রমিক ঘটনার তালিকা' : 'Chronological Event Chain'}</h5>
                </div>
                <div class="timeline-nodes">
                  ${(chron.timeline || []).map((node, i) => `
                    <div class="timeline-node ${node.importance === 'critical' ? 'critical-node' : ''}">
                      <div class="node-marker">${i + 1}</div>
                      <div class="node-content">
                        <div class="node-header">
                          <span class="node-date">${cIcon('calendar', 11)} ${escapeHtml(node.date_str)}</span>
                          ${node.importance === 'critical' ? `<span class="badge-critical">${cIcon('alert', 10)} ${isBn ? 'গুরুত্বপূর্ণ তারিখ' : 'Critical Date'}</span>` : ''}
                        </div>
                        <strong class="node-title">${escapeHtml(node.title)}</strong>
                        <p class="node-desc">${escapeHtml(node.description)}</p>
                        ${node.source_reference ? `<small class="node-source">${cIcon('doc', 11)} ${escapeHtml(node.source_reference)}</small>` : ''}
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
            <div class="intro-callout-badge">
              ${cIcon('target', 12)}
              <span>COURTROOM ADVOCACY & STRATEGY</span>
            </div>
            <strong>${isBn ? 'এক ক্লিকে শুনানির প্রস্তুতি প্যাক (Courtroom Hearing Pack)' : 'One-Click Courtroom Hearing Preparation Pack'}</strong>
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
                ${cIcon('sparkle', 13)}
                <span>${isBn ? 'হিয়ারিং প্যাক তৈরি করুন' : 'Generate Hearing Pack'}</span>
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
                  <span class="tactical-badge">
                    ${cIcon('target', 11)}
                    <span>${isBn ? 'আজকের মূল বেঞ্চ লক্ষ্য' : 'Today\'s Core Tactical Objective'}</span>
                  </span>
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
                      <span class="auth-title">${cIcon('book', 12)} ${isBn ? 'প্রযোজ্য ধারা:' : 'Controlling Sections:'}</span>
                      <div class="tag-row">${pack.governing_statutes.map((s) => `<span class="statute-badge">${escapeHtml(s)}</span>`).join('')}</div>
                    </div>
                  ` : ''}
                  ${pack.precedents?.length ? `
                    <div class="auth-col">
                      <span class="auth-title">${cIcon('gavel', 12)} ${isBn ? 'সুপ্রিম কোর্টের নজির:' : 'Leading Precedents:'}</span>
                      <div class="tag-row">${pack.precedents.map((p) => `<span class="precedent-badge">${escapeHtml(p)}</span>`).join('')}</div>
                    </div>
                  ` : ''}
                </div>
              ` : ''}

              <!-- Evidence Battle Board: In-Hand vs Missing/Risky -->
              <div class="evidence-dual-grid">
                <div class="evidence-box in-hand">
                  <h4>${cIcon('check', 13)} <span>${isBn ? 'হাতে প্রস্তুত প্রমাণাদি ও প্রদর্শনী' : 'Evidence in Hand (Ready for Bench)'}</span></h4>
                  ${pack.evidence_in_hand?.length ? `
                    <ul class="clean-bullet-list">${pack.evidence_in_hand.map((e) => `<li><span class="bullet-dot green"></span><span>${escapeHtml(e)}</span></li>`).join('')}</ul>
                  ` : `<p class="empty-hint">${isBn ? 'কোনো তালিকা নেই।' : 'None noted.'}</p>`}
                </div>
                <div class="evidence-box risky">
                  <h4>${cIcon('alert', 13)} <span>${isBn ? 'অনুপস্থিত বা ঝুঁকিপূর্ণ নথি (প্রতিপক্ষ আক্রমণ করতে পারে)' : 'Missing Proofs / Opponent Targets'}</span></h4>
                  ${pack.evidence_missing_or_risky?.length ? `
                    <ul class="clean-bullet-list">${pack.evidence_missing_or_risky.map((e) => `<li><span class="bullet-dot red"></span><span>${escapeHtml(e)}</span></li>`).join('')}</ul>
                  ` : `<p class="empty-hint">${isBn ? 'কোনো তালিকা নেই।' : 'None noted.'}</p>`}
                </div>
              </div>

              <!-- Tactical Arguments Matrix -->
              <div class="tactics-arguments-grid">
                <div class="tactic-card opposing">
                  <h4>${cIcon('shield', 13)} <span>${isBn ? 'প্রতিপক্ষের সম্ভাব্য যুক্তি' : 'Anticipated Opposing Arguments'}</span></h4>
                  ${pack.anticipated_opposing_arguments?.length ? `
                    <ul class="clean-bullet-list">${pack.anticipated_opposing_arguments.map((a) => `<li><span class="bullet-dot amber"></span><span>${escapeHtml(a)}</span></li>`).join('')}</ul>
                  ` : `<p class="empty-hint">${isBn ? 'কোনো তথ্য নেই।' : 'None noted.'}</p>`}
                </div>
                <div class="tactic-card rebuttal">
                  <h4>${cIcon('zap', 13)} <span>${isBn ? 'আপনার তাৎক্ষণিক খণ্ডন ও জবাব' : 'Effective Statutory Rebuttals'}</span></h4>
                  ${pack.effective_counter_arguments?.length ? `
                    <ul class="clean-bullet-list">${pack.effective_counter_arguments.map((c) => `<li><span class="bullet-dot blue"></span><span>${escapeHtml(c)}</span></li>`).join('')}</ul>
                  ` : `<p class="empty-hint">${isBn ? 'কোনো তথ্য নেই।' : 'None noted.'}</p>`}
                </div>
              </div>

              <!-- Witness Cross-Examination Deck -->
              ${pack.witness_questions?.length ? `
                <div class="witness-deck-section">
                  <div class="section-badge-header">
                    <span class="sec-num">${pack.witness_questions.length}</span>
                    <h5 class="sec-title">${isBn ? 'জেরা ও সাক্ষ্য গ্রহণের প্রশ্নমালা' : 'Witness Cross-Examination & Trial Deck'}</h5>
                  </div>
                  <div class="witness-cards-grid">
                    ${pack.witness_questions.map((w, idx) => `
                      <div class="witness-question-card">
                        <div class="witness-target-tag">Target: <strong>${escapeHtml(w.target || 'Witness')}</strong> (#${idx + 1})</div>
                        <div class="witness-q-text">"${escapeHtml(w.question || '')}"</div>
                        <div class="witness-admission">
                          <span class="witness-meta-lbl">${cIcon('target', 11)} ${isBn ? 'লক্ষ্য:' : 'Goal:'}</span>
                          <span>${escapeHtml(w.intended_admission || '')}</span>
                        </div>
                        ${w.caution ? `
                          <div class="witness-caution">
                            <span class="witness-meta-lbl">${cIcon('alert', 11)} ${isBn ? 'সতর্কতা:' : 'Caution:'}</span>
                            <span>${escapeHtml(w.caution)}</span>
                          </div>
                        ` : ''}
                      </div>
                    `).join('')}
                  </div>
                </div>
              ` : ''}

              <!-- Closing Standing Prayer -->
              ${pack.closing_prayer ? `
                <div class="closing-prayer-card">
                  <div class="prayer-header">
                    <h4>${cIcon('quote', 13)} <span>${isBn ? 'বেঞ্চের সামনে সমাপনী মৌখিক প্রার্থনা (Verbal Submission)' : 'Stand-up Closing Submission & Prayer'}</span></h4>
                    <button type="button" class="button button-small button-outline" id="copy-prayer-btn" data-text="${escapeHtml(pack.closing_prayer)}">
                      ${cIcon('copy', 12)}
                      <span>${isBn ? 'প্রার্থনা কপি করুন' : 'Copy Prayer'}</span>
                    </button>
                  </div>
                  <blockquote class="prayer-quote">${escapeHtml(pack.closing_prayer)}</blockquote>
                </div>
              ` : ''}

              <!-- Footer Bridge Action -->
              <div class="pack-footer-actions">
                <button type="button" class="button button-secondary send-matter-prompt-btn" data-goal="${isBn ? 'এই হিয়ারিং প্যাকের তথ্যের আলোকে আজকের শুনানির জন্য একটি পূর্ণাঙ্গ লিখিত সাবমিশন বা পিটিশন ড্রাফট করুন।' : 'Draft a comprehensive written submission for court based on this hearing pack.'}">
                  ${cIcon('pen', 13)}
                  <span>${isBn ? 'Justor AI-তে ড্রাফট তৈরি করুন' : 'Draft Full Written Submission in Justor'}</span>
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
            <div class="intro-callout-badge">
              ${cIcon('scales', 12)}
              <span>CONTRADICTION DETECTOR & PROOF AUDIT</span>
            </div>
            <strong>${isBn ? 'মোকদ্দমা সঙ্গতি ও এভিডেন্স ম্যাট্রিক্স (Consistency & Proof Audit)' : 'Matter Consistency Checker & Evidence Matrix'}</strong>
            <p>${isBn 
              ? 'ফাইলের আরজি, নোটিশ, রশিদ ও ডিকটেশনের মধ্যে তারিখের অমিল, টাকার গরমিল বা দাগ নম্বরের অসঙ্গতি স্বয়ংক্রিয়ভাবে চিহ্নিত করুন এবং মামলায় প্রতিটি দাবি প্রমাণের জন্য প্রয়োজনীয় দলিলের শূন্যতা যাচাই করুন।'
              : 'Cross-audits all documents, pleadings, and notes for factual contradictions (dates, claim sums, CS/SA/RS Dag & Khatian numbers) and builds an evidentiary proof matrix.'}
            </p>
          </div>

          <div class="audit-controls-bar">
            <button type="button" class="button button-primary" id="run-consistency-btn">
              ${cIcon('search', 13)}
              <span>${isBn ? 'ফাইলের সঙ্গতি ও প্রমাণাদি অডিট চালান' : 'Run Consistency & Evidence Audit'}</span>
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
                  <h4>${cIcon('shield', 14)} <span>${isBn ? 'আইনি অডিট ফলাফল' : 'Litigation Record Audit Verdict'}</span></h4>
                  <p>${escapeHtml(audit.audit_summary || 'Audit complete.')}</p>
                </div>
              </div>

              <!-- Factual Contradictions Section -->
              <div class="contradictions-section">
                <div class="section-badge-header">
                  <span class="sec-num">${audit.contradictions?.length || 0}</span>
                  <h5 class="sec-title">${isBn ? 'চিহ্নিত তথ্যগত বৈপরীত্য ও অসঙ্গতি' : 'Detected Factual Contradictions'}</h5>
                </div>
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
                            <span class="source-lbl">${cIcon('doc', 11)} Source A:</span>
                            <p>${escapeHtml(c.source_a || '')}</p>
                          </div>
                          <div class="contra-source b">
                            <span class="source-lbl">${cIcon('doc', 11)} Source B:</span>
                            <p>${escapeHtml(c.source_b || '')}</p>
                          </div>
                        </div>
                        ${c.impact ? `<div class="contra-impact"><strong>${isBn ? 'আইনি প্রভাব:' : 'Courtroom Impact:'}</strong> ${escapeHtml(c.impact)}</div>` : ''}
                        ${c.remedy ? `<div class="contra-remedy"><strong>${isBn ? 'আইনজীবীর করণীয় প্রতিকার:' : 'Recommended Cure:'}</strong> ${escapeHtml(c.remedy)}</div>` : ''}
                      </div>
                    `).join('')}
                  </div>
                ` : `
                  <div class="no-contradictions-box">
                    <span>${cIcon('check', 14)} ${isBn ? 'নথি ও তথ্যের মধ্যে কোনো স্পষ্ট বৈপরীত্য পাওয়া যায়নি।' : 'No material factual contradictions detected across current matter entries.'}</span>
                  </div>
                `}
              </div>

              <!-- Evidentiary Proof Matrix Section -->
              <div class="evidence-matrix-section">
                <div class="section-badge-header">
                  <span class="sec-num">${audit.evidence_matrix?.length || 0}</span>
                  <h5 class="sec-title">${isBn ? 'দাবির উপাদান ও প্রমাণের ম্যাট্রিক্স (Evidence Matrix)' : 'Evidentiary Proof Matrix'}</h5>
                </div>
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
                  ${cIcon('search', 13)}
                  <span>${isBn ? 'Justor AI-তে সমাধানের কৌশল খুঁজুন' : 'Research Solutions in Justor AI'}</span>
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
            <div class="intro-callout-badge">
              ${cIcon('memo', 12)}
              <span>IRAC CITATION-GROUNDED MEMORANDA</span>
            </div>
            <strong>${isBn ? 'উৎস-সংযুক্ত লিগ্যাল মেমোরেন্ডাম জেনারেটর (IRAC Method)' : 'Source-Linked Legal Memorandum Generator'}</strong>
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
                ${cIcon('book', 11)}
                <span>${isBn ? 'এনআই অ্যাক্ট সিকিউরিটি চেক' : 'NI Act Security Cheque'}</span>
              </button>
              <button type="button" class="memo-tag-btn" data-q="${isBn ? 'অস্থায়ী নিষেধাজ্ঞার ৩টি মূল শর্ত (Prima Facie Case, Balance of Convenience, Irreparable Loss) কীভাবে পূরণ হবে?' : 'Whether the requirements of prima facie case and irreparable loss are satisfied for temporary injunction under Order 39 CPC?'}">
                ${cIcon('book', 11)}
                <span>${isBn ? 'অস্থায়ী নিষেধাজ্ঞার শর্ত' : 'Temporary Injunction Order 39'}</span>
              </button>
            </div>

            <div class="dictate-actions" style="margin-top:10px;">
              <button type="button" class="button button-primary" id="generate-memo-btn">
                ${cIcon('sparkle', 13)}
                <span>${isBn ? 'আনুষ্ঠানিক লিগ্যাল মেমো তৈরি করুন' : 'Generate Formal Legal Memo'}</span>
              </button>
            </div>
          </div>

          <div id="memo-loading" class="matter-loading-indicator" style="display:none;">
            <div class="pulse-spinner"></div>
            <span>${isBn ? 'আইনগত প্রশ্ন, বাংলাদেশ কোড ও সুপ্রিম কোর্টের নজির গবেষণা করে মেমোরেন্ডাম তৈরি হচ্ছে...' : 'Researching statutory provisions, DLR/BLD precedents, and drafting IRAC analysis...'}</span>
          </div>

          <!-- Existing Legal Memos -->
          <div class="legal-memos-list">
            <div class="memos-list-header">
              <span class="memos-count-badge">${memos.length} ${isBn ? 'টি সংরক্ষিত মেমো' : 'Memoranda On Record'}</span>
              <h4 class="memos-list-title">${isBn ? 'চেম্বার আইনি মেমোরেন্ডাম ভল্ট' : 'Chambers Legal Memoranda'}</h4>
            </div>
            ${memos.length === 0 ? `<div class="empty-state-card"><p class="empty-hint">${isBn ? 'এই মোকদ্দমায় এখনো কোনো আনুষ্ঠানিক লিগ্যাল মেমোরেন্ডাম তৈরি করা হয়নি। উপরে আইনি প্রশ্ন লিখে তৈরি করুন।' : 'No legal memoranda on record. Formulate an inquiry above to draft your first partner-grade opinion.'}</p></div>` : ''}
            ${memos.map((memo, idx) => `
              <div class="legal-memo-document">
                <!-- Top Work Product Classification Ribbon -->
                <div class="memo-watermark-band">
                  <div class="memo-ribbon-left">
                    <span class="memo-seal-icon">${cIcon('scales', 13)}</span>
                    <span class="memo-ribbon-tag">MEMORANDUM OF LAW #${idx + 1}</span>
                  </div>
                  <span class="memo-classification">CONFIDENTIAL ATTORNEY WORK PRODUCT · PRIVILEGED</span>
                </div>

                <!-- Formal Chambers Header Grid -->
                <div class="memo-metadata-box">
                  <div class="meta-item">
                    <span class="meta-label">TO:</span>
                    <span class="meta-value">Briefing Counsel & Senior Advocates</span>
                  </div>
                  <div class="meta-item">
                    <span class="meta-label">FROM:</span>
                    <span class="meta-value">Justor Chamber Practice Intelligence</span>
                  </div>
                  <div class="meta-item">
                    <span class="meta-label">MATTER:</span>
                    <span class="meta-value highlight">${escapeHtml(currentMatter.title)}</span>
                  </div>
                  <div class="meta-item">
                    <span class="meta-label">FORUM:</span>
                    <span class="meta-value">${escapeHtml(currentMatter.court || 'Supreme Court / District Judiciary')}</span>
                  </div>
                  <div class="meta-item">
                    <span class="meta-label">DATE:</span>
                    <span class="meta-value">${new Date(memo.createdAt).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                  </div>
                  <div class="meta-item">
                    <span class="meta-label">DOCKET:</span>
                    <span class="meta-value docket">${escapeHtml(currentMatter.caseNumber || 'Pre-Filing Advisory')}</span>
                  </div>
                </div>

                <!-- 01. Question Presented -->
                <div class="memo-section">
                  <div class="section-badge-header">
                    <span class="sec-num">01</span>
                    <h5 class="sec-title">${isBn ? 'আইনি প্রশ্ন (Question Presented)' : 'Question Presented'}</h5>
                  </div>
                  <p class="memo-lead-text">${escapeHtml(memo.question_presented)}</p>
                </div>

                <!-- 02. Executive Legal Conclusion -->
                ${memo.short_answer ? `
                  <div class="memo-section">
                    <div class="section-badge-header">
                      <span class="sec-num">02</span>
                      <h5 class="sec-title">${isBn ? 'নির্বাহী আইনি সিদ্ধান্ত (Executive Conclusion)' : 'Executive Legal Conclusion'}</h5>
                    </div>
                    <div class="memo-conclusion-card">
                      <p>${escapeHtml(memo.short_answer)}</p>
                    </div>
                  </div>
                ` : ''}

                <!-- 03. Statement of Material Facts -->
                ${memo.facts_considered?.length ? `
                  <div class="memo-section">
                    <div class="section-badge-header">
                      <span class="sec-num">03</span>
                      <h5 class="sec-title">${isBn ? 'মোকদ্দমার উপাদান ও প্রাসঙ্গিক ঘটনাবলী' : 'Statement of Material Facts'}</h5>
                    </div>
                    <ul class="memo-facts-list">
                      ${memo.facts_considered.map((f) => `
                        <li>
                          <span class="fact-bullet">•</span>
                          <span>${escapeHtml(f)}</span>
                        </li>
                      `).join('')}
                    </ul>
                  </div>
                ` : ''}

                <!-- 04. Governing Statutory Provisions -->
                ${memo.applicable_statutes?.length ? `
                  <div class="memo-section">
                    <div class="section-badge-header">
                      <span class="sec-num">04</span>
                      <h5 class="sec-title">${isBn ? 'প্রযোজ্য সংবিধিবদ্ধ বিধান ও ধারা (Bangladesh Code)' : 'Governing Statutory Provisions'}</h5>
                    </div>
                    <div class="statutes-callouts">
                      ${memo.applicable_statutes.map((st) => `
                        <div class="statute-callout interactive-citation" data-act="${escapeHtml(st.act || '')}" data-sec="${escapeHtml(st.section || '')}">
                          <div class="statute-callout-header">
                            <div class="auth-header-left">
                              <span class="auth-type-pill statute">STATUTE</span>
                              <strong class="auth-name">${escapeHtml(st.act || 'Act')} — ${escapeHtml(st.section || 'Section')}</strong>
                            </div>
                            <button type="button" class="btn-jump-provision" data-act="${escapeHtml(st.act || '')}" data-sec="${escapeHtml(st.section || '')}" data-passage="${escapeHtml(st.exact_passage || st.rule_of_law || '')}" title="Inspect verified statutory gazette text">
                              ${cIcon('book', 13)}
                              <span>${isBn ? 'পূর্ণ ধারা দেখুন' : 'Inspect Provision'}</span>
                              ${cIcon('external', 11)}
                            </button>
                          </div>
                          <p class="auth-body-text">${escapeHtml(st.rule_of_law || '')}</p>
                        </div>
                      `).join('')}
                    </div>
                  </div>
                ` : ''}

                <!-- 05. Binding Supreme Court Precedents -->
                ${memo.relevant_precedents?.length ? `
                  <div class="memo-section">
                    <div class="section-badge-header">
                      <span class="sec-num">05</span>
                      <h5 class="sec-title">${isBn ? 'সুপ্রিম কোর্টের নির্দেশক নজির (DLR / BLD / BLC)' : 'Binding Precedents & Case Law'}</h5>
                    </div>
                    <div class="precedents-callouts">
                      ${memo.relevant_precedents.map((pr) => `
                        <div class="precedent-callout interactive-citation" data-act="Supreme Court of Bangladesh" data-sec="${escapeHtml(pr.case_citation || '')}">
                          <div class="precedent-callout-header">
                            <div class="auth-header-left">
                              <span class="auth-type-pill precedent">REPORTED PRECEDENT</span>
                              <strong class="auth-name law-report">${escapeHtml(pr.case_citation || 'Case Law')}</strong>
                            </div>
                            <button type="button" class="btn-jump-provision" data-act="Supreme Court of Bangladesh" data-sec="${escapeHtml(pr.case_citation || '')}" data-passage="${escapeHtml(pr.exact_passage || pr.principle_held || '')}" title="View judicial holding">
                              ${cIcon('gavel', 13)}
                              <span>${isBn ? 'নজির দেখুন' : 'Inspect Precedent'}</span>
                              ${cIcon('external', 11)}
                            </button>
                          </div>
                          <p class="auth-body-text holding">${escapeHtml(pr.principle_held || '')}</p>
                        </div>
                      `).join('')}
                    </div>
                  </div>
                ` : ''}

                <!-- 06. IRAC Legal Analysis & Merits -->
                ${memo.irac_analysis?.application ? `
                  <div class="memo-section">
                    <div class="section-badge-header">
                      <span class="sec-num">06</span>
                      <h5 class="sec-title">${isBn ? 'আইনি বিশ্লেষণ ও প্রয়োগ (IRAC Method)' : 'IRAC Legal Analysis & Merits'}</h5>
                    </div>
                    <div class="irac-card-elevated">
                      <div class="irac-item issue">
                        <div class="irac-item-header">
                          <span class="irac-tag">ISSUE</span>
                          <span class="irac-sub">Legal Question Identified</span>
                        </div>
                        <p>${escapeHtml(memo.irac_analysis.issue || memo.question_presented)}</p>
                      </div>
                      <div class="irac-item rule">
                        <div class="irac-item-header">
                          <span class="irac-tag">RULE</span>
                          <span class="irac-sub">Governing Doctrine & Standard</span>
                        </div>
                        <p>${escapeHtml(memo.irac_analysis.rule || 'Applicable statutory rules and Supreme Court ratio decidendi.')}</p>
                      </div>
                      <div class="irac-item application">
                        <div class="irac-item-header">
                          <span class="irac-tag">APPLICATION</span>
                          <span class="irac-sub">Synthesis to Matter Record</span>
                        </div>
                        <div class="irac-prose">${escapeHtml(memo.irac_analysis.application || '')}</div>
                      </div>
                      <div class="irac-item conclusion">
                        <div class="irac-item-header">
                          <span class="irac-tag">CONCLUSION</span>
                          <span class="irac-sub">Definitive Finding</span>
                        </div>
                        <p>${escapeHtml(memo.irac_analysis.conclusion || memo.short_answer || '')}</p>
                      </div>
                    </div>
                  </div>
                ` : ''}

                <!-- 07. Procedural Risks & Counterarguments -->
                ${memo.counterarguments_and_risks?.length ? `
                  <div class="memo-section">
                    <div class="section-badge-header">
                      <span class="sec-num">07</span>
                      <h5 class="sec-title">${isBn ? 'প্রতিপক্ষের সম্ভাব্য যুক্তি ও পদ্ধতিগত ঝুঁকি' : 'Anticipated Counterarguments & Procedural Risks'}</h5>
                    </div>
                    <ul class="memo-risks-list">
                      ${memo.counterarguments_and_risks.map((cr) => `
                        <li class="risk-item">
                          <span class="risk-indicator"></span>
                          <span>${escapeHtml(cr)}</span>
                        </li>
                      `).join('')}
                    </ul>
                  </div>
                ` : ''}

                <!-- 08. Practical Recommendation -->
                ${memo.final_recommendation ? `
                  <div class="memo-section recommendation">
                    <div class="section-badge-header">
                      <span class="sec-num">08</span>
                      <h5 class="sec-title">${isBn ? 'চেম্বার কর্মপরিকল্পনা ও পরামর্শ' : 'Practical Litigation Strategy & Next Steps'}</h5>
                    </div>
                    <p class="recommendation-text">${escapeHtml(memo.final_recommendation)}</p>
                  </div>
                ` : ''}

                <!-- 09. Primary Source Citations -->
                ${memo.source_citations?.length ? `
                  <div class="memo-section sources">
                    <div class="section-badge-header">
                      <span class="sec-num">09</span>
                      <h5 class="sec-title">${isBn ? 'যাচাইকৃত মূল উদ্ধৃতি ও দলিলসূত্র' : 'Primary Source Passages & Citations'}</h5>
                    </div>
                    <div class="sources-snippets">
                      ${memo.source_citations.map((src) => {
                        const actName = src.act || src.title || 'Statute';
                        const secRef = src.section || src.title || '';
                        return `
                        <div class="source-snippet-card interactive-citation" data-act="${escapeHtml(actName)}" data-sec="${escapeHtml(secRef)}">
                          <div class="source-snippet-header">
                            <div class="src-title-group">
                              <span class="quote-glyph">“</span>
                              <strong class="src-title">${escapeHtml(src.title || 'Citation')}</strong>
                            </div>
                            <button type="button" class="btn-jump-provision" data-act="${escapeHtml(actName)}" data-sec="${escapeHtml(secRef)}" data-passage="${escapeHtml(src.passage || '')}" title="Open canonical source passage">
                              ${cIcon('external', 13)}
                              <span>${isBn ? 'মূল ধারা দেখুন' : 'View Source'}</span>
                            </button>
                          </div>
                          <blockquote class="src-passage">${escapeHtml(src.passage || '')}</blockquote>
                        </div>
                      `}).join('')}
                    </div>
                  </div>
                ` : ''}

                <!-- Memo Actions -->
                <div class="memo-action-bar-elevated">
                  <button type="button" class="button button-small button-outline copy-memo-btn" data-id="${memo.id}">
                    ${cIcon('copy', 14)} <span>${isBn ? 'মেমো কপি করুন' : 'Copy Memorandum'}</span>
                  </button>
                  <button type="button" class="button button-small button-primary send-matter-prompt-btn" data-goal="${isBn ? `এই লিগ্যাল মেমোরেন্ডামের সুনির্দিষ্ট আইনি ভিত্তি ও নজিরের আলোকে আদালতের জন্য একটি আনুষ্ঠানিক আরজি বা পিটিশন ড্রাফট করুন:\n\nবিষয়: ${escapeHtml(memo.question_presented)}\n\nসিদ্ধান্ত: ${escapeHtml(memo.short_answer || '')}\n\nআইনি বিশ্লেষণ: ${escapeHtml(memo.irac_analysis?.application || '')}` : `Draft formal court pleading/petition strictly grounded in this legal memo:\n\nQuestion: ${escapeHtml(memo.question_presented)}\n\nShort Answer: ${escapeHtml(memo.short_answer || '')}\n\nIRAC Analysis: ${escapeHtml(memo.irac_analysis?.application || '')}`}">
                    ${cIcon('pen', 14)} <span>${isBn ? 'Justor AI-তে ড্রাফট করুন' : 'Draft Pleading in Justor'}</span>
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
              <div class="vault-header-info">
                <div class="vault-title-wrap">
                  ${cIcon('folder', 18)}
                  <h3 class="vault-title">${escapeHtml(currentMatter.title)}</h3>
                </div>
                <div class="vault-meta-row">
                  <span class="vault-meta-item">${cIcon('user', 12)} <span>${isBn ? 'মক্কেল:' : 'Client:'} <strong>${escapeHtml(currentMatter.clientName || 'Unspecified')}</strong></span></span>
                  <span class="vault-meta-item">${cIcon('scales', 12)} <span>${isBn ? 'মোকদ্দমা:' : 'Type:'} <strong>${escapeHtml(currentMatter.matterType || 'General Litigation')}</strong></span></span>
                  ${currentMatter.court ? `<span class="vault-meta-item">${cIcon('gavel', 12)} <span>${escapeHtml(currentMatter.court)}</span></span>` : ''}
                </div>
              </div>
              <button type="button" class="button button-secondary button-small" id="edit-matter-title-btn">
                ${cIcon('pen', 12)}
                <span>${isBn ? 'বিবরণ সম্পাদনা' : 'Edit Details'}</span>
              </button>
            </div>

            <div class="vault-stats-grid">
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.notes.length}</span>
                <span class="stat-lbl">${cIcon('mic', 12)} ${isBn ? 'ডিকটেশন নোট' : 'Dictation Notes'}</span>
              </div>
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.consultations.length}</span>
                <span class="stat-lbl">${cIcon('headphones', 12)} ${isBn ? 'পরামর্শ অডিও' : 'Consultations'}</span>
              </div>
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.summaries.length}</span>
                <span class="stat-lbl">${cIcon('gavel', 12)} ${isBn ? 'রায়ের সারসংক্ষেপ' : 'Judgment Briefs'}</span>
              </div>
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.chronology?.timeline?.length || 0}</span>
                <span class="stat-lbl">${cIcon('calendar', 12)} ${isBn ? 'কালপঞ্জি ঘটনা' : 'Timeline Events'}</span>
              </div>
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.hearingPack ? '1' : '0'}</span>
                <span class="stat-lbl">${cIcon('target', 12)} ${isBn ? 'হিয়ারিং প্যাক' : 'Hearing Pack'}</span>
              </div>
              <div class="vault-stat-box">
                <span class="stat-num">${currentMatter.legalMemos?.length || 0}</span>
                <span class="stat-lbl">${cIcon('memo', 12)} ${isBn ? 'লিগ্যাল মেমো' : 'Legal Memos'}</span>
              </div>
            </div>

            <div class="vault-rag-bridge">
              <div class="bridge-header">
                ${cIcon('sparkle', 14)}
                <h4>${isBn ? 'Justor AI দিয়ে মোকদ্দমার খসড়া ও আইনি গবেষণা' : 'Matter-Aware Legal RAG Bridge'}</h4>
              </div>
              <p>${isBn 
                ? 'এই মোকদ্দমার সকল তথ্য, কালপঞ্জি ও প্রমাণ সরাসরি Justor AI-এর আরএজি সার্চে যুক্ত করে নোটিশ, জামিন পিটিশন বা সিভিল রিভিশন ড্রাফট করুন।' 
                : 'Pre-infuses this matter\'s entire facts, chronology, and evidence matrix directly into Justor AI\'s Bangladesh legal RAG engine.'}
              </p>
              <div class="bridge-actions">
                <button type="button" class="button button-primary send-matter-prompt-btn" data-goal="${isBn ? 'এই মোকদ্দমার তথ্যের ভিত্তিতে একটি আনুষ্ঠানিক লিগ্যাল নোটিশ বা আরজি ড্রাফট করুন।' : 'Draft a formal legal notice or plaint based on this matter file.'}">
                  ${cIcon('pen', 13)}
                  <span>${isBn ? 'লিগ্যাল নোটিশ ড্রাফট করুন' : 'Draft Legal Demand Notice'}</span>
                </button>
                <button type="button" class="button button-secondary send-matter-prompt-btn" data-goal="${isBn ? 'দেওয়ানি কার্যবিধির অর্ডার ৩৯ বা ফৌজদারি কার্যবিধির ৪৯৮ ধারায় সুপ্রিম কোর্টের নজিরসহ প্রার্থনার গ্রাউন্ডস বের করুন।' : 'Research strongest grounds and Supreme Court of Bangladesh precedents for bail or injunction.'}">
                  ${cIcon('search', 13)}
                  <span>${isBn ? 'জামিন / নিষেধাজ্ঞার নজির খুঁজুন' : 'Research Grounds & Case Law'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      `;
    }

    // ── 9. WHATSAPP CHAMBER BRIDGE & CLIENT AUTOMATION ──
    if (currentTab === 'whatsapp') {
      const chamberPhone = localStorage.getItem('justor_chamber_phone') || '+8801700000000';
      const cleanPhoneDigits = chamberPhone.replace(/[^0-9]/g, '');
      const waLink = `https://wa.me/${cleanPhoneDigits}?text=STATUS%20${encodeURIComponent(currentMatter.id)}`;
      const clientSmsBn = `সম্মানিত মক্কেল ${currentMatter.clientName || 'ক্লায়েন্ট'}, আপনার মোকদ্দমা "${currentMatter.title}"-এর পরবর্তী শুনানির তারিখ ও তথ্যের জন্য আমাদের চেম্বার হোয়াটসঅ্যাপে ক্লিক করুন অথবা STATUS ${currentMatter.id} লিখে পাঠান: ${waLink}`;
      const clientSmsEn = `Dear Client ${currentMatter.clientName || ''}, to check the next court date and verified updates for "${currentMatter.title}", send STATUS ${currentMatter.id} to our Chamber WhatsApp: ${waLink}`;

      return `
        <div class="matter-tab-content">
          <div class="matter-intro-callout">
            <div class="intro-callout-badge">
              ${cIcon('whatsapp', 13)}
              <span>CHAMBERS 24/7 CLIENT TRACKING & DICTATION</span>
            </div>
            <strong>${isBn ? 'আইনজীবী চেম্বার হোয়াটসঅ্যাপ ব্রিজ (Lawyer Chamber WhatsApp Gateway)' : 'Lawyer Chamber WhatsApp Gateway & Client Automation'}</strong>
            <p>${isBn 
              ? 'মক্কেলদের প্রতিদিনের ঘনঘন ফোনকল থেকে মুক্তি এবং আদালত চত্বর থেকে তাৎক্ষণিক ভয়েস ডিকটেশন সরাসরি মোকদ্দমা ফাইলে সংরক্ষণ করার সুপ্রিম কোর্ট ও জজ কোর্ট স্ট্যান্ডার্ড অটোমেশন।'
              : 'Free your chamber from repetitive client status phone calls. Give clients verified 24/7 automated hearing updates and dictate voice notes on-the-go directly into this active matter vault.'}
            </p>
          </div>

          <!-- Section 1: Active Matter Client WhatsApp Hub -->
          <div class="dictaphone-composer-card" style="margin-bottom: 24px;">
            <div class="dictaphone-input-header">
              <span class="composer-label">
                ${cIcon('user', 14)}
                <span>${isBn ? '১. এই মোকদ্দমার মক্কেল হোয়াটসঅ্যাপ ট্র্যাকিং লিংক' : '1. Active Client WhatsApp Tracking Link'}</span>
              </span>
              <span style="font-size: 11.5px; color: #25D366; font-weight: 700; background: rgba(37, 211, 102, 0.1); padding: 2px 8px; border-radius: 4px; border: 1px solid rgba(37, 211, 102, 0.25);">
                LIVE AUTO-RESPONDER READY
              </span>
            </div>

            <div style="background: #FAF7F0; border: 1px solid #E2D9C8; border-radius: 8px; padding: 16px; margin: 12px 0;">
              <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; margin-bottom: 14px;">
                <div>
                  <small style="color: #64748B; display: block; font-size: 11px; text-transform: uppercase;">মোকদ্দমা রেফারেন্স / Case ID</small>
                  <strong style="color: #0F172A; font-family: monospace; font-size: 14px;">${escapeHtml(currentMatter.id)}</strong>
                </div>
                <div>
                  <small style="color: #64748B; display: block; font-size: 11px; text-transform: uppercase;">মক্কেলের নাম / Client</small>
                  <strong style="color: #0F172A; font-size: 13.5px;">${escapeHtml(currentMatter.clientName || 'General Client')}</strong>
                </div>
                <div>
                  <small style="color: #64748B; display: block; font-size: 11px; text-transform: uppercase;">আদালতের এখতিয়ার / Court</small>
                  <strong style="color: #0F172A; font-size: 13.5px;">${escapeHtml(currentMatter.court || 'বিজ্ঞ আদালত')}</strong>
                </div>
                <div>
                  <small style="color: #64748B; display: block; font-size: 11px; text-transform: uppercase;">চেম্বার হোয়াটসঅ্যাপ নম্বর</small>
                  <strong style="color: #128C7E; font-size: 13.5px;">${escapeHtml(chamberPhone)}</strong>
                </div>
              </div>

              <!-- 1-Click Link Row -->
              <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center; background: #FFFFFF; border: 1px solid #CBD5E1; padding: 10px 12px; border-radius: 6px;">
                <code style="flex: 1; color: #0F172A; font-size: 12px; word-break: break-all;">${waLink}</code>
                <button type="button" class="button button-small btn-wa-copy" data-copy="${escapeHtml(waLink)}" style="display: inline-flex; align-items: center; gap: 6px;">
                  ${cIcon('copy', 13)}
                  <span>${isBn ? 'লিংক কপি করুন' : 'Copy Link'}</span>
                </button>
                <button type="button" class="button button-small" id="btn-wa-launch-web" style="background: #25D366; color: #0F172A; font-weight: 700; border: none; display: inline-flex; align-items: center; gap: 6px;">
                  ${cIcon('external', 13)}
                  <span>${isBn ? 'হোয়াটসঅ্যাপে খুলুন' : 'Open WhatsApp'}</span>
                </button>
              </div>

              <!-- Ready SMS Copy Buttons -->
              <div style="display: flex; gap: 10px; margin-top: 12px; flex-wrap: wrap;">
                <button type="button" class="button button-small button-outline btn-wa-copy" data-copy="${escapeHtml(clientSmsBn)}">
                  📋 ${isBn ? 'মক্কেলকে পাঠানোর বাংলা এসএমএস কপি' : 'Copy Bengali SMS for Client'}
                </button>
                <button type="button" class="button button-small button-outline btn-wa-copy" data-copy="${escapeHtml(clientSmsEn)}">
                  📋 ${isBn ? 'ইংরেজি এসএমএস কপি' : 'Copy English SMS'}
                </button>
              </div>
            </div>
          </div>

          <!-- Section 2: Court Corridor Mobile Dictation & In-Tab Simulator -->
          <div class="dictaphone-composer-card" style="margin-bottom: 24px;">
            <div class="dictaphone-input-header">
              <span class="composer-label">
                ${cIcon('mic', 14)}
                <span>${isBn ? '২. আদালত চত্বর থেকে মোবাইল ডিকটেশন ও লাইভ টেস্ট' : '2. Court Corridor Mobile Dictation & Live Testing'}</span>
              </span>
              <button type="button" class="button button-small button-secondary" id="btn-wa-open-full-sim" style="display: inline-flex; align-items: center; gap: 6px;">
                ${cIcon('sparkle', 13)}
                <span>${isBn ? 'সম্পূর্ণ মোবাইল সিমুলেটর খুলুন' : 'Launch Full WhatsApp Simulator'}</span>
              </button>
            </div>

            <p style="font-size: 13px; color: #475569; margin: 8px 0 14px; line-height: 1.5;">
              ${isBn 
                ? `সুপ্রিম কোর্ট বা জজ কোর্ট থেকে বের হয়ে আপনার চেম্বার হোয়াটসঅ্যাপ নম্বরে <code>#${escapeHtml(currentMatter.id)}</code> দিয়ে মেসেজ বা অডিও পাঠান। Justor AI সাথে সাথে নোটটি এই মোকদ্দমা ফাইলে সংরক্ষণ করে দেবে।`
                : `Dictate or message directly from the court corridor. Start your message or voice note with <code>#${escapeHtml(currentMatter.id)}</code> to automatically transcribe and log into this matter file.`}
            </p>

            <div style="display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px;">
              <button type="button" class="button button-small button-outline btn-wa-chip" data-query="What needs my attention?">🌅 ${isBn ? 'সকাল ৮:০০টার ব্রিফিং' : 'Morning Briefing'}</button>
              <button type="button" class="button button-small button-outline btn-wa-chip" data-query="Rahim matter—hearing Sunday. Opposite party submitted this affidavit.">⚡ ${isBn ? 'অটোনোমাস ইনটেক' : 'Autonomous Intake'}</button>
              <button type="button" class="button button-small button-outline btn-wa-chip" data-query="DEADLINES">⏳ ${isBn ? 'তামাদি অ্যালার্ট' : 'Deadlines'}</button>
              <button type="button" class="button button-small button-outline btn-wa-chip" data-query="CAUSELIST">📅 ${isBn ? 'কার্যতালিকা' : 'Cause List'}</button>
              <button type="button" class="button button-small button-outline btn-wa-chip" data-query="PRECEDENT 138 NI Act notice limitation">📚 ${isBn ? 'নজির (PRECEDENT)' : 'Precedent'}</button>
              <button type="button" class="button button-small button-outline btn-wa-chip" data-query="#${currentMatter.id} অন্তর্বর্তীকালীন জামিন মঞ্জুর, আগামী ২০ নভেম্বর জবাব দাখিল।">🎙️ ${isBn ? 'কোর্ট ডিকটেশন (#)' : 'Corridor Dictation'}</button>
              <button type="button" class="button button-small button-outline btn-wa-chip" data-query="STATUS ${currentMatter.id}">📂 STATUS ${currentMatter.id}</button>
              <button type="button" class="button button-small button-outline btn-wa-chip" data-query="DOCS ${currentMatter.id}">📑 ${isBn ? 'দলিল চেকলিস্ট' : 'Evidence Docs'}</button>
            </div>

            <div style="display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap;">
              <input type="text" id="wa-tab-query-input" value="STATUS ${currentMatter.id}" style="flex: 1; min-width: 200px; padding: 10px 14px; border: 1px solid #CBD5E1; border-radius: 6px; font-size: 13.5px;" placeholder="Type WhatsApp message to test..." />
              <button type="button" class="button button-primary" id="btn-wa-run-query" style="display: inline-flex; align-items: center; gap: 6px;">
                ${cIcon('search', 13)}
                <span>${isBn ? 'টেস্ট কোয়েরি চালান' : 'Send Test Query'}</span>
              </button>
              <button type="button" class="button" id="btn-wa-trigger-morning-brief" style="background: rgba(245, 158, 11, 0.15); color: #D97706; border: 1px solid rgba(245, 158, 11, 0.35); font-weight: 600; display: inline-flex; align-items: center; gap: 6px;">
                <span>🌅 ${isBn ? 'সকাল ৮:০০টার ব্রিফিং দেখুন' : 'Trigger 8:00 AM Brief'}</span>
              </button>
            </div>

            <!-- Live Response Container -->
            <div id="wa-tab-response-box" style="display: none; background: #0F172A; color: #F8FAFC; padding: 16px 20px; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 13px; line-height: 1.6; border: 1px solid rgba(37, 211, 102, 0.3);">
              <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 8px; margin-bottom: 12px;">
                <span style="color: #25D366; font-weight: 700; display: inline-flex; align-items: center; gap: 6px;">
                  ${cIcon('whatsapp', 14)} Justor WhatsApp Bot Live Output
                </span>
                <button type="button" id="btn-wa-save-tab-note" class="button button-small" style="background: rgba(56, 189, 248, 0.15); color: #38BDF8; border: 1px solid rgba(56, 189, 248, 0.3); font-size: 11.5px; padding: 3px 8px;">
                  📥 ${isBn ? 'এই ফলাফল মোকদ্দমা নোটে যুক্ত করুন' : 'File to Matter Notes'}
                </button>
              </div>
              <div id="wa-tab-response-text" style="white-space: pre-wrap;"></div>
            </div>
          </div>

          <!-- Section 3: Official Webhook & Chamber Business Number Setup -->
          <div class="dictaphone-composer-card">
            <div class="dictaphone-input-header">
              <span class="composer-label">
                ${cIcon('sparkle', 14)}
                <span>${isBn ? '৩. চেম্বার হোয়াটসঅ্যাপ বিজনেস ওয়েবহুক সেটআপ (Meta Cloud API / Twilio)' : '3. Official Chamber WhatsApp Business Webhook Setup'}</span>
              </span>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-top: 12px;">
              <!-- Meta Setup Card -->
              <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px;">
                <strong style="color: #0F172A; display: block; font-size: 13.5px; margin-bottom: 4px;">Meta WhatsApp Cloud API (Recommended)</strong>
                <p style="font-size: 12px; color: #64748B; margin-bottom: 10px;">Meta-র অফিসিয়াল বিনামূল্যে প্রতি মাসে ১,০০০ কথোপকথন সুবিধা:</p>
                <div style="font-size: 11.5px; margin-bottom: 6px;">
                  <span style="color: #64748B;">Callback URL:</span>
                  <div style="display: flex; gap: 4px; margin-top: 2px;">
                    <input type="text" readonly value="https://api.justor.ai/api/whatsapp/meta" style="flex: 1; padding: 4px 8px; font-size: 11px; font-family: monospace; border: 1px solid #CBD5E1; border-radius: 4px;" />
                    <button type="button" class="button button-small btn-wa-copy" data-copy="https://api.justor.ai/api/whatsapp/meta">Copy</button>
                  </div>
                </div>
                <div style="font-size: 11.5px;">
                  <span style="color: #64748B;">Verify Token:</span>
                  <div style="display: flex; gap: 4px; margin-top: 2px;">
                    <input type="text" readonly value="justor_wa_verify_2026" style="flex: 1; padding: 4px 8px; font-size: 11px; font-family: monospace; border: 1px solid #CBD5E1; border-radius: 4px;" />
                    <button type="button" class="button button-small btn-wa-copy" data-copy="justor_wa_verify_2026">Copy</button>
                  </div>
                </div>
              </div>

              <!-- Twilio Setup Card -->
              <div style="background: #F8FAFC; border: 1px solid #E2E8F0; padding: 14px; border-radius: 8px;">
                <strong style="color: #0F172A; display: block; font-size: 13.5px; margin-bottom: 4px;">Twilio WhatsApp Sandbox</strong>
                <p style="font-size: 12px; color: #64748B; margin-bottom: 10px;">দ্রুত টেস্টিং ও এসএমএস ট্রায়ালের জন্য:</p>
                <div style="font-size: 11.5px; margin-bottom: 6px;">
                  <span style="color: #64748B;">Webhook URL (HTTP POST):</span>
                  <div style="display: flex; gap: 4px; margin-top: 2px;">
                    <input type="text" readonly value="https://api.justor.ai/api/whatsapp/twilio" style="flex: 1; padding: 4px 8px; font-size: 11px; font-family: monospace; border: 1px solid #CBD5E1; border-radius: 4px;" />
                    <button type="button" class="button button-small btn-wa-copy" data-copy="https://api.justor.ai/api/whatsapp/twilio">Copy</button>
                  </div>
                </div>
                <div style="margin-top: 10px;">
                  <label style="font-size: 11.5px; color: #64748B; display: block;">চেম্বার হোয়াটসঅ্যাপ নম্বর সেভ করুন:</label>
                  <div style="display: flex; gap: 6px; margin-top: 3px;">
                    <input type="text" id="wa-chamber-phone-input" value="${escapeHtml(chamberPhone)}" placeholder="+88017..." style="flex: 1; padding: 4px 8px; font-size: 12px; border: 1px solid #CBD5E1; border-radius: 4px;" />
                    <button type="button" class="button button-small" id="btn-save-chamber-phone">Save</button>
                  </div>
                </div>
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
              dictateMicToggle.innerHTML = `<span class="pulse-dot"></span><span>${isBn ? 'রেকর্ড হচ্ছে...' : 'Recording...'}</span>`;
            } catch (err) {
              console.warn('Speech start error:', err);
            }
          } else {
            if (recognition) recognition.stop();
            isRec = false;
            dictateMicToggle.classList.remove('is-recording');
            dictateMicToggle.innerHTML = `${cIcon('mic', 13)} <span>${isBn ? 'ভয়েস টাইপিং' : 'Start Speaking'}</span>`;
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
          filenameSpan.textContent = `${selectedFile.name} (${(selectedFile.size / (1024 * 1024)).toFixed(1)} MB)`;
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
          btn.innerHTML = `${cIcon('check', 12)} <span>${isBn ? 'কপি সম্পন্ন' : 'Copied!'}</span>`;
          setTimeout(() => {
            btn.innerHTML = `${cIcon('copy', 12)} <span>${isBn ? 'প্রার্থনা কপি করুন' : 'Copy Prayer'}</span>`;
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
            btn.innerHTML = `${cIcon('check', 14)} <span>${isBn ? 'কপি সম্পন্ন' : 'Copied!'}</span>`;
            setTimeout(() => {
              btn.innerHTML = `${cIcon('copy', 14)} <span>${isBn ? 'মেমো কপি করুন' : 'Copy Memorandum'}</span>`;
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

    // ── Tab 9: WhatsApp Chamber Bridge Handlers ──
    if (currentTab === 'whatsapp') {
      // Copy buttons
      backdrop.querySelectorAll<HTMLButtonElement>('.btn-wa-copy').forEach((btn) => {
        btn.addEventListener('click', () => {
          const text = btn.getAttribute('data-copy') || '';
          if (text) {
            navigator.clipboard.writeText(text);
            const orig = btn.innerHTML;
            btn.innerHTML = `${cIcon('check', 13)} <span>${isBn ? 'কপি সম্পন্ন' : 'Copied!'}</span>`;
            setTimeout(() => { btn.innerHTML = orig; }, 1800);
          }
        });
      });

      // Launch WhatsApp Web
      backdrop.querySelector('#btn-wa-launch-web')?.addEventListener('click', () => {
        const waUrl = `https://api.whatsapp.com/send?text=${encodeURIComponent(`STATUS ${currentMatter.id}`)}`;
        window.open(waUrl, '_blank');
      });

      // Launch full WhatsApp modal
      backdrop.querySelector('#btn-wa-open-full-sim')?.addEventListener('click', async () => {
        const { openWhatsAppModal } = await import('./whatsapp-modal');
        openWhatsAppModal(currentMatter);
      });

      // Save chamber phone
      backdrop.querySelector('#btn-save-chamber-phone')?.addEventListener('click', () => {
        const phoneInput = backdrop.querySelector('#wa-chamber-phone-input') as HTMLInputElement;
        if (phoneInput && phoneInput.value.trim()) {
          localStorage.setItem('justor_chamber_phone', phoneInput.value.trim());
          const saveBtn = backdrop.querySelector('#btn-save-chamber-phone') as HTMLButtonElement;
          if (saveBtn) {
            saveBtn.textContent = 'Saved!';
            setTimeout(() => { saveBtn.textContent = 'Save'; }, 1500);
          }
          renderModalContent();
        }
      });

      // Quick chips
      const queryInput = backdrop.querySelector('#wa-tab-query-input') as HTMLInputElement;
      const runQueryBtn = backdrop.querySelector('#btn-wa-run-query') as HTMLButtonElement;
      const responseBox = backdrop.querySelector('#wa-tab-response-box') as HTMLElement;
      const responseText = backdrop.querySelector('#wa-tab-response-text') as HTMLElement;

      backdrop.querySelectorAll<HTMLButtonElement>('.btn-wa-chip').forEach((chip) => {
        chip.addEventListener('click', () => {
          const q = chip.getAttribute('data-query');
          if (q && queryInput) {
            queryInput.value = q;
            runQueryBtn?.click();
          }
        });
      });

      // Run live test query
      runQueryBtn?.addEventListener('click', async () => {
        const query = queryInput?.value.trim();
        if (!query) return;

        runQueryBtn.disabled = true;
        runQueryBtn.innerHTML = `<span>${isBn ? 'প্রসেসিং হচ্ছে...' : 'Processing...'}</span>`;
        if (responseBox) responseBox.style.display = 'block';
        if (responseText) responseText.innerHTML = `<em>Justor WhatsApp Gateway responding...</em>`;

        try {
          const chamberPhone = localStorage.getItem('justor_chamber_phone') || '+8801700000000';
          const resp = await fetch('/api/whatsapp/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              message: query,
              sender: chamberPhone,
              matter_id: currentMatter.id
            })
          });

          if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
          const data = await resp.json();
          const reply = data.reply || 'কোনো উত্তর পাওয়া যায়নি।';

          if (responseText) {
            responseText.textContent = reply;
          }
        } catch (err: any) {
          if (responseText) {
            responseText.textContent = `Error connecting to WhatsApp endpoint: ${err.message || err}`;
          }
        } finally {
          runQueryBtn.disabled = false;
          runQueryBtn.innerHTML = `${cIcon('search', 13)} <span>${isBn ? 'টেস্ট কোয়েরি চালান' : 'Send Test Query'}</span>`;
        }
      });

      // Trigger 8:00 AM Morning Brief
      backdrop.querySelector('#btn-wa-trigger-morning-brief')?.addEventListener('click', async () => {
        const briefBtn = backdrop.querySelector('#btn-wa-trigger-morning-brief') as HTMLButtonElement;
        if (briefBtn) {
          briefBtn.disabled = true;
          briefBtn.innerHTML = `<span>${isBn ? 'ব্রিফিং তৈরি হচ্ছে...' : 'Generating Brief...'}</span>`;
        }
        if (responseBox) responseBox.style.display = 'block';
        if (responseText) responseText.innerHTML = `<em>${isBn ? 'সকাল ৮:০০টার চেম্বার ব্রিফিং তৈরি হচ্ছে...' : 'Generating 8:00 AM Chamber Briefing...'}</em>`;

        try {
          const chamberPhone = localStorage.getItem('justor_chamber_phone') || '+8801700000000';
          const resp = await fetch('/api/whatsapp/send-morning-brief', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: chamberPhone })
          });
          const data = await resp.json();
          if (resp.ok && data.brief) {
            if (responseText) responseText.textContent = data.brief;
          } else {
            if (responseText) responseText.textContent = 'ব্রিফিং তৈরিতে ত্রুটি হয়েছে।';
          }
        } catch (e: any) {
          if (responseText) responseText.textContent = `নেটওয়ার্ক ত্রুটি: ${e.message}`;
        } finally {
          if (briefBtn) {
            briefBtn.disabled = false;
            briefBtn.innerHTML = `<span>🌅 ${isBn ? 'সকাল ৮:০০টার ব্রিফিং দেখুন' : 'Trigger 8:00 AM Brief'}</span>`;
          }
        }
      });

      // Save tab response to notes
      backdrop.querySelector('#btn-wa-save-tab-note')?.addEventListener('click', () => {
        const text = responseText?.textContent || '';
        if (!text) return;

        if (!currentMatter.notes) currentMatter.notes = [];
        currentMatter.notes.unshift({
          id: 'note_' + Date.now(),
          rawText: `[WhatsApp Chamber Gateway Output]\n${text}`,
          data: {
            matter_type: currentMatter.matterType,
            dispute_summary: text.slice(0, 160),
            next_actions: ['WhatsApp communication logged to chamber vault']
          },
          createdAt: new Date().toISOString()
        });

        saveStoredMatters(matters);
        void syncMatterToCloud(currentMatter);
        alert(isBn ? 'নোটটি সফলভাবে এই মোকদ্দমা ফাইলে সংরক্ষিত হয়েছে!' : 'Successfully filed into matter notes!');
      });
    }
  };

  renderModalContent();
  document.body.appendChild(backdrop);
}
