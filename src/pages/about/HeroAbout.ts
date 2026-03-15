// src/pages/about/HeroAbout.ts

export function renderHeroAbout(): string {
  return `
  <section id="about-hero" class="inv-hero">
    <div class="inv-hero__inner">
      <span class="inv-hero__badge">🏛️ About Us</span>
      <h1 class="inv-hero__title">About Justor AI: The Digital Infrastructure for Justice</h1>
      <p class="inv-hero__subtitle">We are building the bridge between 170 million Bangladeshis and their fundamental rights.</p>
      
      <div class="inv-hero__pillars">
        <div class="inv-hero__pillar">
          <div class="inv-hero__pillar-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
          </div>
          <h3>Our Mission</h3>
          <p>To democratize legal access in Bangladesh by translating complex legal codes and Acts into instant, transparent, and actionable civic power.</p>
        </div>
        <div class="inv-hero__pillar">
          <div class="inv-hero__pillar-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
          </div>
          <h3>Our Vision</h3>
          <p>A Digital Bangladesh where no citizen pays a bribe out of ignorance, no law student struggles without mentorship, and no lawyer wastes billable hours on manual research.</p>
        </div>
      </div>
    </div>
  </section>
  `;
}
