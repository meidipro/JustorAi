import { renderHeroAbout } from './about/HeroAbout';
import { renderJusticeGap } from './about/JusticeGap';
import { renderEcosystem } from './about/Ecosystem';
import { renderCompetitiveAdvantage } from './about/CompetitiveAdvantage';
import { renderMarketSize } from './about/MarketSize';
import { renderStoryRoadmap } from './about/StoryRoadmap';
import { renderTeam } from './about/Team';

const aboutHTML = `
<div class="about-container inv-about-page">

  ${renderHeroAbout()}
  ${renderJusticeGap()}
  ${renderEcosystem()}
  ${renderCompetitiveAdvantage()}
  ${renderMarketSize()}
  ${renderStoryRoadmap()}
  ${renderTeam()}

  <!-- FAQ SECTION -->
  <section class="about-section faq-section">
    <h2 class="section-title">Frequently Asked Questions</h2>
    <div class="faq-container">
      <div class="faq-item">
        <button class="faq-question">Is Justor AI free to use?</button>
        <div class="faq-answer">
          <p>Absolutely. Justor AI is innovating within its current beta release. We are focused on gathering essential user feedback and securing strategic investments that will allow us to fully launch and scale the platform, bringing comprehensive legal intelligence to everyone.</p>
        </div>
      </div>
      <div class="faq-item">
        <button class="faq-question">Is this a substitute for a real lawyer?</button>
        <div class="faq-answer">
          <p><strong>No.</strong> The information provided by Justor AI is for informational and educational purposes only. It is not legal advice and should not be used as a substitute for consultation with a qualified legal professional. Always consult a lawyer for serious legal matters.</p>
        </div>
      </div>
      <div class="faq-item">
        <button class="faq-question">How up-to-date is the legal information?</button>
        <div class="faq-answer">
          <p>We strive to keep our knowledge base as current as possible by incorporating the latest laws and amendments from official government sources. However, there may be a delay between the official publication of a new law and its inclusion in our database.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- UPCOMING FEATURES SECTION -->
  <section class="about-section upcoming-features-section">
    <div class="features-header">
      <h2 class="section-title animate__animated animate__fadeIn">🔮 Upcoming Features</h2>
      <p class="section-subtitle">The future of legal intelligence is here</p>
    </div>
    
    <div class="features-grid">
      <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.1s;">
        <div class="feature-icon">📄</div>
        <h3>Multilingual Document Analysis</h3>
        <p>Upload any legal document in Bangla, English, or other languages for instant AI review, risk highlights, and plain-language explanation.</p>
      </div>
      
      <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.2s;">
        <div class="feature-icon">✅</div>
        <h3>Client Document Verification</h3>
        <p>Lawyers can cross-check NID, passport, receipts, and case documents for accuracy in seconds.</p>
      </div>
      
      <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.3s;">
        <div class="feature-icon">🤝</div>
        <h3>Student–Lawyer Networking Profiles</h3>
        <p>Dedicated profiles for law students and legal professionals to connect, collaborate, and build mentorship or apprenticeship opportunities.</p>
      </div>
      
      <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.4s;">
        <div class="feature-icon">📍</div>
        <h3>Location-Based Suggestions</h3>
        <p>AI recommends relevant government authorities or lawyers near your location for immediate action.</p>
      </div>
      
      <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.5s;">
        <div class="feature-icon">🔍</div>
        <h3>Precedent Navigator</h3>
        <p>Search and explore past legal cases, sorted by topic, jurisdiction, and relevance.</p>
      </div>
      
      <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.6s;">
        <div class="feature-icon">⚖️</div>
        <h3>Compare Laws Tool</h3>
        <p>Side-by-side comparison of similar laws (e.g., BPC vs IPC, civil vs criminal) for better understanding.</p>
      </div>
      
      <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.7s;">
        <div class="feature-icon">🗺️</div>
        <h3>Concept Map Generator</h3>
        <p>Automatic visual maps showing connections between laws, related acts, exceptions, and key case laws.</p>
      </div>
      
      <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.8s;">
        <div class="feature-icon">📋</div>
        <h3>PDF Law Extractor</h3>
        <p>Upload Bangladeshi law PDFs to instantly extract and summarize relevant sections.</p>
      </div>
      
      <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 0.9s;">
        <div class="feature-icon">📝</div>
        <h3>AI Filing Templates</h3>
        <p>Ready-to-use formats for drafting legal notices, petitions, and contracts with legal checklists.</p>
      </div>
      
      <div class="feature-card animate__animated animate__fadeInUp" style="animation-delay: 1s;">
        <div class="feature-icon">🛡️</div>
        <h3>Consumer Guider</h3>
        <p>Guides consumers through legal battles step-by-step, from lower court to appeals in higher courts, with clear instructions for every stage.</p>
      </div>
    </div>
    
    <div class="beta-notice animate__animated animate__fadeIn" style="animation-delay: 1.2s;">
      <span class="beta-badge">BETA</span>
      <p>💡 <strong>Note:</strong> Justor AI is currently in its Beta version. The full-scale release with advanced features is coming soon.</p>
    </div>
  </section>

  <!-- FINAL CTA SECTION -->
  <section class="about-section final-cta-section">
    <h2 class="section-title">Ready to Explore?</h2>
    <p>Get instant answers to your legal questions and simplify complex laws.</p>
    <a href="/app" class="cta-button cta-primary" data-link>Try Justor AI Now</a>
  </section>

  <!-- CONTACT SECTION -->
  <section id="contact" class="about-section contact-section">
    <h2 class="section-title animate__animated animate__fadeIn">Get in Touch</h2>
    <p class="section-subtitle animate__animated animate__fadeIn">Have questions or feedback? We'd love to hear from you.</p>
    
    <div class="contact-grid">
      <div class="contact-card animate__animated animate__fadeInLeft">
        <div class="contact-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
            <polyline points="22,6 12,13 2,6"></polyline>
          </svg>
        </div>
        <h3>Email</h3>
        <a href="mailto:tajuddinahamed.contact@gmail.com" class="contact-link">tajuddinahamed.contact@gmail.com</a>
        <p class="contact-desc">Send us an email anytime</p>
      </div>
      
      <div class="contact-card animate__animated animate__fadeInRight">
        <div class="contact-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
          </svg>
        </div>
        <h3>WhatsApp</h3>
        <a href="https://wa.me/8801643462539" target="_blank" rel="noopener noreferrer" class="contact-link">+880 1643-462539</a>
        <p class="contact-desc">Chat with us on WhatsApp</p>
      </div>
    </div>
  </section>

</div>
`;

export function renderAboutPage(container: HTMLElement) {
    const animateCSSLinkId = 'animate-css-cdn';
    if (!document.getElementById(animateCSSLinkId)) {
        const link = document.createElement('link');
        link.id = animateCSSLinkId;
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css';
        document.head.appendChild(link);
    }

    container.innerHTML = aboutHTML;

    // Scroll to contact section if hash is present
    setTimeout(() => {
        if (window.location.hash === '#contact') {
            const contactSection = document.getElementById('contact');
            contactSection?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 100);

    // Add event listeners for the FAQ accordion
    const faqItems = container.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        question?.addEventListener('click', () => {
            const isVisible = answer?.classList.contains('visible');
            // Close all other answers
            faqItems.forEach(otherItem => {
                otherItem.querySelector('.faq-answer')?.classList.remove('visible');
                otherItem.querySelector('.faq-question')?.classList.remove('active');
            });
            // Toggle the clicked one
            if (!isVisible) {
                answer?.classList.add('visible');
                question?.classList.add('active');
            }
        });
    });
}
