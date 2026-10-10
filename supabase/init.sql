-- Cubeville: profiles, nick lookup, account deletion and private realtime channels.
-- Run once in Supabase → SQL Editor. Safe to re-run.

create table if not exists public.profiles (
  id          uuid primary key references auth.users (id) on delete cascade,
  nick_a      smallint not null check (nick_a between 0 and 63),
  nick_b      smallint not null check (nick_b between 0 and 63),
  nick_n      smallint not null check (nick_n between 1 and 99),
  save        jsonb    not null default '{}'::jsonb check (pg_column_size(save) < 20000),
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now(),
  constraint profiles_nick_unique unique (nick_a, nick_b, nick_n)
);

alter table public.profiles enable row level security;

drop policy if exists "profiles: read own"   on public.profiles;
drop policy if exists "profiles: insert own" on public.profiles;
drop policy if exists "profiles: update own" on public.profiles;
create policy "profiles: read own"   on public.profiles for select to authenticated using (auth.uid() = id);
create policy "profiles: insert own" on public.profiles for insert to authenticated with check (auth.uid() = id);
create policy "profiles: update own" on public.profiles for update to authenticated using (auth.uid() = id) with check (auth.uid() = id);

-- Nick indices may not be changed after registration (the login is derived from them).
create or replace function public.profiles_lock_nick() returns trigger
language plpgsql as $$
begin
  if new.nick_a <> old.nick_a or new.nick_b <> old.nick_b or new.nick_n <> old.nick_n then
    raise exception 'nick is fixed';
  end if;
  new.updated_at := now();
  return new;
end $$;
drop trigger if exists profiles_lock_nick on public.profiles;
create trigger profiles_lock_nick before update on public.profiles
  for each row execute function public.profiles_lock_nick();

-- "Is this nick taken?" without exposing anyone's profile.
create or replace function public.nick_taken(a int, b int, n int) returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.profiles where nick_a = a and nick_b = b and nick_n = n);
$$;
revoke all on function public.nick_taken(int, int, int) from public;
grant execute on function public.nick_taken(int, int, int) to anon, authenticated;

-- A signed-in player (or parent with the device) can delete the account and everything in it.
create or replace function public.delete_my_account() returns void
language plpgsql security definer set search_path = public, auth as $$
begin
  if auth.uid() is null then raise exception 'not signed in'; end if;
  delete from auth.users where id = auth.uid();
end $$;
revoke all on function public.delete_my_account() from public;
grant execute on function public.delete_my_account() to authenticated;

-- Realtime: only signed-in players may join the world channel (private channels).
do $$
begin
  if exists (select 1 from pg_namespace where nspname = 'realtime')
     and exists (select 1 from information_schema.tables where table_schema = 'realtime' and table_name = 'messages') then
    execute 'drop policy if exists "cubeville: read world" on realtime.messages';
    execute 'drop policy if exists "cubeville: write world" on realtime.messages';
    execute $p$create policy "cubeville: read world" on realtime.messages for select to authenticated
             using (realtime.topic() = 'cv-world')$p$;
    execute $p$create policy "cubeville: write world" on realtime.messages for insert to authenticated
             with check (realtime.topic() = 'cv-world' and realtime.messages.extension in ('broadcast','presence'))$p$;
  end if;
end $$;
