import logging
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse

import config
import db
from prompts import PERSPECTIVES, build_system_prompt

logger = logging.getLogger(__name__)


class PerspectiveAnswer(BaseModel):
    response: str = Field(
        description=f"The answer for this perspective, {config.MIN_WORDS}-{config.MAX_WORDS} words, addressed to the user."
    )


class FourPerspectives(BaseModel):
    # Filled first so the model extracts the user's details before writing. Not shown in the UI.
    key_facts: str = Field(
        description="Not shown to the user. 2-4 short lines: what happened; what the user wants; any contradiction or unfairness they mention; thoughts or feelings they actually expressed, quoted. 'none' where not said."
    )
    willingness: PerspectiveAnswer
    reasoning: PerspectiveAnswer
    loving_heart: PerspectiveAnswer
    still_witness: PerspectiveAnswer


# Keeps prompts.PERSPECTIVES and the output model in step.
assert [p.key for p in PERSPECTIVES] == list(FourPerspectives.model_fields)[1:]


class Fallback(BaseModel):
    """Use ONLY when the message is not about the user's own personal situation, feelings,
    relationships, work or life decisions (general knowledge, facts, coding, news, trivia,
    requests to write or translate, questions about the AI). Never use it for a crisis message."""

    message: Literal["FALLBACK"]


def answers_dict(output: FourPerspectives) -> dict[str, str]:
    """Plain {column: text} form of an answer, used for saving and for display."""
    return {
        "key_facts": output.key_facts,
        **{p.key: getattr(output, p.key).response for p in PERSPECTIVES},
    }


class UserError(Exception):
    """Bad input or missing setup. The message is safe to show the user."""


@lru_cache
def get_agent() -> Agent[None, FourPerspectives | Fallback]:
    return Agent(
        config.MODEL_NAME,
        output_type=[FourPerspectives, Fallback],
        system_prompt=build_system_prompt(),
    )


def get_perspectives(situation: str) -> FourPerspectives | None:
    """The four answers, or None when the model returned FALLBACK (not a personal issue)."""
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

    output = result.output if isinstance(result.output, FourPerspectives) else None
    try:
        db.save_request(
            text,
            answers_dict(output) if output else None,
            config.MODEL_NAME,
            usage.input_tokens,
            usage.output_tokens,
            cost,
        )
    except Exception:  # never hide the answers because saving failed
        logger.exception("Could not save request")
    return output
