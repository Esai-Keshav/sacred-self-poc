import logging
from datetime import datetime
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext
from pydantic_ai.messages import ModelResponse

import config
import db
from prompts import build_system_prompt, today_line

logger = logging.getLogger(__name__)


class WillingnessCard(BaseModel):
    # Filled in this order: the model writes the body first, then the hook that teases it.
    expanded: str = Field(
        description=f"{config.EXPANDED_MIN_WORDS}-{config.EXPANDED_MAX_WORDS} words, 2-3 short paragraphs. Appreciate one specific thing the person did, build belief in their capacity, and focus on one process step they can try."
    )
    hook: str = Field(
        description=f"{config.HOOK_MIN_WORDS}-{config.HOOK_MAX_WORDS} words. A specific pull that teases the strongest idea in expanded. Do not repeat the person's message."
    )
    practise: str = Field(
        description="One sentence with a deadline, such as 'In 3 days, ...'. One concrete task the person can do from their own words."
    )
    say_it: str = Field(
        description="One first-person sentence the person says aloud, in their own voice, using details from their message."
    )


class Fallback(BaseModel):
    """Use ONLY when the message is not about the user's own personal situation, feelings,
    relationships, work or life decisions (general knowledge, facts, coding, news, trivia,
    requests to write or translate, questions about the AI). Never use it for a crisis message."""

    message: Literal["FALLBACK"]


class UserError(Exception):
    """Bad input or missing setup. The message is safe to show the user."""


def word_count(text: str) -> int:
    return len(text.split())


def check_hook_length(hook: str) -> None:
    n = word_count(hook)
    if not config.HOOK_MIN_WORDS <= n <= config.HOOK_MAX_WORDS:
        raise ModelRetry(
            f"The hook has {n} words. Write it in {config.HOOK_MIN_WORDS}-{config.HOOK_MAX_WORDS} words."
        )


def check_punctuation(card: WillingnessCard) -> None:
    """No exclamation marks anywhere. No question marks outside expanded, and at most one there."""
    fields = card.model_dump()
    for name, text in fields.items():
        if "!" in text:
            raise ModelRetry(f"The {name} has an exclamation mark. Remove it.")
    for name in ("hook", "practise", "say_it"):
        if "?" in fields[name]:
            raise ModelRetry(f"The {name} has a question mark. Only expanded may ask one soft question.")
    if fields["expanded"].count("?") > 1:
        raise ModelRetry("expanded asks more than one question. Keep at most one soft question.")


@lru_cache
def get_agent() -> Agent[None, WillingnessCard | Fallback]:
    agent = Agent(
        config.MODEL_NAME,
        output_type=[WillingnessCard, Fallback],
        system_prompt=build_system_prompt(),
    )

    @agent.system_prompt
    def _today() -> str:
        # Read on every run, so a cached agent still knows today's date.
        return today_line(datetime.now(config.DISPLAY_TZ))

    @agent.output_validator
    def _check_card(ctx: RunContext[None], output):
        if isinstance(output, WillingnessCard):
            check_hook_length(output.hook)
            check_punctuation(output)
        return output

    return agent


def _run(situation: str):
    """Validate the input, call the model, print usage. Returns (text, result, cost)."""
    text = situation.strip()
    if not text:
        raise UserError(config.ERROR_EMPTY_INPUT)
    if len(text) > config.settings.max_input_chars:
        raise UserError(
            config.ERROR_INPUT_TOO_LONG.format(max=config.settings.max_input_chars)
        )

    try:
        result = get_agent().run_sync(
            text,
            model_settings={
                "max_tokens": config.settings.max_output_tokens,
                **({"thinking": config.REASONING_EFFORT} if config.REASONING_EFFORT else {}),
                **(
                    {"temperature": config.settings.temperature}
                    if config.settings.temperature is not None
                    else {}
                ),
            },
            timeout=config.settings.request_timeout,
        )
    except TimeoutError:
        raise UserError(config.ERROR_TIMEOUT) from None

    usage = result.usage
    print(usage)
    try:
        cost = float(
            sum(
                m.cost().total_price
                for m in result.all_messages()
                if isinstance(m, ModelResponse)
            )
        )
        cost_text = f"${cost:.6f}"
    except Exception:  # model has no price data (e.g. "test")
        cost = None
        cost_text = "n/a"
    print(
        f"[usage] in={usage.input_tokens} out={usage.output_tokens} est_cost={cost_text}"
    )
    return text, result, cost


def get_card(situation: str) -> tuple[WillingnessCard | None, int | None]:
    """(card, saved card id). The card is None when the model returned FALLBACK (not a
    personal issue), and fallbacks are never saved. The id is None when saving failed."""
    text, result, cost = _run(situation)
    if not isinstance(result.output, WillingnessCard):
        return None, None
    usage = result.usage
    card_id = None
    try:
        card_id = db.save_card(
            text,
            result.output.model_dump(),
            config.MODEL_NAME,
            usage.input_tokens,
            usage.output_tokens,
            cost,
        )
    except Exception:  # never hide the card because saving failed
        logger.exception("Could not save card")
    return result.output, card_id
