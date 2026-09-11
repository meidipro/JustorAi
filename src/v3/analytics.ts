/**
 * Justor AI — Google Analytics 4 (GA4) Telemetry Service
 * Automatically initializes if VITE_GA_MEASUREMENT_ID is defined in .env
 */

declare global {
  interface Window {
    dataLayer: any[];
    gtag: (...args: any[]) => void;
  }
}

class AnalyticsService {
  private initialized = false;
  private measurementId: string | null = null;

  constructor() {
    this.measurementId = (import.meta as any).env?.VITE_GA_MEASUREMENT_ID || null;
    this.init();
  }

  private init() {
    if (this.initialized || !this.measurementId || typeof window === 'undefined') {
      return;
    }

    try {
      // 1. Inject gtag.js script
      const script = document.createElement('script');
      script.async = true;
      script.src = `https://www.googletagmanager.com/gtag/js?id=${this.measurementId}`;
      document.head.appendChild(script);

      // 2. Initialize dataLayer
      window.dataLayer = window.dataLayer || [];
      window.gtag = function () {
        window.dataLayer.push(arguments);
      };

      window.gtag('js', new Date());
      window.gtag('config', this.measurementId, {
        send_page_view: true,
        cookie_flags: 'SameSite=None;Secure'
      });

      this.initialized = true;
      console.log(`[Justor Analytics] GA4 initialized with ID: ${this.measurementId}`);
    } catch (e) {
      console.warn('[Justor Analytics] Failed to initialize GA4:', e);
    }
  }

  public event(eventName: string, params: Record<string, any> = {}) {
    if (typeof window !== 'undefined' && typeof window.gtag === 'function' && this.measurementId) {
      window.gtag('event', eventName, params);
    }
  }

  public pageView(pagePath: string, pageTitle?: string) {
    this.event('page_view', {
      page_path: pagePath,
      page_title: pageTitle || document.title
    });
  }

  public trackSearch(query: string, persona: string, status: string = 'ok') {
    this.event('legal_search_query', {
      search_term: query.slice(0, 100),
      persona: persona,
      status: status
    });
  }

  public trackCitationClick(act: string, section: string) {
    this.event('citation_click', {
      act_name: act,
      section: section
    });
  }

  public trackDocumentOCR(docType: string, filename: string) {
    this.event('document_ocr_analyzed', {
      document_type: docType,
      file_name: filename
    });
  }

  public trackRoleSwitch(newRole: string) {
    this.event('role_switched', {
      target_role: newRole
    });
  }

  public trackPilotApply(chamberName?: string) {
    this.event('founding_pilot_applied', {
      chamber: chamberName || 'Independent'
    });
  }
}

export const analytics = new AnalyticsService();
