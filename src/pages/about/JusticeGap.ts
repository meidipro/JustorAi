// src/pages/about/JusticeGap.ts

export function renderJusticeGap(): string {
  return `
  <section id="justice-gap" class="inv-section">
    <div class="inv-section__header">
      <span class="inv-section__eyebrow">The Crisis</span>
      <h2 class="inv-section__title">The Problem: The "Justice Gap"</h2>
      <p class="inv-section__intro">The legal system in Bangladesh is suffocating under the weight of a <strong>4.2 million pending case backlog</strong>. But the real crisis happens outside the courtroom:</p>
    </div>

    <div class="inv-stats-grid">
      <!-- Card 1: The Awareness Crisis -->
      <div class="inv-stat-card">
        <div class="inv-stat-card__icon inv-stat-card__icon--red">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <span class="inv-stat-card__label">The Awareness Crisis</span>
        <div class="inv-stat-card__number">170M</div>
        <p class="inv-stat-card__text">Citizens face daily exploitation. From telecom overcharging to expired products, citizens lack basic rights awareness and cannot read complex legal notices, leading to fear and extortion.</p>
      </div>

      <!-- Card 2: The Education Crisis -->
      <div class="inv-stat-card">
        <div class="inv-stat-card__icon inv-stat-card__icon--amber">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
        </div>
        <span class="inv-stat-card__label">The Education Crisis</span>
        <div class="inv-stat-card__number inv-stat-card__number--text">Broken System</div>
        <p class="inv-stat-card__text">Law students struggle to decode archaic legal jargon. Heavy books are inefficient, and traditional education lacks instant, real-world case scenarios.</p>
      </div>

      <!-- Card 3: The Professional Bottleneck -->
      <div class="inv-stat-card">
        <div class="inv-stat-card__icon inv-stat-card__icon--blue">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        </div>
        <span class="inv-stat-card__label">The Professional Bottleneck</span>
        <div class="inv-stat-card__number">40%</div>
        <p class="inv-stat-card__text">Of billable hours wasted by lawyers manually researching physical Dhaka Law Reports (DLR) and explaining fundamental rights to confused clients.</p>
      </div>
    </div>
  </section>
  `;
}
