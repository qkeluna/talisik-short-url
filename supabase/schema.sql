-- Talisik Short URL - Supabase schema
-- Run this once in the Supabase SQL editor (or via `supabase db query`) before
-- setting STORAGE_BACKEND=supabase. Works for both a dedicated project and a
-- project shared with other apps (adjust the schema name below if sharing).

-- Change this if this project is shared with other apps and you want
-- isolation, e.g. `create schema if not exists talisik;` and replace
-- `public` below with `talisik`. Set SUPABASE_DB_SCHEMA to match.
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

alter table public.short_urls enable row level security;

-- Dedicated login role for this app. Never point SUPABASE_DB_URL at the
-- `postgres` admin role -- a compromise of this public URL shortener would
-- otherwise expose every table in the project and bypass RLS everywhere.
-- This role can only see this one table.
create role talisik_app with login password 'REPLACE_WITH_A_STRONG_PASSWORD';

grant usage on schema public to talisik_app;
grant select, insert, update, delete on public.short_urls to talisik_app;

-- talisik_app is not the table owner, so RLS applies to it too (owners
-- bypass RLS by default; non-owner roles are denied by default once RLS is
-- enabled). This policy grants talisik_app full CRUD on all rows -- the
-- service is trusted to enforce its own access rules in the API layer, RLS
-- here exists only to keep talisik_app from ever seeing rows through some
-- other path (e.g. the PostgREST Data API, if this schema is ever exposed
-- there to anon/authenticated).
create policy "talisik_app full access" on public.short_urls
    for all
    to talisik_app
    using (true)
    with check (true);

-- After running this, build SUPABASE_DB_URL from the Transaction pooler
-- connection string using the talisik_app role instead of postgres, e.g.
-- postgresql://talisik_app.your-project-ref:your-password@aws-0-region.pooler.supabase.com:6543/postgres
-- Confirm the exact pooler username format for your project (it's role.project-ref)
-- via the Supabase dashboard's connection string picker -- it lets you choose
-- role there directly.
