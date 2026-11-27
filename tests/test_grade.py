import sys
from pathlib import Path

import pytest
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import FunctionModel

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from grade import Grade, card_text, grade, lifted  # noqa: E402

CARD = {
    "id": 1,
    "thought": "I failed again.",
    "hook": "You are not finished yet.",
    "expanded": "Failing is information, and you can use it.",
    "practise": "Write down one thing you will try tomorrow.",
}

GRADE = {
    "before": "guilt",
    "after": "willingness",
    "hook": 4,
    "expanded": 3,
    "practise": 5,
    "weakest_line": "Failing is information, and you can use it.",
    "why": "The reader feels ready to try again.",
}


@pytest.mark.parametrize(
    ("before", "after", "expected"),
    [
        ("guilt", "willingness", True),
        ("fear", "courage", False),
        ("willingness", "willingness", False),
        ("shame", "acceptance", True),
    ],
)
def test_lifted(before, after, expected):
    assert lifted(before, after) is expected


def test_card_text_includes_thought_and_all_parts():
    text = card_text(CARD)
    assert "I failed again." in text
    assert "You are not finished yet." in text
    assert "Failing is information, and you can use it." in text
    assert "Write down one thing you will try tomorrow." in text


def test_grade_returns_model_output():
    def fn(messages, info):
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, GRADE)])

    result = grade(CARD, model=FunctionModel(fn))
    assert result == Grade(**GRADE)
