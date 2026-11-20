from datetime import datetime
from pathlib import Path

import config

PROMPT_DIR = Path(__file__).parent / "prompt"

LANGUAGE_FILES = {"v1": "language_v1.md", "v2": "language_v2.md"}

# Placed above the language guide so the model knows which rules win when they clash.
PRECEDENCE = (
    "The guide below sets wording and tone only. If it conflicts with Safety, Scope, "
    "Grounding or Card fields above, those win. Example responses inside the guide show "
    "voice only; their length, number of questions and layout do not apply."
)

EXAMPLES: list[dict] = [
    {
        "thought": "My husband doesn't appreciate anything I do for the family.",
        "expanded": (
            "Your giving has been steady, and it hurts when it goes unnoticed. Wanting to be "
            "seen is a fair need, not a weakness. Your part is the sincere effort of saying what "
            "you need, calmly. How he responds is not yours to carry. Each honest try teaches "
            "you what words land and when."
        ),
        "hook": (
            "Your giving has been steady, and it hurts to feel unseen. Strength grows when you "
            "ask for what you need, one clear sentence at a time."
        ),
        "practise": (
            "In 3 days, choose one calm moment and tell him one thing you would like him to notice."
        ),
        "say_it": (
            "I do so much for our family, and it would mean a lot to me if you noticed."
        ),
    },
    {
        "thought": "My colleague got promoted instead of me. I feel jealous and inferior.",
        "expanded": (
            "Jealousy and feeling inferior are heavy to carry, and it is honest of you to name "
            "them. One promotion does not decide your worth or your ability. Your part is steady "
            "effort, and the outcome is not yours to hold. Look at the process: what did your "
            "colleague do regularly that you could try?"
        ),
        "hook": (
            "This promotion is a mirror, showing where you are ready to grow. Learn one clear "
            "thing from your colleague's path this week, and let it steady you."
        ),
        "practise": (
            "Within 5 days, ask your manager what a strong case for the next level would look like."
        ),
        "say_it": (
            "I feel jealous, and I am still willing to learn what it takes to grow."
        ),
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
    text = text.replace("{{perspective}}", "willingness")
    return text.replace("{{user_context}}", "the person's message, sent as the next message")


def _render_examples() -> str:
    blocks = []
    for number, example in enumerate(EXAMPLES, start=1):
        blocks.append(
            f"### Example {number}\n"
            f'Person: "{example["thought"]}"\n'
            f"- expanded: {example['expanded']}\n"
            f"- hook: {example['hook']}\n"
            f"- practise: {example['practise']}\n"
            f"- say_it: {example['say_it']}"
        )
    return "\n\n".join(blocks)


def today_line(now: datetime) -> str:
    """e.g. 'Today is Friday, 20 November 2026.' Added per request so the date is current."""
    return f"Today is {now:%A}, {now.day} {now:%B %Y}."


def build_system_prompt() -> str:
    willingness = _fill((PROMPT_DIR / "willingness.md").read_text(encoding="utf-8"))
    return "\n\n".join(
        [
            willingness,
            "## Language guide",
            PRECEDENCE,
            language_guide(),
            "## Examples",
            _render_examples(),
        ]
    )
