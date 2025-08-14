// src/pages/login.ts
import { supabase } from '../supabaseClient';
import { i18n } from '../i18n';

let authMode: 'signIn' | 'signUp' = 'signIn';

async function handleGoogleSignIn() {
    const redirectUrl = `${window.location.origin}/app`;
    const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: { redirectTo: redirectUrl }
    });
    if (error) {
        console.error("Error signing in with Google:", error);
        alert("Error signing in with Google: " + error.message);
    }
}

async function handleEmailAuth(e: Event) {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const email = (form.elements.namedItem('email') as HTMLInputElement).value;
    const password = (form.elements.namedItem('password') as HTMLInputElement).value;

    if (authMode === 'signUp') {
        const fullName = (form.elements.namedItem('fullName') as HTMLInputElement).value;
        if (!fullName) {
            alert('Please enter your full name.');
            return;
        }

        // --- SIGN UP LOGIC with Full Name ---
        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: {
                data: {
                    full_name: fullName // This saves the name to user_metadata
                }
            }
        });
        if (error) {
            alert(error.message);
        } else {
            alert(i18n.t('login_page_confirmEmail'));
            console.log("Sign up successful, user needs to confirm email.", data);
        }
    } else {
        // --- SIGN IN LOGIC (unchanged) ---
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) { 
            alert(error.message); 
        }
    }
}

