// src/pages/about/CompetitiveAdvantage.ts

export function renderCompetitiveAdvantage(): string {
  return `
  <section id="competitive-advantage" class="inv-section">
    <div class="inv-section__header">
      <span class="inv-section__eyebrow">Our Edge</span>
      <h2 class="inv-section__title">Our Technology: The "Zero Hallucination" Guarantee</h2>
    </div>

    <div class="inv-advantage-layout">
      <!-- Left: Explanation -->
      <div class="inv-advantage__text">
        <p class="inv-advantage__body">Generic AI models (like ChatGPT) are built for creative writing—they <strong>guess</strong>, <strong>make up facts</strong>, and <strong>hallucinate fake laws</strong>. In the legal sector, a hallucination is a <em>liability</em>.</p>
        <p class="inv-advantage__body">Justor AI eliminates this risk. We built a <strong>Proprietary RAG Architecture</strong> powered by a self-hosted vector database (Supabase) containing verified Bangladeshi Acts and Dhaka Law Reports.</p>
        
        <div class="inv-advantage__comparison">
          <div class="inv-advantage__vs inv-advantage__vs--bad">
            <div class="inv-advantage__vs-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="m15 9-6 6"/><path d="m9 9 6 6"/></svg>
            </div>
            <span>Generic AI: Guesses &amp; Hallucinates</span>
          </div>
          <div class="inv-advantage__vs inv-advantage__vs--good">
            <div class="inv-advantage__vs-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>
            </div>
            <span>Justor AI: Verified &amp; Precise</span>
          </div>
        </div>
      </div>

      <!-- Right: Checkmark List -->
      <div class="inv-advantage__features">
        <div class="inv-advantage__features-header">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
          <span>Zero Hallucination Guarantees</span>
        </div>
        <ul class="inv-advantage__checklist">
          <li>
            <div class="inv-check-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <span>AI is securely "locked" into our verified database.</span>
          </li>
          <li>
            <div class="inv-check-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <span>Answers strictly use specific legal texts we have verified.</span>
          </li>
          <li>
            <div class="inv-check-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <span>If a law is not found, the AI defaults to: <strong>"I do not have this verified law in my database."</strong></span>
          </li>
          <li>
            <div class="inv-check-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
            <span>Guarantees absolute precision and protects users from legal misinformation.</span>
          </li>
        </ul>
      </div>
    </div>
  </section>
  `;
}
