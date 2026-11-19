-- À exécuter une fois dans Supabase > SQL Editor
create table public.docs (
  user_id uuid not null default auth.uid() references auth.users(id) on delete cascade,
  id text not null,
  data jsonb not null,
  updated_at timestamptz not null default now(),
  primary key (user_id, id)
);
alter table public.docs enable row level security;
create policy "chacun ses données" on public.docs
  for all to authenticated
  using (user_id = auth.uid())
  with check (user_id = auth.uid());
alter publication supabase_realtime add table public.docs;
