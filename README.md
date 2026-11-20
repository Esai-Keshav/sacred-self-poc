# Sacred Self POC

You share a thought, and the Willingness bot returns one card: a hook, an expanded body, a practise task with a deadline, and a line to say aloud. Cards and feedback are stored in Supabase and shown to all users (internal testing).

## Requirements

- [uv](https://docs.astral.sh/uv/)
- A [Supabase](https://supabase.com) project
- An API key for the model provider used by `MODEL_NAME` in `config.py` (a [Pydantic AI](https://ai.pydantic.dev/models/) model string, `provider:model`)

## Setup

```bash
uv sync
cp .env.example .env
```

Edit `.env` and set `SUPABASE_URL`, `SUPABASE_KEY` (the anon key) and the API key for your provider.

## Database

Run `supabase/schema.sql` once in the Supabase SQL editor. It creates the `cards` and `feedback` tables and their row-level security policies.

## Run

```bash
uv run streamlit run app.py
```

## Tests

```bash
uv run pytest
```

## Dry run without a model key

```bash
MODEL_NAME=test uv run streamlit run app.py
```

This uses Pydantic AI's test model, which returns placeholder text. The card fails the hook length check, so an error message is expected. This confirms the app and the error path run.
