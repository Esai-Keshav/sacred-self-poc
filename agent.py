import logging
import re
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
        description=f"{config.EXPANDED_MIN_WORDS}-{config.EXPANDED_MAX_WORDS} words, exactly 2 short paragraphs separated by a blank line. Appreciate one specific thing the person did and build belief in their capacity. Do not state the task or a deadline, except on a crisis card."
    )
    hook: str = Field(
        description=f"{config.HOOK_MIN_WORDS}-{config.HOOK_MAX_WORDS} words, in exactly two sentences: 8 to 10 words, then 14 to 18 words. Wisdom that reframes the situation. Do not name the task, except on a crisis card. Do not repeat the person's message."
    )
    practise: str = Field(
        description="One sentence with a deadline, such as 'In 3 days, ...'. The only place that names the task: one verb and one object, never two tasks joined with 'and'."
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


def check_expanded(expanded: str) -> None:
    n = word_count(expanded)
    if n > config.EXPANDED_MAX_WORDS:
        raise ModelRetry(
            f"expanded has {n} words. Cut it to at most {config.EXPANDED_MAX_WORDS} words."
        )
    if ";" in expanded:
        raise ModelRetry("expanded has a semicolon. Use a full stop instead.")


def check_stock_word(text: str) -> None:
    if re.search(r"\bsting(s|ing)?\b", text, re.IGNORECASE):
        raise ModelRetry("Do not use the word 'sting'. Name this person's hurt in plain words.")


def check_no_gender(text: str) -> None:
    if re.search(r"\b(he|she|him|her|his|hers|himself|herself)\b", text, re.IGNORECASE):
        raise ModelRetry(
            "Do not assume gender. Replace he, she, him, her or his with the role, "
            "such as 'your friend', or with 'they'."
        )


def check_punctuation(card: WillingnessCard) -> None:
    """No exclamation marks anywhere. No question marks outside expanded, and at most one there."""
    fields = card.model_dump()
    for name, text in fields.items():
        if "!" in text:
            raise ModelRetry(f"The {name} has an exclamation mark. Remove it.")
    for name in ("hook", "practise"):
        if "?" in fields[name]:
            raise ModelRetry(
                f"The {name} has a question mark. Only expanded may ask one soft question."
            )
    if fields["expanded"].count("?") > 1:
        raise ModelRetry(
            "expanded asks more than one question. Keep at most one soft question."
        )


@lru_cache
def get_agent() -> Agent[None, WillingnessCard | Fallback]:
    agent = Agent(
        config.MODEL_NAME,
        output_type=[WillingnessCard, Fallback],
        system_prompt=build_system_prompt(),
        retries=5,
    )

    @agent.system_prompt
    def _today() -> str:
        # Read on every run, so a cached agent still knows today's date.
        return today_line(datetime.now(config.DISPLAY_TZ))

    @agent.output_validator
    def _check_card(ctx: RunContext[None], output):
        if isinstance(output, WillingnessCard):
            check_hook_length(output.hook)
            check_expanded(output.expanded)
            check_stock_word(f"{output.hook} {output.expanded}")
            check_no_gender(f"{output.hook} {output.expanded} {output.practise}")
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
                **(
                    {"thinking": config.REASONING_EFFORT}
                    if config.REASONING_EFFORT
                    else {}
                ),
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
