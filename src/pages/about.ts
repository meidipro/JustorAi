
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
      <h1 class="about-title fade-in-up">About JustorAI</h1>
      <p class="about-subtitle fade-in-up">Democratizing access to Bangladeshi law through the power of artificial intelligence and making legal knowledge accessible to everyone.</p>
      <div class="hero-stats fade-in-up">
        <div class="stat-item">
          <div class="stat-number">10K+</div>
          <div class="stat-label">Legal Documents</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">5K+</div>
          <div class="stat-label">Users Served</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">99.9%</div>
          <div class="stat-label">Accuracy Rate</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Story Section -->
  <section class="story-section fade-in-section">
    <div class="section-header">
      <div class="section-badge">
        <span>📖 Our Story</span>
      </div>
      <h2 class="section-title">Why We Built JustorAI</h2>
      <p class="section-subtitle">The story behind Bangladesh's first AI-powered legal assistant</p>
    </div>
    <div class="story-content">
      <div class="story-text">
        <p class="story-paragraph">
          <strong>The Problem:</strong> In Bangladesh, millions of citizens struggle to understand their legal rights and obligations. 
          Complex legal language, expensive consultations, and limited access to legal resources create barriers to justice.
        </p>
        <p class="story-paragraph">
          <strong>Our Solution:</strong> We created JustorAI to bridge this gap using cutting-edge artificial intelligence. 
          Our platform transforms complex legal texts into simple, actionable guidance that anyone can understand.
        </p>
        <p class="story-paragraph">
          <strong>The Impact:</strong> Today, thousands of Bangladeshis use JustorAI to understand their rights, 
          navigate legal procedures, and make informed decisions about their legal matters.
        </p>
      </div>
      <div class="story-visual">
        <div class="impact-metrics">
          <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-number">5,000+</div>
            <div class="metric-label">Users Helped</div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">💬</div>
            <div class="metric-number">25,000+</div>
            <div class="metric-label">Questions Answered</div>
          </div>
          <div class="metric-card">
            <div class="metric-icon">⏱️</div>
            <div class="metric-number">10,000+</div>
            <div class="metric-label">Hours Saved</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Mission & Vision Section -->
  <section class="about-section mission-vision-section">
    <div class="about-grid two-cols enhanced-grid">
      <div class="about-card enhanced-mission-card">
        <div class="card-icon">🎯</div>
        <h3>Our Mission</h3>
        <p>To empower every citizen, student, and legal professional in Bangladesh with instant, clear, and reliable legal information. We bridge the gap between complex legal texts and the people they serve, making justice more accessible for all.</p>
        <div class="mission-points">
          <div class="point-item">✓ Instant legal guidance</div>
          <div class="point-item">✓ Plain language explanations</div>
          <div class="point-item">✓ Free access for everyone</div>
        </div>
      </div>
      <div class="about-card enhanced-vision-card">
        <div class="card-icon">🔮</div>
        <h3>Our Vision</h3>
        <p>We envision a future where understanding your rights and legal obligations is no longer a barrier, but a simple conversation away. A future where technology fosters a more just and informed society across Bangladesh.</p>
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
      <h2 class="section-title">How JustorAI Works</h2>
      <p class="section-subtitle">Powered by advanced AI technology and comprehensive legal knowledge</p>
    </div>
    <div class="process-flow">
      <div class="process-step enhanced-step">
        <div class="step-number">1</div>
        <div class="step-content">
          <div class="step-icon">💬</div>
          <h4>Ask Your Question</h4>
          <p>Type your legal question in plain English or Bengali. Our AI understands natural language and context, so you can ask as you would speak to a lawyer.</p>
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
          <h4>AI-Powered Analysis</h4>
          <p>Our advanced AI searches through thousands of Bangladeshi legal documents, case laws, and precedents to find the most relevant and accurate information.</p>
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
          <h4>Clear Answers</h4>
          <p>Receive detailed, easy-to-understand legal guidance with relevant citations, next steps, and actionable advice tailored to your situation.</p>
          <div class="step-features">
            <span class="feature">Legal Citations</span>
            <span class="feature">Action Steps</span>
          </div>
        </div>
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
      <p class="section-subtitle">The technology stack that makes JustorAI possible</p>
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
      <h2 class="section-title">Meet the Team</h2>
      <p class="section-subtitle">The passionate individuals behind LegalAI.bd</p>
    </div>
    <div class="team-grid">
      <div class="team-card enhanced-team-card">
        <div class="team-photo-wrapper">
          <img src="https://avatars.githubusercontent.com/u/86288624?v=4" alt="Mehide Hasan" class="team-photo">
          <div class="photo-overlay">
            <div class="social-links">
              <a href="#" class="social-link">💼</a>
              <a href="#" class="social-link">📧</a>
            </div>
          </div>
        </div>
        <div class="team-info">
          <h3>Mehide Hasan</h3>
          <p class="team-role">Co-Founder & Lead Developer</p>
          <p class="team-description">Full-stack developer and project manager who designed, built, and deployed the entire JustorAI platform. Passionate about using technology to solve real-world problems and make legal knowledge accessible.</p>
          <div class="expertise-tags">
            <span class="tag">Full-Stack Development</span>
            <span class="tag">AI Integration</span>
            <span class="tag">Product Management</span>
          </div>
        </div>
      </div>
      
      <div class="team-card enhanced-team-card">
        <div class="team-photo-wrapper">
          <img src="https://media.licdn.com/dms/image/D5603AQG859G9o21jHw/profile-displayphoto-shrink_400_400/0/1718563998655?e=1727308800&v=beta&t=3E1zHnYM01u6eBSo_t2j5qV2j5iYFkZ3e2c5Y5E3E2c" alt="Tajuddin Ahmed" class="team-photo">
          <div class="photo-overlay">
            <div class="social-links">
              <a href="#" class="social-link">💼</a>
              <a href="#" class="social-link">📧</a>
            </div>
          </div>
        </div>
        <div class="team-info">
          <h3>Tajuddin Ahmed</h3>
          <p class="team-role">Co-Founder & Legal Knowledge Curator</p>
          <p class="team-description">Legal expert and AI trainer who curated our comprehensive database of Bangladeshi laws and ensured the accuracy and quality of AI responses. Dedicated to making legal knowledge accessible to all citizens.</p>
          <div class="expertise-tags">
            <span class="tag">Legal Research</span>
            <span class="tag">AI Training</span>
            <span class="tag">Quality Assurance</span>
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
      <p class="section-subtitle">Common questions about JustorAI</p>
    </div>
    <div class="faq-container">
      <div class="faq-item">
        <button class="faq-question">
          <span>Is JustorAI free to use?</span>
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-answer">
          <p>Yes, JustorAI offers a generous free tier for both guest users and registered users. Our goal is to make legal knowledge accessible to everyone. For heavy usage or premium features, we may introduce paid plans in the future to cover operational costs, but basic access will always remain free.</p>
        </div>
      </div>
      
      <div class="faq-item">
        <button class="faq-question">
          <span>Is this a substitute for a real lawyer?</span>
          <span class="faq-icon">+</span>
        </button>
        <div class="faq-answer">
          <p><strong>No.</strong> JustorAI provides information and guidance for educational purposes only. It is not legal advice and should not replace consultation with a qualified legal professional. For serious legal matters, court proceedings, or complex situations, always consult a licensed lawyer.</p>
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
          <p>Absolutely! JustorAI supports both English and Bengali. You can ask questions in either language and receive responses in your preferred language. Our AI is specifically trained to understand legal concepts in both languages and provide culturally appropriate guidance.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- CTA Section -->
  <section class="about-section final-cta-section enhanced-cta">
    <div class="cta-content">
      <h2 class="cta-title">Ready to Get Legal Guidance?</h2>
      <p class="cta-subtitle">Join thousands of Bangladeshis who trust JustorAI for their legal questions</p>
      <div class="cta-buttons">
        <a href="/app" class="cta-button cta-primary" data-link>Try JustorAI Now</a>
        <a href="/login" class="cta-button cta-secondary" data-link>Create Free Account</a>
      </div>
      <div class="cta-features">
        <span class="cta-feature">✓ Free to use</span>
        <span class="cta-feature">✓ Instant answers</span>
        <span class="cta-feature">✓ Available 24/7</span>
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
