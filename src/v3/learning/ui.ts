import type { Language } from '../services';
import type { LearningCard, LearningCatalog, LearningHandoff, LearningSection } from './types';
import { addReport, getProgress, reviewQueue, sectionStats, setCardProgress, subjectStats } from './progress';

const esc = (value: unknown): string => String(value ?? '').replace(/[&<>'"]/g, (c) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;',
}[c] ?? c));

const txt = (card: LearningCard, lang: Language, field: 'hook' | 'question' | 'answer' | 'explanation' | 'key_principle'): string =>
  (lang === 'bn' ? card[`${field}_bn`] : card[`${field}_en`]) as string;

const conceptGlyph = (card: LearningCard): string => {
  const type = card.card_type;
  if (type === 'counterintuitive') {
    return `<svg class="learn-glyph" viewBox="0 0 80 80" aria-hidden="true"><circle cx="40" cy="40" r="28" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M28 40h24M40 28v24" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/><path d="M52 28 28 52" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>`;
  }
  if (type === 'myth_buster') {
    return `<svg class="learn-glyph" viewBox="0 0 80 80" aria-hidden="true"><path d="M40 14 58 22v16c0 14-8 24-18 28-10-4-18-14-18-28V22z" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="m32 40 6 6 12-14" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>`;
  }
  if (type === 'rule_visualizer') {
    return `<svg class="learn-glyph" viewBox="0 0 80 80" aria-hidden="true"><rect x="16" y="20" width="48" height="40" rx="6" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M16 32h48M28 20v40M40 40h16M40 50h12" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>`;
  }
  if (type === 'edge_case') {
    return `<svg class="learn-glyph" viewBox="0 0 80 80" aria-hidden="true"><path d="M40 16 62 56H18z" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linejoin="round"/><path d="M40 34v12M40 52v2" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>`;
  }
  return `<svg class="learn-glyph" viewBox="0 0 80 80" aria-hidden="true"><circle cx="28" cy="36" r="10" fill="none" stroke="currentColor" stroke-width="2.5"/><circle cx="52" cy="36" r="10" fill="none" stroke="currentColor" stroke-width="2.5"/><path d="M38 36h4M24 52c4 6 12 8 16 8s12-2 16-8" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/></svg>`;
};

const assetMarkup = (card: LearningCard): string => {
  const kind = card.asset_type;
  const tone = kind === 'spline' ? 'tone-spline' : kind === 'lottie' ? 'tone-lottie' : 'tone-image';
  if (card.asset_url) {
    return `
    <div class="learn-asset ${tone} has-image" aria-hidden="true">
      <img class="learn-asset-img" src="${esc(card.asset_url)}" alt="" width="160" height="160" loading="lazy" decoding="async" />
    </div>`;
  }
  return `
    <div class="learn-asset ${tone}" aria-hidden="true">
      <div class="learn-asset-plate">
        ${conceptGlyph(card)}
        <span class="learn-asset-ring"></span>
      </div>
    </div>`;
};

const typeLabel = (card: LearningCard, lang: Language): string => {
  const map: Record<string, [string, string]> = {
    counterintuitive: ['Counterintuitive', 'অপ্রত্যাশিত'],
    myth_buster: ['Myth check', 'ভ্রান্ত ধারণা'],
    rule_visualizer: ['Rule visual', 'নিয়ম চিত্র'],
    scenario: ['Scenario', 'পরিস্থিতি'],
    edge_case: ['Edge case', 'সূক্ষ্ম কেস'],
  };
  const pair = map[card.card_type] ?? ['Concept', 'ধারণা'];
  return lang === 'bn' ? pair[1] : pair[0];
};

