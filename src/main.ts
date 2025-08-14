// src/main.ts
import './style.css'
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
    console.log('🔥 main.ts: Auth state change event:', _event, session ? `USER: ${session.user?.email}` : 'NULL');
    auth.setSession(session);
    // CHANGE 1: Pass the current path
    renderNavbar(navbarContainer, window.location.pathname);
    
    // Dispatch custom event for app page to update user profile link
    console.log('📡 main.ts: Dispatching authStateChange event');
    window.dispatchEvent(new CustomEvent('authStateChange'));

    const currentPath = window.location.pathname;
    console.log('🛣️ main.ts: Current path:', currentPath);
    if (!session) {
        console.log('❌ main.ts: No session, handling logout redirect...');
        if (currentPath === '/app' || currentPath === '/profile') {
            history.pushState(null, '', '/');
            router(); 
        } else {
            router();
        }
    } else {
        console.log('✅ main.ts: Session exists, handling login redirect...');
        if (currentPath === '/login') {
            history.pushState(null, '', '/app');
            router();
        } else {
            router();
        }
    }
});

document.addEventListener('DOMContentLoaded', async () => {
  console.log('🎯 main.ts: DOMContentLoaded, getting initial session...');
  const { data: { session } } = await supabase.auth.getSession();
  console.log('🔍 main.ts: Initial session from DOMContentLoaded:', session ? `USER: ${session.user?.email}` : 'NULL');
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