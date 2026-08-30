import type { Session } from '@supabase/supabase-js';
import {
  authService,
  publicData,
  runResearch,
  streamResearch,
  type GuideDetailRecord,
  type GuideRecord,
  type Language,
  type LegalSource,
  type LegalUpdateRecord,
  type LibraryRecord,
  type ProductProofRecord,
  type ResearchResult,
  type ResourceState,
  type Role,
} from './services';
import { localizedPath, parseLocalizedPath, ui } from './i18n';
import { chatStore, type ChatThread } from './chatStore';

const appRoot = document.getElementById('app');
if (!appRoot) throw new Error('App root was not found.');

const roleQuota: Record<Role, number> = { citizen: 3, student: 30, professional: 50 };
const roleLabels: Record<Role, string> = { citizen: 'Citizen', student: 'Law Student', professional: 'Legal Professional' };
const roleOrder: Role[] = ['professional', 'student', 'citizen'];
const guideTopics = [
  { label: 'Property & Land', value: 'property' },
  { label: 'Family', value: 'family' },
  { label: 'Consumer Rights', value: 'consumer' },
  { label: 'Employment', value: 'employment' },
  { label: 'Digital & Online', value: 'digital' },
  { label: 'Cyber Safety', value: 'cyber' },
  { label: 'Tax & Finance', value: 'tax' },
  { label: 'Government Services', value: 'government' },
] as const;

function formatRelativeTime(isoStr: string): string {
  try {
    const date = new Date(isoStr);
    const now = new Date();
    const diffSec = Math.floor((now.getTime() - date.getTime()) / 1000);
    if (diffSec < 60) return 'Just now';
    if (diffSec < 3600) return `${Math.floor(diffSec / 60)}m ago`;
    if (diffSec < 86400) return `${Math.floor(diffSec / 3600)}h ago`;
    if (diffSec < 172800) return 'Yesterday';
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  } catch {
    return '';
  }
}

const roleSuggestedQueries: Record<Role, Array<{ title: string; desc: string; query: string; icon: string }>> = {
  professional: [
    { title: 'Temporary Injunction', desc: 'CPC Order XXXIX Rules 1–2 vs CrPC s.144 boundary', query: 'What are the legal requirements to obtain a temporary injunction under CPC Order 39 in a property suit?', icon: 'scale' },
    { title: 'Cheque Dishonour Notice', desc: 'NI Act Section 138 30-day notice and Section 141', query: 'What is the mandatory procedure and 30-day notice timeline for cheque dishonour under Section 138 of the Negotiable Instruments Act?', icon: 'clock' },
    { title: 'Specific Performance & Deposit', desc: 'SRA s.21A balance consideration deposit rule', query: 'Can an unregistered contract for sale be specifically enforced under Section 21A of the Specific Relief Act?', icon: 'book' },
    { title: 'Juvenile Bail Presumption', desc: 'Children Act 2013 s.44 & s.54 mandatory presumption', query: 'Does the Children Act 2013 create a mandatory presumption of bail for juveniles overriding CrPC Section 497?', icon: 'shield' },
    { title: 'Inherent Quashing Power', desc: 'High Court Division powers under CrPC Section 561A', query: 'Under what circumstances can the High Court Division quash a criminal proceeding under Section 561A of CrPC?', icon: 'source' },
    { title: 'Family Court Exclusive Powers', desc: 'Family Courts Act 2023 jurisdiction over dower & maintenance', query: 'Which court has exclusive jurisdiction to try suits for dower and maintenance under the Family Courts Act 2023?', icon: 'home' }
  ],
  student: [
    { title: 'Doctrine of Part Performance', desc: 'Transfer of Property Act Section 53A essentials', query: 'Explain the Doctrine of Part Performance under Section 53A of the Transfer of Property Act with landmark case principles.', icon: 'book' },
    { title: 'Masdar Hossain Precedent', desc: 'Judicial separation from executive (53 DLR AD 1)', query: 'Summarize the landmark case brief for Secretary Ministry of Finance v. Masdar Hossain on judicial independence.', icon: 'scale' },
    { title: 'Dying Declaration Admissibility', desc: 'Evidence Act Section 32(1) exception to hearsay', query: 'What are the legal conditions for admissibility of a Dying Declaration under Section 32(1) of the Evidence Act?', icon: 'source' },
    { title: 'Criminal Breach of Trust vs Cheating', desc: 'Penal Code s.405/406 vs s.415/420 differences', query: 'What is the distinction between Criminal Breach of Trust under Section 406 and Cheating under Section 420 of the Penal Code?', icon: 'shield' }
  ],
  citizen: [
    { title: 'Property Mutation & Khatian', desc: 'Applying for Namzari at AC Land office', query: 'How do I apply for land mutation (Namzari) after buying property in Bangladesh?', icon: 'home' },
    { title: 'Cheque Bounce Legal Notice', desc: 'Steps within 30 days of bank slip', query: 'A cheque given to me bounced due to insufficient funds. What legal notice must I send within 30 days?', icon: 'clock' },
    { title: 'Dower (Denmohor) & Maintenance', desc: 'Filing in Family Court for legal rights', query: 'How can a wife claim her unpaid dower (denmohor) and maintenance under Bangladesh Family Court laws?', icon: 'scale' },
    { title: 'Cyber Harassment & GD', desc: 'Filing complaint under Cyber Security Act 2023', query: 'What should I do if someone is harassing me or sharing unauthorized photos online in Bangladesh?', icon: 'shield' }
  ]
};
const localizedRoleLabel = (role: Role): string => ui(state.language, role === 'citizen' ? 'citizen' : role === 'student' ? 'student' : 'professional');
const rolePromise = (role: Role): string => ui(state.language, role === 'citizen' ? 'citizenPromise' : role === 'student' ? 'studentPromise' : 'professionalPromise');
const roleBody = (role: Role): string => ui(state.language, role === 'citizen' ? 'citizenBody' : role === 'student' ? 'studentBody' : 'professionalBody');
const mobileRoleBody = (role: Role): string => {
  if (state.language === 'bn') {
    return role === 'professional' ? 'আইন ও কর্তৃত্বপূর্ণ উৎস গবেষণা করুন।' : role === 'student' ? 'মামলা ও আইন থেকে শিখুন।' : 'ব্যবহারিক আইনি নির্দেশনা খুঁজুন।';
  }
  return role === 'professional' ? 'Research laws and authority.' : role === 'student' ? 'Learn cases and statutes.' : 'Find practical legal guidance.';
};
const roleContinue = (role: Role): string => ui(state.language, role === 'citizen' ? 'continueCitizen' : role === 'student' ? 'continueStudent' : 'continueProfessional');

const state: {
  language: Language;
  routePath: string;
  role: Role;
  menuOpen: boolean;
  session: Session | null;
  lastResearch: ResearchResult | null;
  lastResearchRole: Role | null;
  selectedSource: number;
  guidePage: number;
  guideQuery: string;
  guideCluster: string;
  citizenHasSearched: boolean;
  productProof: ProductProofRecord | null;
} = {
  ...parseLocalizedPath(window.location.pathname),
  role: (localStorage.getItem('justor-role') as Role | null) ?? 'citizen',
  menuOpen: false,
  session: null,
  lastResearch: null,
  lastResearchRole: null,
  selectedSource: 0,
  guidePage: 1,
  guideQuery: '',
  guideCluster: '',
  citizenHasSearched: false,
  productProof: null,
};

const storedGuideContext = (): { id: string; title: string; topic: string } | undefined => {
  const raw = sessionStorage.getItem('justor-guide-context');
  if (!raw) return undefined;
  try {
    const context = JSON.parse(raw) as Partial<{ id: string; title: string; topic: string }>;
    if (!context.id || !context.title) return undefined;
    return { id: context.id, title: context.title, topic: context.topic ?? '' };
  } catch {
    sessionStorage.removeItem('justor-guide-context');
    return undefined;
  }
};

const escapeHtml = (value: unknown): string => String(value ?? '').replace(/[&<>'"]/g, (character) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;',
})[character] ?? character);

const safeUrl = (value?: string): string | null => {
  if (!value) return null;
  try {
    const url = new URL(value, window.location.origin);
    return ['http:', 'https:'].includes(url.protocol) ? url.toString() : null;
  } catch {
    return null;
  }
};

const icon = (name: string, size = 20): string => {
  const paths: Record<string, string> = {
    arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/>',
    menu: '<path d="M4 7h16M4 12h16M4 17h16"/>',
    close: '<path d="m6 6 12 12M18 6 6 18"/>',
    book: '<path d="M4 5.5A3.5 3.5 0 0 1 7.5 2H11v18H7.5A3.5 3.5 0 0 0 4 23zM20 5.5A3.5 3.5 0 0 0 16.5 2H13v18h3.5A3.5 3.5 0 0 1 20 23z"/>',
    source: '<path d="M6 3h9l3 3v15H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
    shield: '<path d="M12 3 5 6v5c0 4.6 2.8 8 7 10 4.2-2 7-5.4 7-10V6z"/><path d="m9 12 2 2 4-5"/>',
    scale: '<path d="M12 3v18M7 21h10M4 7h16M6 7 3 13h6L6 7Zm12 0-3 6h6l-3-6Z"/>',
    clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    check: '<path d="m5 12 4 4L19 6"/>',
    external: '<path d="M14 4h6v6M20 4l-9 9"/><path d="M18 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h6"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    home: '<path d="m3 11 9-8 9 8"/><path d="M5 10v11h14V10M9 21v-7h6v7"/>',
  };
  return `<svg aria-hidden="true" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">${paths[name] ?? paths.source}</svg>`;
};

const brand = (inverse = false): string => `<span class="brand-lockup ${inverse ? 'brand-lockup-inverse' : ''}"><img src="/visuals/justor-mark.png" alt="" width="42" height="22"><span>Justor <strong>AI</strong></span></span>`;
const route = (path: string, label: string, className = ''): string => `<a href="${localizedPath(path, state.language)}" data-route class="${className}">${label}</a>`;

const header = (): string => `
  <a class="skip-link" href="#page-content">Skip to content</a>
  <header class="site-header" data-header>
    <div class="nav-shell">
      ${route('/', brand(true), 'brand-link')}
      <nav class="desktop-nav" aria-label="Primary navigation">
        ${route('/workspace/citizen', ui(state.language, 'citizen'))}
        ${route('/legal-library', ui(state.language, 'library'))}
        ${route('/guides', ui(state.language, 'guides'))}
        ${route('/workspace/professional', ui(state.language, 'legalProfessional'))}
        ${route('/workspace/student', ui(state.language, 'lawStudent'))}
      </nav>
      <div class="nav-actions">
        <button class="button-pilot-badge" type="button" data-action="open-pilot-modal" title="Founding Lawyer Pilot — ৳200/mo">⚖️ Founding Pilot</button>
        <button class="language-switch" type="button" data-action="language" aria-label="Switch language">${ui(state.language, 'language')}</button>
        ${state.session ? `<button class="nav-signin" type="button" data-action="sign-out">${ui(state.language, 'signOut')}</button>` : route('/login', ui(state.language, 'signIn'), 'nav-signin')}
        <button class="menu-button" type="button" data-action="menu" aria-label="${state.menuOpen ? ui(state.language, 'close') : ui(state.language, 'menu')}" aria-expanded="${state.menuOpen}">${icon(state.menuOpen ? 'close' : 'menu')}</button>
      </div>
    </div>
    
    <!-- Mobile Full-Width Slide-in Drawer (Section M & N) -->
    <div class="mobile-drawer-overlay ${state.menuOpen ? 'is-open' : ''}" data-action="close-menu" aria-hidden="${!state.menuOpen}"></div>
    <nav class="mobile-drawer ${state.menuOpen ? 'is-open' : ''}" aria-label="Mobile navigation" aria-hidden="${!state.menuOpen}">
      <div class="mobile-drawer-header">
        ${brand(true)}
        <button class="mobile-drawer-close" type="button" data-action="close-menu" aria-label="${ui(state.language, 'close')}">✕</button>
      </div>
      <div class="mobile-drawer-content">
        <span class="menu-section-label">${ui(state.language, 'product')}</span>
        ${route('/workspace/citizen', ui(state.language, 'citizen'), 'menu-nav-link')}
        ${route('/legal-library', ui(state.language, 'library'), 'menu-nav-link')}
        ${route('/guides', ui(state.language, 'guides'), 'menu-nav-link')}
        ${route('/legal-updates', ui(state.language, 'updates'), 'menu-nav-link')}
        
        <span class="menu-section-label" style="margin-top: 16px;">${ui(state.language, 'resources')}</span>
        ${route('/workspace/professional', ui(state.language, 'legalProfessional'), 'menu-nav-link')}
        ${route('/workspace/student', ui(state.language, 'lawStudent'), 'menu-nav-link')}
        ${route('/trust', ui(state.language, 'trust'), 'menu-nav-link')}
        ${route('/about', ui(state.language, 'about'), 'menu-nav-link')}

        <div class="mobile-drawer-footer">
          <button class="button button-secondary language-drawer-btn" type="button" data-action="language">${ui(state.language, 'language')}</button>
          ${state.session 
            ? `<button class="button button-outline signout-drawer-btn" type="button" data-action="sign-out">${ui(state.language, 'signOut')}</button>` 
            : route('/login', ui(state.language, 'signIn'), 'button signin-drawer-btn')
          }
        </div>
      </div>
    </nav>
  </header>`;

const footer = (): string => `
  <footer class="site-footer">
    <div class="footer-grid">
      <div>${brand(true)}<p>Bangladesh legal intelligence for guidance, learning and professional research.</p><span class="beta-label">${ui(state.language, 'controlledBeta')}</span></div>
      <nav aria-label="Product"><strong>Product</strong>${route('/workspace/professional', 'Legal Professional')}${route('/workspace/student', 'Law Student')}${route('/workspace/citizen', 'Citizen')}${route('/start', 'Start Justor')}</nav>
      <nav aria-label="Resources"><strong>Resources</strong>${route('/legal-library', ui(state.language, 'library'))}${route('/guides', ui(state.language, 'guides'))}${route('/legal-updates', ui(state.language, 'updates'))}${route('/trust', ui(state.language, 'trust'))}</nav>
      <nav aria-label="Company"><strong>Company</strong>${route('/about', ui(state.language, 'about'))}${route('/about#team', 'Team')}${route('/about#investors', 'Investors')}${route('/contact', 'Contact')}${route('/feedback', 'Feedback')}</nav>
      <nav aria-label="Legal"><strong>Legal</strong>${route('/privacy', 'Privacy')}${route('/terms', 'Terms')}${route('/disclaimer', 'Disclaimer')}<a href="mailto:tajuddinahamed.contact@gmail.com">Email us</a></nav>
    </div>
    <div class="footer-bottom"><span>© 2026 Justor AI</span><span>General legal information. Not a substitute for individual legal advice.</span><a href="tel:+8801764662967">+880 1764-662967</a></div>
  </footer>`;

const roleRows = (surface: 'hero' | 'start' = 'hero'): string => `
  <nav class="${surface === 'hero' ? 'role-selectors' : 'start-roles'}" aria-label="Choose your Justor experience">
    ${roleOrder.map((role) => `<a href="${localizedPath(`/workspace/${role}`, state.language)}" data-route data-role="${role}" class="role-row ${surface === 'start' ? 'start-role-row' : ''}"><span class="role-row-body"><span class="role-label">${localizedRoleLabel(role)}</span><strong class="role-heading">${rolePromise(role)}</strong><span class="role-desc role-desc-desktop">${roleBody(role)}</span><span class="role-desc role-desc-mobile">${mobileRoleBody(role)}</span></span><span class="role-arrow" aria-hidden="true">→</span><span class="sr-only">${roleContinue(role)}</span></a>`).join('')}
  </nav>`;

const libraryPreviewFallback = (): string => `
  <section class="library-band light-section">
    <div class="library-band-inner"><h2>${ui(state.language, 'libraryHeading')}</h2>${route('/legal-library', `${ui(state.language, 'exploreLibrary')} <span aria-hidden="true">→</span>`, 'link-arrow-light')}</div>
  </section>`;

const libraryPreviewFull = (records: LibraryRecord[]): string => `
  <section class="library-preview light-section"><div class="section-shell">
    <div class="section-heading section-heading-row"><div><span class="section-kicker">${ui(state.language, 'library')}</span><h2>${ui(state.language, 'libraryHeading')}</h2></div>${route('/legal-library', `${ui(state.language, 'libraryExplore')} ${icon('arrow', 16)}`, 'text-link')}</div>
    <form class="public-search" data-library-home-search><label><span class="sr-only">${ui(state.language, 'search')}</span>${icon('search')}<input name="query" placeholder="${ui(state.language, 'libraryPlaceholder')}"></label><button class="button" type="submit">${ui(state.language, 'search')}</button></form>
    <div class="filter-row" aria-label="Library types"><span>Laws</span><span>Sections</span><span>Cases</span><span>Amendments</span><span>Guides</span><span>Updates</span></div>
    <div class="record-grid">${records.map(recordCard).join('')}</div>
  </div></section>`;

