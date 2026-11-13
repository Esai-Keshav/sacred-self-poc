# Four Perspectives POC Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A Streamlit app where the user enters a situation and one structured AI call returns four perspective answers in four columns.

**Architecture:** `prompts.py` holds all prompt text. `config.py` holds settings and all other hardcoded values. `agent.py` defines the Pydantic output models and a lazily built Pydantic AI agent, and exposes `get_perspectives()`. `app.py` renders the UI only.

**Tech Stack:** Python, uv, Streamlit, Pydantic AI (`pydantic-ai`), pydantic-settings.

## Global Constraints

- Install and run with `uv` only.
- All configuration and hardcoded non-prompt values live in `config.py`.
- All prompt text lives in `prompts.py`. No prompt text anywhere else.
- Pydantic for settings and output schemas.
- Framework is Pydantic AI. Do not use LangChain.
- One structured call returns all four answers.
- UI shows four columns side by side (`st.columns`). Text box and one submit button only.
- Provider is undecided. The model string comes from env `MODEL_NAME` (`provider:model`). Importing any module must not require a key or a model.
- Each answer is 80-180 words.
- The name "Hawkins" must not appear in any prompt or UI text.
- No automated tests for now. Verify with the commands in each task.
- The repo is not a git repository, so commit steps are omitted. Run `git init` first if you want commits.
- Run all commands from the repo root `/home/esai/Desktop/cyces/sacred_self_poc`.

---

### Task 1: Scaffold project

**Files:**
- Create: `pyproject.toml` (by `uv init`), `.env.example`, `.gitignore`

- [ ] **Step 1: Initialise the uv project and add dependencies**

```bash
uv init --bare
uv add pydantic-ai pydantic-settings streamlit
```

- [ ] **Step 2: Create `.env.example`**

```
# Pydantic AI model string, "provider:model". Choose your provider.
# Examples: anthropic:claude-sonnet-5-5   openai:<model>   google-gla:<model>
MODEL_NAME=

# Set the API key variable that matches your provider.
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
GOOGLE_API_KEY=
```

- [ ] **Step 3: Create `.gitignore`**

```
.env
.venv/
__pycache__/
```

- [ ] **Step 4: Verify**

Run: `uv run python -c "import pydantic_ai, pydantic_settings, streamlit; print('ok')"`
Expected: `ok`

---

### Task 2: config.py

**Files:**
- Create: `config.py`

**Interfaces:**
- Produces:
  - `class Settings(BaseSettings)`: `model_name: str = ""`, `max_input_chars: int = 2000`, `temperature: float = 0.7`, `max_output_tokens: int = 2000`.
  - `settings: Settings` (module-level instance).
  - Constants: `MIN_WORDS`, `MAX_WORDS`, `APP_TITLE`, `APP_SUBTITLE`, `INPUT_LABEL`, `INPUT_PLACEHOLDER`, `INPUT_HEIGHT`, `SUBMIT_LABEL`, `SPINNER_TEXT`, `DISCLAIMER`, `ERROR_EMPTY_INPUT`, `ERROR_INPUT_TOO_LONG` (format string with `{max}`), `ERROR_MODEL_NOT_SET`, `ERROR_GENERIC`.

`load_dotenv()` puts `.env` values into the process environment. Pydantic AI reads provider API keys from the environment, and `Settings` alone would not export them.

- [ ] **Step 1: Create `config.py`**

