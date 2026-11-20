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
# Reasoning effort: "minimal", "low", "medium" or "high". None = do not send it.
REASONING_EFFORT = "low"

# --- Card length (words) ---
HOOK_MIN_WORDS = 25
HOOK_MAX_WORDS = 30
EXPANDED_MIN_WORDS = 80
EXPANDED_MAX_WORDS = 120

# --- History ---
HISTORY_LIMIT = 50
DISPLAY_TZ = timezone(timedelta(hours=5, minutes=30))
DISPLAY_TZ_LABEL = "IST"

# --- UI text ---
APP_TITLE = "Sacred Self"
APP_SUBTITLE = "Share a thought. Get one card to build your willingness."
INPUT_LABEL = "What is on your mind?"
INPUT_PLACEHOLDER = "My child keeps making the same mistakes despite repeated corrections."
SPINNER_TEXT = "Reflecting..."
EXPANDED_LABEL = "Read more"
PRACTISE_LABEL = "Practise"
SAY_IT_LABEL = "Say it"
FEEDBACK_HEADING = "Your feedback"
FEEDBACK_COMMENT_LABEL = "Comment (optional)"
FEEDBACK_SUBMIT_LABEL = "Send feedback"
FEEDBACK_THANKS = "Thanks. Your feedback is saved."
TAB_NEW_LABEL = "New card"
TAB_HISTORY_LABEL = "History"
FEEDBACK_HINT = "Rate this card and leave a comment in the History tab."
HISTORY_EMPTY = "No saved cards yet."
DISCLAIMER = (
    "This is a reflection tool, not medical, psychological, legal or crisis support. "
    "If you are in danger or in crisis, contact local emergency services or a trusted person."
)
SAVE_NOTICE = (
    "Your thought, the card and any feedback are saved and visible to all users of this app."
)
FALLBACK_MESSAGE = "I can't help with it."

# --- Error messages ---
ERROR_EMPTY_INPUT = "Please describe your situation first."
ERROR_INPUT_TOO_LONG = "Please keep your message under {max} characters."
ERROR_TIMEOUT = "This is taking longer than expected. Please try again."
ERROR_SAVE = "Your card is shown, but it could not be saved."
ERROR_HISTORY = "The history could not be loaded."
ERROR_FEEDBACK = "Your feedback could not be saved. Please try again."
ERROR_GENERIC = "Something went wrong while generating the card. Please try again."
