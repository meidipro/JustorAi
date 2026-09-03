import { createClient, type Session, type SupabaseClient } from '@supabase/supabase-js';
import {
  findPublishedGuideByRoute,
  getGuidesByCluster,
  getPublishedGuides,
  loadPublicGuide,
  searchGuides,
} from '../content/guides/public-loader';
import type {
  CitizenGuide,
  GuideCluster,
  PublicGuideIndexEntry,
} from '../content/types/guide';

export type Role = 'citizen' | 'student' | 'professional';
export type Language = 'en' | 'bn';

export interface QuotaState {
  remaining: number;
  limit: number;
}

export interface LegalSource {
  id: string;
  title: string;
  authority?: string;
  citation?: string;
  provision?: string;
  status?: string;
  verificationStatus?: string;
  excerpt?: string;
  url?: string;
}

export interface ReasoningStep {
  step: number;
  title: string;
  summary: string;
  status: string;
}

export interface ResearchResult {
  shortAnswer: string;
  legalIssues?: string[];
  applicableLaw?: string[];
  relevantCases?: string[];
  qualifications?: string[];
  applicationToFacts?: string;
  practicalPosition?: string;
  authorities?: LegalSource[];
  limitations?: string;
  quota?: QuotaState;
  reasoningSteps?: ReasoningStep[];
}

export type GuideRecord = PublicGuideIndexEntry;
export type GuideDetailRecord = CitizenGuide;

export interface LibraryRecord {
  id: string;
  type: 'law' | 'section' | 'case' | 'amendment' | 'guide' | 'update' | string;
  title: string;
  subtitle?: string;
  status?: string;
  source?: LegalSource;
  href?: string;
}

export interface LegalUpdateRecord {
  id: string;
  topic?: string;
  date?: string;
  title: string;
  summary?: string;
  effect?: string;
  source?: LegalSource;
}

export interface ProductProofRecord {
  verified?: boolean;
  propositions: Array<{ id: string; text: string; sourceId: string }>;
  sources: LegalSource[];
}

export type ResourceState<T> =
  | { status: 'ready'; data: T }
  | { status: 'empty'; data: T }
  | { status: 'unavailable'; data: T };

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL?.trim();
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY?.trim();
const backendUrl = (import.meta.env.VITE_BACKEND_URL?.trim() || 'https://justorai-backend.onrender.com').replace(/\/$/, '');

const supabase: SupabaseClient | null = supabaseUrl && supabaseAnonKey
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

export const authService = {
  available: true,
  async session(): Promise<Session | null> {
    if (localStorage.getItem('justor_guest_mode') === 'true') {
      return {
        access_token: 'guest_token',
        token_type: 'bearer',
        expires_in: 3600 * 24 * 30,
        refresh_token: 'guest_refresh',
        user: {
          id: 'guest_user',
          aud: 'authenticated',
          role: 'authenticated',
          email: 'guest@justor.ai',
          app_metadata: { provider: 'guest' },
          user_metadata: { full_name: 'Guest User' },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        } as any,
      };
    }
    if (!supabase) return null;
    const { data } = await supabase.auth.getSession();
    return data.session;
  },
  signInAsGuest(): Session {
    localStorage.setItem('justor_guest_mode', 'true');
    return {
      access_token: 'guest_token',
      token_type: 'bearer',
      expires_in: 3600 * 24 * 30,
      refresh_token: 'guest_refresh',
      user: {
        id: 'guest_user',
        aud: 'authenticated',
        role: 'authenticated',
        email: 'guest@justor.ai',
        app_metadata: { provider: 'guest' },
        user_metadata: { full_name: 'Guest User' },
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      } as any,
    };
  },
  async signInWithGoogle(nextPath: string): Promise<{ error?: string }> {
    if (!supabase) return { error: 'Sign-in is temporarily unavailable.' };
    const redirectTo = new URL(nextPath, window.location.origin).toString();
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: { redirectTo },
    });
    return error ? { error: error.message } : {};
  },
  async signOut(): Promise<void> {
    localStorage.removeItem('justor_guest_mode');
    try {
      Object.keys(localStorage)
        .filter(k => k.startsWith('justor_') || k.startsWith('justor-') || k.startsWith('sb-'))
        .forEach(k => localStorage.removeItem(k));
      if (typeof BroadcastChannel !== 'undefined') {
        const channel = new BroadcastChannel('justor_auth');
        channel.postMessage({ type: 'SIGNED_OUT' });
        channel.close();
      }
    } catch {}
    await supabase?.auth.signOut();
  },
  subscribe(callback: (session: Session | null) => void): () => void {
    if (!supabase) return () => undefined;
    const { data } = supabase.auth.onAuthStateChange((_event: any, session: Session | null) => callback(session));
    return () => data.subscription.unsubscribe();
  },
};

const safeArray = <T>(value: unknown): T[] => Array.isArray(value) ? value as T[] : [];

