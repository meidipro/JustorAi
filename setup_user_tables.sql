-- ==========================================================
-- JustorAI User Profiles, Chat History & Feedback Tables
-- Run this single block in your Supabase SQL Editor
-- ==========================================================

-- 1. Create Profiles Table (Stores user roles: Legal Professional, Law Student, General Public)
create table if not exists public.profiles (
    id uuid references auth.users on delete cascade primary key,
    email text,
    full_name text,
    role text default 'General Public', -- 'Legal Professional', 'Law Student', 'General Public'
    created_at timestamp with time zone default timezone('utc', now()) not null
);

-- Enable RLS for Profiles
alter table public.profiles enable row level security;

create policy "Users can view own profile"
    on public.profiles for select
    using (auth.uid() = id);

create policy "Users can update own profile"
    on public.profiles for update
    using (auth.uid() = id);

create policy "Service role has full access to profiles"
    on public.profiles for all
    using (true);

-- Auto-create profile trigger on signup
create or replace function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email, full_name, role)
  values (new.id, new.email, new.raw_user_meta_data->>'full_name', coalesce(new.raw_user_meta_data->>'role', 'General Public'))
  on conflict (id) do nothing;
  return new;
end;
$$ language plpgsql security definer;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

-- 2. Create Chats Table
create table if not exists public.chats (
    id uuid primary key default gen_random_uuid(),
    user_id uuid references auth.users on delete cascade,
    title text not null default 'New Chat',
    has_document boolean default false,
    created_at timestamp with time zone default timezone('utc', now()) not null
);

alter table public.chats enable row level security;

create policy "Users can manage own chats"
    on public.chats for all
    using (auth.uid() = user_id);

-- 3. Create Messages Table
create table if not exists public.messages (
    id bigint generated always as identity primary key,
    chat_id uuid references public.chats(id) on delete cascade not null,
    user_id uuid references auth.users on delete cascade,
    sender text not null check (sender in ('user', 'ai')),
    content text not null,
    created_at timestamp with time zone default timezone('utc', now()) not null
);

alter table public.messages enable row level security;

create policy "Users can manage own messages"
    on public.messages for all
    using (auth.uid() = user_id);

-- 4. Create Message Feedback Table
create table if not exists public.message_feedback (
    id uuid primary key default gen_random_uuid(),
    chat_id text,
    message_content text,
    rating text check (rating in ('good', 'bad')),
    created_at timestamp with time zone default timezone('utc', now()) not null
);

alter table public.message_feedback enable row level security;

create policy "Anyone can submit feedback"
    on public.message_feedback for insert
    with check (true);