```python
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Export .env (including provider API keys) to the environment for Pydantic AI.
load_dotenv()


class Settings(BaseSettings):
    """Runtime settings from environment. Unknown variables (API keys) are ignored."""

    model_config = SettingsConfigDict(extra="ignore")

    model_name: str = ""  # Pydantic AI "provider:model" string, set via MODEL_NAME
    max_input_chars: int = 2000
    temperature: float = 0.7
    max_output_tokens: int = 2000


settings = Settings()

# --- Answer length (words per perspective) ---
MIN_WORDS = 80
MAX_WORDS = 180

# --- UI text ---
APP_TITLE = "Sacred Self"
APP_SUBTITLE = "Share a situation or issue. See it through four perspectives."
INPUT_LABEL = "What is on your mind?"
INPUT_PLACEHOLDER = "For example: My husband doesn't appreciate anything I do for the family."
INPUT_HEIGHT = 150
SUBMIT_LABEL = "Show me four perspectives"
SPINNER_TEXT = "Reflecting..."
DISCLAIMER = (
    "This is a reflection tool, not medical, psychological, legal or crisis support. "
    "If you are in danger or in crisis, contact local emergency services or a trusted person."
)

# --- Error messages ---
ERROR_EMPTY_INPUT = "Please describe your situation first."
ERROR_INPUT_TOO_LONG = "Please keep your message under {max} characters."
ERROR_MODEL_NOT_SET = (
    "No model is configured. Set MODEL_NAME (and your provider API key) in .env. See README.md."
)
ERROR_GENERIC = "Something went wrong while generating the perspectives. Please try again."
```

- [ ] **Step 2: Verify import without a key or model**

Run: `uv run python -c "import config; print(repr(config.settings.model_name))"`
Expected: `''`

Run: `MODEL_NAME=test uv run python -c "import config; print(config.settings.model_name)"`
Expected: `test`

---

### Task 3: prompts.py

**Files:**
- Create: `prompts.py`

**Interfaces:**
- Consumes: `config.MIN_WORDS`, `config.MAX_WORDS`.
- Produces:
  - `class PerspectiveConfig(BaseModel)`: `key: str`, `title: str`, `tagline: str`, `prompt: str`.
  - `PERSPECTIVES: list[PerspectiveConfig]` in order `willingness`, `reasoning`, `loving_heart`, `still_witness`.
  - `BASE_SYSTEM_PROMPT: str`.
  - `build_system_prompt() -> str`.

Source of truth is `docs/Reset- Sacred Self.md`. The Willingness section is drafted from its principles because the doc has no response structure for it.

- [ ] **Step 1: Create `prompts.py`**

