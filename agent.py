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


class UserError(Exception):
    """Bad input or missing setup. The message is safe to show the user."""


@lru_cache
def get_agent() -> Agent[None, FourPerspectives]:
    return Agent(
        config.MODEL_NAME,
        output_type=FourPerspectives,
        system_prompt=build_system_prompt(),
    )


def get_perspectives(situation: str) -> FourPerspectives:
    text = situation.strip()
    if not text:
        raise UserError(config.ERROR_EMPTY_INPUT)
    if len(text) > config.settings.max_input_chars:
        raise UserError(config.ERROR_INPUT_TOO_LONG.format(max=config.settings.max_input_chars))

    try:
        result = get_agent().run_sync(
            text,
            model_settings={
                "max_tokens": config.settings.max_output_tokens,
                **({"temperature": config.settings.temperature} if config.settings.temperature is not None else {}),
            },
            timeout=config.settings.request_timeout,
        )
    except TimeoutError:
        raise UserError(config.ERROR_TIMEOUT) from None
    return result.output
