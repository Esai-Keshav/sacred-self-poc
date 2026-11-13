# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

- Install: `uv sync`
- Run: `uv run streamlit run app.py` (needs `.env` copied from `.env.example`)
- Dry run without a key: `MODEL_NAME=test uv run streamlit run app.py`
- There are no automated tests yet. No git history.

## Architecture

One structured Pydantic AI call returns all four perspective answers. `app.py` (UI) calls `agent.get_perspectives()`, which validates input, builds the agent lazily from `config.settings.model_name`, and returns a `FourPerspectives`. All prompt text is in `prompts.py`. All other config and hardcoded strings are in `config.py`. `PERSPECTIVES` in `prompts.py` fixes column order, and an import-time `assert` in `agent.py` requires its keys to equal the `FourPerspectives` field names.

The source design is `docs/Reset- Sacred Self.md`, a ~1000-line product and prompt-design document. Spec and plan are in `docs/superpowers/`.

## What the design doc defines

The app responds to a user's life problem through four "consciousness perspectives". Each perspective is meant to become a distinct AI persona or system prompt:

1. **Willingness**: asks what the user can learn, improve or contribute.
2. **The Reasoning Mind**: asks for evidence and separates facts from interpretation.
3. **The Loving Heart**: responds with compassion, without excusing harm.
4. **The Still Witness**: asks the user to observe thoughts and emotions without identifying with them.

The doc opens with an example table: each row is one user problem, answered once per perspective. The doc requires four things for every perspective:

- Worldview
- Thinking pattern (the questions it naturally asks)
- Response pattern (responses to 20-30 real-life problems)
- Transformation (the insight the user should ideally reach)

Perspectives 2-4 each have the same sections: Core Identity, Worldview, Characteristics, Communication Style, Response Structure, What You Must Avoid, Desired Transformation, and worked examples. Perspective 1 is less complete, ending with a "Next step" section. Treat these sections as the source material for persona prompts and evaluation examples. Keep new perspective material in the same structure.

## Constraints from the doc

- The perspectives are modelled on the Hawkins Map of Consciousness. Do not use Hawkins's name anywhere in the app, and do not reuse the original map directly. The doc requires an original expression of the principles and a licensing review for any direct reuse.
- Responses must not be generic reassurance such as "Everything will be okay. Stay positive." The doc's examples show guiding questions grounded in the user's specific situation.

## Workflow

1. **Graph first.** If `graphify-out/graph.json` exists, run `graphify query "<question>"` before grep or file reads. No graph exists yet.
2. **Clarify.** Ask the user (AskUserQuestion) when intent, approach, or scope is ambiguous. Do not pick silently.
3. **Plan before code.** Do not run scripts while planning. Prefer the smallest change that fixes the root cause.
4. **Skills.** Use `ponytail`, `graphify`, and `brainstorming`. For bugs, find the root cause before fixing.
5. **Features are spec-driven.** `brainstorming` writes the design to `docs/superpowers/specs/`. `writing-plans` writes the plan to `docs/superpowers/plans/`.
6. **Implement small.** Readable, modular code. Update tests with the change.
7. **Verify.** Run the affected tests, then the full suite. State plainly what could not be verified.

## Behavior guidelines

- **Think before coding.** State assumptions. Present multiple interpretations when they exist. Say so when a simpler approach exists. Stop and ask when unclear.
- **Simplicity first.** Write the minimum code that solves the problem. No unrequested features, abstractions, or configurability. No error handling for impossible scenarios.
- **Surgical changes.** Every changed line traces to the request. Match existing style. Do not refactor what is not broken. Mention unrelated dead code but do not delete it. Remove only the imports, variables, and functions your change made unused.
- **Goal-driven execution.** Turn tasks into verifiable goals. For a bug, write a test that reproduces it first. For multi-step work, state a short plan: `1. [step] → verify: [check]`.
