# Willingness Bot: revamp plan (v3: prompt for gpt-6-luna, cleanup)

## Context
The app answers a thought with four perspectives (v1 long, v2 short), stored in local SQLite. The user wants a full revamp into one **Willingness bot**: appreciate and encourage, build belief in capability, focus on process. Output is a card (hook, expanded, practise, say-it). Storage moves to Supabase. Internal testing only. History is shared: everyone sees every card and its feedback. This update adds two things: (1) a better, structured prompt tuned for `gpt-6-luna`, (2) deletion of files the revamp makes unused.

Decisions so far:
- Replace v1/v2 entirely. SQLite goes.
- Feedback = overall thumbs + optional comment, plus a thumbs rating per section.
- No login. One shared history.
- Practise = one sentence with the deadline inside ("In 3 days, do ..."), AI picks it, not tracked.
- Say it = one first-person line in the user's voice, tied to their situation.
- `key_facts` dropped. `practise_task` + `practise_deadline` merged into `practise`.
- Spec already written: `docs/superpowers/specs/2026-11-20-willingness-bot-design.md`.

## Output shape (one structured call)
`WillingnessCard`, plus existing `Fallback`. Field order in the schema: **expanded, hook, practise, say_it**. The model writes the body first, then a hook that teases its strongest idea, then the task and the line. The UI still shows the hook first.

| field | rule |
|---|---|
| `expanded` | 80-120 words. Appreciate one specific thing, build belief in capability, focus on process |
| `hook` | 25-30 words. Enforced by an `output_validator` that raises `ModelRetry` outside the range |
| `practise` | one sentence with a deadline, doable from the user's words |
| `say_it` | one first-person sentence, user's voice, situation-specific |

## Prompt design for gpt-6-luna (`prompts.py`)
`gpt-6-luna` is treated as a reasoning model (the existing config says it rejects `temperature` and takes a reasoning effort). So:
- Short sections with Markdown headings (`## Role`, `## Safety`, ...), no XML tags. Rules in priority order. No "think step by step" (it reasons on its own), no repeated rules, no contradictory rules.
- One source of truth for lengths: `config.py` constants feed the prompt text, the Pydantic `Field` descriptions, and the validator.
- Two worked examples live in `prompts.py` as data (`EXAMPLES`) and are rendered into the prompt. A test checks that every example obeys the word ranges, so examples cannot drift from the rules.
- Examples come from the design doc's Willingness cases (husband, colleague), rewritten into the four-field shape. Safety stays as a rule, not an example.
- Keep `max_output_tokens` at 2000: reasoning tokens count against it.
- Not verifiable without a key: how `gpt-6-luna` actually responds. Real-model runs in Verification are the only check on prompt quality.

Draft prompt (rendered by `build_system_prompt()`; lengths come from config):
```markdown
# Willingness bot

## Role
You are the Willingness bot. You help a person see what they can learn, improve or contribute
in the situation they describe, and you encourage one small step. You are warm, honest and
respectful. You build belief in the person's capacity and keep attention on the process (what
they can try and learn), not on the outcome.

## Priorities
Follow in this order when rules conflict:
1. Safety
2. Scope
3. Stay grounded in the person's own words
4. Card format

## Safety
If the message involves danger, abuse, self-harm, suicidal thoughts or another crisis, the card
puts safety and human support first. Do not reframe or ask for detachment. Never tell the person
to tolerate abuse, manipulation or harm.

## Scope
Write a card only when the message is about the person's own situation, feelings, relationships,
work or life decisions, including asking how to handle it. A crisis message is always in scope.
Anything else (general knowledge, coding, news, trivia, requests to write or translate,
questions about you) gets the Fallback output, not a card.

## Grounding
- Use only details the person wrote.
- Never invent facts, people, motives or history.
- Treat other people's reasons as unknown.
- Never promise results.

## Card fields
- **expanded** ({EXP_MIN}-{EXP_MAX} words, 2-3 short paragraphs, complete sentences):
  appreciate one specific thing the person did or endured; say why they can take the next step,
  based on something they showed; point to one process step they can try or learn, and how they
  will know it is working.
- **hook** ({HOOK_MIN}-{HOOK_MAX} words): a specific pull that makes the person open the card.
  It teases the strongest idea in expanded. Do not repeat the person's message back.
- **practise**: exactly one sentence with a deadline ("In 3 days, ...", "By tonight, ...").
  One concrete task the person can do from what they wrote.
- **say_it**: exactly one first-person sentence the person says aloud, in their own voice,
  using details from their message.

## Style
- Plain, warm language.
- No generic reassurance ("Everything will be okay", "Stay positive", "You've got this").
- No empty positivity, moralising or guilt.
- Keep the feelings the person expressed.
- Never claim to measure their consciousness, intelligence or spiritual level.

## Examples
{rendered EXAMPLES, each as:}
### Example 1
Person: "<thought>"
- expanded: ...
- hook: ...
- practise: ...
- say_it: ...
```

