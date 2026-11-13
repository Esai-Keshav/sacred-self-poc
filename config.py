from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Export .env (including provider API keys) to the environment for Pydantic AI.
load_dotenv()


class Settings(BaseSettings):
    """Runtime settings from environment. Unknown variables (API keys) are ignored."""

    model_config = SettingsConfigDict(extra="ignore")

    max_input_chars: int = 2000
    # None = do not send temperature. Reasoning models (e.g. gpt-6-luna) reject it and warn.
    # Set a number (e.g. 0.5) only for non-reasoning models such as gpt-4o-mini.
    temperature: float | None = None
    # temperature: float | None = 0.5
    # Four answers of at most MAX_WORDS words need roughly 700 tokens, plus headroom.
    max_output_tokens: int = 1200
    # Seconds to wait for the model before giving up and inviting a retry.
    request_timeout: float = 60.0


settings = Settings()

# --- Model ---
# Pydantic AI "provider:model" string. The matching API key goes in .env.
# Use "test" for a no-key dry run that returns placeholder text.
# MODEL_NAME = "openai:gpt-4.1-mini"
# MODEL_NAME = "openai:gpt-5.4-mini"


# MODEL_NAME = "openai:gpt-4o-mini"
MODEL_NAME = "openai:gpt-6-luna"
# Reasoning effort: "minimal", "low", "medium" or "high". None = do not send it.
# Non-reasoning models (e.g. gpt-4o-mini) ignore it.
REASONING_EFFORT = "low"

# --- Saved requests (SQLite) ---
DB_PATH = "data/answers.db"
# --- Answer length (words per perspective) ---
MIN_WORDS = 70
MAX_WORDS = 120

# --- UI text ---
APP_TITLE = "Sacred Self"
APP_SUBTITLE = "Share a situation or issue. See it through four perspectives."
INPUT_LABEL = "What is on your mind?"
INPUT_PLACEHOLDER = (
    "My child keeps making the same mistakes despite repeated corrections."
)
ANSWER_BOX_HEIGHT = 420
SPINNER_TEXT = "Reflecting..."
DISCLAIMER = (
    "This is a reflection tool, not medical, psychological, legal or crisis support. "
    "If you are in danger or in crisis, contact local emergency services or a trusted person."
)
FALLBACK_MESSAGE = "I can't help with it."
HISTORY_FALLBACK_LABEL = "Out of scope"
HISTORY_HEADING = "History"
HISTORY_EMPTY = "No saved requests yet."
HISTORY_SNIPPET_CHARS = 90
HISTORY_BOX_HEIGHT = 420
BACK_LABEL = "← Back"
DETAIL_NOT_FOUND = "That request was not found. Go back and pick one from the history."
COPY_HEADING = "Copy question and answers"
COPY_QUESTION_LABEL = "Question"
SAVE_NOTICE = "Your message and the answers are saved to help improve this app."

# --- Error messages ---
ERROR_EMPTY_INPUT = "Please describe your situation first."
ERROR_INPUT_TOO_LONG = "Please keep your message under {max} characters."
ERROR_TIMEOUT = "This is taking longer than expected. Please try again."
ERROR_MODEL_NOT_SET = "No model is configured. Set MODEL_NAME (and your provider API key) in .env. See README.md."
ERROR_GENERIC = (
    "Something went wrong while generating the perspectives. Please try again."
)
