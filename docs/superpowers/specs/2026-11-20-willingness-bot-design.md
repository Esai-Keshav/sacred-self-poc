# Willingness Bot: Design Spec

Date: 2026-11-20
Status: Draft for review. Internal testing only.

## 1. Purpose

Replace the four-perspective app with one perspective: **Willingness**. A user writes a thought. The bot returns a card that:

- appreciates and encourages the user,
- builds belief that they are capable,
- shifts focus to the process (what they can do and learn), not the outcome,
- gives one small practice and one spoken line that boosts their thinking frequency.

The app is for internal testing. History is shared. Every card and its feedback is visible to all testers.

## 2. Scope

In scope:
- One text input. One card per submission.
- Card face: hook. Expanded section: body, practise, say-it.
- Feedback on the whole card and on each section.
- Shared history feed, newest first.
- Storage in Supabase.

Out of scope:
- Login, user accounts, per-user history.
- Practise tracking, reminders, or deadline countdowns.
- Public launch hardening (see section 10).
- Any v1/v2 four-perspective output. Those are removed.

## 3. Decisions

| Topic | Decision |
|---|---|
| Perspectives | Willingness only. Reasoning, Loving Heart, Still Witness removed. |
| Old versions | v1 and v2 removed. SQLite removed. |
| Users | None. Anonymous. One shared history. |
| Feedback | Overall thumbs up/down with optional comment, plus a thumbs rating per section (hook, expanded, practise, say-it). |
| Practise | One sentence. Deadline written inside it by the model (e.g. "In 3 days, do ..."). Not tracked. Must be doable from the user's own words. |
| Say it | One first-person line the user says aloud, in their own voice, tied to their situation. |
| Storage | Supabase (Postgres). |

## 4. Output: the card

One structured model call returns a `WillingnessCard`. Out-of-scope messages return the existing `Fallback` output instead.

| Field | Rule |
|---|---|
| `hook` | 25–30 words. A short pull that makes the user open the card. Shown on the card face. |
| `expanded` | About 80–120 words. Appreciates one specific thing the user did or endured. Builds belief in their capability. Focuses on process: what to try, what to learn. |
| `practise` | One sentence. Includes a deadline (e.g. "In 3 days", "By tonight"). Doable from what the user wrote. Not a generic task. |
| `say_it` | One first-person sentence, written in the user's voice, specific to their situation. Quoted in the UI. |

Rules for all fields:
- Use only details the user wrote. Do not invent facts, people, or motives.
- No generic reassurance ("Everything will be okay", "Stay positive").
- No guaranteed outcomes.
- No moralising. No guilt.
- Keep the user's expressed feelings. Do not dismiss pain.

Validation:
- `hook` word count is checked by a Pydantic AI output validator. Outside 25–30 words raises `ModelRetry`, so the model retries.
- Other fields are not counted. They are checked by the prompt only.

Dropped from earlier design: `key_facts`. It was a hidden scratch field. It is removed to keep the card short. Add it back only if testing shows invented details.

## 5. Bot role and responsibility

The system prompt defines the bot's role:

- **Role:** a willingness coach. It helps a person see what they can learn, improve, or contribute, and encourages them to take one small step.
- **Responsibility:** every card is kind, grounded in the user's words, and safe. It never replaces professional or crisis help.

Safety rules override everything else:
- If the message shows danger, abuse, self-harm, or suicidal thoughts, the card puts safety and human support first. It does not use reframing or detachment. It never tells the user to tolerate abuse.
- Crisis messages are always in scope. They never get the fallback.

Scope rule:
- Personal situations, feelings, relationships, work, and life decisions are in scope.
- General knowledge, coding, news, trivia, writing or translation requests, and questions about the bot are out of scope. The bot returns the fallback message.

## 6. Application flow

1. User submits a thought in the chat input (`max_input_chars` applies).
2. Input is validated (empty, too long). Errors show `UserError` text.
3. One model call returns `WillingnessCard` or `Fallback`.
4. If a card: show it. Save it to `cards`.
5. If fallback: show `FALLBACK_MESSAGE`. Do not save.
6. Feedback can be given on the new card and any card in history.

Failure handling:
- Timeout: show `ERROR_TIMEOUT`.
- Save failure: still show the card, log the error. Do not hide the answer because saving failed.
- Feedback save failure: show a short error. Keep the user's typed comment in the widget.

## 7. UI

