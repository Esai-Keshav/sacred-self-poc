import sys
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pydantic import BaseModel, Field  # noqa: E402
from pydantic_ai import Agent  # noqa: E402

import config  # noqa: E402
import db  # noqa: E402

LEVELS = ["shame", "guilt", "apathy", "grief", "fear", "desire", "anger", "pride", "courage", "neutrality", "willingness", "acceptance"]
Level = Literal["shame", "guilt", "apathy", "grief", "fear", "desire", "anger", "pride", "courage", "neutrality", "willingness", "acceptance"]


class Grade(BaseModel):
    before: Level = Field(description="The reader's emotional level from their message")
    after: Level = Field(description="The level a reader would most likely feel after reading the whole card")
    hook: int = Field(ge=1, le=5, description="How much the hook lifts the reader")
    expanded: int = Field(ge=1, le=5, description="How much the expanded part lifts the reader")
    practise: int = Field(ge=1, le=5, description="How much the practise part lifts the reader")
    weakest_line: str = Field(description="Exact line from the card that pulls the level down")
    why: str = Field(description="One sentence explaining the grade")


def lifted(before: str, after: str) -> bool:
    return LEVELS.index(after) >= LEVELS.index("willingness") and LEVELS.index(after) > LEVELS.index(before)


RUBRIC = """You are a strict judge of emotional lift. Grade the reader's likely state after reading the card, not the writer's intent.

Levels, low to high:
- shame: worthless, hiding
- guilt: blame, regret
- apathy: hopeless, stuck
- grief: loss, sadness
- fear: anxious, unsafe
- desire: craving, wanting
- anger: resentment, frustration
- pride: defensive superiority
- courage: first empowerment, can try
- neutrality: okay, flexible
- willingness: energised, optimistic, eager to act and learn
- acceptance: at peace, responsible

Comforting text that leaves the reader sitting in the feeling does not lift them.
Quote the weakest line exactly."""


def card_text(card: dict) -> str:
    return f"Person: {card['thought']}\n\nHook: {card['hook']}\n\nExpanded: {card['expanded']}\n\nPractise: {card['practise']}"


def get_judge(model=None) -> Agent[None, Grade]:
    return Agent(model or config.MODEL_NAME, output_type=Grade, system_prompt=RUBRIC)


def grade(card: dict, model=None) -> Grade:
    return get_judge(model).run_sync(card_text(card)).output


def main(argv: list[str]) -> None:
    n = int(argv[1]) if len(argv) > 1 else 1
    # The rubric measures energised lift, so it only fits Willingness cards.
    cards = [c for c in db.list_cards() if c.get("perspective", "willingness") == "willingness"][:n]
    lifted_count = 0
    for card in cards:
        g = grade(card)
        ok = lifted(g.before, g.after)
        lifted_count += ok
        mark = "✓ lifted" if ok else "✗ not lifted"
        print(f"#{card['id']} {g.before} → {g.after} {mark} | hook {g.hook}/5 · expanded {g.expanded}/5 · practise {g.practise}/5")
        print(f'  weakest: "{g.weakest_line}"')
        print(f"  why: {g.why}")
    print(f"Lifted {lifted_count}/{len(cards)} cards")


if __name__ == "__main__":
    main(sys.argv)
