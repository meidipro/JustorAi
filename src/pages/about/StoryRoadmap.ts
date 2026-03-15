// src/pages/about/StoryRoadmap.ts

export function renderStoryRoadmap(): string {
  return `
  <section id="story-roadmap" class="inv-section">
    <!-- Origin Story -->
    <div class="inv-story">
      <div class="inv-story__content">
        <span class="inv-section__eyebrow">Origin Story</span>
        <h2 class="inv-story__title">Built by the "User Zero"</h2>
        <div class="inv-story__quote">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V21zM15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/></svg>
        </div>
        <p class="inv-story__text">Justor AI was built by our CEO, <strong>Tajuddin Ahamed</strong>, after he faced illegal extortion from a monopoly ISP and a corrupt railway official. Unable to afford a lawyer, he spent weeks manually decoding dense government websites until he found the exact Consumer Rights and Railway Acts needed to fight back and win.</p>
        <p class="inv-story__text">He realized an instant AI research tool could change the country. He teamed up with CTO <strong>Mehedi Hasan</strong> to build the core AI engine, and COO <strong>Anisur Rahman Sanjib</strong> to verify the legal data.</p>
      </div>
    </div>

    <!-- Roadmap -->
    <div class="inv-roadmap">
      <div class="inv-section__header">
        <span class="inv-section__eyebrow">What's Next</span>
        <h2 class="inv-section__title">Our Objectives &amp; Roadmap</h2>
      </div>

      <div class="inv-roadmap-timeline">
        <!-- Phase 1 -->
        <div class="inv-roadmap-step inv-roadmap-step--active">
          <div class="inv-roadmap-step__marker">
            <div class="inv-roadmap-step__dot"></div>
            <span class="inv-roadmap-step__phase">Phase 1</span>
            <span class="inv-roadmap-step__status">Current</span>
          </div>
          <div class="inv-roadmap-step__card">
            <h4>Database Expansion &amp; University Pilots</h4>
            <p>Expand our Zero-Hallucination database to include the top 500 critical Bangladeshi Acts and complete pilot programs with university law faculties.</p>
          </div>
        </div>

        <!-- Phase 2 -->
        <div class="inv-roadmap-step">
          <div class="inv-roadmap-step__marker">
            <div class="inv-roadmap-step__dot"></div>
            <span class="inv-roadmap-step__phase">Phase 2</span>
          </div>
          <div class="inv-roadmap-step__card">
            <h4>Native Android App with OCR</h4>
            <p>Launch the Justor AI Native Android App featuring advanced OCR so citizens can simply take a photo of a legal document to have it explained in Bangla.</p>
          </div>
        </div>

        <!-- Phase 3 -->
        <div class="inv-roadmap-step">
          <div class="inv-roadmap-step__marker">
            <div class="inv-roadmap-step__dot"></div>
            <span class="inv-roadmap-step__phase">Phase 3</span>
          </div>
          <div class="inv-roadmap-step__card">
            <h4>Enterprise SaaS &amp; NGO Partnerships</h4>
            <p>Scale our B2B Enterprise SaaS to major law firms in Dhaka and partner with Legal Aid NGOs to bring instant legal triage to rural Bangladesh.</p>
          </div>
        </div>
      </div>
    </div>
  </section>
  `;
}