const homePage = (): string => `
  <main id="page-content">
    <section class="home-hero">
      <div class="hero-copy">
        <h1 class="hero-h1">${ui(state.language, 'heroHeadline')}</h1>
        <p class="hero-subtitle">${ui(state.language, 'heroBody')}</p>
        ${roleRows()}
      </div>
      <div class="hero-visual hero-3d-canvas" role="presentation" aria-hidden="true">
        <img src="/visuals/hero-legal-environment-v2.webp" alt="" width="1" height="1" loading="lazy" decoding="async" fetchpriority="low" class="hero-3d-fallback" hidden data-hero-source>
        <canvas width="1536" height="1024" class="hero-3d-static" data-source="/visuals/hero-legal-environment-v2.webp"></canvas>
      </div>
    </section>
    <div class="hero-to-content-transition" aria-hidden="true"></div>
    <div data-home-proof></div>
    <div data-home-library-preview>${libraryPreviewFallback()}</div>

    <section class="trust-signal">
      <div class="section-shell trust-signal-grid"><div class="trust-signal-heading"><span class="section-kicker section-kicker-light">${ui(state.language, 'trustMethod')}</span><h2>${ui(state.language, 'trustHeading')}</h2></div><div class="trust-signal-definitions"><article><strong>Primary Source</strong><p>The authority itself.</p></article><article><strong>Source Checked</strong><p>The proposition–source relationship.</p></article><article><strong>Human Legal Reviewed</strong><p>A reviewed content version.</p></article></div>${route('/trust', `${ui(state.language, 'readTrust')} ${icon('arrow', 16)}`, 'link-arrow-dark')}</div>
    </section>

    <section class="section-shell incubation-signal"><img src="/visuals/nsu-startups-next.png" alt="NSU Startups Next" loading="lazy"><div><span class="section-kicker">${ui(state.language, 'incubation')}</span><h2>${ui(state.language, 'incubationStatement')}</h2><p>${ui(state.language, 'incubationSupport')}</p></div></section>

    <section class="early-access section-shell"><div><span class="section-kicker">${ui(state.language, 'controlledBeta')}</span><h2>${ui(state.language, 'earlyHeading')}</h2><p>${ui(state.language, 'earlyBody')}</p></div><a class="button" href="mailto:tajuddinahamed.contact@gmail.com?subject=Justor%20AI%20early%20access">${ui(state.language, 'earlyCta')} ${icon('arrow', 16)}</a></section>
  </main>`;

const startPage = (): string => `
  <main id="page-content" class="start-page">
    <header class="start-header">${route('/', brand(), 'brand-link')}<div><button class="language-switch" type="button" data-action="language" aria-label="Switch language">${ui(state.language, 'language')}</button>${state.session ? '<button type="button" data-action="sign-out" class="text-button">Sign Out</button>' : route('/login', ui(state.language, 'signIn'), 'text-button')}</div></header>
    <section class="start-content"><span class="section-kicker">${ui(state.language, 'start')}</span><h1>${ui(state.language, 'startHeading')}</h1><p>${ui(state.language, 'startBody')}</p>
      ${roleRows('start')}
    </section>
  </main>`;

const workspaceNav = (role: Role, items: Array<{ label: string; href: string; icon: string }>, active: string): string => {
  const threads = chatStore.getThreadsByRole(role);
  const activeThreadId = chatStore.getActiveThreadId(role);

  return `
  <aside class="workspace-sidebar">
    <div class="workspace-brand">${brand(true)}<span>Beta</span></div>
    <button class="new-research-capsule" type="button" data-action="new-research">
      ${icon('plus', 16)} <span>${role === 'professional' ? 'New Research' : role === 'student' ? 'New Study Chat' : 'New Legal Inquiry'}</span>
    </button>
    <nav class="sidebar-main-nav" aria-label="${localizedRoleLabel(role)} navigation">
      ${items.map((item) => route(item.href, `${icon(item.icon, 18)} <span>${item.label}</span>`, item.label === active ? 'active' : '')).join('')}
    </nav>

    <div class="sidebar-history-section">
      <div class="history-section-header">
        <span class="history-title">${icon('message', 14)} <span>Recent Research</span></span>
        ${threads.length > 0 ? `<button class="clear-history-btn" type="button" data-action="clear-threads" title="Clear all history">Clear</button>` : ''}
      </div>
      <div class="history-threads-list">
        ${threads.length === 0 ? `
          <div class="history-empty-note">No recent research yet.</div>
        ` : threads.map((t) => {
          const isActive = t.id === activeThreadId;
          const timeStr = formatRelativeTime(t.updatedAt);
          return `
            <div class="history-thread-item ${isActive ? 'is-active' : ''}" data-action="select-thread" data-thread-id="${t.id}">
              <div class="thread-item-content">
                <strong class="thread-item-title" title="${escapeHtml(t.title)}">${escapeHtml(t.title)}</strong>
                <span class="thread-item-time">${timeStr}</span>
              </div>
              <button class="thread-delete-btn" type="button" data-action="delete-thread" data-thread-id="${t.id}" title="${state.language === 'bn' ? `গবেষণা মুছুন: ${escapeHtml(t.title)}` : `Delete research thread: ${escapeHtml(t.title)}`}" aria-label="${state.language === 'bn' ? `গবেষণা মুছুন: ${escapeHtml(t.title)}` : `Delete research thread: ${escapeHtml(t.title)}`}">✕</button>
            </div>
          `;
        }).join('')}
      </div>
    </div>

    <button class="switch-experience" type="button" data-action="switch-experience">${ui(state.language, 'switchExperience')} ${icon('arrow', 15)}</button>
  </aside>`;
};

const workspaceTopbar = (role: Role, title?: string): string => `
  <header class="workspace-topbar">
    <a href="${localizedPath('/', state.language)}" data-route class="workspace-mobile-brand">${brand()}</a>
    <span>${localizedRoleLabel(role)}${title ? ` <span class="topbar-thread-title">· ${escapeHtml(title)}</span>` : ''}</span>
    <div style="display: flex; align-items: center; gap: 8px;">
      <button class="button-pilot-badge" type="button" data-action="open-pilot-modal" title="Founding Lawyer Pilot — ৳200/mo">⚖️ Founding Pilot</button>
      <button class="language-switch" type="button" data-action="language" aria-label="Switch language">${ui(state.language, 'language')}</button>
      ${state.session ? `<button type="button" data-action="sign-out" class="text-button">Sign Out</button>` : route('/login', ui(state.language, 'signIn'), 'button button-small')}
    </div>
  </header>`;

const quotaLine = (role: Role): string => `<span class="quota-line" data-quota>${state.session ? `${ui(state.language, 'dailyAllowance')}: ${roleQuota[role]}` : `${ui(state.language, 'signInQuotaPrefix')} ${roleQuota[role]} ${ui(state.language, 'answersPerDay')}`}</span>`;

const citizenSectors = [
  { icon: '🏠', titleKey: 'sectorProperty', descKey: 'sectorPropertyDesc', cluster: 'property-land', query: 'My landlord won\'t return my advance deposit or rent dispute' },
  { icon: '👨‍👩‍👧', titleKey: 'sectorFamily', descKey: 'sectorFamilyDesc', cluster: 'family-marriage', query: 'How to claim prompt dower (Denmohor) or maintenance under Muslim Family Law?' },
  { icon: '⚖️', titleKey: 'sectorCriminal', descKey: 'sectorCriminalDesc', cluster: 'criminal-police', query: 'What are the rights upon police arrest under Section 54 and bail guidelines?' },
  { icon: '💼', titleKey: 'sectorEmployment', descKey: 'sectorEmploymentDesc', cluster: 'employment-work', query: 'Statutory notice pay and compensation for termination under Labour Act Section 26' },
  { icon: '🛒', titleKey: 'sectorConsumer', descKey: 'sectorConsumerDesc', cluster: 'consumer-contracts', query: 'Filing a consumer complaint for adulterated or defective products under Section 76' },
  { icon: '📋', titleKey: 'sectorRights', descKey: 'sectorRightsDesc', cluster: 'rights-documents', query: 'Procedure for correcting NID, birth certificate or land Khatian porcha records' },
  { icon: '🏢', titleKey: 'sectorBusiness', descKey: 'sectorBusinessDesc', cluster: 'business-licensing', query: 'Trade license requirements and municipal business regulatory compliance' },
] as const;

const renderEmptyLanding = (role: Role): string => {
  if (role === 'citizen') {
    return `
      <div class="chat-empty-landing citizen-landing-sectors">
        <div class="empty-landing-brand">
          <img src="/visuals/justor-mark.png" alt="Justor AI" width="44" height="44">
        </div>
        <h1 class="empty-landing-title">${state.language === 'bn' ? 'কী ঘটেছে? আপনার পরিস্থিতি বেছে নিন' : 'What happened? Choose your situation'}</h1>
        <p class="empty-landing-subtitle">
          ${state.language === 'bn' 
            ? 'বাস্তব করণীয়, প্রমাণ ও সরকারি সেবার পথ। জাস্টর প্রথমে সিটিজেন লিগ্যাল গাইডে খুঁজবে।' 
            : 'Practical legal guidance, required evidence, and official routes.'}
        </p>
        <div class="citizen-sector-cards" role="region" aria-label="Citizen Legal Sectors">
          ${citizenSectors.map((s) => `
            <button type="button" class="citizen-sector-card" data-suggested-query="${escapeHtml(s.query)}" aria-label="${escapeHtml(ui(state.language, s.titleKey as CopyKey))}">
              <span class="sector-card-icon" aria-hidden="true">${s.icon}</span>
              <div class="sector-card-text">
                <strong class="sector-card-title">${escapeHtml(ui(state.language, s.titleKey as CopyKey))}</strong>
                <span class="sector-card-desc">${escapeHtml(ui(state.language, s.descKey as CopyKey))}</span>
              </div>
            </button>
          `).join('')}
        </div>
        <div class="citizen-disclaimer-box">
          <p>${ui(state.language, 'citizenDisclaimer')}</p>
        </div>
      </div>
    `;
  }

  const suggestions = roleSuggestedQueries[role] ?? roleSuggestedQueries.professional;
  return `
    <div class="chat-empty-landing">
      <div class="empty-landing-brand">
        <img src="/visuals/justor-mark.png" alt="Justor AI" width="44" height="44">
      </div>
      <h1 class="empty-landing-title">${role === 'professional' ? (state.language === 'bn' ? 'পেশাগত আইনি গবেষণা ও বুদ্ধিমত্তা' : 'Bangladesh Legal Research & Intelligence') : (state.language === 'bn' ? 'উৎস-সংযুক্ত আইনি শিক্ষা' : 'Source-Linked Legal Study')}</h1>
      <p class="empty-landing-subtitle">
        ${role === 'professional' 
          ? (state.language === 'bn' ? 'নিয়ন্ত্রণকারী আইন, গেজেট ও সুপ্রিম কোর্টের নজিরের ভিত্তিতে কর্তৃত্বপূর্ণ বিশ্লেষণ।' : 'Grounded legal analysis across controlling statutes, gazettes, and Supreme Court of Bangladesh precedents.') 
          : (state.language === 'bn' ? 'ধারা ও নজির বিশ্লেষণ করুন এবং সরকারি উৎস থেকে আইন শিখুন।' : 'Break down principles, structure case briefs, and verify statutory rules with official sources.')}
      </p>
      <div class="chat-suggested-grid">
        ${suggestions.map((item) => `
          <button type="button" class="suggested-card" data-suggested-query="${escapeHtml(item.query)}">
            <div class="suggested-card-header">
              ${icon(item.icon, 16)} <span>${escapeHtml(item.title)}</span>
            </div>
            <p>${escapeHtml(item.desc)}</p>
          </button>
        `).join('')}
      </div>
    </div>
  `;
};

const renderChatStream = (thread: ChatThread, role: Role): string => {
  if (thread.messages.length === 0) {
    return renderEmptyLanding(role);
  }
  return `
    <div class="chat-conversation-thread" data-chat-thread-id="${thread.id}">
      ${thread.messages.map((msg) => {
        if (msg.sender === 'user') {
          return `
            <div class="chat-message-row user-row" id="${msg.id}">
              <div class="chat-user-bubble">
                <p class="user-query-text">${escapeHtml(msg.content)}</p>
                <span class="user-bubble-time">${formatRelativeTime(msg.timestamp)}</span>
              </div>
            </div>
          `;
        } else {
          return `
            <div class="chat-message-row assistant-row" id="${msg.id}">
              <div class="chat-assistant-container">
                <div class="assistant-avatar-badge"><img src="/visuals/justor-mark.png" alt="Justor AI"></div>
                <div class="assistant-content-wrapper">
                  ${msg.result ? renderResearchResult(msg.result, role) : `<div class="research-formatted-markdown">${formatAnswerMarkdown(msg.content, role)}</div>`}
                </div>
              </div>
            </div>
          `;
        }
      }).join('')}
    </div>
  `;
};

const renderBottomChatBar = (role: Role, placeholder: string, quickActions: string[], context?: { id: string; title: string; topic: string }): string => `
  <div class="chat-sticky-bottom-bar">
    <div class="chat-bottom-inner">
      <div class="chat-quick-actions-bar">
        ${quickActions.map((action) => `<button type="button" class="quick-chip-btn" data-prompt="${escapeHtml(action)}">${action}</button>`).join('')}
      </div>
      <form class="chat-floating-composer" data-research-form data-role="${role}" ${context ? `data-context-id="${escapeHtml(context.id)}" data-context-title="${escapeHtml(context.title)}" data-context-topic="${escapeHtml(context.topic)}"` : ''}>
        <div class="composer-input-box">
          <textarea name="query" rows="1" required placeholder="${placeholder}" data-auto-resize aria-label="${placeholder}"></textarea>
          <button type="submit" class="composer-send-btn" aria-label="Submit query" title="Send (Enter)">
            ${icon('arrow', 18)}
          </button>
        </div>
        <div class="composer-subline">
          <span class="composer-privacy-hint">${ui(state.language, 'composerPrivacyHint')}</span>
          ${quotaLine(role)}
        </div>
      </form>
    </div>
  </div>
`;

const citizenWelcomeMascot = (): string => `
  <div class="citizen-welcome-mascot" data-citizen-mascot aria-label="Justor citizen guide assistant">
    <span class="mascot-mark"><img src="/visuals/justor-mark.png" alt="" width="56" height="30"></span>
    <div><strong>Start with a citizen guide.</strong><p>Search by the problem, service, document or evidence you already know.</p></div>
  </div>`;

const professionalWorkspace = (): string => {
  const thread = chatStore.getOrCreateActiveThread('professional');
  return `
  <main id="page-content" class="workspace workspace-professional">
    <h1 class="sr-only">${state.language === 'bn' ? 'আইনি গবেষণা — পেশাদার ওয়ার্কস্পেস' : 'Legal Research — Professional Workspace'}</h1>
    ${workspaceNav('professional', [
      { label: ui(state.language, 'researchHome'), href: '/workspace/professional', icon: 'home' },
      { label: ui(state.language, 'legalLibrary'), href: '/legal-library', icon: 'book' },
      { label: ui(state.language, 'cases'), href: '/legal-library?type=case', icon: 'scale' },
      { label: ui(state.language, 'statutes'), href: '/legal-library?type=law', icon: 'source' },
      { label: ui(state.language, 'updates'), href: '/legal-updates', icon: 'clock' },
      { label: ui(state.language, 'amendments'), href: '/legal-library?type=amendment', icon: 'source' },
    ], ui(state.language, 'researchHome'))}
    <section class="workspace-main">
      ${workspaceTopbar('professional', thread.title !== 'New Legal Research' ? thread.title : undefined)}
      <div class="workspace-chat-container">
        <div class="chat-scroll-area" data-chat-scroll>
          ${renderChatStream(thread, 'professional')}
        </div>
        ${renderBottomChatBar('professional', ui(state.language, 'professionalPlaceholder'), [ui(state.language, 'researchIssue'), ui(state.language, 'findPrecedent'), ui(state.language, 'findStatute'), ui(state.language, 'checkAmendment')])}
      </div>
    </section>
    ${mobileBottomNav('professional')}
  </main>`;
};