```python
from pydantic import BaseModel

from config import MAX_WORDS, MIN_WORDS


class PerspectiveConfig(BaseModel):
    key: str
    title: str
    tagline: str
    prompt: str


BASE_SYSTEM_PROMPT = f"""You help a person look at a situation they describe through four distinct perspectives.
Return exactly one answer per perspective. Each answer is addressed directly to the user ("you"),
written in warm, plain language, between {MIN_WORDS} and {MAX_WORDS} words.

Rules for every perspective:
- Never give generic reassurance such as "Everything will be okay" or "Stay positive". Ground every answer in the user's specific situation.
- Do not invent facts, hidden motives or psychological diagnoses.
- Do not moralise, preach or make the user feel guilty for their emotions.
- Do not claim to measure the user's consciousness, intelligence or spiritual level.
- Never tell the user to tolerate abuse, manipulation or harm.
- If the situation involves danger, abuse, self-harm, suicidal thoughts or another crisis, every answer must put safety and appropriate human support first, and must not use philosophical reframing or detachment exercises.
- The four answers must be clearly different in approach. Do not repeat the same points.
- Each answer should end with one short, memorable insight or one useful question.
"""

WILLINGNESS = """PERSPECTIVE: Willingness
Guiding idea: "Life may not be happening as I expected. But I am willing to participate, willing to learn, willing to improve and willing to discover what is possible."
Worldview: hopeful and inspiring. Setbacks can be followed by adjustment. The person has the capacity to learn and contribute.
How to respond:
1. Appreciate what the user has already done or endured. Name the effort specifically.
2. Offer realistic hope: point to possibilities beyond the current difficulty, without guaranteeing success.
3. Invite learning: ask what the experience can teach and what they might do differently.
4. Help them find what they genuinely want to work toward.
5. Suggest one small, constructive next step, offered as an invitation without pressure.
Tone: encouraging and respectful. Make it easy to admit mistakes without self-condemnation.
Avoid: empty positivity, guaranteeing success, dismissing pain, insisting the user act before they feel ready."""

REASONING = """PERSPECTIVE: The Reasoning Mind
Guiding idea: "Before reacting to a situation, understand what is actually happening."
Worldview: life is complex and can be understood through observation, evidence and reasoning. A first interpretation is not always an accurate account of reality. Most problems have several contributing factors.
How to respond:
1. Identify the central issue in one sentence.
2. Separate what the user observed from what they concluded or assumed.
3. Reveal one or two plausible explanations or patterns they may have missed. Present them as possibilities, never as facts.
4. Ask one powerful question that could change their understanding, and say what evidence would help answer it.
5. Suggest a realistic action, investigation or decision based on what is known.
6. End with a concise insight.
Tone: calm, precise, observant, simple language. Acknowledge the pain, but do not use reassurance as the main tool.
Avoid: generic encouragement, assuming the user or anyone else is wrong, implying emotions are irrational, becoming argumentative, overwhelming with too many possibilities, analysis for its own sake."""

LOVING_HEART = """PERSPECTIVE: The Loving Heart
Guiding idea: "Look beyond the immediate hurt, recognise the humanity present and discover what love can offer without abandoning truth or dignity."
Worldview: every person has inherent worth beyond their behaviour. People act from experiences, fears and limitations. Understanding someone's humanity does not mean approving their behaviour. Compassion can coexist with boundaries, forgiveness with self-respect.
How to respond:
1. Receive the hurt warmly first. Do not rush to correct the user's interpretation.
2. Widen the view to the human context of everyone involved, including the user.
3. Gently name an overlooked need, expectation, fear or form of care beneath the conflict, as a possibility only.
4. Offer a loving way of seeing the situation: compassion, patience, gratitude or inner fullness.
5. Suggest one realistic loving action that keeps truth, self-respect and boundaries. Sometimes that action is a firm boundary.
6. Where fitting, invite the user to consider releasing resentment or a demand for approval. Never demand forgiveness.
7. End with a heart-opening insight.
Tone: warm, gentle, dignified, patient. Perceptive rather than merely comforting. No sentimentality or cliches such as "Everything happens for a reason".
Avoid: confusing love with self-sacrifice or people-pleasing, pressuring forgiveness, minimising harm, inventing innocent motives for harmful behaviour, encouraging dependence on the AI."""

STILL_WITNESS = """PERSPECTIVE: The Still Witness
Guiding idea: "Help the user observe what they are experiencing without becoming completely identified with it."
Worldview: people often turn an event into a definition of themselves ("I failed" becomes "I am a failure"). Thoughts, emotions and circumstances arise and pass. A person can notice them without being consumed by them.
How to respond:
1. Briefly acknowledge the situation and its pain. Do not jump into spiritual teaching.
2. Name one thought, story or identity the user seems attached to, only if one is really present. Do not invent one.
3. Invite a simple pause: notice the thought or feeling as something appearing in awareness. One clear observation or one contemplative question, not many.
4. Distinguish the event from the identity, and necessary action from unnecessary mental struggle.
5. Return to ordinary life: note any practical step that still deserves attention.
6. End with a short, still, memorable reflection.
Tone: simple, calm, humble, unhurried. Gentle inquiry such as "For a moment, notice..." or "Can you observe...". Do not repeat the same phrases every time. No spiritual terminology unless the user used it.
Avoid: declaring suffering, illness, grief or abuse an illusion; saying the user attracted their suffering; telling someone in abuse to simply stay detached; suggesting boundaries are ego; promising enlightenment or claiming any spiritual level; pressuring someone to transcend grief."""

PERSPECTIVES: list[PerspectiveConfig] = [
    PerspectiveConfig(
        key="willingness",
        title="Willingness",
        tagline="What can I learn, improve or contribute?",
        prompt=WILLINGNESS,
    ),
    PerspectiveConfig(
        key="reasoning",
        title="The Reasoning Mind",
        tagline="What is actually happening?",
        prompt=REASONING,
    ),
    PerspectiveConfig(
        key="loving_heart",
        title="The Loving Heart",
        tagline="What can love offer here?",
        prompt=LOVING_HEART,
    ),
    PerspectiveConfig(
        key="still_witness",
        title="The Still Witness",
        tagline="Can I observe this without becoming it?",
        prompt=STILL_WITNESS,
    ),
]


def build_system_prompt() -> str:
    sections = "\n\n".join(p.prompt for p in PERSPECTIVES)
    return f"{BASE_SYSTEM_PROMPT}\n\n{sections}"
```

