from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Export .env (including provider API keys) to the environment for Pydantic AI.
load_dotenv()


class Settings(BaseSettings):
    """Runtime settings from environment. Unknown variables (API keys) are ignored."""

    model_config = SettingsConfigDict(extra="ignore")

    max_input_chars: int = 2000
    temperature: float = 0.5
    max_output_tokens: int = 2000


settings = Settings()

# --- Model ---
# Pydantic AI "provider:model" string. The matching API key goes in .env.
# Use "test" for a no-key dry run that returns placeholder text.
# MODEL_NAME = "openai:gpt-4.1-mini"
MODEL_NAME = "openai:gpt-5.4-mini"

# --- Answer length (words per perspective) ---
MIN_WORDS = 70
MAX_WORDS = 120

# --- UI text ---
APP_TITLE = "Sacred Self"
APP_SUBTITLE = "Share a situation or issue. See it through four perspectives."
INPUT_LABEL = "What is on your mind?"
INPUT_PLACEHOLDER = (
    "For example: My husband doesn't appreciate anything I do for the family."
)
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
ERROR_MODEL_NOT_SET = "No model is configured. Set MODEL_NAME (and your provider API key) in .env. See README.md."
ERROR_GENERIC = (
    "Something went wrong while generating the perspectives. Please try again."
)
