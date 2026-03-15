// src/pages/landing.ts
import { auth } from '../auth'; // <-- CORRECTED PATH
import { i18n } from '../i18n';   // <-- CORRECTED PATH

declare const particlesJS: any;

// --- Main render function for the landing page ---
export function renderLandingPage(container: HTMLElement) {
    // --- NEW: Check the user's session state ---
    const session = auth.getSession();

    // --- NEW: Dynamically generate the Call-to-Action buttons ---
    let ctaButtonsHTML = '';
    if (session) {
        // User is LOGGED IN: Show a single button to go to the app.
        ctaButtonsHTML = `
            <a href="/app" class="cta-button cta-primary" data-link>${i18n.t('landing_cta_goToApp')}</a>
        `;
    } else {
        // User is LOGGED OUT: Show the original two buttons.
        ctaButtonsHTML = `
            <a href="/app" class="cta-button cta-secondary" data-link>${i18n.t('landing_cta_guest')}</a>
            <a href="/login" class="cta-button cta-primary" data-link>${i18n.t('landing_cta_signup')}</a>
        `;
    }

    // --- Build the final HTML using the dynamic buttons ---
    const landingHTML = `
      <div class="landing-page-wrapper">
        <section class="hero-section">
          <div id="particles-js"></div> 
          <div class="hero-content">
            <h1>${i18n.t('landing_heroTitle_1')} <span class="highlight">${i18n.t('landing_heroTitle_2')}</span></h1>
            <p class="hero-subtitle">${i18n.t('landing_heroSubtitle')}</p>
            <p class="hero-description">${i18n.t('landing_heroDescription')}</p>
            <div class="cta-buttons">
              ${ctaButtonsHTML}
            </div>
          </div>
        </section>

        <section id="features" class="features-section fade-in-section">
          <div class="section-header">
            <h2>${i18n.t('landing_featuresTitle')}</h2>
            <p>${i18n.t('landing_featuresSubtitle')}</p>
          </div>
          <div class="features-grid">
            <div class="feature-card feature-card-animated">
              <div class="feature-icon-wrapper">
                <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-4.67c.625-.93.928-2.036.928-3.185V11a3 3 0 00-3-3H9.375a3 3 0 00-3 3v1.375c0 1.15.303 2.255.927 3.185z" /></svg>
              </div>
              <h3>${i18n.t('landing_feature1_title')}</h3>
              <p>${i18n.t('landing_feature1_text')}</p>
            </div>
            <div class="feature-card feature-card-animated">
              <div class="feature-icon-wrapper">
                <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 006 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 016 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 016-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0018 18a8.967 8.967 0 00-6 2.292m0-14.25v14.25" /></svg>
              </div>
              <h3>${i18n.t('landing_feature2_title')}</h3>
              <p>${i18n.t('landing_feature2_text')}</p>
            </div>
            <div class="feature-card feature-card-animated">
              <div class="feature-icon-wrapper">
                <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3.75 21h16.5M4.5 3h15M5.25 3v18M18.75 3v18M9 21V7.5M15 21V7.5M3 12h18M3 15h18M3 9h18" /></svg>
              </div>
              <h3>${i18n.t('landing_feature3_title')}</h3>
              <p>${i18n.t('landing_feature3_text')}</p>
            </div>
          </div>
        </section>

        <section class="example-questions-section fade-in-section">
          <button class="try-these-btn">${i18n.t('landing_tryTheseBtn')}</button>
          <h2>${i18n.t('landing_exampleQuestionsTitle')}</h2>
          <p class="section-subtitle">${i18n.t('landing_exampleQuestionsSubtitle')}</p>
          <div class="example-questions-grid">
            <div class="example-question-card">
              <div class="question-icon">📄</div>
              <p>${i18n.t('app_query_1')}</p>
            </div>
            <div class="example-question-card">
              <div class="question-icon">🏠</div>
              <p>${i18n.t('app_query_2')}</p>
            </div>
            <div class="example-question-card">
              <div class="question-icon">👮</div>
              <p>${i18n.t('app_query_3')}</p>
            </div>
            <div class="example-question-card">
              <div class="question-icon">💼</div>
              <p>${i18n.t('app_query_4')}</p>
            </div>
          </div>
        </section>

        <section class="final-cta-section fade-in-section">
          <div class="final-cta-gradient">
            <h2>${i18n.t('landing_finalCtaTitle')}</h2>
            <p>${i18n.t('landing_finalCtaSubtitle')}</p>
          </div>
        </section>

        <footer class="footer">
          <div class="footer-content">
            <p class="footer-copyright">© ${new Date().getFullYear()} Justor AI - All Rights Reserved.</p>
            
            <div class="footer-links">
              <a href="/about" data-link>${i18n.t('footer_about')}</a>
              <a href="/about#contact" data-link>${i18n.t('footer_contact')}</a>
              <a href="#">${i18n.t('footer_privacy')}</a>
              <a href="#">${i18n.t('footer_terms')}</a>
            </div>
            
            <div class="footer-social">
              <span class="social-label">Follow Us:</span>
              <a href="https://www.linkedin.com/company/justor-ai/posts/?feedView=all" target="_blank" rel="noopener noreferrer" class="social-link" title="LinkedIn">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
                </svg>
              </a>
              <a href="https://www.facebook.com/justorai1/about" target="_blank" rel="noopener noreferrer" class="social-link" title="Facebook">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M9 8h-3v4h3v12h5v-12h3.642l.358-4h-4v-1.667c0-.955.192-1.333 1.115-1.333h2.885v-5h-3.808c-3.596 0-5.192 1.583-5.192 4.615v3.385z"/>
                </svg>
              </a>
              <a href="https://x.com/justor_ai" target="_blank" rel="noopener noreferrer" class="social-link" title="Twitter/X">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
                </svg>
              </a>
              <a href="https://www.instagram.com/justor_ai/" target="_blank" rel="noopener noreferrer" class="social-link" title="Instagram">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
              </a>
            </div>
          </div>
        </footer>
      </div>
    `;

    container.innerHTML = landingHTML;
    initParticles(); 
    setupFadeInAnimations();
    setupInteractiveBackground();
}


