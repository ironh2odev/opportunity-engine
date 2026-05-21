-- Public-safe schema draft for Supabase/Postgres

create type opportunity_category as enum (
  'job',
  'freelance',
  'client-lead',
  'partnership'
);

create type opportunity_status as enum (
  'new',
  'reviewed',
  'saved',
  'contacted',
  'rejected'
);

create table if not exists opportunities (
  id uuid primary key default gen_random_uuid(),
  title text not null,
  organization text not null,
  source text not null,
  category opportunity_category not null,
  relevance_score int not null check (relevance_score between 0 and 100),
  summary text not null,
  why_it_matches text not null,
  suggested_action text not null,
  status opportunity_status not null default 'new',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists tailoring_drafts (
  id uuid primary key default gen_random_uuid(),
  opportunity_id uuid not null references opportunities(id) on delete cascade,
  cv_bullets jsonb not null,
  motivation_letter text not null,
  outreach_draft text not null,
  project_emphasis jsonb not null,
  confidence_signals jsonb not null,
  human_approved boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists opportunity_pipeline_events (
  id uuid primary key default gen_random_uuid(),
  opportunity_id uuid not null references opportunities(id) on delete cascade,
  from_status opportunity_status,
  to_status opportunity_status not null,
  actor text not null default 'human',
  note text,
  created_at timestamptz not null default now()
);

create table if not exists rag_document_registry (
  id uuid primary key default gen_random_uuid(),
  label text not null,
  file_name text not null,
  source_scope text not null check (source_scope in ('demo', 'private-local')),
  checksum text,
  embedded_at timestamptz,
  created_at timestamptz not null default now()
);
