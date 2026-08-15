// src/pages/guides.ts
import { LEGAL_GUIDES, type LegalGuide } from '../data/guidesData';
import { i18n } from '../i18n';

export function renderGuidesPage(container: HTMLElement, slug?: string) {
  if (slug) {
    const guide = LEGAL_GUIDES.find(g => g.slug === slug);
    if (guide) {
      renderSingleGuide(container, guide);
      return;
    }
  }

  // Render Guide Catalog
  renderGuideCatalog(container);
}

function renderGuideCatalog(container: HTMLElement) {
  const isBn = i18n.getLanguage() === 'bn';

  container.innerHTML = `
    <div class="guides-container">
      <header class="guides-header">
        <div class="guides-badge">
          <span>${isBn ? 'নাগরিক আইনি নির্দেশিকা' : 'Citizen Legal Authority Guides'}</span>
        </div>
        <h1 class="guides-title">
          ${isBn ? 'বাংলাদেশের নির্ভরযোগ্য ও যাচাইকৃত আইনি গাইড' : 'Trustworthy & Source-Verified Bangladesh Legal Guides'}
        </h1>
        <p class="guides-subtitle">
          ${isBn 
            ? 'সরকারি আইন ও বিধিমালা অনুযায়ী সঠিক তথ্য জানুন। কোনো এআই অনুমান নয় — প্রতিটি তথ্যে মূল সরকারি আইনের সূত্র সংযুক্ত।'
            : 'Understand your rights with verified Bangladesh Code provisions. No AI guesses — every statement links to primary statutory authorities.'}
        </p>

        <div class="guides-search-bar">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input type="text" id="guides-search-input" placeholder="${isBn ? 'বিষয় খুঁজুন (যেমন: জমি নিবন্ধন, নামজারি, ভোক্তা অধিকার)...' : 'Search legal guides (e.g., land registration, mutation, consumer rights)...'}">
        </div>

        <div class="guides-category-pills">
          <button class="cat-pill active" data-cat="all">${isBn ? `সকল গাইড (${LEGAL_GUIDES.length})` : `All Guides (${LEGAL_GUIDES.length})`}</button>
          <button class="cat-pill" data-cat="property">${isBn ? 'জমি ও সম্পত্তি' : 'Property & Land'}</button>
          <button class="cat-pill" data-cat="tax">${isBn ? 'কর ও অর্থ' : 'Tax & Finance'}</button>
          <button class="cat-pill" data-cat="family">${isBn ? 'পারিবারিক আইন' : 'Family & Succession'}</button>
          <button class="cat-pill" data-cat="employment">${isBn ? 'চাকরি ও শ্রম' : 'Employment & Labour'}</button>
          <button class="cat-pill" data-cat="consumer">${isBn ? 'ভোক্তা অধিকার' : 'Consumer Rights'}</button>
          <button class="cat-pill" data-cat="digital">${isBn ? 'সাইবার ও ডিজিটাল' : 'Cyber & Digital'}</button>
        </div>
      </header>

      <div class="guides-grid" id="guides-grid">
        ${LEGAL_GUIDES.map(guide => renderGuideCard(guide, isBn)).join('')}
      </div>

      <div class="guides-cta-banner">
        <div class="cta-content">
          <h3>${isBn ? 'আপনার কি কোনো নির্দিষ্ট আইনি প্রশ্ন আছে?' : 'Have a specific legal situation?'}</h3>
          <p>${isBn ? 'Justor AI-কে আপনার ঘটনাটি বিস্তারিত বলুন এবং তাৎক্ষণিক সরকারি আইনের সূত্রসহ উত্তর পান।' : 'Ask Justor AI to get structured next steps and verified Bangladesh law citations.'}</p>
        </div>
        <a href="/app" class="cta-button" data-link>
          ${isBn ? 'জাস্টিস এআই-এ প্রশ্ন করুন →' : 'Ask Justor AI Now →'}
        </a>
      </div>
    </div>
  `;

  // Search filter interaction
  const searchInput = document.getElementById('guides-search-input') as HTMLInputElement;
  const grid = document.getElementById('guides-grid') as HTMLDivElement;
  const pills = document.querySelectorAll('.cat-pill');

  let currentCategory = 'all';

  function filterGuides() {
    const query = (searchInput?.value || '').toLowerCase().trim();
    const filtered = LEGAL_GUIDES.filter(g => {
      const matchCat = currentCategory === 'all' || g.category === currentCategory;
      const matchQuery = !query || 
        g.titleBn.toLowerCase().includes(query) || 
        g.titleEn.toLowerCase().includes(query) || 
        g.directAnswer.toLowerCase().includes(query) ||
        g.applicableLaw.toLowerCase().includes(query);
      return matchCat && matchQuery;
    });

    if (filtered.length === 0) {
      grid.innerHTML = `
        <div class="no-guides-found">
          <p>${isBn ? 'কোনো গাইড খুঁজে পাওয়া যায়নি।' : 'No guides found matching your search.'}</p>
          <a href="/app" class="btn-ask-ai" data-link>${isBn ? 'Justor AI-কে সরাসরি প্রশ্ন করুন' : 'Ask Justor AI Directly'}</a>
        </div>
      `;
    } else {
      grid.innerHTML = filtered.map(g => renderGuideCard(g, isBn)).join('');
    }
  }

  searchInput?.addEventListener('input', filterGuides);

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      currentCategory = pill.getAttribute('data-cat') || 'all';
      filterGuides();
    });
  });
}