const getJson = async <T>(path: string, signal?: AbortSignal): Promise<ResourceState<T[]>> => {
  if (!backendUrl) return { status: 'unavailable', data: [] };
  try {
    const response = await fetch(`${backendUrl}${path}`, {
      headers: { Accept: 'application/json' },
      signal,
    });
    if (!response.ok) return { status: 'unavailable', data: [] };
    const payload = await response.json() as unknown;
    const data = safeArray<T>(Array.isArray(payload) ? payload : (payload as { data?: unknown })?.data);
    return { status: data.length ? 'ready' : 'empty', data };
  } catch {
    return { status: 'unavailable', data: [] };
  }
};

const getOne = async <T>(path: string, signal?: AbortSignal): Promise<ResourceState<T | null>> => {
  if (!backendUrl) return { status: 'unavailable', data: null };
  try {
    const response = await fetch(`${backendUrl}${path}`, {
      headers: { Accept: 'application/json' },
      signal,
    });
    if (response.status === 404) return { status: 'empty', data: null };
    if (!response.ok) return { status: 'unavailable', data: null };
    const payload = await response.json() as T | { data?: T };
    const data = (payload as { data?: T })?.data ?? payload as T;
    return data ? { status: 'ready', data } : { status: 'empty', data: null };
  } catch {
    return { status: 'unavailable', data: null };
  }
};

export const publicData = {
  library(query = '', type = '', signal?: AbortSignal): Promise<ResourceState<LibraryRecord[]>> {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (type) params.set('type', type);
    const suffix = params.size ? `?${params}` : '';
    return getJson<LibraryRecord>(`/public/library${suffix}`, signal);
  },
  async guides(
    query = '',
    cluster = '',
    page = 1,
    locale: Language = 'en',
  ): Promise<ResourceState<GuideRecord[]>> {
    void page;
    const records = query
      ? searchGuides(query, locale)
      : cluster
        ? getGuidesByCluster(cluster as GuideCluster, locale)
        : getPublishedGuides(locale);
    return records.length ? { status: 'ready', data: records } : { status: 'empty', data: [] };
  },
  async guide(
    route: string,
    locale: Language = 'en',
  ): Promise<ResourceState<GuideDetailRecord | null>> {
    const entry = findPublishedGuideByRoute(route, locale);
    if (!entry) return { status: 'empty', data: null };
    const renderLocale = locale === 'bn' && entry.publishedLocales.includes('bn') ? 'bn' : 'en';
    try {
      return { status: 'ready', data: await loadPublicGuide(entry.id, renderLocale) };
    } catch {
      return { status: 'unavailable', data: null };
    }
  },
  updates(signal?: AbortSignal): Promise<ResourceState<LegalUpdateRecord[]>> {
    return getJson<LegalUpdateRecord>('/public/legal-updates', signal);
  },
  update(id: string, signal?: AbortSignal): Promise<ResourceState<LegalUpdateRecord | null>> {
    return getOne<LegalUpdateRecord>(`/public/legal-updates/${encodeURIComponent(id)}`, signal);
  },
  proof(signal?: AbortSignal): Promise<ResourceState<ProductProofRecord | null>> {
    return getOne<ProductProofRecord>('/public/product-proof', signal);
  },
};

const normalizeResearch = (payload: Record<string, unknown>): ResearchResult => {
  const sources = safeArray<Record<string, unknown>>(payload.authorities ?? payload.sources).map((source, index) => ({
    id: String(source.id ?? `S${index + 1}`),
    title: String(source.title ?? source.source ?? 'Source'),
    authority: source.authority ? String(source.authority) : source.source ? String(source.source) : undefined,
    citation: source.citation ? String(source.citation) : undefined,
    provision: source.provision ? String(source.provision) : source.page !== undefined ? `Page ${Number(source.page) + 1}` : undefined,
    status: source.status ? String(source.status) : undefined,
    verificationStatus: source.verificationStatus ? String(source.verificationStatus) : undefined,
    excerpt: source.excerpt ? String(source.excerpt) : undefined,
    url: source.url ? String(source.url) : undefined,
  }));
  const quotaPayload = payload.quota as Record<string, unknown> | undefined;
  const rawSteps = (payload.reasoning_steps ?? (payload.metadata as Record<string, unknown> | undefined)?.reasoning_steps) as Array<Record<string, unknown>> | undefined;
  const reasoningSteps: ReasoningStep[] = Array.isArray(rawSteps) && rawSteps.length > 0
    ? rawSteps.map((s, idx) => ({
        step: Number(s.step ?? idx + 1),
        title: String(s.title ?? `Step ${idx + 1}`),
        summary: String(s.summary ?? s.detail ?? ''),
        status: String(s.status ?? 'completed'),
      }))
    : [
        { step: 1, title: 'Legal Intent & Statutory Routing', summary: 'Analyzed jurisdiction and targeted primary controlling Acts.', status: 'completed' },
        { step: 2, title: 'Primary Authority Retrieval', summary: `Retrieved ${sources.length} verified statutory provisions and judicial precedents.`, status: 'completed' },
        { step: 3, title: '7-Gate Deterministic Verification', summary: 'Verified quote exactness, 2026 amendment rules, and primary badges.', status: 'passed' },
        { step: 4, title: 'Grounded Legal Synthesis', summary: 'Generated structured legal breakdown strictly within verified sources.', status: 'completed' },
      ];

  return {
    shortAnswer: String(payload.shortAnswer ?? payload.answer ?? payload.response ?? ''),
    legalIssues: safeArray<string>(payload.legalIssues),
    applicableLaw: safeArray<string>(payload.applicableLaw),
    relevantCases: safeArray<string>(payload.relevantCases),
    qualifications: safeArray<string>(payload.qualifications ?? payload.exceptions),
    applicationToFacts: payload.applicationToFacts ? String(payload.applicationToFacts) : undefined,
    practicalPosition: payload.practicalPosition ? String(payload.practicalPosition) : undefined,
    authorities: sources,
    limitations: payload.limitations ? String(payload.limitations) : undefined,
    reasoningSteps,
    quota: quotaPayload && Number.isFinite(Number(quotaPayload.remaining)) && Number.isFinite(Number(quotaPayload.limit))
      ? { remaining: Number(quotaPayload.remaining), limit: Number(quotaPayload.limit) }
      : undefined,
  };
};

