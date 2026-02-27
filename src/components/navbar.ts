// src/components/navbar.ts
import { supabase } from '../supabaseClient';
import { auth } from '../auth';
import { i18n } from '../i18n';

async function handleSignOut() {
  await supabase.auth.signOut();
}

// The 'currentPath' argument is still needed to decide if the hamburger menu should be shown.
export function renderNavbar(container: HTMLElement, currentPath: string) {
  const session = auth.getSession();

  const hasSidebar = ['/app', '/profile'].includes(currentPath);

  let navHTML = '';

  if (session) {
    // Logged-in view
    navHTML = `
          <nav class="navbar">
            <div class="navbar-left">
              ${hasSidebar ? `
                <button id="hamburger-menu" aria-label="Open sidebar">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                </button>
              ` : ''}
              <a href="/app" class="navbar-brand" data-link>JustorAI</a>
            </div>
            <div class="navbar-right">
              <div class="nav-links">
                <a href="/app" class="nav-link" data-link>${i18n.t('nav_myChats')}</a>
                <a href="/doc-analysis" class="nav-link" data-link>Doc Analysis</a>
                <a href="/about" class="nav-link" data-link>${i18n.t('nav_about')}</a>
              </div>
              <div class="nav-buttons">
                <a href="/profile" class="nav-link" data-link>${i18n.t('nav_profile')}</a>
                <button id="sign-out-btn" class="nav-button nav-button-primary">${i18n.t('nav_signOut')}</button>
                ${hasSidebar ? `<button id="navbar-new-chat-btn" class="navbar-new-chat-btn" title="New Chat" aria-label="New Chat">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                </button>` : ''}
              </div>
            </div>
          </nav>
        `;
  } else {
    // Logged-out view
    navHTML = `
          <nav class="navbar">
            <div class="navbar-left">
              ${hasSidebar ? `
                <button id="hamburger-menu" aria-label="Open sidebar">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
                </button>
              ` : ''}
              <a href="/" class="navbar-brand" data-link>JustorAI</a>
            </div>
            <div class="navbar-right">
              <div class="nav-links">
                <a href="/#features" class="nav-link">${i18n.t('nav_features')}</a>
                <a href="/about" class="nav-link" data-link>${i18n.t('nav_about')}</a>
              </div>
              <div class="nav-buttons">
                <a href="/login" class="nav-link" data-link>${i18n.t('nav_signIn')}</a>
                <a href="/login" class="nav-button nav-button-primary" data-link>${i18n.t('nav_signUp')}</a>
                ${hasSidebar ? `<button id="navbar-new-chat-btn" class="navbar-new-chat-btn" title="New Chat" aria-label="New Chat">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
                </button>` : ''}
              </div>
            </div>
          </nav>
        `;
  }

  container.innerHTML = navHTML;

  // Hamburger menu listener
  document.getElementById('hamburger-menu')?.addEventListener('click', () => {
    document.dispatchEvent(new CustomEvent('toggle-sidebar'));
  });

  // + New Chat button in navbar — dispatches event that app.ts listens to
  document.getElementById('navbar-new-chat-btn')?.addEventListener('click', () => {
    document.dispatchEvent(new CustomEvent('navbar-new-chat'));
  });

  // Sign-out listener
  document.getElementById('sign-out-btn')?.addEventListener('click', handleSignOut);
}