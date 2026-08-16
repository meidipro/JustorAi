import type { Session } from '@supabase/supabase-js';
import {
  authService,
  publicData,
  runResearch,
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
        ${route('/legal-library', ui(state.language, 'library'))}
        ${route('/guides', ui(state.language, 'guides'))}
        ${route('/legal-updates', ui(state.language, 'updates'))}
        ${route('/trust', ui(state.language, 'trust'))}
        ${route('/about', ui(state.language, 'about'))}
      </nav>
      <div class="nav-actions">
        <button class="language-switch" type="button" data-action="language" aria-label="Switch language">${ui(state.language, 'language')}</button>
        ${state.session ? `<button class="nav-signin" type="button" data-action="sign-out">Sign Out</button>` : route('/login', ui(state.language, 'signIn'), 'nav-signin')}
        ${route('/start', `${ui(state.language, 'start')} ${icon('arrow', 16)}`, 'button button-small desktop-start')}
        <button class="menu-button" type="button" data-action="menu" aria-label="${state.menuOpen ? ui(state.language, 'close') : ui(state.language, 'menu')}" aria-expanded="${state.menuOpen}">${icon(state.menuOpen ? 'close' : 'menu')}</button>
      </div>
    </div>
    <nav class="mobile-menu ${state.menuOpen ? 'is-open' : ''}" aria-label="Mobile navigation" aria-hidden="${!state.menuOpen}">
      ${route('/legal-library', ui(state.language, 'library'))}
      ${route('/guides', ui(state.language, 'guides'))}
      ${route('/legal-updates', ui(state.language, 'updates'))}
      ${route('/trust', ui(state.language, 'trust'))}
      ${route('/about', ui(state.language, 'about'))}
      <span class="mobile-menu-divider" aria-hidden="true"></span>
      <button class="mobile-nav-action" type="button" data-action="language">${ui(state.language, 'language')}</button>
      ${state.session ? '<button class="mobile-nav-action" type="button" data-action="sign-out">Sign Out</button>' : route('/login', ui(state.language, 'signIn'))}
      ${route('/start', ui(state.language, 'start'), 'button mobile-start')}
    </nav>
  </header>`;

const footer = (): string => `
  <footer class="site-footer">
    <div class="footer-grid">
      <div>${brand(true)}<p>Bangladesh legal intelligence for guidance, learning and professional research.</p><span class="beta-label">${ui(state.language, 'controlledBeta')}</span></div>
      <nav aria-label="Product"><strong>Product</strong>${route('/workspace/professional', 'Legal Professional')}${route('/workspace/student', 'Law Student')}${route('/workspace/citizen', 'Citizen')}${route('/start', 'Start Justor')}</nav>
      <nav aria-label="Resources"><strong>Resources</strong>${route('/legal-library', ui(state.language, 'library'))}${route('/guides', ui(state.language, 'guides'))}${route('/legal-updates', ui(state.language, 'updates'))}${route('/trust', ui(state.language, 'trust'))}</nav>
      <nav aria-label="Company"><strong>Company</strong>${route('/about', ui(state.language, 'about'))}${route('/about#team', 'Team')}${route('/about#investors', 'Investors')}${route('/contact', 'Contact')}</nav>
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

const workspaceNav = (role: Role, items: Array<{ label: string; href: string; icon: string }>, active: string): string => `
  <aside class="workspace-sidebar">
    <div class="workspace-brand">${brand(true)}<span>Beta</span></div>
    ${role === 'professional' ? `<button class="new-research" type="button" data-action="new-research">${icon('plus', 17)} ${ui(state.language, 'newResearch')}</button>` : ''}
    <nav aria-label="${localizedRoleLabel(role)} navigation">${items.map((item) => route(item.href, `${icon(item.icon, 18)} <span>${item.label}</span>`, item.label === active ? 'active' : '')).join('')}</nav>
    <button class="switch-experience" type="button" data-action="switch-experience">${ui(state.language, 'switchExperience')} ${icon('arrow', 15)}</button>
  </aside>`;

const workspaceTopbar = (role: Role): string => `<header class="workspace-topbar"><a href="${localizedPath('/', state.language)}" data-route class="workspace-mobile-brand">${brand()}</a><span>${localizedRoleLabel(role)}</span><div><button class="language-switch" type="button" data-action="language" aria-label="Switch language">${ui(state.language, 'language')}</button>${state.session ? `<button type="button" data-action="sign-out" class="text-button">Sign Out</button>` : route('/login', ui(state.language, 'signIn'), 'button button-small')}</div></header>`;

const quotaLine = (role: Role): string => `<span class="quota-line" data-quota>${state.session ? `${ui(state.language, 'dailyAllowance')}: ${roleQuota[role]}` : `${ui(state.language, 'signInQuotaPrefix')} ${roleQuota[role]} ${ui(state.language, 'answersPerDay')}`}</span>`;

const researchComposer = (role: Role, placeholder: string, actions: string[], context?: { id: string; title: string; topic: string }): string => `
  ${context ? `<div class="research-context"><span>You're asking from:</span><strong>${escapeHtml(context.title)}</strong><button type="button" data-action="remove-context">Remove context ×</button></div>` : ''}
  <form class="research-composer" data-research-form data-role="${role}" ${context ? `data-context-id="${escapeHtml(context.id)}" data-context-title="${escapeHtml(context.title)}" data-context-topic="${escapeHtml(context.topic)}"` : ''}>
    <label><span class="sr-only">Research query</span><textarea name="query" rows="3" required placeholder="${placeholder}"></textarea><button type="submit" aria-label="Submit">${icon('arrow')}</button></label>
    <footer><span>${icon('source', 15)} ${ui(state.language, 'sourcesShown')}</span>${quotaLine(role)}</footer>
  </form>
  <div class="quick-actions">${actions.map((action) => `<button type="button" data-prompt="${escapeHtml(action)}">${action}</button>`).join('')}</div>`;

const citizenWelcomeMascot = (): string => `
  <div class="citizen-welcome-mascot" data-citizen-mascot aria-label="Justor citizen guide assistant">
    <span class="mascot-mark"><img src="/visuals/justor-mark.png" alt="" width="56" height="30"></span>
    <div><strong>Start with a citizen guide.</strong><p>Search by the problem, service, document or evidence you already know.</p></div>
  </div>`;

const professionalWorkspace = (): string => `
  <main id="page-content" class="workspace workspace-professional">
    ${workspaceNav('professional', [
      { label: ui(state.language, 'researchHome'), href: '/workspace/professional', icon: 'home' },
      { label: ui(state.language, 'legalLibrary'), href: '/legal-library', icon: 'book' },
      { label: ui(state.language, 'cases'), href: '/legal-library?type=case', icon: 'scale' },
      { label: ui(state.language, 'statutes'), href: '/legal-library?type=law', icon: 'source' },
      { label: ui(state.language, 'updates'), href: '/legal-updates', icon: 'clock' },
      { label: ui(state.language, 'amendments'), href: '/legal-library?type=amendment', icon: 'source' },
    ], ui(state.language, 'researchHome'))}
    <section class="workspace-main">${workspaceTopbar('professional')}
      <div class="workspace-content research-home"><span class="section-kicker">${ui(state.language, 'professionalKicker')}</span><h1>${ui(state.language, 'professionalHeading')}</h1><p>${ui(state.language, 'professionalSubtitle')}</p>
        ${researchComposer('professional', ui(state.language, 'professionalPlaceholder'), [ui(state.language, 'researchIssue'), ui(state.language, 'findPrecedent'), ui(state.language, 'findStatute'), ui(state.language, 'checkAmendment')])}
        <div data-research-output class="research-output" hidden></div>
        <section class="workspace-secondary" data-professional-updates-section><div class="section-heading section-heading-row"><div><span class="section-kicker">${ui(state.language, 'secondaryModule')}</span><h2>${ui(state.language, 'recentUpdates')}</h2></div>${route('/legal-updates', `${ui(state.language, 'viewAll')} ${icon('arrow', 16)}`, 'text-link')}</div><div data-professional-updates class="update-list"><div class="data-loading">Checking current update records…</div></div></section>
      </div>
    </section>${mobileBottomNav('professional')}
  </main>`;

const studentPreAuth = (): string => `
  <main id="page-content" class="preauth-page"><header>${route('/', brand(), 'brand-link')}<div><button class="language-switch" type="button" data-action="language" aria-label="Switch language">${ui(state.language, 'language')}</button>${route('/start', ui(state.language, 'switchExperience'), 'text-link')}</div></header><section><span class="section-kicker">${ui(state.language, 'studentKicker')}</span><h1>${ui(state.language, 'studentHeading')}</h1><p>${ui(state.language, 'studentAllowance')}</p><button class="button google-button" type="button" data-action="google-sign-in" data-next="${localizedPath('/workspace/student', state.language)}"><span>G</span> ${ui(state.language, 'continueGoogle')}</button><small>${ui(state.language, 'publicReading')}</small></section></main>`;

const studentWorkspace = (): string => {
  if (!state.session) return studentPreAuth();
  return `<main id="page-content" class="workspace workspace-student">
    ${workspaceNav('student', [
      { label: ui(state.language, 'studyHome'), href: '/workspace/student', icon: 'home' },
      { label: ui(state.language, 'askJustor'), href: '/workspace/student#ask', icon: 'source' },
      { label: ui(state.language, 'cases'), href: '/legal-library?type=case', icon: 'scale' },
      { label: ui(state.language, 'statutes'), href: '/legal-library?type=law', icon: 'book' },
      { label: ui(state.language, 'concepts'), href: '/legal-library?type=concept', icon: 'source' },
    ], ui(state.language, 'studyHome'))}
    <section class="workspace-main">${workspaceTopbar('student')}<div class="workspace-content student-home"><span class="section-kicker">Source-linked learning</span><h1>What are you studying?</h1><p>Ask about a case, statute, legal concept or principle.</p>
      <div id="ask">${researchComposer('student', 'Ask about a case, statute, legal concept or principle...', ['Explain a Statute', 'Brief a Case', 'Explain a Concept', 'Compare Cases', 'Quiz Me', 'Practice a Problem'])}</div>
      <div data-research-output class="research-output" hidden></div>
      <section class="study-method"><h2>Study from authority</h2><div><article><strong>Explain</strong><p>Break down the principle in plain language.</p></article><article><strong>Case Brief</strong><p>Structure facts, issue, rule and reasoning.</p></article><article><strong>Source</strong><p>Keep the relevant authority beside the explanation.</p></article></div></section>
    </div></section>${mobileBottomNav('student')}</main>`;
};

const citizenWorkspace = (): string => {
  const guideContext = storedGuideContext();
  return `
  <main id="page-content" class="workspace workspace-citizen">
    ${workspaceNav('citizen', [
      { label: ui(state.language, 'home'), href: '/workspace/citizen', icon: 'home' },
      { label: ui(state.language, 'guides'), href: '/guides', icon: 'book' },
      { label: ui(state.language, 'askJustor'), href: '/workspace/citizen#ask', icon: 'source' },
    ], ui(state.language, 'home'))}
    <section class="workspace-main">${workspaceTopbar('citizen')}<div class="workspace-content citizen-home"><span class="section-kicker">${ui(state.language, 'citizenKicker')}</span><h1>${ui(state.language, 'citizenHeading')}</h1><p>${ui(state.language, 'citizenSubtitle')}</p>
      ${state.citizenHasSearched ? '' : citizenWelcomeMascot()}
      <form class="citizen-guide-search" data-citizen-guide-form><label>${icon('search')}<span class="sr-only">${ui(state.language, 'problemPlaceholder')}</span><input name="query" placeholder="${ui(state.language, 'problemPlaceholder')}"></label><button class="button" type="submit">${ui(state.language, 'findGuidance')}</button></form>
      <section class="topic-directory"><h2>${ui(state.language, 'chooseTopic')}</h2><div>${guideTopics.map((topic) => `<button type="button" data-citizen-topic="${topic.value}"><span>${topic.label}</span>${icon('arrow', 16)}</button>`).join('')}</div></section>
      <section class="citizen-results" data-citizen-results-section><div class="section-heading section-heading-row"><div><span class="section-kicker">${ui(state.language, 'citizenGuides')}</span><h2>${ui(state.language, 'publishedGuidance')}</h2></div>${route('/guides', `${ui(state.language, 'browseDirectory')} ${icon('arrow', 16)}`, 'text-link')}</div><div data-citizen-results class="guide-list"><div class="data-loading">Loading published citizen guides…</div></div></section>
      <section id="ask" class="citizen-ai-handoff"><div><span class="section-kicker section-kicker-light">${ui(state.language, 'couldntFind')}</span><h2>${ui(state.language, 'askSituation')}</h2><p>${ui(state.language, 'citizenAiGate')}</p></div>${state.session ? researchComposer('citizen', 'Describe your specific situation...', ['Explain my next step', 'What evidence should I keep?'], guideContext) : `<button class="button button-light google-button" type="button" data-action="google-sign-in" data-next="${localizedPath('/workspace/citizen', state.language)}#ask"><span>G</span> ${ui(state.language, 'continueGoogle')}</button><a href="${localizedPath('/guides', state.language)}" data-route>${ui(state.language, 'continueBrowsing')}</a>`}<div data-research-output class="research-output" hidden></div></section>
    </div></section>${mobileBottomNav('citizen')}</main>`;
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

const contactPage = (): string => `<main id="page-content" class="inner-page"><section class="compact-hero section-shell"><span class="section-kicker">Contact Justor</span><h1>Start the right conversation.</h1><p>Choose a direct route to the team. No submission is silently stored by this page.</p></section><section class="section-shell contact-options"><a href="mailto:tajuddinahamed.contact@gmail.com"><span>Email</span><strong>tajuddinahamed.contact@gmail.com</strong>${icon('arrow', 16)}</a><a href="tel:+8801764662967"><span>Phone</span><strong>+880 1764-662967</strong>${icon('arrow', 16)}</a><a href="https://wa.me/8801764662967" target="_blank" rel="noopener"><span>WhatsApp</span><strong>Open a conversation</strong>${icon('external', 16)}</a></section><section class="section-shell inquiry-links"><h2>Inquiry type</h2><div><a href="mailto:tajuddinahamed.contact@gmail.com?subject=University%20partnership">University partnership</a><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Legal%20collaboration">Legal collaboration</a><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Media%20inquiry">Media & press</a><a href="mailto:tajuddinahamed.contact@gmail.com?subject=Investor%20inquiry">Investor / strategic partnership</a></div></section></main>`;

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
  const normalized = status?.trim().toLowerCase();
  if (!normalized) return '';
  if (normalized === 'primary source') return '<span class="semantic-badge badge-primary">Primary Source</span>';
  if (normalized === 'source checked') return '<span class="semantic-badge badge-checked">Source Checked</span>';
  if (normalized === 'human legal reviewed') return '<span class="semantic-badge badge-reviewed">Human Legal Reviewed</span>';
  return '';
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

const renderProductProof = (proof: ProductProofRecord): string => {
  if (proof.verified !== true || !proof.propositions.length || !proof.sources.length) return '';
  const selected = proof.sources[0];
  return `<div class="proof-analysis"><span class="section-kicker">AI analysis</span>${proof.propositions.map((proposition) => {
    const sourceIndex = proof.sources.findIndex((source) => source.id === proposition.sourceId);
    return `<p>${escapeHtml(proposition.text)}${sourceIndex >= 0 ? ` <button type="button" data-proof-source="${sourceIndex}" aria-label="Show source ${sourceIndex + 1}">[${sourceIndex + 1}]</button>` : ''}</p>`;
  }).join('')}</div>${sourcePanel(selected, 'proof-source')}`;
};

const sourcePanel = (source?: LegalSource, className = 'result-source-panel'): string => {
  if (!source) return `<aside class="${className}" data-source-panel>${unavailable('No source record was supplied for this result.')}</aside>`;
  const url = safeUrl(source.url);
  return `<aside class="${className}" data-source-panel><span class="section-kicker">Selected authority</span><h3>${escapeHtml(source.title)}</h3>${source.authority ? `<p>${escapeHtml(source.authority)}</p>` : ''}<div class="source-badges">${verificationBadge(source.verificationStatus)}${source.status ? `<span class="semantic-badge">${escapeHtml(source.status)}</span>` : ''}</div><dl>${source.citation ? `<div><dt>Citation</dt><dd>${escapeHtml(source.citation)}</dd></div>` : ''}${source.provision ? `<div><dt>Provision</dt><dd>${escapeHtml(source.provision)}</dd></div>` : ''}</dl>${source.excerpt ? `<blockquote>${escapeHtml(source.excerpt)}</blockquote>` : ''}${url ? `<a href="${url}" target="_blank" rel="noopener">Open source record ${icon('external', 15)}</a>` : '<small>No source link was supplied.</small>'}</aside>`;
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
};

const formatAnswerMarkdown = (text: string): string => {
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
      const formatted = escapeHtml(line)
        .replace(/\[(ACT-\d+|S\d+)\]/g, '<span class="inline-citation">[$1]</span>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
      htmlParts.push(`<p>${formatted}</p>`);
    }
  }
  flushList();
  return htmlParts.join('');
};

const renderResearchResult = (result: ResearchResult): string => {
  const sources = result.authorities ?? [];
  const steps = result.reasoningSteps ?? [];

  const reasoningBlock = steps.length ? `
    <details class="reasoning-accordion" open>
      <summary class="reasoning-summary">
        <span class="reasoning-icon">✨</span>
        <span class="reasoning-heading">Reasoning process</span>
        <span class="reasoning-count">${steps.length} steps verified</span>
        <span class="reasoning-chevron">▼</span>
      </summary>
      <div class="reasoning-steps-list">
        ${steps.map((step) => `
          <div class="reasoning-step-item">
            <div class="step-num">${step.step}</div>
            <div class="step-content">
              <strong>${escapeHtml(step.title)}</strong>
              <p>${escapeHtml(step.summary)}</p>
            </div>
          </div>
        `).join('')}
      </div>
    </details>` : '';

  const section = (title: string, body?: string | string[]) => {
    if (!body || (Array.isArray(body) && !body.length)) return '';
    return `<section><h3>${title}</h3>${Array.isArray(body) ? `<ul>${body.map((item) => `<li>${escapeHtml(item)}</li>`).join('')}</ul>` : `<p>${escapeHtml(body)}</p>`}</section>`;
  };

  const hasStructuredSections = Boolean(
    (result.legalIssues && result.legalIssues.length) ||
    (result.applicableLaw && result.applicableLaw.length) ||
    (result.relevantCases && result.relevantCases.length)
  );

  const mainContent = hasStructuredSections
    ? `${section('Short Answer', result.shortAnswer)}${section('Legal Issues', result.legalIssues)}${section('Applicable Law', result.applicableLaw)}${section('Relevant Case Law', result.relevantCases)}${section('Exceptions / Qualifications', result.qualifications)}${section('Application to Facts', result.applicationToFacts)}${section('Practical Position', result.practicalPosition)}`
    : `<div class="research-formatted-markdown">${formatAnswerMarkdown(result.shortAnswer)}</div>`;

  return `
    <div class="research-result-layout">
      <article class="research-analysis">
        <span class="section-kicker">Research analysis</span>
        ${reasoningBlock}
        ${mainContent}
        ${sources.length ? `<section class="authorities-section"><h3>Authorities</h3><div class="citation-list">${sources.map((source, index) => `<button type="button" data-result-source="${index}" class="${index === 0 ? 'active' : ''}"><span>[${index + 1}]</span>${escapeHtml(source.title)}</button>`).join('')}</div></section>` : ''}
        ${result.limitations ? `<section class="limitations"><h3>Coverage / limitations</h3><p>${escapeHtml(result.limitations)}</p></section>` : ''}
      </article>
      ${sourcePanel(sources[0])}
    </div>`;
};

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
        <strong>Thinking...</strong>
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
  const role = form.dataset.role as Role;
  const context = form.dataset.contextId ? { id: form.dataset.contextId, title: form.dataset.contextTitle ?? '', topic: form.dataset.contextTopic ?? '' } : undefined;
  if (!state.session) {
    sessionStorage.setItem('justor-pending-research', JSON.stringify({ query, role, context }));
    navigate(`${localizedPath('/login', state.language)}?next=${encodeURIComponent(`${localizedPath(`/workspace/${role}`, state.language)}${role === 'citizen' ? '#ask' : ''}`)}`);
    return;
  }
  const output = form.closest('.workspace-content, .citizen-ai-handoff')?.querySelector<HTMLElement>('[data-research-output]') ?? document.querySelector<HTMLElement>('[data-research-output]');
  if (!output) return;
  output.hidden = false;
  
  let elapsed = 0;
  let activeStep = 0;
  output.innerHTML = renderLiveThinking(elapsed, activeStep);
  output.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  const timerInterval = setInterval(() => {
    elapsed += 0.2;
    if (elapsed > 0.8 && activeStep === 0) activeStep = 1;
    if (elapsed > 2.0 && activeStep === 1) activeStep = 2;
    if (elapsed > 3.4 && activeStep === 2) activeStep = 3;
    const headerTimer = output.querySelector<HTMLElement>('.thinking-timer');
    if (headerTimer) headerTimer.textContent = `(${elapsed.toFixed(1)}s)`;
    
    const stepRows = output.querySelectorAll<HTMLElement>('.live-step-row');
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
    const result = await runResearch(query, role, state.language, context);
    clearInterval(timerInterval);
    state.lastResearch = result;
    state.lastResearchRole = role;
    state.selectedSource = 0;
    output.innerHTML = renderResearchResult(result);
    const quota = result.quota;
    if (quota) document.querySelectorAll<HTMLElement>('[data-quota]').forEach((element) => { element.textContent = `${quota.remaining} of ${quota.limit} AI answers remaining today`; });
    output.scrollIntoView({ behavior: 'smooth', block: 'start' });
  } catch (error) {
    clearInterval(timerInterval);
    const message = error instanceof Error && error.message === 'authentication-required'
      ? 'Your session has ended. Sign in again to continue.'
      : 'The legal research service is unavailable. No answer was generated.';
    output.innerHTML = unavailable(message);
  }
};

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
    navigate(localizedPath('/workspace/professional', state.language));
  }
  if (action === 'close-toast') actionElement?.closest('.toast')?.remove();
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
    const textarea = document.querySelector<HTMLTextAreaElement>('.research-composer textarea');
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
});

window.addEventListener('popstate', () => render());

const restorePendingContext = (): void => {
  if (state.routePath !== '/workspace/citizen' || !state.session) return;
  const raw = sessionStorage.getItem('justor-guide-context');
  if (!raw) return;
  try {
    const context = JSON.parse(raw) as { id: string; title: string; topic: string };
    const handoff = document.querySelector<HTMLElement>('.citizen-ai-handoff');
    if (handoff && !handoff.querySelector('.research-composer')) {
      handoff.insertAdjacentHTML('beforeend', researchComposer('citizen', 'Describe your specific situation...', ['Explain my next step', 'What evidence should I keep?'], context));
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