export function renderLoginPage(container: HTMLElement) {
    const isSignInMode = authMode === 'signIn';
    const title = isSignInMode ? i18n.t('login_page_signInTitle') : i18n.t('login_page_signUpTitle');
    const buttonText = isSignInMode ? i18n.t('login_page_signInButton') : i18n.t('login_page_signUpButton');
    const switchPrompt = isSignInMode ? i18n.t('login_page_askSignUp') : i18n.t('login_page_askSignIn');
    const switchLinkText = isSignInMode ? i18n.t('login_page_linkSignUp') : i18n.t('login_page_linkSignIn');
    
    // --- Dynamically add the Full Name field for Sign Up mode ---
    const fullNameFieldHTML = isSignInMode ? '' : `
      <div class="form-field">
        <label for="fullName">${i18n.t('login_page_fullNameLabel')}</label>
        <input type="text" id="fullName" name="fullName" required autocomplete="name">
      </div>
    `;

    container.innerHTML = `
      <div class="modern-login-container">
        <div class="login-background">
          <div class="gradient-orb orb-1"></div>
          <div class="gradient-orb orb-2"></div>
          <div class="gradient-orb orb-3"></div>
          
          <!-- Law-themed graphics -->
          <div class="legal-graphics">
            <div class="scales-of-justice">
              <svg width="120" height="120" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g opacity="0.1">
                  <circle cx="30" cy="85" r="20" stroke="white" stroke-width="2" fill="none"/>
                  <circle cx="90" cy="85" r="20" stroke="white" stroke-width="2" fill="none"/>
                  <line x1="30" y1="65" x2="90" y2="65" stroke="white" stroke-width="2"/>
                  <line x1="60" y1="25" x2="60" y2="65" stroke="white" stroke-width="3"/>
                  <circle cx="60" cy="25" r="5" fill="white"/>
                  <line x1="30" y1="65" x2="30" y2="85" stroke="white" stroke-width="2"/>
                  <line x1="90" y1="65" x2="90" y2="85" stroke="white" stroke-width="2"/>
                </g>
              </svg>
            </div>
            
            <div class="gavel-icon">
              <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g opacity="0.08">
                  <rect x="20" y="15" width="40" height="8" rx="4" fill="white"/>
                  <rect x="35" y="23" width="10" height="25" rx="2" fill="white"/>
                  <rect x="25" y="45" width="30" height="6" rx="3" fill="white"/>
                  <line x1="15" y1="55" x2="65" y2="65" stroke="white" stroke-width="3" stroke-linecap="round"/>
                </g>
              </svg>
            </div>
            
            <div class="book-icon">
              <svg width="60" height="60" viewBox="0 0 60 60" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g opacity="0.1">
                  <rect x="15" y="10" width="30" height="40" rx="2" stroke="white" stroke-width="2" fill="none"/>
                  <line x1="20" y1="20" x2="40" y2="20" stroke="white" stroke-width="1"/>
                  <line x1="20" y1="25" x2="40" y2="25" stroke="white" stroke-width="1"/>
                  <line x1="20" y1="30" x2="35" y2="30" stroke="white" stroke-width="1"/>
                  <line x1="30" y1="10" x2="30" y2="50" stroke="white" stroke-width="1"/>
                </g>
              </svg>
            </div>
            
            <div class="pillar-left">
              <svg width="40" height="100" viewBox="0 0 40 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g opacity="0.06">
                  <rect x="5" y="85" width="30" height="15" fill="white"/>
                  <rect x="10" y="15" width="20" height="70" fill="white"/>
                  <rect x="5" y="5" width="30" height="10" fill="white"/>
                </g>
              </svg>
            </div>
            
            <div class="pillar-right">
              <svg width="40" height="100" viewBox="0 0 40 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                <g opacity="0.06">
                  <rect x="5" y="85" width="30" height="15" fill="white"/>
                  <rect x="10" y="15" width="20" height="70" fill="white"/>
                  <rect x="5" y="5" width="30" height="10" fill="white"/>
                </g>
              </svg>
            </div>
            
            <div class="legal-pattern">
              <div class="pattern-line"></div>
              <div class="pattern-line"></div>
              <div class="pattern-line"></div>
              <div class="pattern-line"></div>
            </div>
          </div>
        </div>
        
        <div class="login-content">
          <div class="login-card">
            <div class="login-header">
              <div class="brand-logo">
                <div class="logo-icon">⚖️</div>
                <span class="brand-name">JustorAI</span>
              </div>
              <h1 class="login-title">${title}</h1>
              <p class="login-subtitle">${i18n.t('login_page_subtitle')}</p>
            </div>

            <div class="login-form-container">
              <button id="google-signin-btn" class="google-signin-modern">
                <svg class="google-icon" width="20" height="20" viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M17.64 9.20455C17.64 8.56636 17.5827 7.95273 17.4764 7.36364H9V10.845H13.8436C13.635 11.97 13.0009 12.9232 12.0477 13.5614V15.8195H14.9564C16.6582 14.2527 17.64 11.9464 17.64 9.20455Z" fill="#4285F4"></path>
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M9 18C11.43 18 13.4673 17.1941 14.9564 15.8195L12.0477 13.5614C11.2418 14.1014 10.2109 14.4205 9 14.4205C6.96182 14.4205 5.23727 13.0395 4.50545 11.1805H1.51636V13.5095C3.00545 16.2232 5.79409 18 9 18Z" fill="#34A853"></path>
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M4.50545 11.1805C4.31636 10.6405 4.20545 10.0695 4.20545 9.47045C4.20545 8.87136 4.31636 8.29909 4.50545 7.76091V5.43182H1.51636C0.952727 6.61955 0.636364 7.97182 0.636364 9.47045C0.636364 10.9691 0.952727 12.3214 1.51636 13.5091L4.50545 11.1805Z" fill="#FBBC04"></path>
                  <path fill-rule="evenodd" clip-rule="evenodd" d="M9 4.52045C10.0214 4.52045 10.9405 4.88727 11.6836 5.59364L15.0218 2.39182C13.4632 0.902727 11.4259 0 9 0C5.79409 0 3.00545 1.77682 1.51636 4.49045L4.50545 6.81954C5.23727 4.96045 6.96182 4.52045 9 4.52045Z" fill="#EA4335"></path>
                </svg>
                <span>${i18n.t('login_page_googleButton')}</span>
              </button>

              <div class="divider-container">
                <div class="divider-line"></div>
                <span class="divider-text">${i18n.t('login_page_divider')}</span>
                <div class="divider-line"></div>
              </div>

              <form id="email-auth-form" class="modern-email-form">
                ${fullNameFieldHTML ? `
                  <div class="input-group">
                    <div class="input-icon">👤</div>
                    <input type="text" id="fullName" name="fullName" required autocomplete="name" placeholder="${i18n.t('login_page_fullNameLabel')}">
                    <label for="fullName">${i18n.t('login_page_fullNameLabel')}</label>
                  </div>
                ` : ''}
                
                <div class="input-group">
                  <div class="input-icon">📧</div>
                  <input type="email" id="email" name="email" required autocomplete="email" placeholder="${i18n.t('login_page_emailLabel')}">
                  <label for="email">${i18n.t('login_page_emailLabel')}</label>
                </div>
                
                <div class="input-group">
                  <div class="input-icon">🔒</div>
                  <input type="password" id="password" name="password" required autocomplete="current-password" placeholder="${i18n.t('login_page_passwordLabel')}">
                  <label for="password">${i18n.t('login_page_passwordLabel')}</label>
                </div>
                
                <button type="submit" class="submit-button">
                  <span class="button-text">${buttonText}</span>
                  <div class="button-icon">→</div>
                </button>
              </form>

              <div class="auth-switch">
                <span class="switch-text">${switchPrompt}</span>
                <a href="#" id="switch-auth-mode" class="switch-link">${switchLinkText}</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;

    document.getElementById('google-signin-btn')?.addEventListener('click', handleGoogleSignIn);
    document.getElementById('email-auth-form')?.addEventListener('submit', handleEmailAuth);
    
    document.getElementById('switch-auth-mode')?.addEventListener('click', (e) => {
        e.preventDefault();
        authMode = (authMode === 'signIn' ? 'signUp' : 'signIn');
        renderLoginPage(container);
    });
}