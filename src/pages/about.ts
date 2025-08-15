
const aboutHTML = `
<div class="about-container">
  <!-- Hero Section -->
  <section class="about-hero enhanced-hero">
    <div class="hero-background">
      <div class="hero-particles"></div>
    </div>
    <div class="about-hero-content">
      <div class="hero-badge fade-in-up">
        <span class="badge-icon">⚖️</span>
        <span class="badge-text">Legal Tech Innovation</span>
      </div>
      <h1 class="about-title fade-in-up">About Justor AI</h1>
      <p class="about-subtitle fade-in-up">Democratizing access to Bangladeshi law through the power of artificial intelligence.</p>
    </div>
  </section>


  <!-- Our Foundation Section -->
  <section class="about-section foundation-section">
    <div class="section-header">
      <div class="section-badge">
        <span>🎯 Our Foundation</span>
      </div>
      <h2 class="section-title">Mission & Vision</h2>
      <p class="section-subtitle">The driving force behind everything we do</p>
    <div class="about-grid two-cols enhanced-grid">
      <div class="about-card enhanced-mission-card">
        <div class="card-icon">🎯</div>
        <h3>Our Mission</h3>
        <p>To provide justice faster by empowering every citizen, student, and legal professional in Bangladesh with instant, clear, and reliable legal information.</p>
        <p>We bridge the gap between complex legal texts and the people they serve — making law more <strong>accessible, affordable, understandable, and faster to act upon</strong> through AI-driven solutions.</p>
        <div class="mission-points">
          <div class="point-item">✓ Instant legal guidance</div>
          <div class="point-item">✓ Plain language explanations</div>
          <div class="point-item">✓ Free access for everyone</div>
        </div>
      </div>
      <div class="about-card enhanced-vision-card">
        <div class="card-icon">🔮</div>
        <h3>Our Vision</h3>
        <p>We envision a future where understanding your rights and legal obligations is no longer a barrier, but just a simple conversation away.</p>
        <p>A future where technology fosters a more just, connected, and informed society — linking citizens, students, and lawyers into one seamless ecosystem for <strong>faster, smoother, and fairer justice</strong>.</p>
        <div class="vision-points">
          <div class="point-item">✓ Universal legal literacy</div>
          <div class="point-item">✓ Accessible justice system</div>
          <div class="point-item">✓ Empowered citizens</div>
        </div>
      </div>
    </div>
  </section>

  <!-- How It Works Section -->
  <section class="about-section how-it-works-enhanced">
    <div class="section-header">
      <div class="section-badge">
        <span>⚡ Process</span>
      </div>
      <h2 class="section-title">How Justor AI Works</h2>
      <p class="section-subtitle">Powered by advanced AI technology and comprehensive legal knowledge</p>
    </div>
    <div class="process-flow">
      <div class="process-step enhanced-step">
        <div class="step-number">1</div>
        <div class="step-content">
          <div class="step-icon">💬</div>
          <h4>Ask or Upload</h4>
          <p>Ask your legal question in Bangla or English, or upload a legal document for instant AI analysis.</p>
          <div class="step-features">
            <span class="feature">Natural Language Processing</span>
            <span class="feature">Bilingual Support</span>
          </div>
        </div>
      </div>
      
      <div class="process-arrow">
        <svg viewBox="0 0 100 20" class="arrow-svg">
          <path d="M0 10 L80 10 M70 5 L80 10 L70 15" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
      </div>
      
      <div class="process-step enhanced-step">
        <div class="step-number">2</div>
        <div class="step-content">
          <div class="step-icon">🤖</div>
          <h4>AI-Powered Retrieval</h4>
          <p>Our AI searches a curated knowledge base of Bangladeshi laws, case precedents, and legal texts to find the most relevant, accurate, and up-to-date information for your query.</p>
          <div class="step-features">
            <span class="feature">10K+ Legal Documents</span>
            <span class="feature">Real-time Search</span>
          </div>
        </div>
      </div>
      
      <div class="process-arrow">
        <svg viewBox="0 0 100 20" class="arrow-svg">
          <path d="M0 10 L80 10 M70 5 L80 10 L70 15" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
      </div>
      
      <div class="process-step enhanced-step">
        <div class="step-number">3</div>
        <div class="step-content">
          <div class="step-icon">📋</div>
          <h4>Get a Clear Answer</h4>
          <p>Receive a structured, easy-to-understand answer with relevant citations, real-life examples, and actionable steps — all tailored to your role (citizen, student, or legal professional).</p>
          <div class="step-features">
            <span class="feature">Legal Citations</span>
            <span class="feature">Action Steps</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Upcoming Features Section -->
  <section class="about-section upcoming-features-section">
    <div class="section-header">
      <div class="section-badge">
        <span>🔮 Coming Soon</span>
      </div>
      <h2 class="section-title">Upcoming Features – Justor AI</h2>
      <p class="section-subtitle">Exciting new capabilities we're building to enhance your legal experience</p>
    </div>
    <div class="features-showcase">
      <div class="feature-item">
        <div class="feature-icon-wrapper">
          <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3s-4.5 4.03-4.5 9 2.015 9 4.5 9z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3l1.5 1.5" />
          </svg>
        </div>
        <h4>Multilingual Document Analysis</h4>
        <p>Upload any legal document in Bangla, English, or other languages for instant AI review, risk highlights, and plain-language explanation.</p>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon-wrapper">
          <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h4>Client Document Verification</h4>
        <p>Lawyers can cross-check NID, passport, receipts, and case documents for accuracy in seconds.</p>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon-wrapper">
          <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-4.67c.625-.93.928-2.036.928-3.185V11a3 3 0 00-3-3H9.375a3 3 0 00-3 3v1.375c0 1.15.303 2.255.927 3.185z" />
          </svg>
        </div>
        <h4>Student–Lawyer Networking Profiles</h4>
        <p>Dedicated profiles for law students and legal professionals to connect, collaborate, and build mentorship or apprenticeship opportunities.</p>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon-wrapper">
          <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 11-6 0 3 3 0 016 0z" />
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1115 0z" />
          </svg>
        </div>
        <h4>Location-Based Authority & Lawyer Suggestions</h4>
        <p>AI recommends relevant government authorities or lawyers near the user's location for immediate action.</p>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon-wrapper">
          <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
        </div>
        <h4>Precedent Navigator</h4>
        <p>Search and explore past legal cases, sorted by topic, jurisdiction, and relevance.</p>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon-wrapper">
          <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.254 48.254 0 0012 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 01-2.031.352 5.988 5.988 0 01-2.031-.352c-.483-.174-.711-.703-.589-1.202L18.75 4.97zm-16.5.52c.99-.203 1.99-.377 3-.52m0 0l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 01-2.031.352 5.988 5.988 0 01-2.031-.352c-.483-.174-.711-.703-.589-1.202L5.25 4.97z" />
          </svg>
        </div>
        <h4>Compare Laws Tool</h4>
        <p>Side-by-side comparison of similar laws (e.g., BPC vs IPC, civil vs criminal) for better understanding.</p>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon-wrapper">
          <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 6.75V15m6-6v8.25m.503 3.498l4.875-2.437c.381-.19.622-.58.622-1.006V4.82c0-.836-.88-1.38-1.628-1.006l-3.869 1.934c-.317.159-.69.159-1.006 0L9.503 3.252a1.125 1.125 0 00-1.006 0L3.622 5.689C3.24 5.88 3 6.27 3 6.695V19.18c0 .836.88 1.38 1.628 1.006l3.869-1.934c.317-.159.69-.159 1.006 0l4.994 2.497c.317.158.69.158 1.006 0z" />
          </svg>
        </div>
        <h4>Concept Map Generator</h4>
        <p>Automatic visual maps showing connections between laws, related acts, exceptions, and key case laws.</p>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon-wrapper">
          <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
        </div>
        <h4>PDF Law Extractor</h4>
        <p>Upload Bangladeshi law PDFs to instantly extract and summarize relevant sections.</p>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon-wrapper">
          <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10" />
          </svg>
        </div>
        <h4>AI Filing Templates & Legal Checklists</h4>
        <p>Ready-to-use formats for drafting legal notices, petitions, and contracts.</p>
      </div>
      
      <div class="feature-item">
        <div class="feature-icon-wrapper">
          <svg class="feature-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197M15 6.75a3 3 0 11-6 0 3 3 0 016 0zm6 3a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0zm-13.5 0a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z" />
          </svg>
        </div>
        <h4>Consumer Guider</h4>
        <p>Guides consumers through legal battles step-by-step, from lower court to appeals in higher courts, with clear instructions for every stage.</p>
      </div>
    </div>
    
    <div class="beta-notice">
      <div class="beta-icon">💡</div>
      <div class="beta-content">
        <h4>Note: Justor AI is currently in its Beta version.</h4>
        <p>The full-scale release with advanced features is coming soon.</p>
      </div>
    </div>
  </section>

  <!-- Technology Section -->
  <section class="about-section technology-section">
    <div class="section-header">
      <div class="section-badge">
        <span>🔬 Technology</span>
      </div>
      <h2 class="section-title">Powered by Advanced AI</h2>
      <p class="section-subtitle">The technology stack that makes Justor AI possible</p>
    </div>
    <div class="tech-grid">
      <div class="tech-card">
        <div class="tech-icon">🧠</div>
        <h4>Large Language Models</h4>
        <p>Advanced AI models trained specifically for legal understanding and natural language processing in Bengali and English.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">📚</div>
        <h4>Legal Knowledge Base</h4>
        <p>Comprehensive database of Bangladeshi laws, regulations, case precedents, and legal procedures, continuously updated.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">🔍</div>
        <h4>Semantic Search</h4>
        <p>Intelligent search algorithms that understand context and intent, not just keywords, for more accurate results.</p>
      </div>
      <div class="tech-card">
        <div class="tech-icon">⚡</div>
        <h4>Real-time Processing</h4>
        <p>Fast, cloud-based infrastructure ensuring instant responses and seamless user experience across all devices.</p>
      </div>
    </div>
  </section>

  <!-- Team Section -->
  <section class="about-section team-section enhanced-team">
    <div class="section-header">
      <div class="section-badge">
        <span>👥 Team</span>
      </div>
      <h2 class="section-title">Meet Our Team</h2>
      <p class="section-subtitle">The passionate individuals behind Justor AI</p>
    </div>
    <div class="team-grid">
      <div class="team-card enhanced-team-card">
        <div class="team-photo-wrapper">
          <img src="https://avatars.githubusercontent.com/u/86288624?v=4" alt="Tajuddin Ahamed" class="team-photo">
          <div class="photo-overlay">
            <div class="social-links">
              <a href="#" class="social-link">💼</a>
              <a href="#" class="social-link">📧</a>
            </div>
          </div>
        </div>
        <div class="team-info">
          <h3>Tajuddin Ahamed</h3>
          <p class="team-role">Co-Founder, CEO & CMO – Product Analyst, LegalTech Innovator, Marketing & Fundraising Lead</p>
          <p class="team-description">Leads product vision, partnerships, marketing, branding, fundraising, and strategic growth for Justor AI. Focused on bridging the legal knowledge gap for millions in Bangladesh through innovative legal technology and public engagement.</p>
          <div class="expertise-tags">
            <span class="tag">Product Vision</span>
            <span class="tag">LegalTech Innovation</span>
            <span class="tag">Strategic Growth</span>
          </div>
        </div>
      </div>
      
      <div class="team-card enhanced-team-card">
        <div class="team-photo-wrapper">
          <img src="https://media.licdn.com/dms/image/D5603AQG859G9o21jHw/profile-displayphoto-shrink_400_400/0/1718563998655?e=1727308800&v=beta&t=3E1zHnYM01u6eBSo_t2j5qV2j5iYFkZ3e2c5Y5E3E2c" alt="Mehide Hasan" class="team-photo">
          <div class="photo-overlay">
            <div class="social-links">
              <a href="#" class="social-link">💼</a>
              <a href="#" class="social-link">📧</a>
            </div>
          </div>
        </div>
        <div class="team-info">
          <h3>Mehide Hasan</h3>
          <p class="team-role">Co-Founder, COO & CTO – Full-Stack Developer, Product Architect & Operations Lead</p>
          <p class="team-description">Built and manages the platform's UI/UX, backend systems, and AI integrations. Leads the product infrastructure; oversees daily operations, team coordination, and ensures smooth technical performance with a scalable architecture to support rapid growth.</p>
          <div class="expertise-tags">
            <span class="tag">Full-Stack Development</span>
            <span class="tag">Product Architecture</span>
            <span class="tag">Operations Lead</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Values Section -->
  <section class="about-section values-section">
    <div class="section-header">
      <div class="section-badge">
        <span>💎 Values</span>
      </div>
      <h2 class="section-title">Our Core Values</h2>
      <p class="section-subtitle">The principles that guide everything we do</p>
    </div>
    <div class="values-grid">
      <div class="value-card">
        <div class="value-icon">🎯</div>
        <h4>Accuracy</h4>
        <p>We ensure every piece of legal information is accurate, verified, and up-to-date with current Bangladeshi law.</p>
      </div>
      <div class="value-card">
        <div class="value-icon">🌍</div>
        <h4>Accessibility</h4>
        <p>Legal knowledge should be available to everyone, regardless of their background, education, or economic status.</p>
      </div>
      <div class="value-card">
        <div class="value-icon">🛡️</div>
        <h4>Privacy</h4>
        <p>Your legal questions and personal information are always kept private and secure. We never share your data.</p>
      </div>
      <div class="value-card">
        <div class="value-icon">⚡</div>
        <h4>Innovation</h4>
        <p>We continuously improve our technology to provide faster, more accurate, and more helpful legal assistance.</p>
      </div>
      <div class="value-card">
        <div class="value-icon">🤝</div>
        <h4>Transparency</h4>
        <p>We're open about our methods, limitations, and always remind users when to consult qualified lawyers.</p>
      </div>
      <div class="value-card">
        <div class="value-icon">📈</div>
        <h4>Continuous Learning</h4>
        <p>We constantly update our knowledge base and improve our AI based on user feedback and legal developments.</p>
      </div>
    </div>
  </section>

  <!-- FAQ Section -->
  <section class="about-section faq-section enhanced-faq">
    <div class="section-header">
      <div class="section-badge">
        <span>❓ FAQ</span>
      </div>
      <h2 class="section-title">Frequently Asked Questions</h2>
      <p class="section-subtitle">Common questions about Justor AI</p>
    </div>
    <div class="faq-container">
      <div class="faq-item">
        <button class="faq-question">
          <span>Is Justor AI free to use?</span>
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-answer">
          <p>Yes, Justor AI offers a generous free tier for both guest users and registered users. Our goal is to make legal knowledge accessible to everyone. For heavy usage or premium features, we may introduce paid plans in the future to cover operational costs, but basic access will always remain free.</p>
        </div>
      </div>
      
      <div class="faq-item">
        <button class="faq-question">
          <span>Is this a substitute for a real lawyer?</span>
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-answer">
          <p><strong>No.</strong> Justor AI provides information and guidance for educational purposes only. It is not legal advice and should not replace consultation with a qualified legal professional. For serious legal matters, court proceedings, or complex situations, always consult a licensed lawyer.</p>
        </div>
      </div>
      
      <div class="faq-item">
        <button class="faq-question">
          <span>How up-to-date is the legal information?</span>
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-answer">
          <p>We continuously update our knowledge base with the latest laws, amendments, and legal developments from official government sources. Our team monitors legal changes and updates the system regularly. However, there may be a brief delay between new legislation and its inclusion in our database.</p>
        </div>
      </div>
      
      <div class="faq-item">
        <button class="faq-question">
          <span>What types of legal questions can I ask?</span>
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-answer">
          <p>You can ask about various areas of Bangladeshi law including family law, employment law, property law, business law, consumer rights, and more. Our AI can help with understanding legal procedures, rights and obligations, and general legal guidance. We're continuously expanding our coverage areas.</p>
        </div>
      </div>
      
      <div class="faq-item">
        <button class="faq-question">
          <span>Is my data safe and private?</span>
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-answer">
          <p>Yes, we take privacy very seriously. Your conversations and personal information are encrypted and never shared with third parties. We only use anonymized data to improve our AI responses. You can use the platform as a guest without creating an account if you prefer maximum privacy.</p>
        </div>
      </div>
      
      <div class="faq-item">
        <button class="faq-question">
          <span>Can I use JustorAI in Bengali?</span>
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-answer">
          <p>Absolutely! Justor AI supports both English and Bengali. You can ask questions in either language and receive responses in your preferred language. Our AI is specifically trained to understand legal concepts in both languages and provide culturally appropriate guidance.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA Section -->
  <section class="about-section final-cta-section enhanced-cta">
    <div class="cta-content">
      <h2 class="cta-title">Ready to Get Legal Guidance?</h2>
      <p class="cta-subtitle">Join thousands of Bangladeshis who trust Justor AI for their legal questions</p>
      <div class="cta-buttons">
        <a href="/app" class="cta-button cta-primary" data-link>Try Justor AI Now</a>
        <a href="/login" class="cta-button cta-secondary" data-link>Create Free Account</a>
      </div>
      <div class="cta-features">
        <span class="cta-feature">✓ Free to use</span>
        <span class="cta-feature">✓ Instant answers</span>
        <span class="cta-feature">✓ Available 24/7</span>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer enhanced-footer">
    <div class="footer-content">
      <div class="footer-brand">
        <h3>Justor AI</h3>
        <p>Democratizing access to Bangladeshi law through the power of artificial intelligence</p>
        <div class="footer-social">
          <a href="#" class="social-link">📧</a>
          <a href="#" class="social-link">📱</a>
          <a href="#" class="social-link">🌐</a>
        </div>
      </div>
      <div class="footer-links-grid">
        <div class="footer-column">
          <h4>Product</h4>
          <a href="/app" data-link>AI Chat</a>
          <a href="/doc-analysis" data-link>Document Analysis</a>
          <a href="/about" data-link>About Us</a>
        </div>
        <div class="footer-column">
          <h4>Legal</h4>
          <a href="/about" data-link>About</a>
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
        </div>
        <div class="footer-column">
          <h4>Support</h4>
          <a href="#">Help Center</a>
          <a href="#">Contact Us</a>
          <a href="#">FAQ</a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <p>© 2025 Justor AI – All Rights Reserved.</p>
      <p class="footer-disclaimer">This is not legal advice. Consult a qualified lawyer for legal matters.</p>
    </div>
  </footer>
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
