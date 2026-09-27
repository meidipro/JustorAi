-- ====================================================================
-- Justor AI: WhatsApp Identity & Chamber Multi-Tenancy Migration
-- Run this migration in Supabase SQL Editor
-- ====================================================================

-- 1. Extend profiles table with WhatsApp identity and Chamber binding
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS whatsapp_phone text UNIQUE,
ADD COLUMN IF NOT EXISTS whatsapp_verified boolean DEFAULT false,
ADD COLUMN IF NOT EXISTS chamber_name text DEFAULT 'Independent Chamber',
ADD COLUMN IF NOT EXISTS chamber_id uuid DEFAULT gen_random_uuid();

-- Create index for sub-millisecond phone number resolution
CREATE INDEX IF NOT EXISTS idx_profiles_whatsapp_phone 
ON public.profiles (whatsapp_phone) 
WHERE whatsapp_phone IS NOT NULL;

-- 2. Create WhatsApp Pairing Tokens table for 1-tap web-to-whatsapp authentication
CREATE TABLE IF NOT EXISTS public.whatsapp_pairing_tokens (
    token text PRIMARY KEY,
    user_id uuid REFERENCES auth.users ON DELETE CASCADE NOT NULL,
    phone_number text NOT NULL,
    created_at timestamptz DEFAULT timezone('utc', now()) NOT NULL,
    expires_at timestamptz NOT NULL,
    is_used boolean DEFAULT false
);

CREATE INDEX IF NOT EXISTS idx_pairing_tokens_lookup 
ON public.whatsapp_pairing_tokens (token, is_used, expires_at);

-- Enable Row Level Security on pairing tokens
ALTER TABLE public.whatsapp_pairing_tokens ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role full access on pairing tokens"
ON public.whatsapp_pairing_tokens FOR ALL
USING (true);

-- 3. Audit trail for WhatsApp write actions (supporting audit-safe UNDO)
CREATE TABLE IF NOT EXISTS public.whatsapp_action_audit (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users ON DELETE CASCADE,
    phone_number text NOT NULL,
    matter_id text,
    action_type text NOT NULL, -- 'DICTATION_NOTE', 'ORDER_SHEET_OCR', 'STATUS_UPDATE'
    payload jsonb DEFAULT '{}'::jsonb,
    is_reversed boolean DEFAULT false,
    reversed_at timestamptz,
    created_at timestamptz DEFAULT timezone('utc', now()) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_whatsapp_action_audit_user 
ON public.whatsapp_action_audit (user_id, created_at DESC);
