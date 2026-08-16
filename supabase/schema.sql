-- Talisik Short URL - Supabase schema
-- Run this once in the Supabase SQL editor (or via `supabase db query`) against
-- a fresh project before setting STORAGE_BACKEND=supabase.

create table if not exists public.short_urls (
    id uuid primary key default gen_random_uuid(),
    original_url text not null,
    short_code text not null unique,
    created_at timestamptz not null default now(),
    expires_at timestamptz,
    click_count integer not null default 0,
    is_active boolean not null default true
);

create index if not exists idx_short_urls_short_code on public.short_urls (short_code);

-- The application connects with the Postgres "postgres" role via SUPABASE_DB_URL
-- (a direct connection string, not the PostgREST Data API), which bypasses RLS as
-- the table owner. RLS is still enabled here as defense in depth: if this table is
-- ever exposed through the Data API to anon/authenticated roles, it defaults to
-- deny-all until policies are added explicitly.
alter table public.short_urls enable row level security;
