# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Install: `uv sync`
- Run: `uv run streamlit run app.py` (needs `.env` copied from `.env.example`)
- Dry run without a key: `MODEL_NAME=test uv run streamlit run app.py`
- Tests: `uv run pytest`

## Architecture

`agent.py` `get_cards` runs one structured Pydantic AI call per perspective in `config.PERSPECTIVES` (Willingness, Love & Joy) in parallel. Each returns a `Card` or a `Fallback`. `Card` fields are `expanded`, `hook`, `practise`, in that order. The hook word range is checked by an output validator that raises `ModelRetry`. Prompt text is in `prompt/` as Markdown: `language_common.md` (safety, scope, grounding, identity and card rules shared by every perspective), `willingness.md` and `love_joy.md` (one perspective each) and `language_v1.md`, `language_v2.md` or `language_v4.md` (the voice guide). `config.PROMPT_VERSION` picks the voice guide, which with the examples applies to Willingness only; `prompts.py` builds the system prompt. `db.py` is the Supabase layer (pure row builders plus client calls). `ui.py` renders cards and feedback. `home.py` is the single page, and `app.py` runs it. `config.py` holds all settings and UI text. `supabase/schema.sql` defines the tables and RLS.

## Workflow

1. **Graph first.** If `graphify-out/graph.json` exists, run `graphify query "<question>"` before grep or file reads. No graph exists yet.
2. **Clarify.** Ask the user (AskUserQuestion) when intent, approach, or scope is ambiguous. Do not pick silently.
3. **Plan before code.** Do not run scripts while planning. Prefer the smallest change that fixes the root cause.
4. **Skills.** Use `ponytail`, `graphify`, and `brainstorming`. For bugs, find the root cause before fixing.
5. **Features are spec-driven.** `brainstorming` writes the design to `docs/superpowers/specs/`. `writing-plans` writes the plan to `docs/superpowers/plans/`.
6. **Implement small.** Readable, modular code. Update tests with the change.
7. **Verify.** Run the affected tests, then the full suite. State plainly what could not be verified.

## Constraints

Internal testing only. Anon Supabase key with open insert and select policies: not for public launch.

## Behavior guidelines

- **Think before coding.** State assumptions. Present multiple interpretations when they exist. Say so when a simpler approach exists. Stop and ask when unclear.
- **Simplicity first.** Write the minimum code that solves the problem. No unrequested features, abstractions, or configurability. No error handling for impossible scenarios.
- **Surgical changes.** Every changed line traces to the request. Match existing style. Do not refactor what is not broken. Mention unrelated dead code but do not delete it. Remove only the imports, variables, and functions your change made unused.
- **Goal-driven execution.** Turn tasks into verifiable goals. For a bug, write a test that reproduces it first. For multi-step work, state a short plan: `1. [step] → verify: [check]`.
