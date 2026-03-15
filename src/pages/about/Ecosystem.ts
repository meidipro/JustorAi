// src/pages/about/Ecosystem.ts

export function renderEcosystem(): string {
  return `
  <section id="ecosystem" class="inv-section">
    <div class="inv-section__header">
      <span class="inv-section__eyebrow">The Solution</span>
      <h2 class="inv-section__title">What is Justor AI?</h2>
      <p class="inv-section__intro">Justor AI is Bangladesh's first bilingual (Bangla and English) <strong>Legal Intelligence Ecosystem</strong>. We are not a generic chatbot. We are a transparent "Law Box" for the public and a high-speed Research Assistant for legal professionals, powered by a custom <strong>Retrieval-Augmented Generation (RAG)</strong> architecture.</p>
    </div>

    <div class="inv-persona-grid">
      <!-- Card 1: Citizen -->
      <div class="inv-persona-card inv-persona-card--citizen">
        <div class="inv-persona-card__header">
          <div class="inv-persona-card__icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
          </div>
          <span class="inv-persona-card__badge inv-persona-card__badge--green">For Citizens</span>
        </div>
        <h3 class="inv-persona-card__title">The Law Box</h3>
        <p class="inv-persona-card__text">Scan complex legal documents for instant, simple summaries. Get step-by-step action plans for consumer scams, expired products, and everyday rights in plain Bangla. It turns vulnerable citizens into informed individuals.</p>
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
        <h3 class="inv-persona-card__title">The Socratic Tutor</h3>
        <p class="inv-persona-card__text">Replace heavy textbooks with an interactive study partner. Understand complex laws, DLRs, and penal codes through relatable, real-life case scenarios. Bridges the gap between textbook theory and courtroom reality.</p>
        <div class="inv-persona-card__accent"></div>
      </div>

      <!-- Card 3: Legal Professional -->
      <div class="inv-persona-card inv-persona-card--professional">
        <div class="inv-persona-card__header">
          <div class="inv-persona-card__icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="36" height="36" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
          </div>
          <span class="inv-persona-card__badge inv-persona-card__badge--blue">For Professionals</span>
        </div>
        <h3 class="inv-persona-card__title">The Junior Associate</h3>
        <p class="inv-persona-card__text">Automate legal research and citation generation. Input a client's case scenario to instantly retrieve applicable Acts and DLRs. Focus on high-value litigation while Justor AI provides you with Educated Clients.</p>
        <div class="inv-persona-card__accent"></div>
      </div>
    </div>
  </section>
  `;
}