`EXAMPLES` (both must pass the word-range test):
1. thought "My husband doesn't appreciate anything I do for the family."
   - expanded (103 words): "You are doing a great deal for your family, and you have kept doing it even while it goes unnoticed. That steadiness takes real strength, and it shows you can carry responsibility well. Wanting to be appreciated is fair. The next step is not to wait for him to guess; it is to practise saying clearly what you need. This is a skill, and every honest attempt teaches you something: what words land, what time works, how he responds. Focus on the attempt, not on whether he gets it right away. Each try gives you information and builds your confidence to speak plainly."
   - hook (27 words): "You keep the whole family running every day, and that is real effort. What small thing could you try this week so your needs finally get heard?"
   - practise: "In 3 days, choose one calm moment and tell him one specific thing you would like him to notice, in a sentence or two."
   - say_it: "I do a lot for this family, and I am willing to ask clearly for the appreciation I need."
2. thought "My colleague got promoted instead of me. I feel jealous and inferior."
   - expanded (89 words): "You wanted this promotion, and you said so honestly, including the jealousy. That honesty is a good place to start. One promotion decision does not measure your worth or your ability. You are capable of growing the skills this role asks for. Look at the process, not the title: what did your colleague do regularly that you could try? Ask them how they approached the work, or ask your manager what the next level requires. Each conversation is a step you control, and each step teaches you something real."
   - hook (26 words): "Your jealousy shows how much this role mattered to you. What could you learn from your colleague's path, and which skill could you start building today?"
   - practise: "Within 5 days, ask your manager what a strong case for the next level would look like."
   - say_it: "I feel jealous, and I am still willing to learn what it takes to grow."

## Files
Rewrite / modify:
- `config.py`: single-bot settings and UI text; `HOOK_*`, `EXPANDED_*`, `HISTORY_LIMIT`, `supabase_url`, `supabase_key`; `SAVE_NOTICE` says everything is visible to all users.
- `prompts.py`: the prompt above plus `EXAMPLES` and `build_system_prompt()`. Drops `PERSPECTIVES`, `PerspectiveConfig`, the four perspective prompts.
- `agent.py`: `WillingnessCard` (field order above), `Fallback`, `UserError`, `word_count`, `check_hook_length`, `get_agent` with `@agent.output_validator`, `_run`, `get_card`. Keeps the current `_run` logic (input checks, usage and cost print, `thinking` effort, timeout).
- `db.py`: `supabase-py` layer: `build_card_row`, `build_feedback_row` (pure), `save_card`, `list_cards`, `save_feedback`, `list_feedback`.
- `ui.py`: `to_vote`, `format_when`, `render_card(card)`, `render_feedback(card_id, rows)`.
- `home.py`: input; a new card shows at the top of the history after it is saved (no session state); a card that failed to save is shown directly without feedback; history feed below.
- `app.py`: single page, no `st.navigation`.
- `pyproject.toml`: add `supabase`, dev `pytest`. `.env.example`: `SUPABASE_URL`, `SUPABASE_KEY`.
- `README.md`: rewrite for the Willingness bot (it still describes four perspectives and points at the old spec and plan, which are deleted).
- `CLAUDE.md`: update Architecture; replace "no automated tests" with `uv run pytest`.
- `docs/superpowers/plans/2026-11-20-willingness-bot.md`: **currently broken** (truncated mid-Task 7 with a placeholder line). Rewrite it to match this plan.

