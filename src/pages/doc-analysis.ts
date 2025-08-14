// src/pages/doc-analysis.ts

const docAnalysisHTML = `
<div class="doc-analysis-container">
  <!-- Hero Section -->
  <section class="doc-hero enhanced-hero">
    <div class="hero-background">
      <div class="hero-particles"></div>
    </div>
    <div class="doc-hero-content">
      <div class="hero-badge fade-in-up">
        <span class="badge-icon">📄</span>
        <span class="badge-text">AI-Powered Document Analysis</span>
      </div>
      <h1 class="doc-title fade-in-up">Legal Document Analysis</h1>
      <p class="doc-subtitle fade-in-up">Upload, analyze, and understand complex legal documents with the power of artificial intelligence. Get instant insights, summaries, and key information extraction.</p>
      <div class="hero-stats fade-in-up">
        <div class="stat-item">
          <div class="stat-number">95%</div>
          <div class="stat-label">Accuracy Rate</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">50+</div>
          <div class="stat-label">Document Types</div>
        </div>
        <div class="stat-item">
          <div class="stat-number">&lt;30s</div>
          <div class="stat-label">Analysis Time</div>
        </div>
      </div>
    </div>
  </section>

  <!-- Upload Demo Section -->
  <section class="upload-demo-section fade-in-section">
    <div class="section-header">
      <div class="section-badge">
        <span>⬆️ Upload</span>
      </div>
      <h2 class="section-title">Try Document Analysis</h2>
      <p class="section-subtitle">Upload a legal document to see how our AI analyzes it</p>
    </div>
    <div class="upload-demo-container">
      <div class="upload-area">
        <div class="upload-icon">📁</div>
        <h3>Drag & Drop Your Document</h3>
        <p>Or click to browse files</p>
        <div class="supported-formats">
          <span class="format-tag">PDF</span>
          <span class="format-tag">DOC</span>
          <span class="format-tag">DOCX</span>
          <span class="format-tag">TXT</span>
        </div>
        <button class="browse-button">Browse Files</button>
      </div>
      <div class="demo-note">
        <div class="note-icon">ℹ️</div>
        <div class="note-content">
          <h4>Coming Soon!</h4>
          <p>Document upload and analysis features are currently in development. This preview shows what will be available soon.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Features Section -->
  <section class="doc-features-section fade-in-section">
    <div class="section-header">
      <div class="section-badge">
        <span>⚡ Capabilities</span>
      </div>
      <h2 class="section-title">What Our AI Can Do</h2>
      <p class="section-subtitle">Comprehensive document analysis powered by advanced AI</p>
    </div>
    <div class="features-grid">
      <div class="feature-card enhanced-card">
        <div class="feature-icon-wrapper">
          <div class="feature-icon">📊</div>
        </div>
        <h3>Smart Summarization</h3>
        <p>Get concise, accurate summaries of lengthy legal documents highlighting key points, clauses, and important provisions.</p>
        <div class="feature-benefits">
          <span class="benefit-item">✓ Key clause extraction</span>
          <span class="benefit-item">✓ Main points summary</span>
          <span class="benefit-item">✓ Risk assessment</span>
        </div>
      </div>
      
      <div class="feature-card enhanced-card">
        <div class="feature-icon-wrapper">
          <div class="feature-icon">🔍</div>
        </div>
        <h3>Information Extraction</h3>
        <p>Automatically extract dates, parties, amounts, deadlines, and other critical information from contracts and agreements.</p>
        <div class="feature-benefits">
          <span class="benefit-item">✓ Date & deadline tracking</span>
          <span class="benefit-item">✓ Party identification</span>
          <span class="benefit-item">✓ Financial terms</span>
        </div>
      </div>
      
      <div class="feature-card enhanced-card">
        <div class="feature-icon-wrapper">
          <div class="feature-icon">⚠️</div>
        </div>
        <h3>Risk Analysis</h3>
        <p>Identify potential risks, unusual clauses, and areas that may require legal attention or negotiation.</p>
        <div class="feature-benefits">
          <span class="benefit-item">✓ Risk flagging</span>
          <span class="benefit-item">✓ Unusual clause detection</span>
          <span class="benefit-item">✓ Compliance checking</span>
        </div>
      </div>
      
      <div class="feature-card enhanced-card">
        <div class="feature-icon-wrapper">
          <div class="feature-icon">🏷️</div>
        </div>
        <h3>Document Classification</h3>
        <p>Automatically categorize and classify documents by type, complexity, and legal domain for better organization.</p>
        <div class="feature-benefits">
          <span class="benefit-item">✓ Document type detection</span>
          <span class="benefit-item">✓ Complexity scoring</span>
          <span class="benefit-item">✓ Topic categorization</span>
        </div>
      </div>
      
      <div class="feature-card enhanced-card">
        <div class="feature-icon-wrapper">
          <div class="feature-icon">🔗</div>
        </div>
        <h3>Cross-Reference Analysis</h3>
        <p>Find connections between different sections, identify contradictions, and ensure internal consistency.</p>
        <div class="feature-benefits">
          <span class="benefit-item">✓ Section linking</span>
          <span class="benefit-item">✓ Contradiction detection</span>
          <span class="benefit-item">✓ Consistency checking</span>
        </div>
      </div>
      
      <div class="feature-card enhanced-card">
        <div class="feature-icon-wrapper">
          <div class="feature-icon">💬</div>
        </div>
        <h3>Q&A with Documents</h3>
        <p>Ask specific questions about uploaded documents and get precise answers with direct references to relevant sections.</p>
        <div class="feature-benefits">
          <span class="benefit-item">✓ Context-aware answers</span>
          <span class="benefit-item">✓ Source citations</span>
          <span class="benefit-item">✓ Multi-document queries</span>
        </div>
      </div>
    </div>
  </section>

  <!-- Document Types Section -->
  <section class="doc-types-section fade-in-section">
    <div class="section-header">
      <div class="section-badge">
        <span>📋 Document Types</span>
      </div>
      <h2 class="section-title">Supported Document Types</h2>
      <p class="section-subtitle">Our AI can analyze various types of legal documents</p>
    </div>
    <div class="doc-types-grid">
      <div class="doc-type-category">
        <div class="category-header">
          <div class="category-icon">📜</div>
          <h3>Contracts & Agreements</h3>
        </div>
        <div class="doc-types-list">
          <span class="doc-type">Employment Contracts</span>
          <span class="doc-type">Service Agreements</span>
          <span class="doc-type">Rental Agreements</span>
          <span class="doc-type">Purchase Agreements</span>
          <span class="doc-type">Partnership Deeds</span>
        </div>
      </div>
      
      <div class="doc-type-category">
        <div class="category-header">
          <div class="category-icon">🏢</div>
          <h3>Business Documents</h3>
        </div>
        <div class="doc-types-list">
          <span class="doc-type">Company Formation</span>
          <span class="doc-type">Board Resolutions</span>
          <span class="doc-type">Shareholder Agreements</span>
          <span class="doc-type">Licensing Agreements</span>
          <span class="doc-type">Non-Disclosure Agreements</span>
        </div>
      </div>
      
      <div class="doc-type-category">
        <div class="category-header">
          <div class="category-icon">⚖️</div>
          <h3>Legal Documents</h3>
        </div>
        <div class="doc-types-list">
          <span class="doc-type">Court Pleadings</span>
          <span class="doc-type">Legal Notices</span>
          <span class="doc-type">Power of Attorney</span>
          <span class="doc-type">Wills & Testaments</span>
          <span class="doc-type">Affidavits</span>
        </div>
      </div>
      
      <div class="doc-type-category">
        <div class="category-header">
          <div class="category-icon">🏠</div>
          <h3>Property Documents</h3>
        </div>
        <div class="doc-types-list">
          <span class="doc-type">Property Deeds</span>
          <span class="doc-type">Mortgage Documents</span>
          <span class="doc-type">Lease Agreements</span>
          <span class="doc-type">Property Registration</span>
          <span class="doc-type">Transfer Documents</span>
        </div>
      </div>
    </div>
  </section>

  <!-- How It Works Section -->
  <section class="doc-process-section fade-in-section">
    <div class="section-header">
      <div class="section-badge">
        <span>⚙️ Process</span>
      </div>
      <h2 class="section-title">How Document Analysis Works</h2>
      <p class="section-subtitle">Our AI-powered document analysis in four simple steps</p>
    </div>
    <div class="process-flow">
      <div class="process-step enhanced-step">
        <div class="step-number">1</div>
        <div class="step-content">
          <div class="step-icon">📤</div>
          <h4>Upload Document</h4>
          <p>Simply drag and drop your legal document or browse to select files. We support PDF, DOC, DOCX, and TXT formats with secure encryption.</p>
          <div class="step-features">
            <span class="feature">Secure Upload</span>
            <span class="feature">Multiple Formats</span>
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
          <h4>AI Processing</h4>
          <p>Our advanced AI models analyze the document structure, extract key information, and understand legal context using natural language processing.</p>
          <div class="step-features">
            <span class="feature">NLP Analysis</span>
            <span class="feature">Context Understanding</span>
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
          <div class="step-icon">📊</div>
          <h4>Generate Insights</h4>
          <p>Get comprehensive analysis including summaries, key terms, risk assessments, and important deadlines with detailed explanations.</p>
          <div class="step-features">
            <span class="feature">Smart Summaries</span>
            <span class="feature">Risk Analysis</span>
          </div>
        </div>
      </div>
      
      <div class="process-arrow">
        <svg viewBox="0 0 100 20" class="arrow-svg">
          <path d="M0 10 L80 10 M70 5 L80 10 L70 15" stroke="currentColor" stroke-width="2" fill="none"/>
        </svg>
      </div>
      
      <div class="process-step enhanced-step">
        <div class="step-number">4</div>
        <div class="step-content">
          <div class="step-icon">💡</div>
          <h4>Interactive Q&A</h4>
          <p>Ask specific questions about the document and get instant answers with citations. Download reports and save analysis for future reference.</p>
          <div class="step-features">
            <span class="feature">Document Q&A</span>
            <span class="feature">Export Reports</span>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Benefits Section -->
  <section class="benefits-section fade-in-section">
    <div class="section-header">
      <div class="section-badge">
        <span>🎯 Benefits</span>
      </div>
      <h2 class="section-title">Why Choose Our Document Analysis?</h2>
      <p class="section-subtitle">Save time, reduce errors, and gain deeper insights into your legal documents</p>
    </div>
    <div class="benefits-grid">
      <div class="benefit-card">
        <div class="benefit-icon">⏱️</div>
        <h3>Save Hours of Review Time</h3>
        <p>What takes hours of manual review can be done in minutes with our AI analysis, without missing critical details.</p>
      </div>
      
      <div class="benefit-card">
        <div class="benefit-icon">🎯</div>
        <h3>Improve Accuracy</h3>
        <p>Reduce human error and ensure nothing important is overlooked with comprehensive AI-powered analysis.</p>
      </div>
      
      <div class="benefit-card">
        <div class="benefit-icon">💰</div>
        <h3>Cost-Effective Analysis</h3>
        <p>Get professional-level document analysis at a fraction of the cost of traditional legal review services.</p>
      </div>
      
      <div class="benefit-card">
        <div class="benefit-icon">🔒</div>
        <h3>Secure & Confidential</h3>
        <p>Your documents are processed securely with end-to-end encryption and are never stored permanently.</p>
      </div>
      
      <div class="benefit-card">
        <div class="benefit-icon">📈</div>
        <h3>Actionable Insights</h3>
        <p>Get clear, actionable recommendations and insights that help you make informed decisions quickly.</p>
      </div>
      
      <div class="benefit-card">
        <div class="benefit-icon">🌍</div>
        <h3>24/7 Availability</h3>
        <p>Analyze documents anytime, anywhere with our cloud-based AI that's always available when you need it.</p>
      </div>
    </div>
  </section>

  <!-- Security Section -->
  <section class="security-section fade-in-section">
    <div class="section-header">
      <div class="section-badge">
        <span>🔐 Security</span>
      </div>
      <h2 class="section-title">Your Documents Are Safe</h2>
      <p class="section-subtitle">Enterprise-grade security for your sensitive legal documents</p>
    </div>
    <div class="security-features">
      <div class="security-feature">
        <div class="security-icon">🔒</div>
        <h3>End-to-End Encryption</h3>
        <p>All documents are encrypted during upload, processing, and storage using industry-standard AES-256 encryption.</p>
      </div>
      
      <div class="security-feature">
        <div class="security-icon">🗑️</div>
        <h3>Automatic Deletion</h3>
        <p>Documents are automatically deleted after analysis is complete. No permanent storage of your sensitive data.</p>
      </div>
      
      <div class="security-feature">
        <div class="security-icon">🛡️</div>
        <h3>Privacy First</h3>
        <p>We never access, read, or use your documents for training. Your data remains completely private and confidential.</p>
      </div>
      
      <div class="security-feature">
        <div class="security-icon">✅</div>
        <h3>Compliance Ready</h3>
        <p>Our platform follows international data protection standards and compliance requirements for legal document handling.</p>
      </div>
    </div>
  </section>

  <!-- CTA Section -->
  <section class="doc-cta-section enhanced-cta fade-in-section">
    <div class="cta-content">
      <h2 class="cta-title">Ready to Analyze Your Documents?</h2>
      <p class="cta-subtitle">Join the future of legal document analysis with AI-powered insights</p>
      <div class="cta-buttons">
        <a href="/app" class="cta-button cta-primary" data-link>Try Free Demo</a>
        <a href="/login" class="cta-button cta-secondary" data-link>Get Started</a>
      </div>
      <div class="cta-features">
        <span class="cta-feature">✓ No credit card required</span>
        <span class="cta-feature">✓ Instant analysis</span>
        <span class="cta-feature">✓ Secure & private</span>
      </div>
      <div class="coming-soon-badge">
        <span class="badge-icon">🚀</span>
        <span class="badge-text">Coming Soon - Currently in Development</span>
      </div>
    </div>
  </section>
</div>
`;

