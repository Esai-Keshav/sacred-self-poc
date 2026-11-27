import logging
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext, capture_run_messages
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    RetryFeedbackPart,
    ToolReturnPart,
)

import config
import db
from prompts import build_system_prompt, today_line

logger = logging.getLogger(__name__)


class Card(BaseModel):
    # Filled in this order: the model writes the body first, then the hook that teases it.
    expanded: str = Field(
        description=f"{config.EXPANDED_MIN_WORDS}-{config.EXPANDED_MAX_WORDS} words, exactly 2 short paragraphs separated by a blank line. Do not open by restating the person's message. Open with a strength or a reframe, never with the hurt. Name the feeling in one short clause after that, then follow the Expanded section of your perspective. Do not state the task or a deadline, except on a crisis card."
    )
    hook: str = Field(
        description=f"{config.HOOK_MIN_WORDS}-{config.HOOK_MAX_WORDS} words, in exactly two sentences: 8 to 10 words, then 14 to 18 words. Sentence 1 names the person's strength or reframes the moment. Sentence 2 moves them forward with energy and assurance, in active verbs (willing, learn, discover, show up, go again, keep growing). No passive or defensive wording ('deserves', 'protect', 'can be seen'). May end with one exclamation mark. Do not name the task, except on a crisis card. Do not repeat the person's message."
    )
    practise: str = Field(
        description=f"{config.PRACTISE_MIN_WORDS}-{config.PRACTISE_MAX_WORDS} words, ONE action, the only place that names the task. In order: context (when, such as 'Within 2 days, ...'), change (the unhelpful behaviour it replaces), concrete instruction (with 'You can say: ...' as its own paragraph for interpersonal situations), continuation (how to follow through without the old pattern), capability (a closing line of courage, enthusiasm, self-respect, participation, teachability or appreciation)."
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


def check_practise(practise: str) -> None:
    n = word_count(practise)
    if not config.PRACTISE_MIN_WORDS <= n <= config.PRACTISE_MAX_WORDS:
        raise ModelRetry(
            f"practise has {n} words. Write it in {config.PRACTISE_MIN_WORDS}-{config.PRACTISE_MAX_WORDS} words: one action through context, change, instruction, continuation, capability."
        )


def check_stock_word(text: str) -> None:
    if re.search(r"\bsting(s|ing)?\b", text, re.IGNORECASE):
        raise ModelRetry("Do not use the word 'sting'. Name this person's hurt in plain words.")


def check_no_gender(text: str) -> None:
    if re.search(r"\b(he|she|him|her|his|hers|himself|herself)\b", text, re.IGNORECASE):
        raise ModelRetry(
            "Do not assume gender. Replace he, she, him, her or his with the role, "
            "such as 'your friend', or with 'they'."
        )


def check_punctuation(card: Card) -> None:
    """The hook may end with one exclamation mark; none elsewhere. No question marks outside
    expanded, and at most one there."""
    fields = card.model_dump()
    hook = fields["hook"]
    if "!" in hook.rstrip()[:-1]:
        raise ModelRetry("The hook may hold one exclamation mark, only at its very end.")
    for name, text in fields.items():
        if name != "hook" and "!" in text:
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
def get_agent(perspective: str) -> Agent[None, Card | Fallback]:
    agent = Agent(
        config.MODEL_NAME,
        output_type=[Card, Fallback],
        system_prompt=build_system_prompt(perspective),
        retries=5,
    )

    @agent.system_prompt
    def _today() -> str:
        # Read on every run, so a cached agent still knows today's date.
        return today_line(datetime.now(config.DISPLAY_TZ))

    @agent.output_validator
    def _check_card(ctx: RunContext[None], output):
        if isinstance(output, Card):
            check_hook_length(output.hook)
            check_expanded(output.expanded)
            check_practise(output.practise)
            check_stock_word(f"{output.hook} {output.expanded}")
            check_no_gender(f"{output.hook} {output.expanded} {output.practise}")
            check_punctuation(output)
        return output

    return agent


def retry_reasons(messages) -> list[str]:
    """Why the model was asked to try again, one entry per retry."""
    reasons = []
    for message in messages:
        if not isinstance(message, ModelRequest):
            continue
        for part in message.parts:
            # Structured output retries are tool returns marked "retried".
            if isinstance(part, RetryFeedbackPart) or (
                isinstance(part, ToolReturnPart) and part.outcome == "retried"
            ):
                content = part.content
                if not isinstance(content, str):  # schema errors arrive as a list
                    content = "; ".join(
                        f"{'.'.join(map(str, error['loc']))}: {error['msg']}"
                        for error in content
                    )
                reasons.append(content)
    return reasons


def _run(situation: str, perspective: str):
    """Validate the input, call the model, print usage. Returns (text, result, cost)."""
    text = situation.strip()
    if not text:
        raise UserError(config.ERROR_EMPTY_INPUT)
    if len(text) > config.settings.max_input_chars:
        raise UserError(
            config.ERROR_INPUT_TOO_LONG.format(max=config.settings.max_input_chars)
        )

    with capture_run_messages() as messages:
        try:
            result = get_agent(perspective).run_sync(
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
        finally:  # also runs when retries are used up, which is when the reason matters most
            for number, reason in enumerate(retry_reasons(messages), start=1):
                print(f"[{perspective}] [retry {number}] {reason}")

    usage = result.usage
    print(f"[{perspective}] {usage}")
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
        f"[{perspective}] [usage] in={usage.input_tokens} out={usage.output_tokens} est_cost={cost_text}"
    )
    return text, result, cost


def get_cards(situation: str) -> list[tuple[str, Card | None, int | None, bool]]:
    """Run every perspective in parallel. One (perspective, card, saved card id, failed)
    per perspective, in config.PERSPECTIVES order. The card is None when the model returned
    FALLBACK (not a personal issue) or the call failed, and neither is saved. The id is None
    when saving failed. Raises the first error only when every perspective failed."""
    with ThreadPoolExecutor() as pool:
        futures = {p: pool.submit(_run, situation, p) for p in config.PERSPECTIVES}
    errors = {p: f.exception() for p, f in futures.items() if f.exception()}
    if len(errors) == len(futures):
        raise next(iter(errors.values()))

    results = {}
    # Saved in reverse, so History (newest id first) lists the first perspective on top.
    for perspective, future in reversed(futures.items()):
        card, card_id = None, None
        if perspective in errors:
            logger.error("%s card failed", perspective, exc_info=errors[perspective])
        else:
            text, result, cost = future.result()
            if isinstance(result.output, Card):
                card = result.output
                try:
                    card_id = db.save_card(
                        text,
                        card.model_dump(),
                        config.MODEL_NAME,
                        result.usage.input_tokens,
                        result.usage.output_tokens,
                        cost,
                        perspective,
                    )
                except Exception:  # never hide the card because saving failed
                    logger.exception("Could not save card")
        results[perspective] = (perspective, card, card_id, perspective in errors)
    return [results[p] for p in config.PERSPECTIVES]