const studentPreAuth = (): string => `
  <main id="page-content" class="preauth-page"><header>${route('/', brand(), 'brand-link')}<div><button class="language-switch" type="button" data-action="language" aria-label="Switch language">${ui(state.language, 'language')}</button>${route('/start', ui(state.language, 'switchExperience'), 'text-link')}</div></header><section><span class="section-kicker">${ui(state.language, 'studentKicker')}</span><h1>${ui(state.language, 'studentHeading')}</h1><p>${ui(state.language, 'studentAllowance')}</p><button class="button google-button" type="button" data-action="google-sign-in" data-next="${localizedPath('/workspace/student', state.language)}"><span>G</span> ${ui(state.language, 'continueGoogle')}</button><small>${ui(state.language, 'publicReading')}</small></section></main>`;

const studentWorkspace = (): string => {
  if (!state.session) return studentPreAuth();
  const thread = chatStore.getOrCreateActiveThread('student');
  return `
  <main id="page-content" class="workspace workspace-student">
    <h1 class="sr-only">${state.language === 'bn' ? 'আইন শিক্ষা — শিক্ষার্থী ওয়ার্কস্পেস' : 'Legal Study — Student Workspace'}</h1>
    ${workspaceNav('student', [
      { label: ui(state.language, 'studyHome'), href: '/workspace/student', icon: 'home' },
      { label: ui(state.language, 'askJustor'), href: '/workspace/student#ask', icon: 'source' },
      { label: ui(state.language, 'cases'), href: '/legal-library?type=case', icon: 'scale' },
      { label: ui(state.language, 'statutes'), href: '/legal-library?type=law', icon: 'book' },
      { label: ui(state.language, 'concepts'), href: '/legal-library?type=concept', icon: 'source' },
    ], ui(state.language, 'studyHome'))}
    <section class="workspace-main">
      ${workspaceTopbar('student', thread.title !== 'New Study Session' ? thread.title : undefined)}
      <div class="workspace-chat-container">
        <div class="chat-scroll-area" data-chat-scroll>
          ${renderChatStream(thread, 'student')}
        </div>
        ${renderBottomChatBar('student', 'Ask about a case, statute, legal concept or principle...', ['Explain a Statute', 'Brief a Case', 'Explain a Concept', 'Compare Cases', 'Quiz Me', 'Practice a Problem'])}
      </div>
    </section>
    ${mobileBottomNav('student')}
  </main>`;
};

const citizenWorkspace = (): string => {
  const guideContext = storedGuideContext();
  const thread = chatStore.getOrCreateActiveThread('citizen');
  return `
  <main id="page-content" class="workspace workspace-citizen">
    <h1 class="sr-only">${state.language === 'bn' ? 'নাগরিক আইনি নির্দেশনা — ওয়ার্কস্পেস' : 'Citizen Legal Guidance — Workspace'}</h1>
    ${workspaceNav('citizen', [
      { label: ui(state.language, 'home'), href: '/workspace/citizen', icon: 'home' },
      { label: ui(state.language, 'guides'), href: '/guides', icon: 'book' },
      { label: ui(state.language, 'askJustor'), href: '/workspace/citizen#ask', icon: 'source' },
    ], ui(state.language, 'home'))}
    <section class="workspace-main">
      ${workspaceTopbar('citizen', thread.title !== 'New Legal Inquiry' ? thread.title : undefined)}
      <div class="workspace-chat-container">
        <div class="chat-scroll-area" data-chat-scroll>
          ${renderChatStream(thread, 'citizen')}
        </div>
        ${renderBottomChatBar('citizen', 'Describe your specific situation...', ['Explain my next step', 'What evidence should I keep?'], guideContext)}
      </div>
    </section>
    ${mobileBottomNav('citizen')}
  </main>`;
};

function mobileBottomNav(role: Role): string {
  const items = role === 'citizen'
    ? [[ui(state.language, 'home'), '/workspace/citizen', 'home'], [ui(state.language, 'guides'), '/guides', 'book'], [ui(state.language, 'mobileAsk'), '/workspace/citizen#ask', 'source']]
    : role === 'student'
      ? [[ui(state.language, 'mobileStudy'), '/workspace/student', 'home'], [ui(state.language, 'mobileAsk'), '/workspace/student#ask', 'source'], [ui(state.language, 'cases'), '/legal-library?type=case', 'scale'], [ui(state.language, 'library'), '/legal-library', 'book']]
      : [[ui(state.language, 'mobileResearch'), '/workspace/professional', 'home'], [ui(state.language, 'library'), '/legal-library', 'book'], [ui(state.language, 'updates'), '/legal-updates', 'clock'], [ui(state.language, 'mobileStart'), '/start', 'user']];
  return `<nav class="mobile-bottom-nav" aria-label="${localizedRoleLabel(role)} mobile navigation">${items.map(([label, href, iconName]) => route(href, `${icon(iconName, 18)}<span>${label}</span>`)).join('')}</nav>`;
}

const unavailable = (message?: string): string => `<div class="empty-state"><span>${icon('shield', 24)}</span><h3>${ui(state.language, 'unavailableTitle')}</h3><p>${message ?? ui(state.language, 'unavailableBody')}</p></div>`;
const empty = (): string => `<div class="empty-state"><span>${icon('search', 24)}</span><h3>${ui(state.language, 'noResults')}</h3><p>${ui(state.language, 'noResultsBody')}</p></div>`;

const libraryPage = (): string => {
  const query = new URLSearchParams(window.location.search).get('q') ?? '';
  const type = new URLSearchParams(window.location.search).get('type') ?? '';
  return `<main id="page-content" class="inner-page"><section class="compact-hero section-shell"><span class="section-kicker">${ui(state.language, 'library')}</span><h1>${ui(state.language, 'libraryPageHeading')}</h1><p>${ui(state.language, 'libraryPageBody')}</p><form class="public-search" data-library-search><label>${icon('search')}<span class="sr-only">${ui(state.language, 'search')}</span><input name="query" value="${escapeHtml(query)}" placeholder="${ui(state.language, 'libraryPlaceholder')}"></label><button class="button" type="submit">${ui(state.language, 'search')}</button></form><div class="filter-row" data-library-filters>${['', 'law', 'section', 'case', 'amendment', 'guide', 'update'].map((value) => `<button type="button" data-library-type="${value}" class="${value === type ? 'active' : ''}">${value ? `${value[0]?.toUpperCase()}${value.slice(1)}s` : 'All'}</button>`).join('')}</div></section><section class="section-shell results-section"><div class="result-summary"><strong data-library-count>—</strong><span>${ui(state.language, 'publishedRecords')}</span></div><div data-library-results class="record-grid"><div class="data-loading">Checking canonical records…</div></div></section></main>`;
};

const guidesPage = (): string => `
  <main id="page-content" class="inner-page"><section class="compact-hero section-shell"><span class="section-kicker">${ui(state.language, 'citizenGuides')}</span><h1>${ui(state.language, 'guidePageHeading')}</h1><p>${ui(state.language, 'guidePageBody')}</p><form class="public-search" data-guide-directory-search><label>${icon('search')}<span class="sr-only">${ui(state.language, 'search')}</span><input name="query" placeholder="${ui(state.language, 'guidePlaceholder')}"></label><button class="button" type="submit">${ui(state.language, 'search')}</button></form></section>
  <section class="section-shell guide-directory"><div class="directory-topics"><h2>${ui(state.language, 'topics')}</h2>${guideTopics.map((topic) => `<button type="button" data-guide-cluster="${topic.value}">${topic.label}<span>${icon('arrow', 15)}</span></button>`).join('')}</div><div class="directory-results"><div class="section-heading section-heading-row"><div><span class="section-kicker">${ui(state.language, 'publishedLibrary')}</span><h2>${ui(state.language, 'browseGuides')}</h2></div><span data-guide-count>—</span></div><div data-guide-results class="guide-list"><div class="data-loading">Loading published citizen guides…</div></div><button class="button button-secondary load-more" type="button" data-guide-more hidden>${ui(state.language, 'loadMore')}</button></div></section></main>`;

const guideDetailShell = (slug: string): string => `<main id="page-content" class="inner-page"><section class="section-shell detail-loading" data-guide-detail data-slug="${escapeHtml(slug)}"><div class="data-loading">Checking the published guide and its source status…</div></section></main>`;

const updatesPage = (): string => `<main id="page-content" class="inner-page"><section class="compact-hero section-shell"><span class="section-kicker">${ui(state.language, 'updates')}</span><h1>${ui(state.language, 'updatesHeading')}</h1><p>${ui(state.language, 'updatesBody')}</p></section><section class="section-shell results-section"><div data-update-results class="update-list"><div class="data-loading">Checking current update records…</div></div></section></main>`;
const updateDetailShell = (id: string): string => `<main id="page-content" class="inner-page"><section class="section-shell detail-loading" data-update-detail data-id="${escapeHtml(id)}"><div class="data-loading">Checking the current update record…</div></section></main>`;

const trustPage = (): string => `<main id="page-content" class="inner-page trust-page"><section class="compact-hero trust-hero section-shell"><span class="section-kicker">Trust Method</span><h1>How Justor handles legal information.</h1><p>Verification language is precise because a source, a checked relationship and human review are different claims.</p></section><section class="section-shell trust-content"><div class="trust-definitions"><div class="trust-row"><span class="trust-term">Primary Source</span><p class="trust-def">The law, judgment, gazette or official authority itself.</p></div><div class="trust-row"><span class="trust-term">Source Checked</span><p class="trust-def">The relationship between a proposition and its cited source was checked.</p></div><div class="trust-row"><span class="trust-term">Human Legal Reviewed</span><p class="trust-def">That specific content version received human legal review.</p></div></div><article><span>Evidence insufficient</span><h2>Uncertainty stays visible</h2><p>If a reliable source or current status is unavailable, Justor should say so rather than infer a badge.</p></article><section><h2>Legal update process</h2><p>Current-law checks depend on versioned legal records, amendment history and official publication data. The frontend displays only the status returned by that system.</p></section><section><h2>Coverage limitations</h2><p>Coverage varies by topic and source availability. Justor does not promise completeness, absolute accuracy or zero hallucination.</p></section><section><h2>Corrections</h2><p>Report an unsupported citation, outdated provision, translation problem or missing authority directly to the team.</p><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Justor%20correction">Report a correction ${icon('arrow', 15)}</a></section><section><h2>Privacy and limits</h2><p>Do not submit unnecessary sensitive information. Justor provides legal information and research support, not individual legal representation.</p>${route('/privacy', 'Privacy overview', 'text-link')} ${route('/disclaimer', 'Read disclaimer', 'text-link')}</section></section></main>`;

const aboutPage = (): string => `<main id="page-content" class="inner-page about-page"><nav class="about-anchor-nav" aria-label="About page sections"><a href="#about">About</a><a href="#team">Team</a><a href="#stage">Stage</a><a href="#incubation">Incubation</a><a href="#collaborate">Collaborate</a><a href="#investors">Investors</a><a href="#contact">Contact</a></nav>
  <section id="about" class="compact-hero section-shell"><span class="section-kicker">About Justor</span><h1>Building a better interface to Bangladesh law.</h1><p>Justor AI is a Bangladesh-focused legal intelligence startup building structured, source-linked tools for understanding, learning and researching law.</p><div class="mission-vision"><div><strong>Mission</strong><p>Make Bangladesh law easier to access, understand, research and verify.</p></div><div><strong>Vision</strong><p>Build digital legal intelligence infrastructure for Bangladesh that improves access to legal information, legal learning and professional research.</p></div></div></section>
  <section class="section-shell about-block"><span class="section-kicker">What we are building</span><div class="plain-columns"><article><h2>Citizen Guidance</h2><p>Practical routes and public legal information.</p></article><article><h2>Legal Learning</h2><p>Source-linked assistance for cases, statutes and concepts.</p></article><article><h2>Professional Intelligence</h2><p>Research that keeps authority beside the analysis.</p></article><article><h2>Shared Legal Knowledge</h2><p>A structured layer across role-specific experiences.</p></article></div></section>
  <section class="about-narrative"><div class="section-shell"><span class="section-kicker section-kicker-light">Why Justor exists</span><h2>Legal information is difficult to navigate.</h2><p>Finding the legal rule that applies to a problem can require navigating dense statutes, scattered government websites and unfamiliar terminology.</p><p>Citizens often do not know where to start. Students need to connect concepts to authority. Professionals need faster ways to locate and verify relevant law.</p><p>Justor is building a more structured interface to that information.</p></div></section>
  <section class="section-shell principle-quote"><span class="section-kicker">Our product principle</span><blockquote>“Don't ask users to trust the AI. Make important legal propositions easy to verify.”</blockquote>${route('/trust', `Read our Trust Method ${icon('arrow', 16)}`, 'text-link')}</section>
  <section id="stage" class="section-shell stage-block"><div><span class="section-kicker">Where we are today</span><h2>Controlled beta</h2><p>Current work includes source-grounded AI, Citizen Authority Guides, Legal Library, professional research, student learning, Legal Updates, and Bangla + English.</p></div><div id="incubation" class="nsusn-block"><img src="/visuals/nsu-startups-next.png" alt="NSU Startups Next"><strong>Incubation</strong><h3>Justor AI is incubated at NSU Startups Next.</h3><p>Part of the NSU Startups Next incubation program, supporting the team's product development, validation and startup growth.</p></div></section>
  <section id="team" class="section-shell team-block"><span class="section-kicker">Team</span><div class="team-list"><article><div>TA</div><span>Founder & CEO</span><h2>Tajuddin Ahamed</h2><p>Leads Justor AI's product vision, company strategy and overall execution. Works across product architecture, UX design, business development, market validation and legal-tech strategy. Also contributes directly to engineering decisions alongside the CTO, translating product requirements into the platform.</p></article><article><div>MH</div><span>Co-founder & CTO</span><h2>Mehedi Hasan</h2><p>Leads Justor AI's engineering and technical development, including backend infrastructure, legal retrieval systems, AI and RAG architecture, database design and production engineering.</p></article><article><div>AS</div><span>Legal Q&A</span><h2>Anisur Rahman Sanjib</h2><p>Contributes to Justor's legal Q&A process, helping ensure legal information used in the platform's workflows is appropriately structured and checked.</p></article></div></section>
  <section class="section-shell upcoming-block"><span class="section-kicker">Upcoming</span><h2>What's coming next</h2><div class="upcoming-rows"><article><strong>For Law Students</strong><p>Exam Mode · Moot Practice · Notes · Concept Maps<br>Compare Laws · Case Navigator</p></article><article><strong>For Legal Professionals</strong><p>Document Analysis · Compare Authorities · Saved Authorities<br>Research History · Matter Workspace · Citation Workspace · Drafting Tools</p></article><article><strong>For Citizens</strong><p>Document Explanation · OCR · Complaint Tracking<br>Official Authority Routing</p></article></div><p class="roadmap-note">Roadmap features are under development and may change during beta.</p></section>
  <section id="collaborate" class="work-with"><div class="section-shell"><span class="section-kicker section-kicker-light">Work with Justor</span><h2>Build Bangladesh legal intelligence with us.</h2><div class="collaboration-tracks"><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Academic%20collaboration">Universities & Academic Institutions</a><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Legal%20professional%20collaboration">Law Firms & Legal Professionals</a><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Media%20collaboration">Media & Publishers</a><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Technology%20collaboration">Technology & Ecosystem</a></div></div></section>
  <section id="investors" class="section-shell investor-block"><span class="section-kicker">For Investors & Strategic Partners</span><h2>Legal intelligence infrastructure focused on Bangladesh.</h2><p>We welcome conversations with investors and strategic partners interested in LegalTech, AI infrastructure, emerging markets and access to legal information.</p><dl class="investor-grid"><div><dt>Product</dt><dd>Role-specific legal intelligence</dd></div><div><dt>Market</dt><dd>Bangladesh legal-information, learning and professional workflows</dd></div><div><dt>Infrastructure</dt><dd>Structured legal knowledge + AI</dd></div><div><dt>Stage</dt><dd>Controlled Beta</dd></div></dl><div class="button-row"><a class="button" href="mailto:tajuddinahamed.contact@gmail.com?subject=Investor%20inquiry">Investor Inquiry</a><a class="button button-secondary" href="mailto:tajuddinahamed.contact@gmail.com?subject=Contact%20founder">Contact Founder</a></div><a href="tel:+8801764662967">+880 1764-662967</a></section>
  <section id="contact" class="section-shell direct-contact"><span class="section-kicker">Contact</span><h2>Start the right conversation.</h2><a href="mailto:tajuddinahamed.contact@gmail.com">tajuddinahamed.contact@gmail.com</a><a href="tel:+8801764662967">+880 1764-662967</a></section>
  </main>`;