export const renderLearningHome = (catalog: LearningCatalog, lang: Language, route: (path: string, label: string, className?: string) => string, nav: string, topbar: string, bottom: string): string => {
  const stats = subjectStats(catalog);
  const sub = catalog.subject;
  const title = lang === 'bn' ? sub.title_bn : sub.title_en;
  const desc = lang === 'bn' ? sub.description_bn : sub.description_en;
  const continueHref = `/workspace/student/learn/${stats.continueSlug}`;
  const continueLabel = stats.pct > 0 ? (lang === 'bn' ? 'চালিয়ে যান' : 'Continue') : (lang === 'bn' ? 'শুরু করুন' : 'Start');
  const coming = sub.coming_soon.map((item) => `
    <article class="learn-soon-card" aria-disabled="true">
      <span class="learn-soon-tag">${lang === 'bn' ? 'শীঘ্রই' : 'Soon'}</span>
      <h3>${esc(lang === 'bn' ? item.title_bn : item.title_en)}</h3>
    </article>`).join('');
  const topics = catalog.sections.map((section) => {
    const s = sectionStats(section);
    const st = s.status === 'complete' ? (lang === 'bn' ? 'সম্পন্ন' : 'Complete')
      : s.status === 'has_review_queue' ? (lang === 'bn' ? 'পুনরায় দেখুন' : 'Review queue')
      : s.status === 'in_progress' ? `${s.pct}%` : (lang === 'bn' ? 'শুরু হয়নি' : 'Not started');
    const statusClass = s.status === 'complete' ? 'is-complete' : s.status === 'in_progress' || s.status === 'has_review_queue' ? 'is-active' : '';
    return `
      <a class="learn-topic-row ${statusClass}" href="/workspace/student/learn/${esc(section.slug)}" data-route>
        <span class="learn-topic-index">${String(section.sort_order).padStart(2, '0')}</span>
        <div class="learn-topic-copy">
          <strong>${esc(lang === 'bn' ? section.title_bn : section.title_en)}</strong>
          <p>${section.card_count} ${lang === 'bn' ? 'কার্ড' : 'cards'} · ~${section.estimated_minutes} ${lang === 'bn' ? 'মিনিট' : 'min'} · ${esc(st)}</p>
          <div class="learn-progress-track" aria-hidden="true"><span style="width:${s.pct}%"></span></div>
        </div>
        <span class="learn-topic-go">${s.done ? (lang === 'bn' ? 'চালিয়ে যান' : 'Continue') : (lang === 'bn' ? 'শুরু' : 'Start')}</span>
      </a>`;
  }).join('');

  return `
  <main id="page-content" class="workspace workspace-student workspace-learn">
    ${nav}
    <section class="workspace-main">
      ${topbar}
      <div class="learn-shell">
        <header class="learn-hero">
          <span class="section-kicker">${lang === 'bn' ? 'বাইট-সাইজ লার্নিং' : 'Bite-Size Learning'}</span>
          <h1>${lang === 'bn' ? 'একবারে একটি আইনি ধারণা শিখুন।' : 'Learn one legal idea at a time.'}</h1>
          <p>${esc(desc)}</p>
        </header>
        <article class="learn-subject-card is-active">
          <div class="learn-subject-meta">
            <span class="learn-level">${esc(sub.level_tag)}</span>
            <span class="learn-subject-stat">${stats.pct}% ${lang === 'bn' ? 'সম্পন্ন' : 'complete'}</span>
          </div>
          <h2>${esc(title)}</h2>
          <p class="learn-subject-summary">${catalog.sections.length} ${lang === 'bn' ? 'বিষয়' : 'topics'} · 50 ${lang === 'bn' ? 'কার্ড' : 'cards'}</p>
          <div class="learn-progress-track learn-progress-lg"><span style="width:${stats.pct}%"></span></div>
          ${route(continueHref, continueLabel, 'button learn-cta')}
        </article>
        <div class="learn-soon-grid">${coming}</div>
        <h2 class="learn-topics-heading">${lang === 'bn' ? 'বিষয়সমূহ' : 'Topics'}</h2>
        <div class="learn-topic-list">${topics}</div>
      </div>
    </section>
    ${bottom}
  </main>`;
};

const REPORT_OPTIONS = [
  ['wrong_legal_content', 'Wrong legal content', 'ভুল আইনি বিষয়'],
  ['wrong_provision', 'Wrong provision/source', 'ভুল ধারা/উৎস'],
  ['outdated_law', 'Outdated law', 'পুরনো আইন'],
  ['bangla_problem', 'Bangla translation problem', 'বাংলা অনুবাদের সমস্যা'],
  ['visual_misleading', 'Visual is misleading', 'ভিজ্যুয়াল বিভ্রান্তিকর'],
  ['confusing', 'Explanation is confusing', 'ব্যাখ্যা অস্পষ্ট'],
  ['technical', 'Technical issue', 'টেকনিক্যাল সমস্যা'],
  ['other', 'Other', 'অন্যান্য'],
];