Single page (Streamlit). `detail.py` and `st.navigation` are removed.

Layout top to bottom:
1. Title and subtitle.
2. Chat input.
3. Latest card (if one was just generated).
4. Disclaimer caption.
5. Save notice: entries and feedback are visible to all users.
6. History: latest `HISTORY_LIMIT` cards, newest first.

Card:
- Bordered container.
- Shows `hook` on the face.
- `st.expander("Read more")` holds `expanded`, then **Practise** (`practise`), then **Say it** (`say_it`, quoted).
- Feedback area below the card.

Feedback area:
- Overall thumbs up/down (`st.feedback("thumbs")`) and an optional comment box with a submit button.
- Per-section thumbs for hook, expanded, practise, say-it.
- Shows existing feedback counts and comments for that card.

## 8. Data model (Supabase)

Table `cards`:

| Column | Type | Notes |
|---|---|---|
| id | bigint identity, PK | |
| created_at | timestamptz | default now() |
| thought | text | user input |
| model | text | `config.MODEL_NAME` |
| hook | text | |
| expanded | text | |
| practise | text | |
| say_it | text | |
| input_tokens | int | nullable |
| output_tokens | int | nullable |
| cost_usd | real | nullable |

Table `feedback`:

| Column | Type | Notes |
|---|---|---|
| id | bigint identity, PK | |
| card_id | bigint, FK to cards.id | on delete cascade |
| created_at | timestamptz | default now() |
| overall | smallint | -1 or 1, nullable |
| hook | smallint | -1 or 1, nullable |
| expanded | smallint | -1 or 1, nullable |
| practise | smallint | -1 or 1, nullable |
| say_it | smallint | -1 or 1, nullable |
| comment | text | nullable |

Row-level security:
- RLS enabled on both tables.
- Anon role: select and insert on both tables.
- No update or delete policies.
- Schema SQL lives in `supabase/schema.sql`. The user runs it in the Supabase SQL editor.

Each feedback submission is one row. Many users can rate one card.

## 9. Code layout (for the implementation plan)

- `prompts.py`: one Willingness system prompt (role, responsibility, safety, scope, content rules, field specs). Drops the four perspective prompts.
- `agent.py`: `WillingnessCard` model, `Fallback`, cached agent, `get_card(thought)`. Drops `FourPerspectives*`, the v2 agent, and the perspectives assert.
- `db.py`: Supabase client (anon key). `save_card`, `list_cards(limit)`, `save_feedback`, `list_feedback(card_ids)`. Drops SQLite and migrations.
- `ui.py`: `render_card`, `render_feedback`.
- `home.py`: input, latest card, history.
- `app.py`: single page. Remove `st.navigation`.
- `config.py`: remove v1/v2 flags and word ranges. Add hook word range, `HISTORY_LIMIT`, Supabase settings, UI strings. Update `SAVE_NOTICE`.
- `pyproject.toml`: add `supabase`.
- `.env.example`: add `SUPABASE_URL`, `SUPABASE_KEY`.
- `CLAUDE.md`: update architecture section.
- Delete: `prompts_v2.py`, `detail.py`.

## 10. Risks and open items

- **Public exposure.** Anon key with open insert and select policies lets anyone with the key read and write rows. Fine for internal testing. Not safe for public launch. Needs auth and tighter policies first.
- **Privacy.** Testers see each other's raw personal thoughts. The save notice states this. Confirm testers accept it.
- **Retention.** No delete path in the app. Rows persist until removed in Supabase.
- **Model cost and latency.** One call per thought. Hook retry adds cost when the word count is wrong.
- **Hook count.** Word counting is simple whitespace split. Hyphenated words count as one.

## 11. Testing

Automated (pytest):
- Hook validator accepts 25 and 30 words, rejects 24 and 31. Use Pydantic AI `TestModel`.
- Save helper maps a card to the row shape.

Manual:
1. Create the Supabase project, run `supabase/schema.sql`, set `.env`.
2. `uv run streamlit run app.py` with a real model.
3. Submit three thoughts: a relationship situation, a work situation, and a general-knowledge question.
4. Check: hook is 25–30 words, practise is one sentence with a deadline, say-it is first person, the general question returns the fallback and is not saved.
5. Give feedback on a card (overall and per section). Confirm the rows appear in Supabase and in the history.

Limits: the Supabase layer is verified by hand against a real project only. No automated test covers it.
