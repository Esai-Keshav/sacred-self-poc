# Sacred Self POC

A Streamlit proof of concept. You describe a situation or issue, and one AI call returns four answers side by side, one for each perspective: Willingness, Reasoning Mind, Loving Heart and Still Witness. The perspectives are defined in `docs/Reset- Sacred Self.md`.

## Requirements

- [uv](https://docs.astral.sh/uv/)
- An API key for a model provider supported by [Pydantic AI](https://ai.pydantic.dev/models/)

## Setup

```bash
uv sync
cp .env.example .env
```

Edit `.env` and set:

- `MODEL_NAME`: a Pydantic AI model string in the form `provider:model`.
- The API key variable for that provider (for example `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`).

The provider is your choice. Without `MODEL_NAME` the app starts, but submitting a situation shows a setup message.

## Run

```bash
uv run streamlit run app.py
```

Open the URL Streamlit prints, type a situation, and press the button.

## Dry run without an API key

```bash
MODEL_NAME=test uv run streamlit run app.py
```

This uses Pydantic AI's built-in test model. It returns placeholder text, so it only shows that the app and the four columns work.

## Tests

There are no automated tests yet.

## Project layout

| File | Purpose |
|---|---|
| `app.py` | Streamlit UI |
| `agent.py` | Output models, Pydantic AI agent and `get_perspectives()` |
| `config.py` | Settings and all hardcoded non-prompt values |
| `prompts.py` | All prompt text and perspective metadata |

## Editing prompts

All prompt text is in `prompts.py`. Edit the perspective sections there. The design doc forbids naming the author of the original consciousness map in the app, so keep that name out of prompts and UI text.

## Design and plan

- Spec: `docs/superpowers/specs/2026-11-13-four-perspectives-poc-design.md`
- Plan: `docs/superpowers/plans/2026-11-13-four-perspectives-poc.md`
