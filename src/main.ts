import './style.css'
import { shouldShowIntro, mountIntroOverlay } from './components/introOverlay';
import { supabase } from './supabaseClient';
import { auth } from './auth';
import { renderNavbar } from './components/navbar';
import { renderLandingPage } from './pages/landing';
import { renderAboutPage } from './pages/about';
import { renderLoginPage } from './pages/login';
import { renderAppPage } from './pages/app';
import { renderUserProfilePage } from './pages/user-profile';
import { renderDocAnalysisPage } from './pages/doc-analysis';

const appContainer = document.getElementById('app') as HTMLElement;
const navbarContainer = document.getElementById('navbar-container') as HTMLElement;

const routes: { [key: string]: (container: HTMLElement) => void } = {
  '/': renderLandingPage,
  '/about': renderAboutPage,
  '/login': renderLoginPage,
  '/app': renderAppPage,
  '/profile': renderUserProfilePage,
  '/doc-analysis': renderDocAnalysisPage,
};

const router = () => {
  const session = auth.getSession();
  let path = window.location.pathname;
  if (path === "" || path === "/index.html") { path = "/"; }
  const protectedRoutes = ['/profile'];
  if (!session && protectedRoutes.includes(path)) {
    history.pushState(null, '', '/login');
    path = '/login';
  }
  const renderPage = routes[path] || routes['/'];
  renderPage(appContainer);
};

supabase.auth.onAuthStateChange((_event, session) => {
  auth.setSession(session);
  // CHANGE 1: Pass the current path
  renderNavbar(navbarContainer, window.location.pathname);

  // Dispatch custom event for app page to update user profile link
  window.dispatchEvent(new CustomEvent('authStateChange'));

  const currentPath = window.location.pathname;
  if (!session) {
    if (currentPath === '/app' || currentPath === '/profile') {
      history.pushState(null, '', '/');
      router();
    } else {
      router();
    }
  } else {
    if (currentPath === '/login') {
      history.pushState(null, '', '/app');
      router();
    } else {
      router();
    }
  }
});

document.addEventListener('DOMContentLoaded', async () => {
  // Show intro overlay once per session
  if (shouldShowIntro()) {
    await mountIntroOverlay();
  }

  // ── Backend Wake-Up & Keep-Alive ──────────────────────────────────────────
  // Pings the Render backend immediately on load, then every 14 min,
  // so the free-tier server never sleeps while a user has the tab open.
  const pingBackend = async () => {
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL;
      if (backendUrl) {
        const cleanUrl = backendUrl.replace(/\/$/, '');
        await fetch(`${cleanUrl}/ping`, { method: 'GET', mode: 'no-cors' });
      }
    } catch (_) {
      // Silently ignore — it's a best-effort wake-up call
    }
  };
  pingBackend(); // Fire immediately on page load
  setInterval(pingBackend, 14 * 60 * 1000); // Then every 14 minutes


  const { data: { session } } = await supabase.auth.getSession();
  auth.setSession(session);

  // CHANGE 2: Pass the current path
  renderNavbar(navbarContainer, window.location.pathname);
  router();

  document.body.addEventListener('click', e => {
    const target = e.target as HTMLElement;
    const link = target.closest('[data-link]') as HTMLAnchorElement;
    if (link) {
      e.preventDefault();
      history.pushState(null, '', link.href);
      // We also need to update the navbar on navigation
      renderNavbar(navbarContainer, link.pathname);
      router();
    }
  });

  window.addEventListener('popstate', () => {
    // And here
    renderNavbar(navbarContainer, window.location.pathname);
    router();
  });

  window.addEventListener('languageChange', () => {
    // And finally here
    renderNavbar(navbarContainer, window.location.pathname);
    router();
  });
});