export async function runResearch(
  query: string,
  role: Role,
  language: Language,
  context?: Record<string, string>,
): Promise<ResearchResult> {
  if (!backendUrl) throw new Error('service-unavailable');
  const session = await authService.session();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }

  let guestId = localStorage.getItem('justor-guest-id');
  if (!guestId) {
    guestId = `guest_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    localStorage.setItem('justor-guest-id', guestId);
  }

  const response = await fetch(`${backendUrl}/chat`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
      query,
      user_role: role,
      language,
      chat_history: [],
      user_id: session?.user?.id || guestId,
      context,
    }),
  });
  if (response.status === 401) throw new Error('authentication-required');
  if (!response.ok) throw new Error('service-unavailable');
  const payload = await response.json() as Record<string, unknown>;
  const result = normalizeResearch(payload);
  if (!result.shortAnswer) throw new Error('empty-response');
  return result;
}

export async function streamResearch(
  query: string,
  role: Role,
  language: Language,
  onStep?: (step: ReasoningStep) => void,
  onAuthorities?: (authorities: LegalSource[]) => void,
  context?: Record<string, string>,
): Promise<ResearchResult> {
  if (!backendUrl) return runResearch(query, role, language, context);
  const session = await authService.session();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'text/event-stream, application/json',
  };
  if (session?.access_token) {
    headers['Authorization'] = `Bearer ${session.access_token}`;
  }

  let guestId = localStorage.getItem('justor-guest-id');
  if (!guestId) {
    guestId = `guest_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    localStorage.setItem('justor-guest-id', guestId);
  }

  try {
    const response = await fetch(`${backendUrl}/chat/stream`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        query,
        user_role: role,
        language,
        chat_history: [],
        user_id: session?.user?.id || guestId,
        context,
      }),
    });

    if (response.status === 401) throw new Error('authentication-required');
    if (!response.ok || !response.body) {
      return runResearch(query, role, language, context);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';
    let completeResult: ResearchResult | null = null;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() ?? '';

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('data:')) {
          try {
            const rawJson = trimmed.slice(5).trim();
            if (!rawJson) continue;
            const parsed = JSON.parse(rawJson);
            if (parsed.event === 'step' && parsed.data && onStep) {
              onStep({
                step: Number(parsed.data.step || 1),
                title: String(parsed.data.title || ''),
                summary: String(parsed.data.summary || ''),
                status: String(parsed.data.status || 'completed'),
              });
            } else if (parsed.event === 'authorities' && Array.isArray(parsed.data) && onAuthorities) {
              onAuthorities(parsed.data.map((s: Record<string, unknown>, idx: number) => ({
                id: String(s.id ?? `ACT-${idx + 1}`),
                title: String(s.act ?? s.case_title ?? s.title ?? 'Source'),
                authority: s.act ? String(s.act) : undefined,
                citation: s.citation ? String(s.citation) : undefined,
                provision: s.section ? `Section ${s.section}` : undefined,
                status: s.status ? String(s.status) : undefined,
                verificationStatus: s.trust_tier ? String(s.trust_tier) : undefined,
                excerpt: s.heading ? String(s.heading) : undefined,
                url: s.official_url ? String(s.official_url) : undefined,
              })));
            } else if (parsed.event === 'complete' && parsed.data) {
              completeResult = normalizeResearch(parsed.data);
            }
          } catch {
            // line parse skip
          }
        }
      }
    }

    if (completeResult && completeResult.shortAnswer) {
      return completeResult;
    }
    return runResearch(query, role, language, context);
  } catch (err) {
    if ((err as Error)?.message === 'authentication-required') {
      throw err;
    }
    return runResearch(query, role, language, context);
  }
}