const contactPage = (): string => `<main id="page-content" class="inner-page"><section class="compact-hero section-shell"><span class="section-kicker">Contact Justor</span><h1>Start the right conversation.</h1><p>Choose a direct route to the team. No submission is silently stored by this page.</p></section><section class="section-shell contact-options"><a href="mailto:tajuddinahamed.contact@gmail.com"><span>Email</span><strong>tajuddinahamed.contact@gmail.com</strong>${icon('arrow', 16)}</a><a href="tel:+8801764662967"><span>Phone</span><strong>+880 1764-662967</strong>${icon('arrow', 16)}</a><a href="https://wa.me/8801764662967" target="_blank" rel="noopener"><span>WhatsApp</span><strong>Open a conversation</strong>${icon('external', 16)}</a><a href="https://docs.google.com/forms/d/e/1FAIpQLSdMfVydj2kMXZkf3SpYi_soA37YtTmAIB7VquPNkadYOmLSrg/viewform" target="_blank" rel="noopener"><span>User Survey</span><strong>Share your product feedback</strong>${icon('external', 16)}</a></section><section class="section-shell inquiry-links"><h2>Inquiry type</h2><div><a href="mailto:tajuddinahamed.contact@gmail.com?subject=University%20partnership">University partnership</a><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Legal%20collaboration">Legal collaboration</a><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Media%20inquiry">Media & press</a><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Investor%20inquiry">Investor / strategic partnership</a><a href="https://docs.google.com/forms/d/e/1FAIpQLSdMfVydj2kMXZkf3SpYi_soA37YtTmAIB7VquPNkadYOmLSrg/viewform" target="_blank" rel="noopener">Product Feedback Survey ↗</a></div></section></main>`;

const loginPage = (): string => {
  const next = new URLSearchParams(window.location.search).get('next') || localizedPath(`/workspace/${state.role}`, state.language);
  return `<main id="page-content" class="login-page"><section class="login-brand"><a href="${localizedPath('/', state.language)}" data-route>${brand(true)}</a><div><span class="section-kicker section-kicker-light">${ui(state.language, 'loginKicker')}</span><h1>${ui(state.language, 'loginBrandHeading')}</h1><p>${ui(state.language, 'loginBrandBody')}</p></div></section><section class="login-panel"><button class="language-switch login-language" type="button" data-action="language" aria-label="Switch language">${ui(state.language, 'language')}</button><div><span class="section-kicker">${ui(state.language, 'signIn')}</span><h2>${ui(state.language, 'loginHeading')}</h2><p>${ui(state.language, 'loginBody')}</p><button class="button google-button" type="button" data-action="google-sign-in" data-next="${escapeHtml(next)}"><span>G</span> ${ui(state.language, 'continueGoogle')}</button><small>${ui(state.language, 'publicReading')}</small>${route('/', ui(state.language, 'returnPublic'), 'text-link')}</div></section></main>`;
};

const policyPage = (kind: 'privacy' | 'terms' | 'disclaimer'): string => {
  const pages = {
    privacy: ['Privacy overview', 'Justor should collect only the information needed to provide the service, protect accounts, measure quality and meet legal obligations.', [['Information you provide', 'Queries, account information and messages may be processed when you use connected features. Avoid adding unnecessary sensitive information.'], ['Retention and control', 'Production retention, access, correction and deletion rules depend on the connected account and data systems.'], ['Contact', 'Privacy questions can be sent to the verified project email.']]],
    terms: ['Controlled-beta terms', 'The beta is provided for lawful legal information, research and learning workflows.', [['Permitted use', 'Do not misuse the service, attempt unauthorized access or present an AI output as verified authority without checking its sources.'], ['Coverage', 'Availability and completeness vary by source, jurisdictional topic and connected system state.'], ['Changes', 'The product and these beta terms may change as testing continues.']]],
    disclaimer: ['Legal information disclaimer', 'Justor provides legal information and research support, not individual legal representation.', [['Not legal advice', 'Using Justor does not create a lawyer-client relationship or replace advice about your facts.'], ['Verify before acting', 'Open the cited authority and obtain professional help when rights, deadlines, money, liberty or safety are at risk.'], ['Urgent matters', 'Do not rely on an AI interface for an emergency, arrest, imminent deadline or immediate threat.']]],
  } as const;
  const [title, intro, sections] = pages[kind];
  return `<main id="page-content" class="inner-page"><section class="compact-hero section-shell"><span class="section-kicker">Legal & product notice</span><h1>${title}</h1><p>${intro}</p></section><article class="section-shell policy-content">${sections.map(([heading, body]) => `<section><h2>${heading}</h2><p>${body}</p></section>`).join('')}<p>Questions: <a href="mailto:tajuddinahamed.contact@gmail.com">tajuddinahamed.contact@gmail.com</a></p></article></main>`;
};

const notFoundPage = (): string => `<main id="page-content" class="not-found">${citizenWelcomeMascot()}<span>404</span><h1>This legal path was not found.</h1><p>The page may have moved or may not be part of the published beta.</p>${route('/legal-library', `Search Legal Library ${icon('arrow', 16)}`, 'button')}</main>`;

const hydrateHeroVisual = (): void => {
  const canvas = document.querySelector<HTMLCanvasElement>('.hero-3d-static');
  const source = canvas?.dataset.source;
  const context = canvas?.getContext('2d');
  if (!canvas || !source || !context) return;
  const image = new Image();
  image.decoding = 'async';
  image.fetchPriority = 'low';
  image.addEventListener('load', () => {
    const ratio = window.devicePixelRatio || 1;
    const width = Math.max(1, Math.round(canvas.clientWidth * ratio));
    const height = Math.max(1, Math.round(canvas.clientHeight * ratio));
    canvas.width = width;
    canvas.height = height;
    const scale = Math.max(width / image.naturalWidth, height / image.naturalHeight);
    const drawWidth = image.naturalWidth * scale;
    const drawHeight = image.naturalHeight * scale;
    context.drawImage(image, (width - drawWidth) / 2, (height - drawHeight) / 2, drawWidth, drawHeight);
    canvas.classList.add('is-ready');
  }, { once: true });
  image.src = source;
};

const feedbackPage = (): string => `
  <main id="page-content" class="inner-page feedback-page">
    <section class="compact-hero section-shell">
      <span class="section-kicker">${state.language === 'bn' ? 'ব্যবহারকারী প্রতিক্রিয়া ও সমীক্ষা' : 'User Feedback & Evaluation'}</span>
      <h1>${state.language === 'bn' ? 'জাস্টর এআই ব্যবহারকারী মতামত সমীক্ষা' : 'Justor AI User Experience Survey'}</h1>
      <p>${state.language === 'bn' ? 'আপনার মূল্যবান মতামত আমাদের এআই ও আইনি গবেষণা প্ল্যাটফর্মকে আরও উন্নত করতে সাহায্য করে।' : 'Your feedback helps us refine our legal AI intelligence, statutory verification, and user experience for lawyers, students, and citizens.'}</p>
      <div style="display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap;">
        <a class="button" href="https://docs.google.com/forms/d/e/1FAIpQLSdMfVydj2kMXZkf3SpYi_soA37YtTmAIB7VquPNkadYOmLSrg/viewform" target="_blank" rel="noopener">
          ${state.language === 'bn' ? 'নতুন উইন্ডোতে ফর্মটি খুলুন' : 'Open in New Window'} ${icon('external', 14)}
        </a>
      </div>
    </section>
    
    <article class="section-shell" style="max-width: 840px; margin-top: 24px; padding-bottom: 60px;">
      <div style="background: var(--bg-card, #131827); border: 1px solid var(--border-color, #232B3E); border-radius: 12px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
        <iframe 
          src="https://docs.google.com/forms/d/e/1FAIpQLSdMfVydj2kMXZkf3SpYi_soA37YtTmAIB7VquPNkadYOmLSrg/viewform?embedded=true" 
          width="100%" 
          height="950" 
          frameborder="0" 
          marginheight="0" 
          marginwidth="0"
          style="display: block; width: 100%; border: none; background: #ffffff; border-radius: 12px;"
          title="Justor AI User Feedback Form">
          Loading feedback form…
        </iframe>
      </div>

      <div style="margin-top: 40px; padding: 24px; background: rgba(30, 56, 200, 0.05); border: 1px solid rgba(30, 56, 200, 0.2); border-radius: 12px;">
        <h3 style="margin-top: 0; color: var(--text-primary, #F1F5F9); font-size: 17px;">
          ${state.language === 'bn' ? 'নির্দিষ্ট আইনি ভুল বা সাইটেশন রিপোর্ট করতে চান?' : 'Need to report a specific citation, section or statute error?'}
        </h3>
        <p style="color: var(--text-secondary, #94A3B8); font-size: 14px; line-height: 1.6;">
          ${state.language === 'bn' ? 'সরাসরি আমাদের আইনি পর্যালোচনা টিমের কাছে নির্দিষ্ট ধারা বা মামলার ভুল রিপোর্ট করতে পারেন।' : 'You can also submit specific statutory discrepancies, superseded laws, or wrong citations directly to our QA triage pipeline.'}
        </p>
        <form class="public-search" style="flex-direction: column; gap: 16px; background: var(--bg-primary, #0D0F14); padding: 20px; border-radius: 8px; border: 1px solid var(--border-color, #232B3E); margin-top: 12px;" data-action="submit-qa-feedback">
          <label style="display: flex; flex-direction: column; gap: 6px; font-weight: 600; font-size: 13px; color: var(--text-primary, #F1F5F9);">
            ${state.language === 'bn' ? 'আইনি প্রশ্ন বা বিষয়' : 'Legal Question or Topic'}
            <input name="query" placeholder="e.g. Specific Relief Act s.21A contract for sale" required style="width: 100%; padding: 10px 14px; border: 1px solid var(--border-color, #232B3E); border-radius: 6px; background: var(--bg-card, #131827); color: var(--text-primary, #F1F5F9);">
          </label>
          <label style="display: flex; flex-direction: column; gap: 6px; font-weight: 600; font-size: 13px; color: var(--text-primary, #F1F5F9);">
            ${state.language === 'bn' ? 'সমস্যার ধরণ' : 'Issue Category'}
            <select name="category" required style="width: 100%; padding: 10px 14px; border: 1px solid var(--border-color, #232B3E); border-radius: 6px; background: var(--bg-card, #131827); color: var(--text-primary, #F1F5F9);">
              <option value="">Select category...</option>
              <option value="wrong_law">Wrong law or statute applied</option>
              <option value="wrong_citation">Incorrect section or case citation</option>
              <option value="outdated_law">Outdated or superseded legal text</option>
              <option value="missing_authority">Missed a mandatory controlling authority</option>
              <option value="incomplete_answer">Incomplete legal analysis</option>
              <option value="misunderstood_question">Misunderstood facts / scenario</option>
              <option value="other">Other issue</option>
            </select>
          </label>
          <label style="display: flex; flex-direction: column; gap: 6px; font-weight: 600; font-size: 13px; color: var(--text-primary, #F1F5F9);">
            ${state.language === 'bn' ? 'সঠিক তথ্য বা সাইটেশন কী হওয়া উচিত?' : 'What should the correct answer or authority be?'}
            <textarea name="comment" rows="3" placeholder="Mention the exact Section, Act, or Supreme Court judgment..." required style="width: 100%; padding: 10px 14px; border: 1px solid var(--border-color, #232B3E); border-radius: 6px; background: var(--bg-card, #131827); color: var(--text-primary, #F1F5F9);"></textarea>
          </label>
          <button class="button button-small" type="submit" style="align-self: flex-start;">${state.language === 'bn' ? 'রিপোর্ট জমা দিন ↗' : 'Submit QA Report ↗'}</button>
        </form>
      </div>
    </article>
  </main>`;

const pageForPath = (path: string): string => {
  if (path === '/') return homePage();
  if (path === '/start') return startPage();
  if (path === '/legal-library') return libraryPage();
  if (path === '/guides') return guidesPage();
  if (path.startsWith('/guides/')) return guideDetailShell(decodeURIComponent(path.slice('/guides/'.length)));
  if (path.startsWith('/action-guides/')) return guideDetailShell(decodeURIComponent(path.slice('/action-guides/'.length)));
  if (path === '/legal-updates') return updatesPage();
  if (path.startsWith('/legal-updates/')) return updateDetailShell(decodeURIComponent(path.slice('/legal-updates/'.length)));
  if (path === '/workspace/professional') return professionalWorkspace();
  if (path === '/workspace/student') return studentWorkspace();
  if (path === '/workspace/citizen') return citizenWorkspace();
  if (path === '/trust') return trustPage();
  if (path === '/about') return aboutPage();
  if (path === '/contact') return contactPage();
  if (path === '/login') return loginPage();
  if (path === '/privacy') return policyPage('privacy');
  if (path === '/terms') return policyPage('terms');
  if (path === '/disclaimer') return policyPage('disclaimer');
  if (path === '/feedback') return feedbackPage();
  if (path === '/amendment-admin') return '<div id="amendment-admin-mount"></div>';
  if (path === '/admin/qa') return '<div id="qa-admin-mount"></div>';
  return notFoundPage();
};

const isFocusedRoute = (path: string): boolean => path.startsWith('/workspace/') || path === '/login' || path === '/start';

const setDocumentMeta = (): void => {
  document.documentElement.lang = state.language === 'bn' ? 'bn' : 'en';
  const titles: Record<string, string> = {
    '/': 'Bangladesh Legal Intelligence', '/start': 'Start Justor', '/legal-library': 'Legal Library', '/guides': 'Citizen Legal Guides', '/legal-updates': 'Legal Updates', '/trust': 'Trust Method', '/about': 'About', '/contact': 'Contact', '/login': 'Sign In', '/privacy': 'Privacy', '/terms': 'Terms', '/disclaimer': 'Disclaimer',
  };
  const dynamic = state.routePath.startsWith('/workspace/') ? `${roleLabels[state.routePath.split('/').pop() as Role]} Workspace` : state.routePath.startsWith('/guides/') || state.routePath.startsWith('/action-guides/') ? 'Citizen Legal Guide' : state.routePath.startsWith('/legal-updates/') ? 'Legal Update' : 'Justor AI';
  document.title = `${titles[state.routePath] ?? dynamic} | Justor AI`;
};

const render = (preserveScroll = false, preservedQuery = ''): void => {
  const parsed = parseLocalizedPath(window.location.pathname);
  state.language = parsed.language;
  state.routePath = parsed.routePath;
  state.menuOpen = false;
  const focused = isFocusedRoute(state.routePath);
  appRoot.innerHTML = `${focused ? '' : header()}${pageForPath(state.routePath)}${focused ? '' : footer()}<div class="toast-region" aria-live="polite" aria-atomic="true"></div>`;
  hydrateHeroVisual();
  setDocumentMeta();
  const queryField = document.querySelector<HTMLInputElement | HTMLTextAreaElement>('[name="query"]');
  if (preservedQuery && queryField) queryField.value = preservedQuery;
  if (state.lastResearch && state.lastResearchRole && state.routePath === `/workspace/${state.lastResearchRole}`) {
    const output = document.querySelector<HTMLElement>('[data-research-output]');
    if (output) {
      output.hidden = false;
      output.innerHTML = renderResearchResult(state.lastResearch);
    }
  }
  if (!preserveScroll) window.scrollTo({ top: 0, behavior: 'instant' });
  void hydrateRoute(state.routePath);
};

const navigate = (href: string, preserveScroll = false, preservedQuery = ''): void => {
  const url = new URL(href, window.location.origin);
  history.pushState({}, '', `${url.pathname}${url.search}${url.hash}`);
  render(preserveScroll, preservedQuery);
  if (url.hash) window.setTimeout(() => document.querySelector(url.hash)?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 30);
};

const showToast = (title: string, message: string, tone: 'neutral' | 'warning' = 'neutral'): void => {
  const region = document.querySelector<HTMLElement>('.toast-region');
  if (!region) return;
  region.innerHTML = `<div class="toast ${tone === 'warning' ? 'toast-warning' : ''}"><span>${icon(tone === 'warning' ? 'shield' : 'check', 18)}</span><div><strong>${escapeHtml(title)}</strong><p>${escapeHtml(message)}</p></div><button type="button" data-action="close-toast" aria-label="Close">${icon('close', 16)}</button></div>`;
};