function renderGuideCard(guide: LegalGuide, isBn: boolean): string {
  return `
    <article class="guide-card">
      <div class="card-meta">
        <span class="card-category">${isBn ? guide.categoryNameBn : guide.categoryNameEn}</span>
        <span class="card-verified">SOURCE CHECKED ✓</span>
      </div>
      <h2 class="card-title">
        <a href="/guides/${guide.slug}" data-link>${isBn ? guide.titleBn : guide.titleEn}</a>
      </h2>
      <p class="card-desc">${guide.directAnswer.substring(0, 140)}...</p>
      <div class="card-footer">
        <span class="card-law">${guide.applicableLaw.split(';')[0]}</span>
        <a href="/guides/${guide.slug}" class="card-read-more" data-link>
          ${isBn ? 'সম্পূর্ণ গাইড পড়ুন →' : 'Read Guide →'}
        </a>
      </div>
    </article>
  `;
}

function renderSingleGuide(container: HTMLElement, guide: LegalGuide) {
  const isBn = i18n.getLanguage() === 'bn';

  container.innerHTML = `
    <div class="single-guide-container">
      <nav class="guide-breadcrumb">
        <a href="/guides" data-link>${isBn ? '← সকল নির্দেশিকা' : '← All Legal Guides'}</a>
        <span>/</span>
        <span>${isBn ? guide.categoryNameBn : guide.categoryNameEn}</span>
      </nav>

      <header class="single-guide-header">
        <div class="trust-badge-row">
          <span class="badge-primary">PRIMARY SOURCE ✓</span>
          <span class="badge-checked">SOURCE CHECKED ✓</span>
          <span class="badge-date">${isBn ? 'সর্বশেষ যাচাইকৃত:' : 'Last Reviewed:'} ${guide.lastReviewed}</span>
        </div>
        <h1 class="single-guide-h1">${isBn ? guide.titleBn : guide.titleEn}</h1>
        <p class="single-guide-subtitle">${guide.subtitleEn}</p>
        <div class="applicable-law-bar">
          <strong>${isBn ? 'প্রযোজ্য আইন:' : 'Governing Law:'}</strong> ${guide.applicableLaw}
        </div>
      </header>

      <!-- Direct Answer Box -->
      <section class="at-a-glance-box">
        <div class="box-header">
          <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
          <h3>${isBn ? 'এক নজরে সরাসরি উত্তর (At a Glance)' : 'Direct Legal Answer (At a Glance)'}</h3>
        </div>
        <p class="direct-text">${guide.directAnswer}</p>
        <div class="glance-grid">
          <div class="glance-item">
            <span class="glance-label">${isBn ? 'কাদের জন্য প্রযোজ্য' : 'Applies To'}</span>
            <span class="glance-val">${guide.highlights.appliesTo}</span>
          </div>
          <div class="glance-item">
            <span class="glance-label">${isBn ? 'সময়সীমা / ডেডলাইন' : 'Statutory Deadline'}</span>
            <span class="glance-val">${guide.highlights.deadline}</span>
          </div>
          <div class="glance-item">
            <span class="glance-label">${isBn ? 'মূল কর্তৃপক্ষ' : 'Primary Authority'}</span>
            <span class="glance-val">${guide.highlights.authority}</span>
          </div>
        </div>
      </section>

      <!-- What the Law Says -->
      <section class="guide-section">
        <h2>${isBn ? 'আইন কী বলে (What the Law Says)' : 'What the Law Says'}</h2>
        <div class="law-content-card">
          <p>${guide.lawSummary}</p>
        </div>
      </section>

      <!-- Step by Step Process -->
      <section class="guide-section">
        <h2>${isBn ? 'ধাপে ধাপে করণীয় প্রক্রিয়া' : 'Step-by-Step Procedure'}</h2>
        <div class="steps-timeline">
          ${guide.steps.map((step, idx) => `
            <div class="step-card">
              <div class="step-num">${idx + 1}</div>
              <div class="step-body">
                <h4>${step.title}</h4>
                <p>${step.desc}</p>
              </div>
            </div>
          `).join('')}
        </div>
      </section>

      <!-- Required Documents -->
      <section class="guide-section">
        <h2>${isBn ? 'প্রয়োজনীয় কাগজপত্রের তালিকা' : 'Required Documents Checklist'}</h2>
        <ul class="doc-checklist">
          ${guide.documentsRequired.map(doc => `
            <li>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5"><polyline points="20 6 9 17 4 12"></polyline></svg>
              <span>${doc}</span>
            </li>
          `).join('')}
        </ul>
      </section>

      <!-- Fees & Timeline -->
      <section class="guide-section">
        <h2>${isBn ? 'সরকারি ফি ও সময়সীমা' : 'Government Fees & Official Timeline'}</h2>
        <div class="fee-card">
          <p>${guide.feesTimeline}</p>
        </div>
      </section>

      <!-- Real Example Scenario -->
      <section class="guide-section">
        <h2>${isBn ? 'বাস্তব উদাহরণ ও সমাধান' : 'Real-Life Scenario & Legal Outcome'}</h2>
        <div class="scenario-card">
          <h4>${guide.exampleScenario.title}</h4>
          <p class="scen-situation"><strong>${isBn ? 'পরিস্থিতি:' : 'Situation:'}</strong> ${guide.exampleScenario.situation}</p>
          <p class="scen-outcome"><strong>${isBn ? 'আইনি ফলাফল:' : 'Legal Outcome:'}</strong> ${guide.exampleScenario.legalOutcome}</p>
        </div>
      </section>

      <!-- Common Mistakes -->
      <section class="guide-section">
        <h2>${isBn ? 'যেসব ভুল অবশ্যই এড়িয়ে চলবেন' : 'Common Mistakes to Avoid'}</h2>
        <ul class="mistake-list">
          ${guide.commonMistakes.map(m => `
            <li>
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
              <span>${m}</span>
            </li>
          `).join('')}
        </ul>
      </section>

      <!-- Primary Sources & References -->
      <section class="guide-section">
        <h2>${isBn ? 'মূল আইনি সূত্র ও রেফারেন্স' : 'Primary Sources & Official Links'}</h2>
        <div class="source-list-box">
          ${guide.primarySources.map(s => `
            <div class="source-row">
              <div class="source-info">
                <span class="source-tag">[${s.id}]</span>
                <strong>${s.name}</strong> (${s.sections})
                <span class="source-status">${s.status}</span>
              </div>
              <a href="${s.url}" target="_blank" rel="noopener noreferrer" class="source-link">
                ${isBn ? 'সরকারি মূল আইন দেখুন ↗' : 'Open Official Source ↗'}
              </a>
            </div>
          `).join('')}
        </div>
        <p class="verification-philosophy-note">
          ⚖️ <em>Justor summarizes the cited material to reduce research time. Please open and verify the primary government authorities before taking formal action.</em>
        </p>
      </section>

      <!-- Ask AI CTA Gateway -->
      <div class="single-guide-cta">
        <div class="cta-text">
          <h3>${isBn ? 'আপনার সমস্যা কি কিছুটা আলাদা?' : 'Is your situation different or more complex?'}</h3>
          <p>${isBn ? 'Justor AI-তে আপনার ঘটনার বিবরণ দিয়ে সরকারি আইন অনুযায়ী পরামর্শ ও দিকনির্দেশনা পান।' : 'Ask Justor AI to get tailored, source-linked answers for your specific scenario.'}</p>
        </div>
        <button id="ask-ai-from-guide-btn" class="cta-btn-large">
          ${isBn ? 'জাস্টিস এআই-এ প্রশ্ন করুন →' : 'Ask Justor AI About This →'}
        </button>
      </div>
    </div>
  `;

  // Handle CTA button click
  document.getElementById('ask-ai-from-guide-btn')?.addEventListener('click', () => {
    sessionStorage.setItem('justor_prefill_query', `I am reading the legal guide on "${guide.titleEn}". Can you explain how this law applies to my specific situation?`);
    history.pushState(null, '', '/app');
    const event = new PopStateEvent('popstate');
    window.dispatchEvent(event);
  });
}
