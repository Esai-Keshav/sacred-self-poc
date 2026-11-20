import logging
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.messages import ModelResponse

import config
import db
from prompts import PERSPECTIVES, build_system_prompt
from prompts_v2 import PERSPECTIVES_V2, build_system_prompt_v2

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


class PerspectiveAnswerV2(BaseModel):
    response: str = Field(
        description=f"The answer for this perspective, {config.V2_MIN_WORDS}-{config.V2_MAX_WORDS} words, addressed to the user."
    )


class FourPerspectivesV2(BaseModel):
    key_facts: str = Field(
        description="Not shown to the user. 2-4 short lines: what happened; what the user wants; any contradiction or unfairness they mention; thoughts or feelings they actually expressed, quoted. 'none' where not said."
    )
    willingness: PerspectiveAnswerV2
    reasoning: PerspectiveAnswerV2
    loving_heart: PerspectiveAnswerV2
    still_witness: PerspectiveAnswerV2


assert [p.key for p in PERSPECTIVES_V2] == list(FourPerspectivesV2.model_fields)[1:]


def answers_dict_v2(output: FourPerspectivesV2) -> dict[str, str]:
    """{perspective: text}, used for saving and display."""
    return {p.key: getattr(output, p.key).response for p in PERSPECTIVES_V2}


class UserError(Exception):
    """Bad input or missing setup. The message is safe to show the user."""


@lru_cache
def get_agent() -> Agent[None, FourPerspectives | Fallback]:
    return Agent(
        config.MODEL_NAME,
        output_type=[FourPerspectives, Fallback],
        system_prompt=build_system_prompt(),
    )


@lru_cache
def get_agent_v2() -> Agent[None, FourPerspectivesV2 | Fallback]:
    return Agent(
        config.MODEL_NAME,
        output_type=[FourPerspectivesV2, Fallback],
        system_prompt=build_system_prompt_v2(),
    )


def _run(agent: Agent, situation: str):
    """Validate the input, call the model, print usage. Returns (text, result, cost)."""
    text = situation.strip()
    if not text:
        raise UserError(config.ERROR_EMPTY_INPUT)
    if len(text) > config.settings.max_input_chars:
        raise UserError(
            config.ERROR_INPUT_TOO_LONG.format(max=config.settings.max_input_chars)
        )

    try:
        result = agent.run_sync(
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


def get_perspectives(situation: str) -> tuple[FourPerspectives | None, int | None]:
    """(four answers, saved request id). Answers are None when the model returned FALLBACK
    (not a personal issue). The id is None when saving failed."""
    text, result, cost = _run(get_agent(), situation)
    usage = result.usage
    output = result.output if isinstance(result.output, FourPerspectives) else None
    request_id = None
    try:
        request_id = db.save_request(
            text,
            answers_dict(output) if output else None,
            config.MODEL_NAME,
            usage.input_tokens,
            usage.output_tokens,
            cost,
        )
    except Exception:  # never hide the answers because saving failed
        logger.exception("Could not save request")
    return output, request_id


def get_perspectives_v2(
    situation: str, request_id: int | None
) -> tuple[dict[str, str] | None, int | None]:
    """(v2 answers or None on FALLBACK, saved request id).

    With a request_id (v1 ran) the answers are saved onto that v1 row. Without one (v1 off)
    a new row is saved: v1 columns NULL, and all NULL for a fallback."""
    text, result, cost = _run(get_agent_v2(), situation)
    answers = (
        answers_dict_v2(result.output)
        if isinstance(result.output, FourPerspectivesV2)
        else None
    )
    try:
        if request_id is None:
            usage = result.usage
            request_id = db.save_request(
                text,
                None,
                config.MODEL_NAME,
                usage.input_tokens,
                usage.output_tokens,
                cost,
            )
        if answers:
            db.save_v2(request_id, answers)
    except Exception:  # never hide the answers because saving failed
        logger.exception("Could not save v2 answers")
    return answers, request_id