export function renderDocAnalysisPage(container: HTMLElement) {
    // Add animate.css for animations
    const animateCSSLinkId = 'animate-css-cdn';
    if (!document.getElementById(animateCSSLinkId)) {
        const link = document.createElement('link');
        link.id = animateCSSLinkId;
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css';
        document.head.appendChild(link);
    }

    container.innerHTML = docAnalysisHTML;

    // Setup fade-in animations for sections
    const sections = container.querySelectorAll('.fade-in-section');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    sections.forEach(section => {
        observer.observe(section);
    });

    // Add click handler for upload demo (placeholder functionality)
    const uploadArea = container.querySelector('.upload-area');
    const browseButton = container.querySelector('.browse-button');
    
    const handleUploadClick = () => {
        // Create file input element
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = '.pdf,.doc,.docx,.txt';
        fileInput.multiple = false;
        fileInput.style.display = 'none';
        
        fileInput.onchange = (event) => {
            const files = (event.target as HTMLInputElement).files;
            if (files && files.length > 0) {
                // Show coming soon message
                alert('Document analysis feature is coming soon! This is a preview of the interface.');
            }
        };
        
        document.body.appendChild(fileInput);
        fileInput.click();
        document.body.removeChild(fileInput);
    };
    
    uploadArea?.addEventListener('click', handleUploadClick);
    browseButton?.addEventListener('click', (e) => {
        e.stopPropagation();
        handleUploadClick();
    });

    // Add drag and drop handlers
    uploadArea?.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea?.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea?.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        alert('Document analysis feature is coming soon! This is a preview of the interface.');
    });
}
