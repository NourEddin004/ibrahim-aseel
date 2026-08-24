-- ═══════════════════════════════════════════════════════════════════
-- Run this once, in the Supabase dashboard → SQL Editor → New query.
-- It makes the table the invitation writes to and locks it down so the
-- public key can only ever add a reply.
-- ═══════════════════════════════════════════════════════════════════

create table if not exists public.rsvp (
  id         bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  name       text        not null check (char_length(trim(name)) between 1 and 80),
  attending  text        not null,
  guests     smallint    not null default 0 check (guests between 0 and 10),
  note       text        check (char_length(note) <= 500)
);

-- Newest first is how the list is read, so index it that way.
create index if not exists rsvp_created_at_idx on public.rsvp (created_at desc);

-- Nothing is allowed until a policy says so.
alter table public.rsvp enable row level security;

-- ── the guests ──────────────────────────────────────────────────────
-- The anon key ships inside the invitation, so anyone can find it. This
-- is the only thing it may do: add one row. It cannot read the list back,
-- cannot change a reply and cannot delete one.
drop policy if exists "a guest may reply" on public.rsvp;
create policy "a guest may reply"
  on public.rsvp for insert
  to anon
  with check (true);

-- ── the couple ──────────────────────────────────────────────────────
-- Reading the list requires being signed in. Create that account under
-- Authentication → Users → Add user (email + password, and tick
-- "Auto Confirm User" so there is no confirmation mail to chase).
drop policy if exists "the couple may read" on public.rsvp;
create policy "the couple may read"
  on public.rsvp for select
  to authenticated
  using (true);

-- Deleting a reply is deliberately not granted to anyone here. If you
-- ever need to remove a row, do it from the dashboard's Table Editor —
-- that runs as the service role and ignores these policies.
