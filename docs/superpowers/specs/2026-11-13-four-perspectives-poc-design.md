# Sacred Self POC: Four Perspectives Streamlit App

Date: 2026-11-13
Source material: `docs/Reset- Sacred Self.md`

## Goal

A Streamlit proof of concept. The user types a situation or issue. One AI call returns four answers, one per consciousness perspective, shown side by side.

## Decisions

| Topic | Decision |
|---|---|
| LLM framework | Pydantic AI. LangChain is dropped. |
| Call design | One structured call returns all four answers. |
| UI | Four columns side by side (`st.columns(4)`). Text box and one submit button only. |
| Provider | Not decided. The model string comes from the environment. `.env.example` holds a placeholder. |
| Perspective 1 prompt | Drafted from its principles. The doc has no Response Structure or Communication Style for it. The user reviews the draft. |
| Package manager | `uv` |
| Config | All configuration and hardcoded non-prompt values live in `config.py`. All prompt text lives in `prompts.py`. |
| Models | Pydantic for settings and output schemas. |
| Tests | None for now. One import-time `assert` guards the perspective keys. Manual checks below. |

## Out of scope

Automated tests, example buttons, chat history, streaming, auth, database, per-perspective regeneration, evaluation harness.

## Files

```
pyproject.toml    uv project and dependencies
.env.example      MODEL_NAME placeholder, provider API key placeholders
config.py         Settings and all hardcoded non-prompt values
prompts.py        All prompt text and perspective metadata
agent.py          Output models, Pydantic AI agent, get_perspectives()
app.py            Streamlit UI only
README.md         Setup and run instructions
```

## Components

### config.py

- `Settings` (pydantic-settings, reads `.env`, ignores unknown variables such as API keys): `model_name` (Pydantic AI `provider:model` string, default empty), `max_input_chars`, `temperature`, `max_output_tokens`.
- `load_dotenv()` runs at import so `.env` values, including provider API keys, reach the process environment where Pydantic AI reads them.
- Module-level `settings = Settings()`. No field is required, so importing `config` never needs a key or a model.
- Word-count bounds (`MIN_WORDS`, `MAX_WORDS`), UI strings, disclaimer, and error messages live here. No prompt text lives here.

### prompts.py

- `PerspectiveConfig` (Pydantic): key, title, tagline, prompt section.
- `PERSPECTIVES`: ordered list of `PerspectiveConfig`. The column order follows this list.
- `BASE_SYSTEM_PROMPT`: shared rules taken from the doc:
  - No generic reassurance such as "Everything will be okay."
  - Do not invent facts, motives, or diagnoses.
  - When danger, abuse, or crisis is present, safety and support come before reframing.
  - Never claim to measure consciousness or spiritual frequency.
  - Never use Hawkins's name.
- `build_system_prompt()` joins the base prompt and the four sections.
- Each perspective section is condensed from the doc: worldview, response structure, what to avoid. The target length for every answer is 80-180 words, taken from the Still Witness rule, so the columns stay balanced.

### agent.py

- `PerspectiveAnswer` (`response: str`) and `FourPerspectives` (fields `willingness`, `reasoning`, `loving_heart`, `still_witness`, each a `PerspectiveAnswer`).
- Import-time `assert` that the `PERSPECTIVES` keys equal the `FourPerspectives` field names, in order.
- `UserError(Exception)`: raised for empty input, input over `max_input_chars`, or an empty `MODEL_NAME`. The message comes from `config.py`.
- `get_agent()`: builds the `Agent` once (`lru_cache`) with `output_type=FourPerspectives` and `system_prompt=build_system_prompt()`. Building is lazy so that importing never needs a key.
- `get_perspectives(situation) -> FourPerspectives`: checks input, calls the agent synchronously.

### app.py

- Title, text area, submit button, spinner.
- Result: four columns, each with the perspective title, tagline, and response.
- `UserError` shows as a warning. Any other error is logged and shows the generic message from `config.py`.

## Data flow

User text, then input check, then `get_perspectives`, then the model returns `FourPerspectives` validated by Pydantic, then `app.py` renders one column per `PERSPECTIVES` entry.

## Error handling

- Empty or oversize input: warning with the config message, no model call.
- Missing `MODEL_NAME`: warning with the setup message at call time.
- Model or schema validation failure: generic retry message. The detail goes to the log.

## Verification (manual, no automated tests)

- Dry run without a key: set `MODEL_NAME=test` (Pydantic AI's built-in test model) and run the app. Confirm four columns render.
- With a real key: submit the four example problems from the doc (husband appreciation, colleague promotion, child mistakes, betrayal). Confirm four distinct answers of about 80-180 words.
- Submit a crisis-style input. Confirm every answer puts safety first.
- Submit empty and oversize input. Confirm the warnings.
- Live model calls need a real key. If none is set, report them as unverified.

## Open items

- Provider and model: the user decides later.
- After implementation, update `CLAUDE.md` with the real run commands.
- Next step after the POC runs on a real key: compare the output with the doc's example table to judge quality.