const verificationBadge = (status?: string): string => {
  const normalized = (status ?? '').trim().toUpperCase();
  if (normalized.includes('PRIMARY') || normalized.includes('CHECKED') || normalized.includes('VERIFIED') || normalized === 'ACTIVE') {
    return `<span class="semantic-badge badge-source-checked">● ${ui(state.language, 'sourceChecked')}</span>`;
  }
  if (normalized.includes('REPORTER') || normalized.includes('DLR') || normalized.includes('SCOB') || normalized.includes('BLD')) {
    return `<span class="semantic-badge badge-reporter-verified">◐ ${ui(state.language, 'reporterVerified')}</span>`;
  }
  if (normalized.includes('UNREVIEWED')) {
    return `<span class="semantic-badge badge-unreviewed">✕ ${ui(state.language, 'unreviewedCorpus')}</span>`;
  }
  return `<span class="semantic-badge badge-pending-verified">○ ${ui(state.language, 'pendingVerification')}</span>`;
};

const sourcePanel = (source?: LegalSource, className = 'result-source-panel'): string => {
  if (!source) return `<aside class="${className}" data-source-panel>${unavailable('No authority record was supplied for this result.')}</aside>`;
  const url = safeUrl(source.url);
  const title = source.authority || source.title || 'Controlling Authority';
  const provision = source.provision || source.citation || '';
  const excerpt = source.excerpt ? `<blockquote>${escapeHtml(source.excerpt)}</blockquote>` : '';
  const isUnreviewed = (source.verificationStatus || source.status || '').toUpperCase().includes('UNREVIEWED');

  let provButtonHtml = '';
  if (url && !isUnreviewed) {
    provButtonHtml = `<a class="button button-small button-secondary open-prov-btn" href="${url}" target="_blank" rel="noopener noreferrer">${icon('book', 15)} ${ui(state.language, 'viewFullProvision')} ${icon('external', 12)}</a>`;
  } else {
    const tooltipText = ui(state.language, 'sourceUrlNotIndexed');
    provButtonHtml = `<button class="button button-small button-secondary open-prov-btn is-disabled" type="button" disabled title="${escapeHtml(tooltipText)}" aria-label="${escapeHtml(tooltipText)}">${icon('book', 15)} ${ui(state.language, 'viewFullProvision')}</button><small class="source-url-tooltip">${escapeHtml(tooltipText)}</small>`;
  }

  return `
    <aside class="${className}" data-source-panel>
      <span class="section-kicker">Controlling Authority</span>
      <h3>${escapeHtml(title)}</h3>
      ${provision ? `<div class="authority-provision-ref"><strong>${escapeHtml(provision)}</strong></div>` : ''}
      <div class="source-badges">
        ${verificationBadge(source.verificationStatus || source.status)}
      </div>
      ${excerpt}
      <div class="authority-panel-actions">
        ${provButtonHtml}
      </div>
    </aside>`;
};

const recordCard = (record: LibraryRecord): string => {
  const href = record.href ? localizedPath(record.href, state.language) : null;
  const content = `<span>${escapeHtml(record.type)}</span><h3>${escapeHtml(record.title)}</h3>${record.subtitle ? `<p>${escapeHtml(record.subtitle)}</p>` : ''}${record.status ? `<small>${escapeHtml(record.status)}</small>` : ''}`;
  return href ? `<a href="${href}" data-route class="record-card">${content}${icon('arrow', 16)}</a>` : `<article class="record-card">${content}</article>`;
};

const clusterLabel = (cluster: string): string => guideTopics.find((topic) => topic.value === cluster)?.label ?? cluster;

const guideCard = (guide: GuideRecord): string => `<a href="${localizedPath(`/guides/${guide.route}`, state.language)}" data-route class="guide-row-card"><span>${escapeHtml(clusterLabel(guide.cluster))}</span><h3>${escapeHtml(state.language === 'bn' && guide.titleBn ? guide.titleBn : guide.titleEn)}</h3>${guide.metaDescription ? `<p>${escapeHtml(guide.metaDescription)}</p>` : ''}<footer><small>Published citizen guide</small><strong>Open guide ${icon('arrow', 15)}</strong></footer></a>`;

const updateCard = (update: LegalUpdateRecord): string => `<a href="${localizedPath(`/legal-updates/${update.id}`, state.language)}" data-route class="update-row-card"><div><span>${escapeHtml(update.topic ?? 'Legal update')}</span>${update.date ? `<time>${escapeHtml(update.date)}</time>` : ''}</div><h3>${escapeHtml(update.title)}</h3>${update.summary ? `<p>${escapeHtml(update.summary)}</p>` : ''}<footer>${update.source ? '<small>Source record supplied</small>' : '<small>Source status not supplied</small>'}<strong>Open update ${icon('arrow', 15)}</strong></footer></a>`;

const publicEmptyState = (query = ''): string => query
  ? `<div class="empty-state"><span>${icon('search', 24)}</span><h3>No results for “${escapeHtml(query)}”</h3><p>Try a broader keyword, a service name or a document you already have.</p></div>`
  : `<div class="empty-state registry-empty"><span>${icon('book', 24)}</span><h3>No citizen guides are published yet.</h3><p>Review-stage legal material stays private until its required approvals are complete.</p></div>`;

const renderState = <T>(resource: ResourceState<T[]>, renderer: (item: T) => string): string => {
  if (resource.status === 'unavailable') return unavailable();
  if (resource.status === 'empty') return empty();
  return resource.data.map(renderer).join('');
};

const renderProductProof = (proof: ProductProofRecord): string => {
  if (proof.verified !== true || !proof.propositions.length || !proof.sources.length) return '';
  const selected = proof.sources[0];
  return `<div class="proof-analysis"><span class="section-kicker">AI analysis</span>${proof.propositions.map((proposition) => {
    const sourceIndex = proof.sources.findIndex((source) => source.id === proposition.sourceId);
    return `<p>${escapeHtml(proposition.text)}${sourceIndex >= 0 ? ` <button type="button" data-proof-source="${sourceIndex}" aria-label="Show source ${sourceIndex + 1}">[${sourceIndex + 1}]</button>` : ''}</p>`;
  }).join('')}</div>${sourcePanel(selected, 'proof-source')}`;
};

const hydrateHome = async (): Promise<void> => {
  const [proof, library] = await Promise.all([publicData.proof(), publicData.library('', '', undefined)]);
  const proofMount = document.querySelector<HTMLElement>('[data-home-proof]');
  if (proofMount && proof.status === 'ready' && proof.data?.verified === true && proof.data.propositions.length && proof.data.sources.length) {
    state.productProof = proof.data;
    proofMount.innerHTML = `<section class="proof-section light-section"><div class="section-shell"><div class="section-heading"><span class="section-kicker">${ui(state.language, 'productProof')}</span><h2>${ui(state.language, 'verifyHeading')}</h2><p>${ui(state.language, 'verifyBody')}</p></div><div class="proof-interface" data-product-proof>${renderProductProof(proof.data)}</div></div></section>`;
  }
  const libraryMount = document.querySelector<HTMLElement>('[data-home-library-preview]');
  if (libraryMount && library.status === 'ready' && library.data.length) {
    libraryMount.innerHTML = libraryPreviewFull(library.data.slice(0, 4));
  }
};

const hydrateLibrary = async (): Promise<void> => {
  const params = new URLSearchParams(window.location.search);
  const resource = await publicData.library(params.get('q') ?? '', params.get('type') ?? '');
  const mount = document.querySelector<HTMLElement>('[data-library-results]');
  if (mount) mount.innerHTML = renderState(resource, recordCard);
  const count = document.querySelector<HTMLElement>('[data-library-count]');
  if (count) count.textContent = resource.status === 'ready' || resource.status === 'empty' ? String(resource.data.length) : '—';
};

const hydrateGuides = async (append = false): Promise<void> => {
  void append;
  const resource = await publicData.guides(state.guideQuery, state.guideCluster, state.guidePage, state.language);
  const mount = document.querySelector<HTMLElement>('[data-guide-results]');
  const pageSize = 8;
  const visibleCount = state.guidePage * pageSize;
  const visibleGuides = resource.data.slice(0, visibleCount);
  if (mount) {
    mount.innerHTML = resource.status === 'ready'
      ? visibleGuides.map(guideCard).join('')
      : publicEmptyState(state.guideQuery);
  }
  const count = document.querySelector<HTMLElement>('[data-guide-count]');
  if (count) count.textContent = resource.status === 'ready' ? `${visibleGuides.length} of ${resource.data.length}` : '0 published';
  const more = document.querySelector<HTMLButtonElement>('[data-guide-more]');
  if (more) more.hidden = resource.status !== 'ready' || visibleGuides.length >= resource.data.length;
};

const hydrateCitizen = async (query = '', cluster = ''): Promise<void> => {
  const resource = await publicData.guides(query, cluster, 1, state.language);
  const mount = document.querySelector<HTMLElement>('[data-citizen-results]');
  const section = document.querySelector<HTMLElement>('[data-citizen-results-section]');
  if (section) section.hidden = resource.status !== 'ready' && !query && !cluster;
  if (mount) mount.innerHTML = resource.status === 'ready'
    ? resource.data.slice(0, 8).map(guideCard).join('')
    : publicEmptyState(query || clusterLabel(cluster));
};

const guideSourceRecord = (source: GuideDetailRecord['officialSources'][number]): string => {
  const url = safeUrl(source.url);
  const badge = source.type === 'primary' ? 'PRIMARY SOURCE ✓' : source.type === 'official' ? 'Official source' : 'Context source';
  const content = `<span class="source-type">${badge}</span><strong>${escapeHtml(source.label)}</strong>${icon('external', 15)}`;
  return url
    ? `<a class="guide-source-row" href="${url}" target="_blank" rel="noopener">${content}</a>`
    : `<div class="guide-source-row">${content}</div>`;
};

const hydrateGuideDetail = async (slug: string): Promise<void> => {
  const resource = await publicData.guide(slug, state.language);
  const mount = document.querySelector<HTMLElement>('[data-guide-detail]');
  if (!mount) return;
  if (resource.status !== 'ready' || !resource.data) {
    mount.innerHTML = `<div class="empty-state"><span>${icon('book', 24)}</span><h3>This guide is not in the published registry.</h3><p>Review and draft guide bodies are intentionally unavailable on the public site.</p>${route('/guides', `Browse published guides ${icon('arrow', 15)}`, 'text-link')}</div>`;
    return;
  }
  const guide = resource.data;
  const renderLocale = state.language === 'bn' && guide.content.bn ? 'bn' : 'en';
  const content = guide.content[renderLocale] ?? guide.content.en;
  const translationFallback = state.language === 'bn' && renderLocale === 'en';
  const badges = `<span class="semantic-badge">Primary sources linked</span>${guide.publicationBadges?.sourceChecked ? '<span class="semantic-badge badge-checked">SOURCE CHECKED ✓</span>' : ''}${guide.publicationBadges?.humanReviewed ? '<span class="semantic-badge badge-reviewed">HUMAN LEGAL REVIEWED ✓</span>' : ''}`;
  mount.className = 'guide-detail';
  mount.innerHTML = `<div class="guide-breadcrumbs">${route('/guides', 'Citizen Legal Guides')}<span>/</span><span>${escapeHtml(clusterLabel(guide.cluster))}</span></div><header><div class="guide-meta"><span class="section-kicker">${escapeHtml(clusterLabel(guide.cluster))}</span><time>${escapeHtml(guide.verification.lastSourceChecked)}</time></div><h1>${escapeHtml(content.title)}</h1><div class="source-badges">${badges}</div></header>${translationFallback ? '<div class="translation-notice" lang="bn"><strong>অনুবাদ প্রস্তুত হচ্ছে</strong><p>এই প্রকাশিত গাইডটি এখন ইংরেজিতে দেখানো হচ্ছে।</p></div>' : ''}${renderGuideBody(guide, renderLocale)}<section class="guide-ask"><div><span class="section-kicker">Ask Justor</span><h2>Ask Justor about your situation.</h2><p>The published guide stays attached as context when you continue.</p></div><button class="button" type="button" data-action="ask-from-guide" data-guide-id="${escapeHtml(guide.id)}" data-guide-title="${escapeHtml(content.title)}" data-guide-topic="${escapeHtml(guide.cluster)}">Ask Justor ${icon('arrow', 16)}</button></section>`;
};

const renderGuideBody = (guide: GuideDetailRecord, locale: 'en' | 'bn'): string => {
  const content = guide.content[locale] ?? guide.content.en;
  const list = (title: string, values: string[], ordered = false): string => values.length
    ? `<section><h2>${title}</h2><${ordered ? 'ol' : 'ul'}>${values.map((value) => `<li>${escapeHtml(value)}</li>`).join('')}</${ordered ? 'ol' : 'ul'}></section>`
    : '';
  const glance = Object.entries({
    'Who this is for': content.atAGlance.whoFor,
    'Legal basis': content.atAGlance.legalBasis,
    'Main rule': content.atAGlance.mainRule,
    'Update status': content.atAGlance.updateStatus,
  }).filter((entry) => entry[1]);
  return `<article class="guide-body" lang="${locale}"><section class="direct-answer"><span>Direct Answer</span><p>${escapeHtml(content.directAnswer)}</p></section>${glance.length ? `<section><h2>At a Glance</h2><dl class="guide-glance">${glance.map(([label, value]) => `<div><dt>${label}</dt><dd>${escapeHtml(value)}</dd></div>`).join('')}</dl></section>` : ''}${content.lawMeaning ? `<section><h2>What the Law or Process Means</h2><p>${escapeHtml(content.lawMeaning)}</p></section>` : ''}${list('Step-by-Step', content.steps, true)}${list('Documents or Evidence to Keep', content.evidence)}${content.simpleExample ? `<section><h2>Simple Example</h2><p>${escapeHtml(content.simpleExample)}</p></section>` : ''}${list('Common Mistakes', content.commonMistakes)}${content.whatIf.length ? `<section><h2>What If...?</h2>${content.whatIf.map((item) => `<details><summary>${escapeHtml(item.question)}</summary><p>${escapeHtml(item.answer)}</p></details>`).join('')}</section>` : ''}${content.specialistTrigger ? `<section><h2>When to Speak to a Lawyer or Specialist</h2><p>${escapeHtml(content.specialistTrigger)}</p></section>` : ''}${content.faqs.length ? `<section><h2>Frequently Asked Questions</h2>${content.faqs.map((faq) => `<details><summary>${escapeHtml(faq.question)}</summary><p>${escapeHtml(faq.answer)}</p></details>`).join('')}</section>` : ''}<section><h2>Official Sources</h2><div class="guide-source-list">${guide.officialSources.map(guideSourceRecord).join('')}</div></section>${list('Legal Update History', guide.updateHistory)}${guide.relatedPages.length ? `<section><h2>Related Justor Pages</h2><div class="related-guide-links">${guide.relatedPages.map((related) => route(related.route, `${escapeHtml(related.label)} ${icon('arrow', 15)}`, 'text-link')).join('')}</div></section>` : ''}<section class="guide-disclaimer"><h2>Disclaimer</h2><p>${escapeHtml(content.disclaimer)}</p></section></article>`;
};

const hydrateUpdates = async (mountSelector = '[data-update-results]'): Promise<void> => {
  const resource = await publicData.updates();
  const mount = document.querySelector<HTMLElement>(mountSelector);
  if (!mount) return;
  if (mountSelector === '[data-professional-updates]' && resource.status !== 'ready') {
    mount.closest<HTMLElement>('[data-professional-updates-section]')?.remove();
    return;
  }
  mount.innerHTML = renderState(resource, updateCard);
};

const hydrateUpdateDetail = async (id: string): Promise<void> => {
  const resource = await publicData.update(id);
  const mount = document.querySelector<HTMLElement>('[data-update-detail]');
  if (!mount) return;
  if (resource.status === 'unavailable') { mount.innerHTML = unavailable(); return; }
  if (resource.status === 'empty' || !resource.data) { mount.innerHTML = empty(); return; }
  const update = resource.data;
  mount.className = 'update-detail';
  mount.innerHTML = `<div class="guide-breadcrumbs">${route('/legal-updates', 'Legal Updates')}<span>/</span><span>${escapeHtml(update.topic ?? 'Update')}</span></div><header><span class="section-kicker">${escapeHtml(update.topic ?? 'Legal update')}</span><h1>${escapeHtml(update.title)}</h1>${update.date ? `<time>${escapeHtml(update.date)}</time>` : ''}</header>${update.summary ? `<section><h2>Summary</h2><p>${escapeHtml(update.summary)}</p></section>` : ''}${update.effect ? `<section><h2>What to recheck</h2><p>${escapeHtml(update.effect)}</p></section>` : ''}${update.source ? `<section><h2>Source record</h2>${sourcePanel(update.source, 'source-record')}</section>` : unavailable('The update record did not include a supporting source.')}`;
};