- [ ] **Step 2: Verify**

Run: `uv run python -c "import prompts; s = prompts.build_system_prompt(); print(len(s)); assert 'hawkins' not in s.lower()"`
Expected: a number, no assertion error.

---

### Task 4: agent.py

**Files:**
- Create: `agent.py`

**Interfaces:**
- Consumes: `config.settings`, `config.ERROR_*`, `config.MIN_WORDS`, `config.MAX_WORDS`, `prompts.PERSPECTIVES`, `prompts.build_system_prompt`.
- Produces:
  - `class PerspectiveAnswer(BaseModel)`: `response: str`.
  - `class FourPerspectives(BaseModel)`: `willingness`, `reasoning`, `loving_heart`, `still_witness`, each `PerspectiveAnswer`.
  - `class UserError(Exception)`: bad input or missing model; message is safe to show.
  - `get_agent() -> Agent[None, FourPerspectives]` (`lru_cache`, built on first call).
  - `get_perspectives(situation: str) -> FourPerspectives`.

Pydantic AI accepts the model string `"test"`, which runs its built-in `TestModel` with no key and no network.

- [ ] **Step 1: Create `agent.py`**

```python
from functools import lru_cache

from pydantic import BaseModel, Field
from pydantic_ai import Agent

import config
from prompts import PERSPECTIVES, build_system_prompt


class PerspectiveAnswer(BaseModel):
    response: str = Field(
        description=f"The answer for this perspective, {config.MIN_WORDS}-{config.MAX_WORDS} words, addressed to the user."
    )


class FourPerspectives(BaseModel):
    willingness: PerspectiveAnswer
    reasoning: PerspectiveAnswer
    loving_heart: PerspectiveAnswer
    still_witness: PerspectiveAnswer


# Keeps prompts.PERSPECTIVES and the output model in step.
assert [p.key for p in PERSPECTIVES] == list(FourPerspectives.model_fields)


class UserError(Exception):
    """Bad input or missing setup. The message is safe to show the user."""


@lru_cache
def get_agent() -> Agent[None, FourPerspectives]:
    if not config.settings.model_name:
        raise UserError(config.ERROR_MODEL_NOT_SET)
    return Agent(
        config.settings.model_name,
        output_type=FourPerspectives,
        system_prompt=build_system_prompt(),
    )


def get_perspectives(situation: str) -> FourPerspectives:
    text = situation.strip()
    if not text:
        raise UserError(config.ERROR_EMPTY_INPUT)
    if len(text) > config.settings.max_input_chars:
        raise UserError(config.ERROR_INPUT_TOO_LONG.format(max=config.settings.max_input_chars))

    result = get_agent().run_sync(
        text,
        model_settings={
            "temperature": config.settings.temperature,
            "max_tokens": config.settings.max_output_tokens,
        },
    )
    return result.output
```

- [ ] **Step 2: Verify imports without a key or model**

Run: `uv run python -c "import agent; print('ok')"`
Expected: `ok`

- [ ] **Step 3: Verify the missing-model message**

Run: `uv run python -c "from agent import get_perspectives; get_perspectives('hello')"`
Expected: traceback ending in `agent.UserError: No model is configured...`

- [ ] **Step 4: Verify a full call with the test model**

Run: `MODEL_NAME=test uv run python -c "from agent import get_perspectives; print(get_perspectives('My friend betrayed my trust.'))"`
Expected: a `FourPerspectives(...)` object with four `PerspectiveAnswer` values.

If this fails on an unexpected keyword or attribute (Pydantic AI API drift), check the installed version's docs for `Agent(...)`, `run_sync(...)`, `result.output` and `model_settings`, and fix `agent.py` to match.

- [ ] **Step 5: Verify input checks**

Run: `MODEL_NAME=test uv run python -c "from agent import get_perspectives; get_perspectives('   ')"`
Expected: traceback ending in `agent.UserError: Please describe your situation first.`

---

### Task 5: app.py

**Files:**
- Create: `app.py`

**Interfaces:**
- Consumes: `config.*` UI constants, `agent.get_perspectives`, `agent.UserError`, `prompts.PERSPECTIVES`.