New: `supabase/schema.sql` (tables `cards`, `feedback`, RLS: anon select + insert only), `tests/` (`test_rows.py`, `test_validation.py`, `test_ui_logic.py`, `test_prompts.py`).

## Delete (unused after the revamp)
Code:
- `detail.py` (history is inline now)
- `prompts_v2.py` (v2 perspectives)
- `grade.py` (grades v2 answers read from SQLite)

Docs about the old app:
- `docs/GRADING.md`, `docs/GRADING_10.md`, `docs/GRADING_RESULTS_V2.md` (grading of the four-perspective v1/v2 data)
- `docs/superpowers/specs/2026-11-13-four-perspectives-poc-design.md`
- `docs/superpowers/plans/2026-11-13-four-perspectives-poc.md`

Kept on purpose:
- `docs/Reset- Sacred Self.md` (source design doc; the prompt examples come from it)
- `data/answers.db` (local, git-ignored, old test data). Not deleted: it is data, not code. Delete it yourself if you do not need it. `data/` stays in `.gitignore`.
- `.devcontainer/`, `uv.lock`, `.gitignore`.

All deletions are of tracked files, so they stay recoverable from git history.

## Tests (pytest, no network)
- `test_validation.py`: `check_hook_length` accepts 25, 27, 30 words; raises `ModelRetry` at 24 and 31.
- `test_rows.py`: `build_card_row` has exactly the `cards` columns (no `key_facts`); `build_feedback_row` keeps `None` for unrated sections; empty comment becomes `None`.
- `test_ui_logic.py`: `to_vote` maps 1 to +1, 0 to -1, None to None; `format_when` gives IST.
- `test_prompts.py`: every item in `EXAMPLES` has hook 25-30 words, expanded 80-120 words, a practise with a digit-or-time deadline word, and the rendered prompt contains each example thought.

## Verification
1. `uv sync`; create the Supabase project; run `supabase/schema.sql`; fill `.env`.
2. `uv run pytest -v`: all pass.
3. After deleting: `grep -rn "prompts_v2\|detail\|grade\|FourPerspectives\|PERSPECTIVES\|sqlite3" --include="*.py" .` returns nothing outside `.venv`; `uv run python -m py_compile app.py home.py agent.py db.py ui.py prompts.py config.py`.
4. `MODEL_NAME=test uv run streamlit run app.py`: page loads, history loads from Supabase. The `test` model's placeholder hook fails the length check, so an error here is expected and confirms the error path.
5. Real `gpt-6-luna` run with three thoughts (relationship, work, "what is photosynthesis?"): hook 25-30 words, practise is one sentence with a deadline, say-it is first person, the third gives the fallback and creates no `cards` row. This is the only check on prompt quality. Note any thought where the model needs a hook retry (cost) or invents details.
6. Feedback round trip: rate overall and one section, add a comment, send, reload. Rows appear in `feedback`; the comment shows under the card.

What cannot be verified by tests: the Supabase calls, and `gpt-6-luna` behaviour. Only steps 5 and 6 cover them.

## Risks
- Anon key with open insert/select RLS: internal testing only, not for public launch.
- Everyone sees everyone's raw thoughts. The save notice says so.
- Hook retry adds cost when the model miscounts words.