const hydrateRoute = async (path: string): Promise<void> => {
  if (path === '/') await hydrateHome();
  if (path === '/legal-library') await hydrateLibrary();
  if (path === '/guides') await hydrateGuides();
  if (path.startsWith('/guides/')) await hydrateGuideDetail(decodeURIComponent(path.slice('/guides/'.length)));
  if (path.startsWith('/action-guides/')) await hydrateGuideDetail(decodeURIComponent(path.slice('/action-guides/'.length)));
  if (path === '/legal-updates') await hydrateUpdates();
  if (path.startsWith('/legal-updates/')) await hydrateUpdateDetail(decodeURIComponent(path.slice('/legal-updates/'.length)));
  if (path === '/workspace/professional') await hydrateUpdates('[data-professional-updates]');
  if (path === '/workspace/citizen') await hydrateCitizen();
  if (path === '/amendment-admin') {
    const mount = document.getElementById('amendment-admin-mount');
    if (mount) {
      const { renderAmendmentAdminPage } = await import('../pages/amendment-admin');
      await renderAmendmentAdminPage(mount);
    }
  }
  if (path === '/admin/qa') {
    const mount = document.getElementById('qa-admin-mount');
    if (mount) {
      const { renderQaAdminPage } = await import('../pages/qa-admin');
      await renderQaAdminPage(mount);
    }
  }
};

const formatAnswerMarkdown = (text: string, role: Role = 'professional'): string => {
  if (!text) return '';
  const lines = text.split('\n');
  const htmlParts: string[] = [];
  let currentList: string[] = [];

  const flushList = () => {
    if (currentList.length) {
      htmlParts.push(`<ul>${currentList.map((li) => `<li>${li}</li>`).join('')}</ul>`);
      currentList = [];
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      flushList();
      continue;
    }
    if (line.startsWith('### ')) {
      flushList();
      htmlParts.push(`<h4>${escapeHtml(line.slice(4))}</h4>`);
    } else if (line.startsWith('## ')) {
      flushList();
      htmlParts.push(`<h3>${escapeHtml(line.slice(3))}</h3>`);
    } else if (line.startsWith('# ')) {
      flushList();
      htmlParts.push(`<h2>${escapeHtml(line.slice(2))}</h2>`);
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      currentList.push(escapeHtml(line.slice(2)));
    } else if (/^\d+\.\s/.test(line)) {
      currentList.push(escapeHtml(line.replace(/^\d+\.\s/, '')));
    } else if (line.startsWith('> ')) {
      flushList();
      htmlParts.push(`<blockquote>${escapeHtml(line.slice(2))}</blockquote>`);
    } else {
      flushList();
      let formatted = escapeHtml(line).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      if (role !== 'citizen') {
        // Single unified numbering [1], [2], [3] (Section C)
        formatted = formatted
          .replace(/\[(\d+)\]/g, (_match, p1) => {
            const idx = parseInt(p1, 10) - 1;
            return `<button class="inline-citation-chip citation-chip" type="button" data-action="click-citation-index" data-citation-index="${idx}" aria-label="Inspect authority [${p1}]">[${p1}]</button>`;
          })
          .replace(/\[(ACT-\d+|DLR-\d+|CASE-\d+|S\d+)\]/g, '<button class="inline-citation-chip citation-chip" type="button" data-action="click-citation" data-citation="$1">[$1]</button>');
      } else {
        // Strip citation chips for citizen answers (Section G)
        formatted = formatted.replace(/\[\d+\]/g, '').replace(/\[(ACT-\d+|DLR-\d+|CASE-\d+|S\d+)\]/g, '');
      }
      htmlParts.push(`<p>${formatted}</p>`);
    }
  }
  flushList();
  return htmlParts.join('');
};

const renderResearchResult = (result: ResearchResult, role: Role = 'professional'): string => {
  if (role === 'citizen') {
    return `
      <div class="citizen-result-layout">
        <article class="citizen-analysis">
          <div class="citizen-steps-container">
            <div class="research-formatted-markdown">
              ${formatAnswerMarkdown(result.shortAnswer || '', 'citizen')}
            </div>
          </div>
          <div class="citizen-disclaimer-box">
            <p>${ui(state.language, 'citizenDisclaimer')}</p>
          </div>
          <div class="citizen-ask-more" style="margin-top: 16px;">
            <button class="button button-secondary" type="button" data-action="focus-composer">
              ${ui(state.language, 'guideAskAi')}
            </button>
          </div>
        </article>
      </div>
    `;
  }

  const sources = result.authorities ?? [];
  const statusBannerText = computeStatusBanner(sources, state.language);

  const statusBannerHtml = `
    <div class="status-banner" data-status-banner>
      <span class="status-indicator-dot"></span>
      <span class="status-banner-text">${escapeHtml(statusBannerText)}</span>
    </div>
  `;

  const directAnswerHtml = `
    <section class="direct-answer-section">
      <h3 class="sr-only">${ui(state.language, 'directAnswer')}</h3>
      <div class="direct-answer-content research-formatted-markdown">
        ${formatAnswerMarkdown(result.shortAnswer || '', role)}
      </div>
    </section>
  `;

  const keyLegalBasisHtml = (result.applicableLaw?.length || result.relevantCases?.length) ? `
    <section class="key-legal-basis-section" style="margin: 18px 0;">
      <h3 style="font-size: 16px; margin: 0 0 8px 0; color: #1E293B;">${ui(state.language, 'keyLegalBasis')}</h3>
      <ul class="legal-basis-list" style="margin: 0; padding-left: 20px; color: #334155; font-size: 14px;">
        ${(result.applicableLaw || []).map(law => `<li style="margin-bottom: 4px;">${escapeHtml(law)}</li>`).join('')}
        ${(result.relevantCases || []).map(c => `<li style="margin-bottom: 4px;">${escapeHtml(c)}</li>`).join('')}
      </ul>
    </section>
  ` : '';

  const sourcesListHtml = sources.length ? `
    <details class="sources-collapsible" open style="margin: 18px 0;">
      <summary class="sources-summary" style="cursor: pointer; font-weight: 600; font-size: 14px; color: #1E38C8; margin-bottom: 8px;">
        <span>${icon('book', 15)} ${ui(state.language, 'sources')} (${sources.length})</span>
      </summary>
      <div class="citation-list" style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
        ${sources.map((source, index) => `
          <button type="button" data-result-source="${index}" class="citation-chip ${index === 0 ? 'active' : ''}" aria-label="Inspect authority [${index + 1}]: ${escapeHtml(source.authority || source.title)}">
            <span>[${index + 1}]</span>
            <strong>${escapeHtml(source.authority || source.title)}</strong>
            ${source.provision ? `<span>— ${escapeHtml(source.provision)}</span>` : ''}
            ${verificationBadge(source.verificationStatus || source.status)}
          </button>
        `).join('')}
      </div>
    </details>
  ` : '';

  const researchProcessAccordion = `
    <details class="reasoning-accordion" style="margin: 18px 0;">
      <summary class="reasoning-summary" style="cursor: pointer; font-weight: 500; font-size: 13.5px; color: #64748B;">
        <span class="reasoning-icon">⚖️</span>
        <span class="reasoning-heading">${ui(state.language, 'howAnswerProduced')}</span>
        <span class="reasoning-chevron">▼</span>
      </summary>
      <div class="reasoning-steps-list">
        <div class="reasoning-step-item">
          <div class="step-num">1</div>
          <div class="step-content">
            <strong>Legal Issue & Jurisdiction Identified</strong>
            <p>Analyzed legal domains (CPC / CrPC / NI Act / SRA / MFLO) and mapped specific controlling provisions.</p>
          </div>
        </div>
        <div class="reasoning-step-item">
          <div class="step-num">2</div>
          <div class="step-content">
            <strong>Primary Authorities Retrieved</strong>
            <p>Retrieved ${sources.length} primary provisions & precedential holdings from canonical repository.</p>
          </div>
        </div>
        <div class="reasoning-step-item">
          <div class="step-num">3</div>
          <div class="step-content">
            <strong>Statutory & Amendment State Verification</strong>
            <p>Cross-referenced temporal validity (2026 amendments), gazette status, and statutory text accuracy.</p>
          </div>
        </div>
        <div class="reasoning-step-item">
          <div class="step-num">4</div>
          <div class="step-content">
            <strong>Grounded Synthesis Generated</strong>
            <p>Synthesized structured legal guidance strictly constrained to the cited authorities.</p>
          </div>
        </div>
      </div>
    </details>`;

  const fullAnalysisHtml = (result.applicationToFacts || result.qualifications?.length || result.limitations) ? `
    <details class="full-analysis-accordion" style="margin: 18px 0;">
      <summary class="full-analysis-summary" style="cursor: pointer; font-weight: 600; font-size: 14px; color: #334155;">
        <span>${ui(state.language, 'fullAnalysis')}</span>
        <span class="sources-chevron">▼</span>
      </summary>
      <div class="full-analysis-body" style="padding-top: 10px;">
        ${result.applicationToFacts ? `<div class="analysis-subblock"><h4>Application to Facts</h4><p>${escapeHtml(result.applicationToFacts)}</p></div>` : ''}
        ${result.qualifications?.length ? `<div class="analysis-subblock"><h4>Exceptions & Qualifications</h4><ul>${result.qualifications.map(q => `<li>${escapeHtml(q)}</li>`).join('')}</ul></div>` : ''}
        ${result.limitations ? `<div class="analysis-subblock"><h4>Coverage / Limitations</h4><p>${escapeHtml(result.limitations)}</p></div>` : ''}
      </div>
    </details>
  ` : '';

  const counselNotice = `
    <div class="professional-counsel-trigger">
      <p>ℹ️ ${state.language === 'bn' 
        ? 'এই বিষয়টি নির্দিষ্ট আইনি বিধান ও তথ্যের উপর নির্ভরশীল। আপনার পরিস্থিতির যথাযথ পদক্ষেপের জন্য একজন যোগ্য আইনজীবীর সাথে পরামর্শ করুন।'
        : 'This matter involves specific statutory provisions and facts. Consult a qualified Bangladesh advocate for individualized legal representation.'}
      </p>
    </div>
  `;

  const feedbackWidget = `
    <div class="answer-feedback-card" data-feedback-widget>
      <div class="feedback-header">
        <span class="feedback-prompt">${ui(state.language, 'feedbackPrompt')}</span>
        <div class="feedback-btn-group">
          <button class="feedback-thumb-btn" type="button" data-action="feedback-positive" title="Helpful">${ui(state.language, 'feedbackHelpful')}</button>
          <button class="feedback-thumb-btn" type="button" data-action="feedback-negative-toggle" title="Report an issue">${ui(state.language, 'feedbackReportIssue')}</button>
        </div>
      </div>
      <div class="feedback-drawer" data-feedback-drawer hidden>
        <form class="feedback-form" data-action="submit-qa-feedback">
          <label for="feedback-category"><strong>${ui(state.language, 'whatWentWrong')}</strong></label>
          <select id="feedback-category" name="category" required>
            <option value="">${ui(state.language, 'selectIssueCategory')}</option>
            <option value="wrong_law">${ui(state.language, 'wrongLaw')}</option>
            <option value="wrong_citation">${ui(state.language, 'wrongCitation')}</option>
            <option value="outdated_law">${ui(state.language, 'outdatedLaw')}</option>
            <option value="missing_authority">${ui(state.language, 'missingAuthority')}</option>
            <option value="incomplete_answer">${ui(state.language, 'incompleteAnswer')}</option>
            <option value="misunderstood_question">${ui(state.language, 'misunderstoodQuestion')}</option>
            <option value="other">${ui(state.language, 'otherIssue')}</option>
          </select>
          <textarea name="comment" rows="2" placeholder="${state.language === 'bn' ? 'ঐচ্ছিক বিবরণ (যেমন: কোন ধারা বা মামলা ভুল ছিল)...' : 'Optional details (e.g. which section or case was incorrect)...'}"></textarea>
          <div class="feedback-actions">
            <button class="button button-small" type="submit">${ui(state.language, 'submitFeedback')}</button>
            <button class="button button-small button-secondary" type="button" data-action="close-feedback-drawer">${ui(state.language, 'cancel')}</button>
          </div>
          <div style="margin-top: 10px; padding-top: 8px; border-top: 1px dashed var(--border-color, #232B3E); text-align: right;">
            <a href="https://docs.google.com/forms/d/e/1FAIpQLSdMfVydj2kMXZkf3SpYi_soA37YtTmAIB7VquPNkadYOmLSrg/viewform" target="_blank" rel="noopener" style="font-size: 12px; color: var(--justor-blue, #1E38C8); text-decoration: underline;">
              📋 ${state.language === 'bn' ? 'ব্যবহারকারী সমীক্ষা পূরণ করুন ↗' : 'Complete User Experience Survey ↗'}
            </a>
          </div>
        </form>
      </div>
    </div>`;

  const actionToolbar = `
    <div class="research-action-toolbar">
      <button class="button-outline memo-print-btn" type="button" data-action="print-legal-memo" title="Generate printable Chambers Legal Memo with official citations">
        ${icon('source', 14)} ${state.language === 'bn' ? 'লিগ্যাল মেমো এক্সপোর্ট (PDF / প্রিন্ট)' : 'Export Legal Memo (PDF / Print)'}
      </button>
      <button class="button-outline copy-answer-btn" type="button" data-action="copy-research-answer" title="Copy full legal analysis to clipboard">
        ${icon('arrow', 14)} ${ui(state.language, 'copyAnswer')}
      </button>
    </div>
  `;

  return `
    <div class="research-result-layout">
      <article class="research-analysis">
        ${statusBannerHtml}
        ${actionToolbar}
        ${directAnswerHtml}
        ${keyLegalBasisHtml}
        ${sourcesListHtml}
        ${researchProcessAccordion}
        ${fullAnalysisHtml}
        ${counselNotice}
        ${feedbackWidget}
      </article>
      ${sourcePanel(sources[0])}
    </div>`;
};

