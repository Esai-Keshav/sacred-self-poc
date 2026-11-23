from db import build_card_row, build_feedback_row

CARD = {
    "hook": "a hook",
    "expanded": "an expanded body",
    "practise": "In 3 days, do one thing.",
}


def test_build_card_row_has_exact_columns():
    row = build_card_row("my thought", CARD, "openai:x", 10, 20, 0.5)
    assert row == {
        "thought": "my thought",
        "model": "openai:x",
        "hook": "a hook",
        "expanded": "an expanded body",
        "practise": "In 3 days, do one thing.",
        "say_it": "",
        "input_tokens": 10,
        "output_tokens": 20,
        "cost_usd": 0.5,
    }


def test_build_feedback_row_keeps_comment():
    row = build_feedback_row(7, 1, None, None, -1, "helpful")
    assert row == {
        "card_id": 7,
        "overall": 1,
        "hook": None,
        "expanded": None,
        "practise": -1,
        "comment": "helpful",
    }


def test_build_feedback_row_empty_comment_is_none():
    row = build_feedback_row(7, 1, None, None, None, "")
    assert row["comment"] is None