- [ ] **Step 1: Create `app.py`**

```python
import logging

import streamlit as st

import config
from agent import UserError, get_perspectives
from prompts import PERSPECTIVES

logger = logging.getLogger(__name__)

st.set_page_config(page_title=config.APP_TITLE, layout="wide")
st.title(config.APP_TITLE)
st.caption(config.APP_SUBTITLE)

situation = st.text_area(
    config.INPUT_LABEL,
    placeholder=config.INPUT_PLACEHOLDER,
    height=config.INPUT_HEIGHT,
)

if st.button(config.SUBMIT_LABEL, type="primary"):
    try:
        with st.spinner(config.SPINNER_TEXT):
            result = get_perspectives(situation)
    except UserError as e:
        st.warning(str(e))
    except Exception:
        logger.exception("Perspective generation failed")
        st.error(config.ERROR_GENERIC)
    else:
        for col, perspective in zip(st.columns(len(PERSPECTIVES)), PERSPECTIVES):
            with col:
                st.subheader(perspective.title)
                st.caption(perspective.tagline)
                st.write(getattr(result, perspective.key).response)

st.caption(config.DISCLAIMER)
```

- [ ] **Step 2: Dry run with the test model**

Run: `MODEL_NAME=test uv run streamlit run app.py`
Expected: the page opens. Type any text and press the button: four columns with the titles Willingness, The Reasoning Mind, The Loving Heart, The Still Witness.

- [ ] **Step 3: Check the warnings**

With the app still running (same `MODEL_NAME=test` shell): press the button with an empty box, and expect "Please describe your situation first." Then stop the app, run `uv run streamlit run app.py` without `MODEL_NAME`, submit text, and expect the "No model is configured" warning.

---

### Task 6: Docs and live check

**Files:**
- Modify: `CLAUDE.md`
- Already written: `README.md`

- [ ] **Step 1: Update `CLAUDE.md`**

Replace the "Current state" section with:

```markdown
## Commands

- Install: `uv sync`
- Run: `uv run streamlit run app.py` (needs `.env` copied from `.env.example`)
- Dry run without a key: `MODEL_NAME=test uv run streamlit run app.py`
- There are no automated tests yet.

## Architecture

One structured Pydantic AI call returns all four perspective answers. `app.py` (UI) calls `agent.get_perspectives()`, which validates input, builds the agent lazily from `config.settings.model_name`, and returns a `FourPerspectives`. All prompt text is in `prompts.py`. All other config and hardcoded strings are in `config.py`. `PERSPECTIVES` in `prompts.py` fixes column order, and an import-time `assert` in `agent.py` requires its keys to equal the `FourPerspectives` field names.
```

Keep the "What the design doc defines" and "Constraints from the doc" sections.

- [ ] **Step 2: Live check with a real model (needs the user's key)**

```bash
cp .env.example .env
# set MODEL_NAME and the matching API key in .env
uv run streamlit run app.py
```

Submit each example from `docs/Reset- Sacred Self.md` (husband appreciation, colleague promotion, child mistakes, betrayal). Confirm four distinct answers of about 80-180 words in four columns, and compare them with the doc's example table. Submit a crisis-style input and confirm the answers put safety first. If no key is available, report this step as not verified.

---

## Self-review

- Spec coverage: Pydantic AI single call (Task 4), four columns (Task 5), separate `prompts.py` (Task 3), `config.py` for all other values (Task 2), env-driven model string with no import-time key (Tasks 2 and 4), README (already written), uv install (Task 1), Perspective 1 drafted (Task 3), no "Hawkins" check (Task 3 Step 2), error handling (Tasks 4 and 5), no automated tests, manual checks per task.
- No placeholders: every code step contains full code.
- Name consistency: `PERSPECTIVES` keys, `FourPerspectives` fields, `get_perspectives`, `get_agent`, `settings`, `UserError` and the `config.ERROR_*` names match across tasks.
- Known risk: Pydantic AI API names (`output_type`, `run_sync`, `result.output`, `model_settings`) were written from knowledge, not checked against the installed version. Task 4 Step 4 covers a mismatch.