export const bindLearningSession = (
  mount: HTMLElement,
  section: LearningSection,
  lang: Language,
  opts: {
    reviewOnly?: boolean;
    onExit: () => void;
    onComplete: (handoff: LearningHandoff) => void;
    onGoDeeper: (handoff: LearningHandoff) => void;
    onViewProvision: (act: string, sectionLabel: string) => void;
    localizedPath: (path: string) => string;
  },
): void => {
  const map = getProgress();
  const deck = opts.reviewOnly
    ? reviewQueue(section, map)
    : [...section.cards].sort((a, b) => a.sort_order - b.sort_order);
  if (deck.length === 0) {
    mount.innerHTML = renderComplete(section, lang, opts);
    wireComplete(mount, section, lang, opts);
    return;
  }

  let index = 0;
  let revealed = false;
  let startX = 0;
  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const paint = (): void => {
    const card = deck[index];
    if (!card) {
      mount.innerHTML = renderComplete(section, lang, opts);
      wireComplete(mount, section, lang, opts);
      return;
    }
    const total = deck.length;
    const pct = Math.round(((index) / total) * 100);
    const badge = card.authority_type === 'doctrine'
      ? (lang === 'bn' ? 'মতবাদ · পর্যালোচনা নোট' : 'Doctrine · reviewer note')
      : (lang === 'bn' ? 'উৎস যাচাইকৃত' : 'Source checked');
    const face = revealed ? `
      <div class="learn-card-face learn-card-back" aria-live="polite">
        <div class="learn-card-top">
          <span class="learn-chip answer">${lang === 'bn' ? 'উত্তর' : 'Answer'}</span>
          <span class="learn-chip type">${esc(typeLabel(card, lang))}</span>
        </div>
        <h2 class="learn-answer">${esc(txt(card, lang, 'answer'))}</h2>
        <p class="learn-explain">${esc(txt(card, lang, 'explanation'))}</p>
        <div class="learn-source">
          <div class="learn-source-head">
            <span class="learn-source-badge">${esc(badge)}</span>
            <button type="button" class="learn-source-link" data-learn="provision">${lang === 'bn' ? 'ধারা দেখুন' : 'View provision'}</button>
          </div>
          <strong>${esc(card.act_name)}</strong>
          <span class="learn-source-ref">${esc(card.section_label)}</span>
        </div>
        <blockquote class="learn-bn-key" lang="bn">
          <span class="learn-bn-label">বাংলা মূলনীতি</span>
          ${esc(card.key_principle_bn)}
        </blockquote>
        ${card.authority_note ? `<p class="learn-doctrine-note">${esc(card.authority_note)}</p>` : ''}
      </div>` : `
      <div class="learn-card-face learn-card-front">
        ${assetMarkup(card)}
        <div class="learn-card-top">
          <span class="learn-chip micro">${esc(card.label)}</span>
          <span class="learn-chip type">${esc(typeLabel(card, lang))}</span>
        </div>
        <h2 class="learn-hook">${esc(txt(card, lang, 'hook'))}</h2>
        <p class="learn-question">${esc(txt(card, lang, 'question'))}</p>
        <button type="button" class="learn-reveal-btn" data-learn="reveal">
          <span>${lang === 'bn' ? 'উত্তর দেখুন' : 'Reveal answer'}</span>
          <span class="learn-reveal-arrow" aria-hidden="true">→</span>
        </button>
      </div>`;

    mount.innerHTML = `
      <div class="learn-session ${revealed ? 'is-revealed' : ''}" data-learn-session>
        <div class="learn-session-top">
          <header class="learn-session-bar">
            <button type="button" class="learn-back-btn" data-learn="exit" aria-label="${lang === 'bn' ? 'ফিরে যান' : 'Back'}">
              <span aria-hidden="true">←</span>
              <span>${lang === 'bn' ? 'বিষয়' : 'Topics'}</span>
            </button>
            <div class="learn-session-meta">
              <strong>${esc(lang === 'bn' ? section.title_bn : section.title_en)}</strong>
              <span>${lang === 'bn' ? `কার্ড ${index + 1} / ${total}` : `Card ${index + 1} of ${total}`}</span>
            </div>
          </header>
          <div class="learn-progress-track learn-session-track" role="progressbar" aria-valuenow="${pct}" aria-valuemin="0" aria-valuemax="100">
            <span style="width:${pct}%"></span>
          </div>
        </div>
        <div class="learn-stage">
          <div class="learn-stack">
            <div class="learn-ghost g2" aria-hidden="true"></div>
            <div class="learn-ghost g1" aria-hidden="true"></div>
            <article class="learn-card ${revealed ? 'is-revealed' : 'is-front'} ${reduced ? 'is-reduced' : ''}" data-learn-card tabindex="0">
              ${face}
            </article>
          </div>
        </div>
        <div class="learn-controls ${revealed ? 'is-active' : 'is-locked'}">
          <button type="button" class="learn-ctrl review" data-learn="review" ${revealed ? '' : 'disabled'} aria-disabled="${revealed ? 'false' : 'true'}">
            <span class="learn-ctrl-ico" aria-hidden="true">↻</span>
            <span>${lang === 'bn' ? 'আবার দেখুন' : 'Review again'}</span>
          </button>
          <button type="button" class="learn-ctrl flag" data-learn="flag" aria-label="${lang === 'bn' ? 'রিপোর্ট' : 'Report'}">⚑</button>
          <button type="button" class="learn-ctrl gotit" data-learn="gotit" ${revealed ? '' : 'disabled'} aria-disabled="${revealed ? 'false' : 'true'}" title="${revealed ? '' : (lang === 'bn' ? 'আগে উত্তর দেখুন' : 'Reveal the answer first')}">
            <span class="learn-ctrl-ico" aria-hidden="true">✓</span>
            <span>${lang === 'bn' ? 'বুঝেছি' : 'Got it'}</span>
          </button>
        </div>
      </div>
      <div class="learn-report-sheet" hidden data-learn-report>
        <div class="learn-report-card">
          <h3>${lang === 'bn' ? 'এই কার্ড রিপোর্ট করুন' : 'Report this card'}</h3>
          <p class="learn-report-hint">${lang === 'bn' ? 'সমস্যা নির্বাচন করুন।' : 'Choose what needs review.'}</p>
          ${REPORT_OPTIONS.map(([id, en, bn]) => `<button type="button" data-learn-issue="${id}">${lang === 'bn' ? bn : en}</button>`).join('')}
          <button type="button" class="button-secondary learn-report-cancel" data-learn="close-report">${lang === 'bn' ? 'বাতিল' : 'Cancel'}</button>
        </div>
      </div>`;
    bindCardMotion();
  };

  const bindCardMotion = (): void => {
    const cardEl = mount.querySelector<HTMLElement>('[data-learn-card]');
    if (!cardEl || reduced) return;
    const reset = () => { cardEl.style.transform = ''; };
    cardEl.onpointermove = (event) => {
      if (revealed) return;
      const rect = cardEl.getBoundingClientRect();
      const px = (event.clientX - rect.left) / rect.width - 0.5;
      const py = (event.clientY - rect.top) / rect.height - 0.5;
      cardEl.style.transform = `perspective(900px) rotateY(${px * 8}deg) rotateX(${-py * 6}deg) translateY(-2px)`;
    };
    cardEl.onpointerleave = reset;
    cardEl.onpointerup = reset;
  };

  const advance = (state: 'got_it' | 'review_again'): void => {
    const card = deck[index];
    if (!card || !revealed) return;
    setCardProgress(card.id, state, true);
    void fetch('/api/learning/cards/' + encodeURIComponent(card.id) + '/progress', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'X-Guest-Id': localStorage.getItem('justor-guest-id') || 'guest_local' },
      body: JSON.stringify({ state, revealed: true }),
    }).catch(() => undefined);
    revealed = false;
    index += 1;
    paint();
  };

  mount.onclick = (event) => {
    const t = (event.target as HTMLElement).closest<HTMLElement>('[data-learn], [data-learn-issue]');
    const action = t?.dataset.learn;
    const issue = t?.dataset.learnIssue;
    if (issue) {
      const card = deck[index];
      if (card) {
        addReport(card.id, issue, '', card.content_version);
        void fetch('/api/learning/cards/' + encodeURIComponent(card.id) + '/report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ issue_type: issue, card_version: card.content_version }),
        }).catch(() => undefined);
      }
      const sheet = mount.querySelector<HTMLElement>('[data-learn-report]');
      if (sheet) sheet.hidden = true;
      return;
    }
    if (action === 'exit') opts.onExit();
    if (action === 'reveal' && !revealed) {
      revealed = true;
      paint();
      return;
    }
    if (action === 'gotit') advance('got_it');
    if (action === 'review') advance('review_again');
    if (action === 'flag') {
      const sheet = mount.querySelector<HTMLElement>('[data-learn-report]');
      if (sheet) sheet.hidden = false;
    }
    if (action === 'close-report') {
      const sheet = mount.querySelector<HTMLElement>('[data-learn-report]');
      if (sheet) sheet.hidden = true;
    }
    if (action === 'provision') {
      const card = deck[index];
      if (card) opts.onViewProvision(card.act_name, card.section_label);
    }
    if (!action && (event.target as HTMLElement).closest('[data-learn-card]') && !revealed) {
      revealed = true;
      paint();
    }
  };

  mount.onkeydown = (event) => {
    if (event.key === ' ' || event.key === 'Enter') {
      if (!revealed) { event.preventDefault(); revealed = true; paint(); }
    }
    if (revealed && event.key === 'ArrowRight') advance('got_it');
    if (revealed && event.key === 'ArrowLeft') advance('review_again');
  };

  mount.ontouchstart = (event) => { startX = event.changedTouches[0]?.clientX ?? 0; };
  mount.ontouchend = (event) => {
    if (!revealed) return;
    const dx = (event.changedTouches[0]?.clientX ?? 0) - startX;
    if (dx > 80) advance('got_it');
    if (dx < -80) advance('review_again');
  };

  paint();
};

