// src/pages/about/MarketSize.ts

export function renderMarketSize(): string {
  return `
  <section id="investor-metrics" class="inv-section inv-market">
    <div class="inv-market__bg-pattern"></div>
    <div class="inv-section__header">
      <span class="inv-section__eyebrow">Market Opportunity</span>
      <h2 class="inv-section__title">Market Size &amp; Opportunity</h2>
    </div>

    <div class="inv-market-grid">
      <!-- TAM -->
      <div class="inv-market-card inv-market-card--tam">
        <div class="inv-market-card__ring">
          <span class="inv-market-card__ring-label">TAM</span>
        </div>
        <div class="inv-market-card__number">77.7M</div>
        <div class="inv-market-card__metric">Total Addressable Market</div>
        <p class="inv-market-card__desc">Active mobile internet users in Bangladesh — every citizen with a smartphone is a potential Justor AI user.</p>
      </div>

      <!-- SAM -->
      <div class="inv-market-card inv-market-card--sam">
        <div class="inv-market-card__ring">
          <span class="inv-market-card__ring-label">SAM</span>
        </div>
        <div class="inv-market-card__number">60K+</div>
        <div class="inv-market-card__metric">Serviceable Addressable Market</div>
        <p class="inv-market-card__desc">Lawyers &amp; 160+ Universities — the legal professional and academic ecosystem ready for AI-powered research tools.</p>
      </div>

      <!-- SOM -->
      <div class="inv-market-card inv-market-card--som">
        <div class="inv-market-card__ring">
          <span class="inv-market-card__ring-label">SOM</span>
        </div>
        <div class="inv-market-card__number">10,000</div>
        <div class="inv-market-card__metric">Serviceable Obtainable Market</div>
        <p class="inv-market-card__desc">Active Users — our Year 1 goal through university pilots, legal community partnerships, and organic adoption.</p>
      </div>
    </div>
  </section>
  `;
}