// --- These helper functions remain unchanged ---
function initParticles() {
  if (document.getElementById('particles-js')) {
    particlesJS('particles-js', { particles: { number: { value: 70, density: { enable: true, value_area: 800 } }, color: { value: ["#7C3AED", "#A78BFA", "#F59E0B"] }, shape: { type: "circle" }, opacity: { value: 0.5, random: true, anim: { enable: true, speed: 1, opacity_min: 0.1, sync: false } }, size: { value: 4, random: true, anim: { enable: true, speed: 2, size_min: 0.5, sync: false } }, line_linked: { enable: true, distance: 150, color: "#7C3AED", opacity: 0.25, width: 1.5 }, move: { enable: true, speed: 2, direction: "none", random: true, straight: false, out_mode: "out", bounce: false } }, interactivity: { detect_on: "canvas", events: { onhover: { enable: true, mode: "grab" }, onclick: { enable: true, mode: "push" }, resize: true }, modes: { grab: { distance: 160, line_linked: { opacity: 0.6 } }, push: { particles_nb: 4 } } }, retina_detect: true });
  }
}

function setupFadeInAnimations() {
  const sections = document.querySelectorAll('.fade-in-section');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });
  sections.forEach(section => { observer.observe(section); });
}

function setupInteractiveBackground() {
  const heroSection = document.querySelector('.hero-section') as HTMLElement;
  if (!heroSection) return;

  heroSection.addEventListener('mousemove', (e) => {
    const rect = heroSection.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    heroSection.style.setProperty('--mouse-x', `${x}%`);
    heroSection.style.setProperty('--mouse-y', `${y}%`);
  });

  heroSection.addEventListener('mouseleave', () => {
    heroSection.style.setProperty('--mouse-x', '50%');
    heroSection.style.setProperty('--mouse-y', '50%');
  });
}