const renderComplete = (section: LearningSection, lang: Language, _opts: { localizedPath: (path: string) => string }): string => {
  const s = sectionStats(section);
  const primaryReview = s.review > 0;
  return `
    <div class="learn-complete">
      <span class="section-kicker">${lang === 'bn' ? 'বিষয় সম্পন্ন' : 'Topic complete'}</span>
      <h1>${esc(lang === 'bn' ? section.title_bn : section.title_en)}</h1>
      <div class="learn-complete-stats">
        <span>✓ ${s.got} ${lang === 'bn' ? 'বুঝেছি' : 'Got it'}</span>
        <span>↻ ${s.review} ${lang === 'bn' ? 'আবার' : 'Review'}</span>
        <span>${section.card_count} ${lang === 'bn' ? 'কার্ড' : 'cards'}</span>
      </div>
      ${primaryReview ? `<button type="button" class="button" data-learn-complete="review">${lang === 'bn' ? `${s.review}টি আবার দেখুন` : `Review ${s.review} again`}</button>` : ''}
      <button type="button" class="${primaryReview ? 'button-secondary' : 'button'}" data-learn-complete="deeper">${lang === 'bn' ? 'Justor AI দিয়ে আরও গভীরে' : 'Go deeper with Justor AI'}</button>
      <a class="text-link" href="${_opts.localizedPath('/workspace/student/learn')}" data-route data-learn-complete="next">${lang === 'bn' ? 'পরবর্তী বিষয়' : 'Next topic'}</a>
    </div>`;
};

