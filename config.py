from datetime import timedelta, timezone

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Export .env (including provider API keys) to the environment for Pydantic AI.
load_dotenv()


class Settings(BaseSettings):
    """Runtime settings from environment. Unknown variables (API keys) are ignored."""

    model_config = SettingsConfigDict(extra="ignore")

    max_input_chars: int = 2000
    # None = do not send temperature. Reasoning models reject it.
    temperature: float | None = None
    # One card (about 300 words) plus reasoning tokens fits within this.
    max_output_tokens: int = 2000
    # Seconds to wait for the model before giving up and inviting a retry.
    request_timeout: float = 60.0
    supabase_url: str = ""
    supabase_key: str = ""


settings = Settings()

# --- Model ---
# Pydantic AI "provider:model" string. The matching API key goes in .env.
MODEL_NAME = "openai:gpt-6-luna"
# MODEL_NAME = "anthropic:claude-haiku-5-5"
# Reasoning effort: "minimal", "low", "medium" or "high". None = do not send it.
REASONING_EFFORT = "low"

# --- Language guide: v1 = Master System Prompt, v2 = Core Language & Voice,
# v4 = Spoken Language & Voice (from the Nidra transcripts),
# v5 = High-energy Willingness voice (from client feedback) ---
PROMPT_VERSION = "v5"
# PROMPT_VERSION = "v4"
# PROMPT_VERSION = "v3"
# PROMPT_VERSION = "v2"
# PROMPT_VERSION = "v1"

# --- Perspectives: key (prompt file name and DB value) -> label. Order is display order. ---
PERSPECTIVES = {"willingness": "Willingness", "love_joy": "Love & Joy"}
# SHOW_LOVE = True  # False: no Love & Joy card, and no model call for it
SHOW_LOVE = False  # False: no Love & Joy card, and no model call for it

# --- Card length (words) ---
HOOK_MIN_WORDS = 20
HOOK_MAX_WORDS = 30
EXPANDED_MIN_WORDS = 60
EXPANDED_MAX_WORDS = 90
PRACTISE_MIN_WORDS = 70
PRACTISE_MAX_WORDS = 90

# --- History ---
HISTORY_LIMIT = 50
DISPLAY_TZ = timezone(timedelta(hours=5, minutes=30))
DISPLAY_TZ_LABEL = "IST"

# --- UI text ---
APP_TITLE = "Sacred Self"
INPUT_PLACEHOLDER = (
    "My child keeps making the same mistakes despite repeated corrections."
)
SPINNER_TEXT = "Reflecting..."
PRACTISE_LABEL = "Practise"
FEEDBACK_HEADING = "Your feedback"
FEEDBACK_SO_FAR = "Feedback so far"
FEEDBACK_NONE = "No feedback yet."
FEEDBACK_COMMENT_LABEL = "Comment (optional)"
FEEDBACK_SUBMIT_LABEL = "Send feedback"
FEEDBACK_THANKS = "Thanks. Your feedback is saved."
TAB_NEW_LABEL = "New card"
TAB_HISTORY_LABEL = "History"
HISTORY_EMPTY = "No saved cards yet."
FALLBACK_MESSAGE = "I can't help with it."

# --- Error messages ---
ERROR_EMPTY_INPUT = "Please describe your situation first."
ERROR_INPUT_TOO_LONG = "Please keep your message under {max} characters."
ERROR_TIMEOUT = "This is taking longer than expected. Please try again."
ERROR_PARTIAL = "One perspective could not be generated. Please try again."
ERROR_SAVE = "Your card is shown, but it could not be saved."
ERROR_HISTORY = "The history could not be loaded."
ERROR_FEEDBACK = "Your feedback could not be saved. Please try again."
ERROR_GENERIC = "Something went wrong while generating the card. Please try again."