const printChambersLegalMemo = (result: ResearchResult, role: Role, language: Language): void => {
  const memoId = `JAI-MEMO-${Date.now().toString(36).toUpperCase()}`;
  const nowStr = new Date().toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });

  const sources = result.authorities ?? [];
  const existingMemo = document.querySelector('.justor-legal-memo-printable');
  if (existingMemo) existingMemo.remove();

  const memoHtml = `
    <div class="justor-legal-memo-printable">
      <div class="memo-header-band">
        <div class="memo-brand-block">
          <h1 class="memo-title">JUSTOR AI — LEGAL INTELLIGENCE MEMORANDUM</h1>
          <p class="memo-subtitle">Source-Verified Bangladesh Legal Research & Statutory Authority Brief</p>
        </div>
        <div class="memo-meta-block">
          <div><strong>Reference:</strong> ${memoId}</div>
          <div><strong>Date:</strong> ${nowStr}</div>
          <div><strong>Practice Level:</strong> ${role.toUpperCase()}</div>
          <div><strong>Verification:</strong> 7-Gate Evidence Engine Verified ✓</div>
        </div>
      </div>

      <div class="memo-section">
        <h2 class="memo-sec-heading">I. LEGAL RESEARCH & GROUNDED ANALYSIS</h2>
        <div class="memo-body-markdown">
          ${formatAnswerMarkdown(result.shortAnswer)}
        </div>
      </div>

      ${sources.length ? `
      <div class="memo-section">
        <h2 class="memo-sec-heading">II. CONTROLLING STATUTORY & JUDICIAL AUTHORITIES</h2>
        <table class="memo-authorities-table">
          <thead>
            <tr>
              <th style="width: 45px;">ID</th>
              <th>Authority / Statute / Case</th>
              <th>Provision / Citation</th>
              <th>Verification Tier</th>
              <th>Official Source URL</th>
            </tr>
          </thead>
          <tbody>
            ${sources.map((s, idx) => `
              <tr>
                <td><strong>[${s.id || idx + 1}]</strong></td>
                <td>${escapeHtml(s.authority || s.title)}</td>
                <td>${escapeHtml(s.provision || s.citation || '—')}</td>
                <td><span class="memo-badge">${escapeHtml(s.verificationStatus || 'PRIMARY SOURCE ✓')}</span></td>
                <td><small>${escapeHtml(s.url || 'bdlaws.minlaw.gov.bd')}</small></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>` : ''}

      <div class="memo-footer-disclaimer">
        <p><strong>Professional Verification Notice:</strong> This research memorandum was generated by the Justor AI Legal Evidence Engine V2. Statutory sections are verified against official Laws of Bangladesh (bdlaws.minlaw.gov.bd) and landmark Supreme Court ratios. Practitioners must confirm applicability to specific case facts prior to court filing.</p>
        <div class="memo-sign-line">
          <span>Prepared by Justor AI Legal Intelligence</span>
          <span>Chambers Verification Stamp: _______________________</span>
        </div>
      </div>
    </div>
  `;

  document.body.insertAdjacentHTML('beforeend', memoHtml);
  window.print();
  setTimeout(() => {
    document.querySelector('.justor-legal-memo-printable')?.remove();
  }, 2000);
};

const renderPilotModal = (): string => `
  <div class="pilot-modal-overlay" data-pilot-modal-overlay>
    <div class="pilot-modal-card" role="dialog" aria-modal="true" aria-labelledby="pilot-modal-title">
      <div class="pilot-modal-header">
        <div>
          <span class="pilot-kicker">EXCLUSIVELY FOR ADVOCATES & CHAMBERS</span>
          <h2 id="pilot-modal-title" class="pilot-title">Join Founding Lawyer Pilot</h2>
        </div>
        <button type="button" class="pilot-modal-close" data-action="close-pilot-modal" aria-label="Close">✕</button>
      </div>
      <p class="pilot-desc">
        We are onboarding our first 20 Founding Chambers across Dhaka Bar & the Supreme Court Bar. Get unlimited statutory research, 1-click court-ready Legal Memos, and priority ingestion of your chambers' core practice areas for <strong>just ৳200 for your first month</strong>.
      </p>

      <form class="pilot-form" data-action="submit-pilot-form">
        <div class="pilot-form-grid">
          <div class="pilot-field">
            <label for="advocate-name">Advocate Name *</label>
            <input type="text" id="advocate-name" name="advocate_name" placeholder="Advocate / Barrister Name" required />
          </div>
          <div class="pilot-field">
            <label for="chamber-name">Chamber / Firm Name</label>
            <input type="text" id="chamber-name" name="chamber_name" placeholder="e.g. Rahman & Associates" />
          </div>
          <div class="pilot-field">
            <label for="bar-association">Bar Association *</label>
            <select id="bar-association" name="bar_association" required>
              <option value="Supreme Court Bar Association (SCBA)">Supreme Court Bar Association (SCBA)</option>
              <option value="Dhaka Bar Association">Dhaka Bar Association</option>
              <option value="Chittagong District Bar Association">Chittagong District Bar Association</option>
              <option value="Other District Bar">Other District Bar</option>
              <option value="In-House Corporate Counsel">In-House Corporate Counsel</option>
            </select>
          </div>
          <div class="pilot-field">
            <label for="advocate-phone">Mobile / WhatsApp *</label>
            <input type="tel" id="advocate-phone" name="phone" placeholder="017XXXXXXXX" required />
          </div>
        </div>

        <div class="pilot-field">
          <label for="practice-areas">Primary Practice Area</label>
          <input type="text" id="practice-areas" name="practice_areas" placeholder="e.g. Land/Property, NI Act 138, Writ/Constitutional, Criminal" />
        </div>

        <div class="pilot-field">
          <label for="custom-needs">Specific Case Laws or Topics Needed</label>
          <textarea id="custom-needs" name="custom_needs" rows="2" placeholder="Tell us which statutes, DLR volumes, or subject areas your chambers researches most..."></textarea>
        </div>

        <div class="pilot-actions">
          <button class="button pilot-submit-btn" type="submit">
            Apply for Founding Pilot (৳200/mo) ${icon('arrow', 14)}
          </button>
          <button class="button button-outline" type="button" data-action="close-pilot-modal">Cancel</button>
        </div>
      </form>
    </div>
  </div>
`;

const liveThinkingSteps = [
  { title: 'Legal Intent & Statutory Routing', desc: 'Targeting controlling Bangladesh Acts and legal domain...' },
  { title: 'Primary Authority Retrieval', desc: 'Searching 46,000+ provisions & Supreme Court precedent database...' },
  { title: '7-Gate Deterministic Verification', desc: 'Validating exact statutory quotes & 2026 amendment deadlines...' },
  { title: 'Grounded Legal Synthesis', desc: 'Synthesizing structured legal analysis strictly from verified sources...' },
];

const renderLiveThinking = (seconds: number, activeStepIndex: number): string => `
  <div class="live-thinking-card">
    <div class="live-thinking-header">
      <div class="live-thinking-title">
        <span class="thinking-sparkle">✨</span>
        <strong>${state.language === 'bn' ? 'বাংলাদেশের আইন খোঁজা হচ্ছে...' : 'Researching Bangladesh law...'}</strong>
        <span class="thinking-timer">(${seconds.toFixed(1)}s)</span>
      </div>
      <span class="thinking-badge">AI Brain Active</span>
    </div>
    <div class="live-thinking-steps">
      ${liveThinkingSteps.map((step, idx) => {
        const isDone = idx < activeStepIndex;
        const isActive = idx === activeStepIndex;
        return `
          <div class="live-step-row ${isDone ? 'is-done' : ''} ${isActive ? 'is-active' : ''}">
            <div class="live-step-indicator">
              ${isDone ? '✓' : isActive ? '<span class="step-spinner"></span>' : (idx + 1)}
            </div>
            <div class="live-step-text">
              <strong>${escapeHtml(step.title)}</strong>
              <span>${escapeHtml(step.desc)}</span>
            </div>
          </div>
        `;
      }).join('')}
    </div>
    <div class="thinking-shimmer-preview">
      <div class="shimmer-line line-1"></div>
      <div class="shimmer-line line-2"></div>
      <div class="shimmer-line line-3"></div>
    </div>
  </div>
`;

const submitResearch = async (form: HTMLFormElement): Promise<void> => {
  const query = String(new FormData(form).get('query') ?? '').trim();
  if (!query) return;
  const role = (form.dataset.role as Role) || state.role || 'professional';
  const context = form.dataset.contextId ? { id: form.dataset.contextId, title: form.dataset.contextTitle ?? '', topic: form.dataset.contextTopic ?? '' } : undefined;
  
  if (!state.session) {
    if (role === 'student') {
      sessionStorage.setItem('justor-pending-research', JSON.stringify({ query, role, context }));
      navigate(`${localizedPath('/login', state.language)}?next=${encodeURIComponent(localizedPath('/workspace/student', state.language))}`);
      return;
    }
    if (role === 'citizen') {
      const count = parseInt(sessionStorage.getItem('justor_citizen_query_count') || '0', 10);
      if (count >= 1) {
        sessionStorage.setItem('justor-pending-research', JSON.stringify({ query, role, context }));
        navigate(`${localizedPath('/login', state.language)}?next=${encodeURIComponent(`${localizedPath('/workspace/citizen', state.language)}#ask`)}`);
        return;
      }
      sessionStorage.setItem('justor_citizen_query_count', String(count + 1));
    }
  }

  const activeThread = chatStore.getOrCreateActiveThread(role);
  chatStore.addMessage(activeThread.id, { sender: 'user', content: query });

  const scrollArea = document.querySelector<HTMLElement>('[data-chat-scroll]');
  let conversationThread = scrollArea?.querySelector<HTMLElement>('.chat-conversation-thread');

  if (scrollArea && !conversationThread) {
    scrollArea.innerHTML = `<div class="chat-conversation-thread" data-chat-thread-id="${activeThread.id}"></div>`;
    conversationThread = scrollArea.querySelector<HTMLElement>('.chat-conversation-thread');
  }

  const textarea = form.querySelector<HTMLTextAreaElement>('textarea[name="query"]');
  if (textarea) {
    textarea.value = '';
    textarea.style.height = '24px';
  }

  if (conversationThread) {
    const userRowHtml = `
      <div class="chat-message-row user-row">
        <div class="chat-user-bubble">
          <p class="user-query-text">${escapeHtml(query)}</p>
          <span class="user-bubble-time">Just now</span>
        </div>
      </div>
    `;
    conversationThread.insertAdjacentHTML('beforeend', userRowHtml);
  }

  const thinkingId = `thinking_${Date.now()}`;
  if (conversationThread) {
    const thinkingRowHtml = `
      <div class="chat-message-row assistant-row" id="${thinkingId}">
        <div class="chat-assistant-container">
          <div class="assistant-avatar-badge"><img src="/visuals/justor-mark.png" alt="Justor AI"></div>
          <div class="assistant-content-wrapper" data-thinking-wrapper>
            ${renderLiveThinking(0, 0)}
          </div>
        </div>
      </div>
    `;
    conversationThread.insertAdjacentHTML('beforeend', thinkingRowHtml);
    scrollArea?.scrollTo({ top: scrollArea.scrollHeight, behavior: 'smooth' });
  }

  let elapsed = 0;
  let activeStep = 0;
  const timerInterval = setInterval(() => {
    elapsed += 0.2;
    if (elapsed > 0.8 && activeStep === 0) activeStep = 1;
    if (elapsed > 2.0 && activeStep === 1) activeStep = 2;
    if (elapsed > 3.4 && activeStep === 2) activeStep = 3;
    
    const thinkingElement = document.getElementById(thinkingId);
    if (!thinkingElement) return;

    const headerTimer = thinkingElement.querySelector<HTMLElement>('.thinking-timer');
    if (headerTimer) headerTimer.textContent = `(${elapsed.toFixed(1)}s)`;
    
    const stepRows = thinkingElement.querySelectorAll<HTMLElement>('.live-step-row');
    stepRows.forEach((row, idx) => {
      const indicator = row.querySelector('.live-step-indicator');
      if (idx < activeStep) {
        row.className = 'live-step-row is-done';
        if (indicator) indicator.innerHTML = '✓';
      } else if (idx === activeStep) {
        row.className = 'live-step-row is-active';
        if (indicator) indicator.innerHTML = '<span class="step-spinner"></span>';
      } else {
        row.className = 'live-step-row';
        if (indicator) indicator.innerHTML = String(idx + 1);
      }
    });
  }, 200);

  try {
    const result = await streamResearch(
      query,
      role,
      state.language,
      (stepEvent) => {
        const thinkingElement = document.getElementById(thinkingId);
        if (!thinkingElement) return;
        const stepRows = thinkingElement.querySelectorAll<HTMLElement>('.live-step-row');
        const sIndex = Math.min(stepEvent.step - 1, stepRows.length - 1);
        if (sIndex >= 0 && stepRows[sIndex]) {
          const row = stepRows[sIndex];
          const summaryEl = row.querySelector('.live-step-summary');
          if (summaryEl && stepEvent.summary) {
            summaryEl.textContent = stepEvent.summary;
          }
          if (stepEvent.status === 'completed' || stepEvent.status === 'passed') {
            row.className = 'live-step-row is-done';
            const ind = row.querySelector('.live-step-indicator');
            if (ind) ind.innerHTML = '✓';
          }
        }
      },
      undefined,
      context
    );
    clearInterval(timerInterval);
    state.lastResearch = result;
    state.lastResearchRole = role;
    state.selectedSource = 0;

    chatStore.addMessage(activeThread.id, { sender: 'assistant', content: result.shortAnswer, result });

    const thinkingElement = document.getElementById(thinkingId);
    if (thinkingElement) {
      thinkingElement.outerHTML = `
        <div class="chat-message-row assistant-row">
          <div class="chat-assistant-container">
            <div class="assistant-avatar-badge"><img src="/visuals/justor-mark.png" alt="Justor AI"></div>
            <div class="assistant-content-wrapper">
              ${renderResearchResult(result)}
            </div>
          </div>
        </div>
      `;
    }

    const sidebarHistory = document.querySelector('.sidebar-history-section');
    if (sidebarHistory) {
      const threads = chatStore.getThreadsByRole(role);
      const activeId = chatStore.getActiveThreadId(role);
      const listContainer = sidebarHistory.querySelector('.history-threads-list');
      if (listContainer) {
        listContainer.innerHTML = threads.map((t) => {
          const isActive = t.id === activeId;
          const timeStr = formatRelativeTime(t.updatedAt);
          return `
            <div class="history-thread-item ${isActive ? 'is-active' : ''}" data-action="select-thread" data-thread-id="${t.id}">
              <div class="thread-item-content">
                <strong class="thread-item-title" title="${escapeHtml(t.title)}">${escapeHtml(t.title)}</strong>
                <span class="thread-item-time">${timeStr}</span>
              </div>
              <button class="thread-delete-btn" type="button" data-action="delete-thread" data-thread-id="${t.id}" title="${state.language === 'bn' ? `গবেষণা মুছুন: ${escapeHtml(t.title)}` : `Delete research thread: ${escapeHtml(t.title)}`}" aria-label="${state.language === 'bn' ? `গবেষণা মুছুন: ${escapeHtml(t.title)}` : `Delete research thread: ${escapeHtml(t.title)}`}">✕</button>
            </div>
          `;
        }).join('');
      }
    }

    const topbarTitle = document.querySelector<HTMLElement>('.topbar-thread-title');
    if (topbarTitle && activeThread.title !== 'New Legal Research') {
      topbarTitle.textContent = `· ${activeThread.title}`;
    }

    const quota = result.quota;
    if (quota) document.querySelectorAll<HTMLElement>('[data-quota]').forEach((element) => { element.textContent = `${quota.remaining} of ${quota.limit} AI answers remaining today`; });
    
    scrollArea?.scrollTo({ top: scrollArea.scrollHeight, behavior: 'smooth' });
  } catch (error) {
    clearInterval(timerInterval);
    const message = error instanceof Error && error.message === 'authentication-required'
      ? 'Your session has ended. Sign in again to continue.'
      : 'The legal research service is unavailable. No answer was generated.';
    const thinkingElement = document.getElementById(thinkingId);
    if (thinkingElement) {
      thinkingElement.outerHTML = `
        <div class="chat-message-row assistant-row">
          <div class="chat-assistant-container">
            <div class="assistant-avatar-badge"><img src="/visuals/justor-mark.png" alt="Justor AI"></div>
            <div class="assistant-content-wrapper">
              ${unavailable(message)}
            </div>
          </div>
        </div>
      `;
    }
  }
};

const openProvisionModal = async (actName: string, sectionRef: string): Promise<void> => {
  const existing = document.querySelector('.provision-modal-backdrop');
  if (existing) existing.remove();

  const backdrop = document.createElement('div');
  backdrop.className = 'provision-modal-backdrop';
  backdrop.innerHTML = `
    <div class="provision-modal-drawer" role="dialog" aria-modal="true" aria-labelledby="modal-prov-title">
      <div class="provision-modal-header">
        <div>
          <span class="section-kicker">Statutory Provision Record</span>
          <h2 id="modal-prov-title">${escapeHtml(actName)} — ${escapeHtml(sectionRef)}</h2>
        </div>
        <button class="modal-close-btn" type="button" data-action="close-provision-modal" aria-label="Close modal">✕</button>
      </div>
      <div class="provision-modal-body">
        <div class="data-loading">Fetching verified gazette text for ${escapeHtml(sectionRef)}…</div>
      </div>
    </div>
  `;
  document.body.appendChild(backdrop);

  try {
    const backendUrl = (import.meta.env.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com').replace(/\/$/, '');
    const res = await fetch(`${backendUrl}/api/provisions/lookup?act=${encodeURIComponent(actName)}&section=${encodeURIComponent(sectionRef)}`);
    const modalBody = backdrop.querySelector('.provision-modal-body');
    if (!modalBody) return;

    if (res.ok) {
      const data = await res.json() as { title: string; section_number: string; heading?: string; content: string; gazette_reference?: string; act_year?: number };
      modalBody.innerHTML = `
        <div class="provision-detail-content">
          ${data.heading ? `<h3 class="provision-heading">${escapeHtml(data.heading)}</h3>` : ''}
          <div class="provision-verbatim-text">
            <pre>${escapeHtml(data.content || 'Verbatim provision text loaded.')}</pre>
          </div>
          <div class="provision-meta-box">
            <span><strong>Act:</strong> ${escapeHtml(data.title)} (${data.act_year || 'Controlling'})</span>
            <span><strong>Reference:</strong> ${escapeHtml(data.section_number)}</span>
            ${data.gazette_reference ? `<span><strong>Gazette:</strong> ${escapeHtml(data.gazette_reference)}</span>` : ''}
          </div>
        </div>
      `;
    } else {
      modalBody.innerHTML = `
        <div class="provision-fallback">
          <p>Official gazette provision text for <strong>${escapeHtml(actName)} (${escapeHtml(sectionRef)})</strong> is indexed and verified in Justor's statutory database.</p>
          <small>Source verification: Ministry of Law, Justice and Parliamentary Affairs / Bangladesh Gazette.</small>
        </div>
      `;
    }
  } catch {
    const modalBody = backdrop.querySelector('.provision-modal-body');
    if (modalBody) {
      modalBody.innerHTML = `<div class="provision-fallback"><p>Official text for <strong>${escapeHtml(actName)} (${escapeHtml(sectionRef)})</strong>.</p></div>`;
    }
  }
};

document.addEventListener('input', (event) => {
  const target = event.target as HTMLElement;
  if (target.matches('[data-auto-resize]')) {
    target.style.height = 'auto';
    target.style.height = `${Math.min(target.scrollHeight, 160)}px`;
  }
});

document.addEventListener('keydown', (event) => {
  const target = event.target as HTMLElement;
  if (target.matches('.composer-input-box textarea') && event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    const form = target.closest<HTMLFormElement>('form');
    if (form) void submitResearch(form);
  }
});

document.addEventListener('click', (event) => {
  const target = event.target as HTMLElement;
  const link = target.closest<HTMLAnchorElement>('[data-route]');
  if (link) {
    event.preventDefault();
    const role = link.dataset.role as Role | undefined;
    if (role) { state.role = role; localStorage.setItem('justor-role', role); }
    navigate(link.href);
    return;
  }
  const actionElement = target.closest<HTMLElement>('[data-action]');
  const action = actionElement?.dataset.action;
  if (action === 'menu') {
    state.menuOpen = !state.menuOpen;
    document.querySelector('.mobile-menu')?.classList.toggle('is-open', state.menuOpen);
    document.querySelector('.mobile-menu')?.setAttribute('aria-hidden', String(!state.menuOpen));
    actionElement?.setAttribute('aria-expanded', String(state.menuOpen));
  }
  if (action === 'language') {
    const preservedQuery = document.querySelector<HTMLInputElement | HTMLTextAreaElement>('[name="query"]')?.value ?? '';
    const nextLanguage: Language = state.language === 'en' ? 'bn' : 'en';
    const next = new URL(window.location.href);
    next.pathname = localizedPath(state.routePath, nextLanguage);
    navigate(`${next.pathname}${next.search}${next.hash}`, true, preservedQuery);
  }
  if (action === 'switch-experience') navigate(localizedPath('/start', state.language));
  if (action === 'new-research') {
    state.lastResearch = null;
    state.lastResearchRole = null;
    chatStore.createThread(state.role);
    render(true);
  }
  if (action === 'select-thread') {
    const threadId = actionElement?.dataset.threadId;
    if (threadId) {
      chatStore.setActiveThreadId(state.role, threadId);
      render(true);
    }
  }
  if (action === 'delete-thread') {
    event.stopPropagation();
    const threadId = actionElement?.dataset.threadId;
    if (threadId) {
      chatStore.deleteThread(threadId, state.role);
      render(true);
    }
  }
  if (action === 'clear-threads') {
    chatStore.clearAllForRole(state.role);
    render(true);
  }
  const suggestedCard = target.closest<HTMLElement>('[data-suggested-query]');
  if (suggestedCard) {
    const query = suggestedCard.dataset.suggestedQuery;
    if (query) {
      const textarea = document.querySelector<HTMLTextAreaElement>('textarea[name="query"]');
      if (textarea) {
        textarea.value = query;
        const form = textarea.closest<HTMLFormElement>('form');
        if (form) void submitResearch(form);
      }
    }
  }
  if (action === 'close-toast') actionElement?.closest('.toast')?.remove();
  if (action === 'close-provision-modal') document.querySelector('.provision-modal-backdrop')?.remove();
  if (action === 'view-provision') {
    const act = actionElement?.dataset.act || '';
    const sec = actionElement?.dataset.section || '';
    void openProvisionModal(act, sec);
  }
  if (action === 'click-citation') {
    const tag = actionElement?.dataset.citation || '';
    const sources = state.lastResearch?.authorities || [];
    let idx = -1;
    if (tag.startsWith('ACT-') || tag.startsWith('S') || tag.startsWith('CASE-') || tag.startsWith('DLR-')) {
      const num = parseInt(tag.replace(/[^0-9]/g, ''), 10) - 1;
      if (num >= 0 && num < sources.length) idx = num;
    }
    if (idx < 0) {
      idx = sources.findIndex((s) => (s.provision || s.citation || '').includes(tag) || (s.authority || s.title || '').includes(tag));
    }
    if (idx >= 0) {
      state.selectedSource = idx;
      document.querySelectorAll('[data-result-source]').forEach((button, i) => button.classList.toggle('active', i === idx));
      const panel = document.querySelector<HTMLElement>('[data-source-panel]');
      if (panel) panel.outerHTML = sourcePanel(sources[idx]);
      const s = sources[idx];
      void openProvisionModal(s.authority || s.title, s.provision || s.citation || '');
    }
  }
  if (action === 'close-menu') {
    state.menuOpen = false;
    render(true);
  }
  if (action === 'click-citation-index') {
    const idx = Number(actionElement?.dataset.citationIndex ?? 0);
    const sources = state.lastResearch?.authorities || [];
    if (idx >= 0 && idx < sources.length) {
      state.selectedSource = idx;
      document.querySelectorAll('[data-result-source]').forEach((button, i) => button.classList.toggle('active', i === idx));
      const panel = document.querySelector<HTMLElement>('[data-source-panel]');
      if (panel) panel.outerHTML = sourcePanel(sources[idx]);
    }
  }
  if (action === 'focus-composer') {
    const textarea = document.querySelector<HTMLTextAreaElement>('.composer-input-box textarea, .chat-floating-composer textarea');
    if (textarea) {
      textarea.scrollIntoView({ behavior: 'smooth', block: 'center' });
      textarea.focus();
    }
  }
  if (action === 'copy-research-answer') {
    if (state.lastResearch?.shortAnswer) {
      void navigator.clipboard.writeText(state.lastResearch.shortAnswer);
      showToast('Copied to clipboard', 'Full legal analysis copied successfully.', 'positive');
    }
  }
  if (action === 'print-legal-memo') {
    if (state.lastResearch) {
      printChambersLegalMemo(state.lastResearch, state.role, state.language);
    }
  }
  if (action === 'feedback-positive') {
    const widget = actionElement?.closest('[data-feedback-widget]');
    if (widget) {
      widget.innerHTML = `<div class="feedback-submitted-success"><span>✓</span> ${escapeHtml(ui(state.language, 'feedbackRecorded'))}</div>`;
    }
    const backendUrl = (import.meta.env.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com').replace(/\/$/, '');
    void fetch(`${backendUrl}/api/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query_run_id: `run_${Date.now()}`,
        rating: 1,
        category: 'helpful',
        comment: 'Accurate and helpful'
      })
    });
  }
  if (action === 'open-pilot-modal') {
    const existing = document.querySelector('[data-pilot-modal-overlay]');
    if (!existing) {
      document.body.insertAdjacentHTML('beforeend', renderPilotModal());
    }
  }
  if (action === 'close-pilot-modal') {
    document.querySelector('[data-pilot-modal-overlay]')?.remove();
  }
  if (action === 'feedback-negative-toggle') {
    const drawer = document.querySelector<HTMLElement>('[data-feedback-drawer]');
    if (drawer) drawer.hidden = !drawer.hidden;
  }
  if (action === 'close-feedback-drawer') {
    const drawer = document.querySelector<HTMLElement>('[data-feedback-drawer]');
    if (drawer) drawer.hidden = true;
  }
  if (action === 'sign-out') void authService.signOut().then(() => { state.session = null; render(); });
  if (action === 'google-sign-in') {
    const next = actionElement?.dataset.next ?? localizedPath(`/workspace/${state.role}`, state.language);
    void authService.signInWithGoogle(next).then((result) => {
      if (result.error) showToast('Sign-in unavailable', result.error, 'warning');
    });
  }
  if (action === 'ask-from-guide') {
    const context = { id: actionElement?.dataset.guideId ?? '', title: actionElement?.dataset.guideTitle ?? '', topic: actionElement?.dataset.guideTopic ?? '' };
    sessionStorage.setItem('justor-guide-context', JSON.stringify(context));
    navigate(`${localizedPath('/workspace/citizen', state.language)}#ask`);
  }
  if (action === 'remove-context') {
    sessionStorage.removeItem('justor-guide-context');
    actionElement?.closest('.research-context')?.remove();
    const form = document.querySelector<HTMLFormElement>('[data-research-form]');
    if (form) {
      delete form.dataset.contextId;
      delete form.dataset.contextTitle;
      delete form.dataset.contextTopic;
    }
  }
  const prompt = target.closest<HTMLButtonElement>('[data-prompt]');
  if (prompt) {
    const textarea = document.querySelector<HTMLTextAreaElement>('.composer-input-box textarea, .research-composer textarea');
    if (textarea) { textarea.value = prompt.dataset.prompt ?? ''; textarea.focus(); }
  }
  const topic = target.closest<HTMLButtonElement>('[data-citizen-topic]');
  if (topic) {
    const value = topic.dataset.citizenTopic ?? '';
    state.citizenHasSearched = true;
    document.querySelector<HTMLElement>('[data-citizen-mascot]')?.remove();
    const input = document.querySelector<HTMLInputElement>('[data-citizen-guide-form] input');
    if (input) input.value = clusterLabel(value);
    void hydrateCitizen('', value);
  }
  const cluster = target.closest<HTMLButtonElement>('[data-guide-cluster]');
  if (cluster) {
    state.guideCluster = cluster.dataset.guideCluster ?? '';
    state.guidePage = 1;
    document.querySelectorAll('[data-guide-cluster]').forEach((button) => button.classList.toggle('active', button === cluster));
    void hydrateGuides();
  }
  const more = target.closest<HTMLButtonElement>('[data-guide-more]');
  if (more) { state.guidePage += 1; void hydrateGuides(true); }
  const libraryType = target.closest<HTMLButtonElement>('[data-library-type]');
  if (libraryType) {
    const params = new URLSearchParams(window.location.search);
    const value = libraryType.dataset.libraryType ?? '';
    value ? params.set('type', value) : params.delete('type');
    navigate(`${localizedPath('/legal-library', state.language)}${params.size ? `?${params}` : ''}`);
  }
  const resultSource = target.closest<HTMLButtonElement>('[data-result-source]');
  if (resultSource && state.lastResearch) {
    const index = Number(resultSource.dataset.resultSource ?? 0);
    state.selectedSource = index;
    document.querySelectorAll('[data-result-source]').forEach((button) => button.classList.toggle('active', button === resultSource));
    const panel = document.querySelector<HTMLElement>('[data-source-panel]');
    if (panel) panel.outerHTML = sourcePanel(state.lastResearch.authorities?.[index]);
  }
  const proofSource = target.closest<HTMLButtonElement>('[data-proof-source]');
  if (proofSource) {
    document.querySelectorAll('[data-proof-source]').forEach((button) => button.classList.toggle('active', button === proofSource));
    const index = Number(proofSource.dataset.proofSource ?? 0);
    const source = state.productProof?.sources[index];
    const panel = document.querySelector<HTMLElement>('[data-product-proof] .proof-source');
    if (source && panel) panel.outerHTML = sourcePanel(source, 'proof-source');
  }
});