const wireComplete = (
  mount: HTMLElement,
  section: LearningSection,
  lang: Language,
  opts: {
    onGoDeeper: (handoff: LearningHandoff) => void;
    onComplete: (handoff: LearningHandoff) => void;
  },
): void => {
  const progress = getProgress();
  const payload: LearningHandoff = {
    subjectId: 'contract-act-1872',
    sectionId: section.slug,
    sessionId: `local-${section.slug}`,
    gotItCardIds: section.cards.filter((c) => progress[c.id]?.state === 'got_it').map((c) => c.id),
    reviewCardIds: section.cards.filter((c) => progress[c.id]?.state === 'review_again').map((c) => c.id),
    language: lang,
  };
  mount.querySelector('[data-learn-complete="review"]')?.addEventListener('click', () => opts.onComplete(payload));
  mount.querySelector('[data-learn-complete="deeper"]')?.addEventListener('click', () => opts.onGoDeeper(payload));
};

export const buildGoDeeperQuery = (section: LearningSection, handoff: LearningHandoff): { query: string; displayQuery: string } => {
  const cards = Object.fromEntries(section.cards.map((c) => [c.id, c]));
  const focusIds = (handoff.reviewCardIds.length ? handoff.reviewCardIds : handoff.gotItCardIds)
    .filter((id) => cards[id]);
  const ids = focusIds.length ? focusIds : section.cards.map((c) => c.id);
  const provisions = [...new Set(ids.map((id) => cards[id]?.section_label).filter(Boolean))].join(', ');
  const hooks = ids.slice(0, 6).map((id) => {
    const card = cards[id];
    return handoff.language === 'bn' ? card.hook_bn : card.hook_en;
  }).join('; ');
  const topic = handoff.language === 'bn' ? section.title_bn : section.title_en;
  const query = `Contract Act 1872 Bangladesh ${provisions}. Teach a first-year law student these ideas: ${hooks}. Quote the controlling statutory rule, give one short Bangladesh example, then ask one check-for-understanding question.`;
  const displayQuery = handoff.language === 'bn'
    ? `বাইট-সাইজ থেকে আরও গভীরে: ${topic}`
    : `Go deeper: ${topic}`;
  return { query, displayQuery };
};
