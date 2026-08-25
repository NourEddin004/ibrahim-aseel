-- ═══════════════════════════════════════════════════════════════════
-- Adds "add a guest" and "remove a guest" to the couple's list.
--
-- Run this AFTER sql/setup.sql, in the SQL Editor.
-- Replace PUT_YOUR_SECRET_HERE (3 times) with the same secret as before.
--
-- Nothing here loosens the table. The public key still cannot touch it
-- directly — every one of these runs as its owner and refuses to do
-- anything until the secret matches, exactly like guest_list already did.
-- ═══════════════════════════════════════════════════════════════════

-- ── the list, now with an id ────────────────────────────────────────
-- A row cannot be deleted without something to name it by. Postgres will
-- not let a function change its return type in place, so this is a drop
-- and a re-create — which loses the grant, hence the re-grant below.
drop function if exists public.guest_list(text);

create function public.guest_list(pass text)
returns table (
  id         bigint,
  name       text,
  attending  text,
  guests     smallint,
  note       text,
  created_at timestamptz
)
language plpgsql security definer set search_path = public
as $$
begin
  if pass is null or pass <> 'PUT_YOUR_SECRET_HERE' then
    raise exception 'not found' using errcode = 'P0002';
  end if;
  return query
    select r.id, r.name, r.attending, r.guests, r.note, r.created_at
    from public.rsvp r
    order by r.created_at desc;
end;
$$;

revoke all on function public.guest_list(text) from public, anon, authenticated;
grant execute on function public.guest_list(text) to anon;


-- ── add a guest by hand ─────────────────────────────────────────────
-- For the relative who replies by phone instead of through the card.
-- The same CHECK constraints on the table apply, so a blank name or a
-- silly headcount is refused here exactly as it is from the invitation.
create or replace function public.guest_add(
  pass text, p_name text, p_attending text, p_guests smallint, p_note text
)
returns bigint
language plpgsql security definer set search_path = public
as $$
declare new_id bigint;
begin
  if pass is null or pass <> 'PUT_YOUR_SECRET_HERE' then
    raise exception 'not found' using errcode = 'P0002';
  end if;
  insert into public.rsvp (name, attending, guests, note)
  values (trim(p_name), p_attending, coalesce(p_guests, 0), nullif(trim(p_note), ''))
  returning id into new_id;
  return new_id;
end;
$$;

revoke all on function public.guest_add(text, text, text, smallint, text)
  from public, anon, authenticated;
grant execute on function public.guest_add(text, text, text, smallint, text) to anon;


-- ── remove one ──────────────────────────────────────────────────────
-- By id only. There is deliberately no "delete everything" here: the
-- worst a slip can do is cost one row.
create or replace function public.guest_remove(pass text, p_id bigint)
returns integer
language plpgsql security definer set search_path = public
as $$
declare n integer;
begin
  if pass is null or pass <> 'PUT_YOUR_SECRET_HERE' then
    raise exception 'not found' using errcode = 'P0002';
  end if;
  delete from public.rsvp where id = p_id;
  get diagnostics n = row_count;
  return n;
end;
$$;

revoke all on function public.guest_remove(text, bigint) from public, anon, authenticated;
grant execute on function public.guest_remove(text, bigint) to anon;