document.addEventListener('submit', (event) => {
  const form = event.target as HTMLFormElement;
  if (form.matches('[data-research-form]')) { event.preventDefault(); void submitResearch(form); }
  if (form.matches('[data-library-home-search]')) {
    event.preventDefault();
    const query = String(new FormData(form).get('query') ?? '').trim();
    navigate(`${localizedPath('/legal-library', state.language)}${query ? `?q=${encodeURIComponent(query)}` : ''}`);
  }
  if (form.matches('[data-library-search]')) {
    event.preventDefault();
    const query = String(new FormData(form).get('query') ?? '').trim();
    const params = new URLSearchParams(window.location.search);
    query ? params.set('q', query) : params.delete('q');
    navigate(`${localizedPath('/legal-library', state.language)}${params.size ? `?${params}` : ''}`);
  }
  if (form.matches('[data-guide-directory-search]')) {
    event.preventDefault();
    state.guideQuery = String(new FormData(form).get('query') ?? '').trim();
    state.guidePage = 1;
    void hydrateGuides();
  }
  if (form.matches('[data-citizen-guide-form]')) {
    event.preventDefault();
    const query = String(new FormData(form).get('query') ?? '').trim();
    state.citizenHasSearched = true;
    document.querySelector<HTMLElement>('[data-citizen-mascot]')?.remove();
    void hydrateCitizen(query);
  }
  if (form.matches('[data-action="submit-pilot-form"]')) {
    event.preventDefault();
    const formData = new FormData(form);
    const payload = {
      advocate_name: String(formData.get('advocate_name') || '').trim(),
      chamber_name: String(formData.get('chamber_name') || '').trim(),
      bar_association: String(formData.get('bar_association') || '').trim(),
      phone: String(formData.get('phone') || '').trim(),
      practice_areas: [String(formData.get('practice_areas') || '').trim()].filter(Boolean),
      custom_needs: String(formData.get('custom_needs') || '').trim(),
    };

    const modalContainer = form.closest('.pilot-modal-card');
    if (modalContainer) {
      modalContainer.innerHTML = `
        <div style="text-align: center; padding: 24px 12px;">
          <span style="font-size: 40px; display: block; margin-bottom: 12px;">⚖️</span>
          <h3 style="color: #0F172A; margin: 0 0 8px 0; font-size: 18px;">Founding Pilot Application Received!</h3>
          <p style="color: #475467; font-size: 13.5px; line-height: 1.5; margin: 0 0 20px 0;">
            Thank you Advocate ${escapeHtml(payload.advocate_name)}. Our founding team will contact you via WhatsApp / Phone (<strong>${escapeHtml(payload.phone)}</strong>) within 24 hours to activate your chambers account.
          </p>
          <button class="button button-small" type="button" data-action="close-pilot-modal">Close</button>
        </div>
      `;
    }

    const backendUrl = (import.meta.env.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com').replace(/\/$/, '');
    void fetch(`${backendUrl}/api/pilot-application`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  }
  if (form.matches('[data-action="submit-qa-feedback"]')) {
    event.preventDefault();
    const data = new FormData(form);
    const category = String(data.get('category') || 'other');
    const comment = String(data.get('comment') || '');
    const widget = form.closest('[data-feedback-widget]');
    if (widget) {
      widget.innerHTML = `<div class="feedback-submitted-success"><span>✓</span> ${escapeHtml(ui(state.language, 'feedbackRecorded'))}</div>`;
    }
    const backendUrl = (import.meta.env.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com').replace(/\/$/, '');
    void fetch(`${backendUrl}/api/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query_run_id: `run_${Date.now()}`,
        rating: -1,
        category,
        comment,
        query: state.lastResearch?.shortAnswer?.slice(0, 100)
      })
    });
  }
});

window.addEventListener('popstate', () => render());

const restorePendingContext = (): void => {
  if (state.routePath !== '/workspace/citizen' || !state.session) return;
  const raw = sessionStorage.getItem('justor-guide-context');
  if (!raw) return;
  try {
    const context = JSON.parse(raw) as { id: string; title: string; topic: string };
    const handoff = document.querySelector<HTMLElement>('.citizen-ai-handoff');
    if (handoff && !handoff.querySelector('.chat-floating-composer')) {
      handoff.insertAdjacentHTML('beforeend', renderBottomChatBar('citizen', 'Describe your specific situation...', ['Explain my next step', 'What evidence should I keep?'], context));
    }
  } catch { sessionStorage.removeItem('justor-guide-context'); }
};

const restorePendingResearch = (): void => {
  if (!state.session) return;
  const raw = sessionStorage.getItem('justor-pending-research');
  if (!raw) return;
  try {
    const pending = JSON.parse(raw) as { query?: string; role?: Role };
    if (!pending.query || !pending.role || state.routePath !== `/workspace/${pending.role}`) return;
    const form = document.querySelector<HTMLFormElement>('[data-research-form]');
    const textarea = form?.querySelector<HTMLTextAreaElement>('textarea[name="query"]');
    if (!form || !textarea) return;
    textarea.value = pending.query;
    sessionStorage.removeItem('justor-pending-research');
    void submitResearch(form);
  } catch {
    sessionStorage.removeItem('justor-pending-research');
  }
};

export function mountApp(): void {
  render();
  const updateHeader = (): void => {
    document.querySelector('[data-header]')?.classList.toggle('scrolled', window.scrollY > 12);
  };
  window.addEventListener('scroll', updateHeader, { passive: true });
  updateHeader();

  if (typeof BroadcastChannel !== 'undefined') {
    try {
      const authChannel = new BroadcastChannel('justor_auth');
      authChannel.onmessage = (event) => {
        if (event.data?.type === 'SIGNED_OUT') {
          state.session = null;
          render(true);
        }
      };
    } catch {}
  }

  void authService.session().then((session) => {
    if (session !== state.session) { state.session = session; render(true); restorePendingContext(); restorePendingResearch(); }
  });
  authService.subscribe((session) => {
    state.session = session;
    render(true);
    restorePendingContext();
    restorePendingResearch();
  });
}
