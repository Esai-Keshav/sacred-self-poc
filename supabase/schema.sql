create table cards (
  id bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  thought text not null,
  model text not null,
  hook text not null,
  expanded text not null,
  practise text not null,
  say_it text not null,
  input_tokens int,
  output_tokens int,
  cost_usd real
);

create table feedback (
  id bigint generated always as identity primary key,
  card_id bigint not null references cards(id) on delete cascade,
  created_at timestamptz not null default now(),
  overall smallint check (overall in (-1, 1)),
  hook smallint check (hook in (-1, 1)),
  expanded smallint check (expanded in (-1, 1)),
  practise smallint check (practise in (-1, 1)),
  say_it smallint check (say_it in (-1, 1)),
  comment text
);

alter table cards enable row level security;

alter table feedback enable row level security;

create policy "anyone can read cards" on cards
  for select to anon using (true);

create policy "anyone can add cards" on cards
  for insert to anon with check (true);

create policy "anyone can read feedback" on feedback
  for select to anon using (true);

create policy "anyone can add feedback" on feedback
  for insert to anon with check (true);
