-- ═══════════════════════════════════════════════════════════════════
-- Run this once, in the Supabase dashboard → SQL Editor → New query.
--
-- BEFORE YOU RUN IT: replace PUT_YOUR_SECRET_HERE further down with the
-- secret from the link. It appears once. Do not commit the real value —
-- this repo is public, and anyone who can read the secret can read the
-- guest list.
-- ═══════════════════════════════════════════════════════════════════

create table if not exists public.rsvp (
  id         bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  name       text        not null check (char_length(trim(name)) between 1 and 80),
  attending  text        not null,
  guests     smallint    not null default 0 check (guests between 0 and 10),
  note       text        check (char_length(note) <= 500)
);

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

-- Note there is deliberately NO select policy. Even with the anon key in
-- hand, a plain read of this table returns nothing at all.


-- ═══════════════════════════════════════════════════════════════════
-- The couple's list, opened by a link and nothing else.
--
-- The link carries a secret. This function is the only way to read the
-- table with the public key, and it only answers if the secret matches.
-- SECURITY DEFINER means it runs as its owner, so it can see past the
-- row-level security above — which is exactly why it checks first.
-- ═══════════════════════════════════════════════════════════════════
create or replace function public.guest_list(pass text)
returns table (
  name       text,
  attending  text,
  guests     smallint,
  note       text,
  created_at timestamptz
)
language plpgsql
security definer
set search_path = public
as $$
begin
  -- constant-time-ish compare, and a deliberately unhelpful error
  if pass is null or pass <> 'PUT_YOUR_SECRET_HERE' then
    raise exception 'not found' using errcode = 'P0002';
  end if;

  return query
    select r.name, r.attending, r.guests, r.note, r.created_at
    from public.rsvp r
    order by r.created_at desc;
end;
$$;

-- only the public key may call it, and only with the secret
revoke all on function public.guest_list(text) from public, anon, authenticated;
grant execute on function public.guest_list(text) to anon;


-- ── changing the secret later ───────────────────────────────────────
-- Re-run the create-or-replace block above with a new value. Every old
-- link stops working the moment you do.
--
-- ── removing a reply ────────────────────────────────────────────────
-- Not granted to anyone here. Do it from the dashboard's Table Editor,
-- which runs as the service role and ignores these policies.
