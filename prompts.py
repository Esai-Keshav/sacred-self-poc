from datetime import datetime
from pathlib import Path

import config

PROMPT_DIR = Path(__file__).parent / "prompt"

# Rules shared by every perspective. Each perspective adds one <name>.md file.
COMMON_FILE = "language_common.md"
PERSPECTIVE = "willingness"

LANGUAGE_FILES = {
    "v1": "language_v1.md",
    "v2": "language_v2.md",
    "v4": "language_v4.md",
}

# Placed above the language guide so the model knows which rules win when they clash.
PRECEDENCE = (
    "The guide below sets wording and tone only. If it conflicts with Who you are, Safety, "
    "Scope, Grounding or Card fields above, those win. Example responses inside the guide "
    "show voice only; their length, number of questions and layout do not apply."
)

EXAMPLES: list[dict] = [
    {
        "thought": "My husband doesn't appreciate anything I do for the family.",
        "expanded": (
            "Feeling unseen after years of giving quietly is a real ache, and it shows how much "
            "you care. Wanting to be noticed is a fair need, not a weakness.\n\n"
            "Your part is speaking what you need, calmly and clearly. How your husband responds is not yours "
            "to carry. You do not have to wait for the perfect moment, only a calm one.\n\n"
            "One clear sentence can open a door."
        ),
        "hook": (
            "Your giving has been steady, and it hurts to feel unseen. Strength grows when you "
            "ask for what you need, one clear sentence at a time."
        ),
        "practise": (
            "In 3 days, choose one calm moment and tell your husband one thing you would like noticed."
        ),
    },
    {
        "thought": "My colleague got promoted instead of me. I feel jealous and inferior.",
        "expanded": (
            "Jealousy and feeling small are heavy, and they show how much you care about growing. "
            "One promotion does not decide your worth. Your colleague's rise has not taken anything "
            "from you.\n\n"
            "You can still learn even from the people you envy. Look at what they do well, "
            "and learn from it without comparing. Then ask your manager what ready looks like.\n\n"
            "Keep your own light steady today."
        ),
        "hook": (
            "Jealousy shows where your heart is ready to grow. Notice one clear thing your "
            "colleague does well this week, and let it steady you today."
        ),
        "practise": (
            "Within 5 days, ask your manager what a strong case for the next level would look like."
        ),
    },
]

# Same thoughts as EXAMPLES, in the spoken v4 voice. Examples sit last in the prompt,
# so old-voice examples would pull the model away from the v4 guide.
EXAMPLES_V4: list[dict] = [
    {
        "thought": EXAMPLES[0]["thought"],
        "expanded": (
            "The day ends. The work is done. And nobody mentions it. After enough evenings "
            "like that, you start to wonder if anyone is looking. There is nothing wrong in "
            "wanting a thank you.\n\n"
            "Maybe your husband has stopped noticing. Maybe the words do not come easily. "
            "How your husband responds is not yours to carry. But your need can stay soft "
            "and steady, without any fight at all."
        ),
        "hook": (
            "Wanting to be seen is not a weakness. You have cared for this family, and what "
            "you need deserves a place in it too."
        ),
        "practise": "In 3 days, tell your husband one thing you would like noticed.",
    },
    {
        "thought": EXAMPLES[1]["thought"],
        "expanded": (
            "Each time that new title comes up, you feel smaller. You wanted to grow too. "
            "There is no shame in feeling jealous about that.\n\n"
            "Their rise has not taken anything from you. And look closely, because jealousy "
            "points to what you want next. Even the person you envy can teach you something. "
            "You have time to find your own way here."
        ),
        "hook": (
            "Jealousy only shows how much you care about growing. Another person's promotion "
            "has not closed your road, and there is still plenty for you to learn."
        ),
        "practise": EXAMPLES[1]["practise"],
    },
]


def _fill(text: str) -> str:
    """Put the card length limits from config into the Markdown guide."""
    values = {
        "{HOOK_MIN}": config.HOOK_MIN_WORDS,
        "{HOOK_MAX}": config.HOOK_MAX_WORDS,
        "{EXP_MIN}": config.EXPANDED_MIN_WORDS,
        "{EXP_MAX}": config.EXPANDED_MAX_WORDS,
    }
    for placeholder, value in values.items():
        text = text.replace(placeholder, str(value))
    return text


def language_guide() -> str:
    """The language guide for config.PROMPT_VERSION, with runtime placeholders filled."""
    version = config.PROMPT_VERSION
    if version not in LANGUAGE_FILES:
        raise ValueError(
            f"PROMPT_VERSION must be one of {', '.join(LANGUAGE_FILES)}, not {version!r}."
        )
    text = (PROMPT_DIR / LANGUAGE_FILES[version]).read_text(encoding="utf-8")
    text = text.replace("{{perspective}}", PERSPECTIVE)
    return text.replace(
        "{{user_context}}", "the person's message, sent as the next message"
    )


def _render_examples() -> str:
    blocks = []
    examples = EXAMPLES_V4 if config.PROMPT_VERSION == "v4" else EXAMPLES
    for number, example in enumerate(examples, start=1):
        blocks.append(
            f"### Example {number}\n"
            f'Person: "{example["thought"]}"\n'
            f"- expanded: {example['expanded']}\n"
            f"- hook: {example['hook']}\n"
            f"- practise: {example['practise']}"
        )
    return "\n\n".join(blocks)


def today_line(now: datetime) -> str:
    """e.g. 'Today is Friday, 20 November 2026.' Added per request so the date is current."""
    return f"Today is {now:%A}, {now.day} {now:%B %Y}."


def build_system_prompt() -> str:
    common = _fill((PROMPT_DIR / COMMON_FILE).read_text(encoding="utf-8"))
    perspective = _fill((PROMPT_DIR / f"{PERSPECTIVE}.md").read_text(encoding="utf-8"))
    return "\n\n".join(
        [
            common,
            perspective,
            "## Language guide",
            PRECEDENCE,
            language_guide(),
            "## Examples",
            _render_examples(),
        ]
    )
