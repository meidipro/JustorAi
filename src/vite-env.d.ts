/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly [key: string]: string | boolean | undefined;
  readonly VITE_SUPABASE_URL?: string;
  readonly VITE_SUPABASE_ANON_KEY?: string;
  readonly VITE_BACKEND_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module '@supabase/supabase-js' {
  export interface User {
    id: string;
    email?: string;
    user_metadata?: Record<string, any>;
    app_metadata?: Record<string, any>;
    aud?: string;
    created_at?: string;
  }

  export interface Session {
    access_token: string;
    refresh_token: string;
    expires_in: number;
    expires_at?: number;
    token_type: string;
    user: User;
  }

  export type AuthChangeEvent =
    | 'SIGNED_IN'
    | 'SIGNED_OUT'
    | 'USER_UPDATED'
    | 'USER_DELETED'
    | 'PASSWORD_RECOVERY'
    | 'TOKEN_REFRESHED';

  export interface SupabaseClient {
    auth: {
      getSession(): Promise<{ data: { session: Session | null }; error: any }>;
      getUser(): Promise<{ data: { user: User | null }; error: any }>;
      onAuthStateChange(
        callback: (event: AuthChangeEvent, session: Session | null) => void
      ): { data: { subscription: { unsubscribe(): void } } };
      signInWithOAuth(credentials: {
        provider: string;
        options?: { redirectTo?: string; queryParams?: Record<string, string> };
      }): Promise<{ data: any; error: any }>;
      signOut(): Promise<{ error: any }>;
    };
    from(table: string): any;
  }

  export function createClient(
    supabaseUrl: string,
    supabaseKey: string,
    options?: any
  ): SupabaseClient;
}

declare module '*?raw' {
  const content: string;
  export default content;
}
