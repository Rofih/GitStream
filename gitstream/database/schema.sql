

create extension if not exists pg_trgm;

create table if not exists public.discovered_repos (
    id               uuid        primary key default gen_random_uuid(),
    tiktok_url       text        not null unique,
    author_name      text        not null default '',
    github_url       text        not null,
    repo_name        text        not null,
    owner            text        not null default '',
    primary_language text,
    star_count       integer     not null default 0,
    fork_count       integer     not null default 0,
    repo_description text,
    topics           text[]      default '{}',
    homepage         text,
    ai_summary       text        not null default '',
    created_at       timestamptz not null default now(),
    updated_at       timestamptz not null default now()
);

create index if not exists idx_discovered_repos_github_url
    on public.discovered_repos (github_url);

create index if not exists idx_discovered_repos_star_count
    on public.discovered_repos (star_count desc);

create index if not exists idx_discovered_repos_repo_name_trgm
    on public.discovered_repos using gin (repo_name gin_trgm_ops);

create or replace function public.set_updated_at()
returns trigger language plpgsql as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

create or replace trigger trg_discovered_repos_updated_at
    before update on public.discovered_repos
    for each row execute function public.set_updated_at();

alter table public.discovered_repos enable row level security;

create policy "Public read access"
    on public.discovered_repos for select using (true);

create policy "Service role write access"
    on public.discovered_repos for all using (auth.role() = 'service_role');
