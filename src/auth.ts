// src/auth.ts
import { supabase } from './supabaseClient';
import { type Session } from '@supabase/supabase-js';

// A simple store to hold the session state
let currentSession: Session | null = null;

export const auth = {
  // A function to get the current session without an async call
  getSession: () => {
    console.log('🔍 auth.getSession() called, current session:', currentSession ? `USER: ${currentSession.user?.email}` : 'NULL');
    return currentSession;
  },
  
  // A function to set the session, called by our main router
  setSession: (session: Session | null) => {
    console.log('📝 auth.setSession() called with:', session ? `USER: ${session.user?.email}` : 'NULL');
    currentSession = session;
  },

  // A helper to get the user ID
  getUserId: () => currentSession?.user?.id ?? null,
};

// Immediately check for a session on load
console.log('🚀 auth.ts: Checking for existing session on load...');
supabase.auth.getSession().then(({ data: { session } }) => {
    console.log('🔄 auth.ts: Initial session check result:', session ? `USER: ${session.user?.email}` : 'NULL');
    auth.setSession(session);
});