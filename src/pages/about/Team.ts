// src/pages/about/Team.ts

export function renderTeam(): string {
  return `
  <section id="team" class="inv-section">
    <div class="inv-section__header">
      <span class="inv-section__eyebrow">Leadership</span>
      <h2 class="inv-section__title">Meet The Team</h2>
    </div>

    <div class="inv-team-grid">
      <!-- Tajuddin Ahamed -->
      <div class="inv-team-card">
        <div class="inv-team-card__avatar">
          <img src="https://media.licdn.com/dms/image/D5603AQG859G9o21jHw/profile-displayphoto-shrink_400_400/0/1718563998655?e=1727308800&v=beta&t=3E1zHnYM01u6eBSo_t2j5qV2j5iYFkZ3e2c5Y5E3E2c" alt="Tajuddin Ahamed" loading="lazy" />
          <div class="inv-team-card__avatar-ring"></div>
        </div>
        <h3 class="inv-team-card__name">Tajuddin Ahamed</h3>
        <span class="inv-team-card__role">CEO &amp; Product Architect</span>
        <span class="inv-team-card__tagline">The Visionary &amp; "User Zero"</span>
        <p class="inv-team-card__bio">Handled frontend UX/UI, market research, and overall product strategy. Drives the business vision to solve real-world civic problems.</p>
        <div class="inv-team-card__links">
          <a href="https://www.linkedin.com/in/tajuddin-ahamed-4r4t4x/" target="_blank" rel="noopener noreferrer" title="LinkedIn">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
          </a>
          <a href="mailto:tajuddinahamed.contact@gmail.com" title="Email">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
          </a>
        </div>
      </div>

      <!-- Mehedi Hasan -->
      <div class="inv-team-card">
        <div class="inv-team-card__avatar">
          <img src="https://avatars.githubusercontent.com/u/86288624?v=4" alt="Mehedi Hasan" loading="lazy" />
          <div class="inv-team-card__avatar-ring"></div>
        </div>
        <h3 class="inv-team-card__name">Mehedi Hasan</h3>
        <span class="inv-team-card__role">CTO &amp; Lead Engineer</span>
        <span class="inv-team-card__tagline">The Builder</span>
        <p class="inv-team-card__bio">Architected the proprietary RAG backend, vector database integration, and secure serverless AI infrastructure.</p>
        <div class="inv-team-card__links">
          <a href="https://www.linkedin.com/in/mehide-hasan/" target="_blank" rel="noopener noreferrer" title="LinkedIn">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
          </a>
          <a href="mailto:mehidehasanbds@gmail.com" title="Email">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
          </a>
        </div>
      </div>

      <!-- Anisur Rahman Sanjib -->
      <div class="inv-team-card">
        <div class="inv-team-card__avatar">
          <img src="https://placehold.co/400" alt="Anisur Rahman Sanjib" loading="lazy" />
          <div class="inv-team-card__avatar-ring"></div>
        </div>
        <h3 class="inv-team-card__name">Anisur Rahman Sanjib</h3>
        <span class="inv-team-card__role">COO &amp; Legal Lead</span>
        <span class="inv-team-card__tagline">The Domain Expert</span>
        <p class="inv-team-card__bio">Law Student managing data verification, ensuring output complies with Bar Council standards, and directing academic university relations.</p>
        <div class="inv-team-card__links">
          <a href="https://www.facebook.com/anisur.rahman.sanjib" target="_blank" rel="noopener noreferrer" title="Facebook">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
          </a>
          <a href="mailto:sanjibrahman1@gmail.com" title="Email">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
          </a>
        </div>
      </div>
    </div>
  </section>
  `;
}
