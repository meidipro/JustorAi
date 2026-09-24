// src/pages/about/Ecosystem.ts

export function renderEcosystem(): string {
  return `
  <section id="ecosystem" class="inv-section">
    <div class="inv-section__header">
      <span class="inv-section__eyebrow">The Solution</span>
      <h2 class="inv-section__title">What is Justor AI?</h2>
      <p class="inv-section__intro">Justor AI is Bangladesh's first bilingual (Bangla and English) <strong>Legal Intelligence Ecosystem</strong> built exclusively for lawyers, advocates, and law students. Powered by a custom <strong>Retrieval-Augmented Generation (RAG)</strong> architecture over canonical Bangladesh Codes, DLR precedents, and Supreme Court judgments.</p>
    </div>

    <div class="inv-persona-grid" style="grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));">
      <!-- Card 1: Legal Professional -->
      <div class="inv-persona-card inv-persona-card--professional">
        <div class="inv-persona-card__header">
          <div class="inv-persona-card__icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
          </div>
          <span class="inv-persona-card__badge inv-persona-card__badge--blue">For Advocates & Chambers</span>
        </div>
        <h3 class="inv-persona-card__title">Chamber OS & Legal Intelligence</h3>
        <p class="inv-persona-card__text">Automate case preparation, citation extraction, and cross-statute validation. Query complex facts against 100+ years of Bangladesh Supreme Court precedents and live gazettes in seconds. WhatsApp Chamber integration delivers instant legal references directly to your phone.</p>
        <div class="inv-persona-card__accent"></div>
      </div>

      <!-- Card 2: Law Student -->
      <div class="inv-persona-card inv-persona-card--student">
        <div class="inv-persona-card__header">
          <div class="inv-persona-card__icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 6 3 6 3s3 0 6-3v-5"/></svg>
          </div>
          <span class="inv-persona-card__badge inv-persona-card__badge--purple">For Law Students</span>
        </div>
        <h3 class="inv-persona-card__title">The Socratic Tutor & Bar Prep</h3>
        <p class="inv-persona-card__text">Replace heavy textbooks with an interactive study partner. Master complex statutory provisions, landmark DLRs, and penal codes through pedagogical breakdowns and practical courtroom scenarios. Accelerates LLB study and Bar Council preparation.</p>
        <div class="inv-persona-card__accent"></div>
      </div>
    </div>
  </section>
  `;
}
