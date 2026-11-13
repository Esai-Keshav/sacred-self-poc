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

Open the URL Streamlit prints, type a situation, and press Enter to send (Shift+Enter adds a new line). Each answer appears in its own box; the box height is `ANSWER_BOX_HEIGHT` in `config.py`.

## Dry run without an API key

```bash
MODEL_NAME=test uv run streamlit run app.py
```

This uses Pydantic AI's built-in test model. It returns placeholder text, so it only shows that the app and the four columns work.

## Reasoning effort

`REASONING_EFFORT` in `config.py` is `"low"`. Set it to `"minimal"`, `"medium"` or `"high"`, or to `None` to leave it out. Models that don't reason ignore it.

## Saved data

Each request is stored in a local SQLite file, `data/answers.db` (git-ignored), in the `requests` table: time, model, the user's text (`situation`), one column per answer (`willingness`, `reasoning`, `loving_heart`, `still_witness`), `key_facts` (the model's notes on the question), input and output tokens, and the estimated cost (empty when the model has no price data). The app tells users their message is saved.

```bash
sqlite3 data/answers.db "select id, created_at, situation, willingness, cost_usd from requests"
```

Databases from an earlier version, which kept all answers as JSON in one `answers` column, are converted to these columns automatically on the next save.

## Scope

The app answers messages about the user's own situation, feelings, relationships, work or life decisions, including asking how to handle them. Crisis messages are always answered, safety first. Anything else (general knowledge or facts, coding, news, trivia, requests to write or translate, questions about the AI) gets the fallback: the model returns `FALLBACK` and the app shows "I can't help with it." (`FALLBACK_MESSAGE` in `config.py`). The scope rules are in `prompts.py`.

Fallback requests are saved too, with empty answer columns, and show "Out of scope" in History. The model decides scope, so borderline messages can be classified wrongly.

## History

Below the main page, a scrollable list shows every saved question, newest first. Click one to open it on its own page with the question, date, model and all four answers, plus the copy box. Use "← Back" to return. Reloading the browser on the detail page loses the selection and shows a "not found" message with the way back.

## Copying a result

Open a request from the History list. The detail page has a "Copy question and answers" box with the question and all four answers as plain text. Use its copy button to paste them elsewhere.

The file holds personal text, so keep it private. Streamlit Community Cloud wipes local files on restart, so use an external database there.

## Tests

There are no automated tests yet.

## Project layout

| File | Purpose |
|---|---|
| `app.py` | Streamlit entry point: page setup and navigation |
| `home.py` | Main page: question form, answers, history list |
| `detail.py` | One saved request: question and answers |
| `ui.py` | Shared rendering: four columns and the copy box |
| `agent.py` | Output models, Pydantic AI agent and `get_perspectives()` |
| `db.py` | SQLite: save, list and read requests |
| `config.py` | Settings and all hardcoded non-prompt values |
| `prompts.py` | All prompt text and perspective metadata |

## Editing prompts

All prompt text is in `prompts.py`. Edit the perspective sections there. The design doc forbids naming the author of the original consciousness map in the app, so keep that name out of prompts and UI text.

## Design and plan

- Spec: `docs/superpowers/specs/2026-11-13-four-perspectives-poc-design.md`
- Plan: `docs/superpowers/plans/2026-11-13-four-perspectives-poc.md`
