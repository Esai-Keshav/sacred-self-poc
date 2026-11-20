import pytest

from ui import feedback_line, format_when, to_vote


@pytest.mark.parametrize(("widget", "stored"), [(1, 1), (0, -1), (None, None)])
def test_to_vote_maps_widget_value_to_stored_vote(widget, stored):
    assert to_vote(widget) == stored


def test_format_when_shows_local_time_with_label():
    assert format_when("2026-11-20T00:00:00+00:00") == "2026-11-20 05:30 IST"


def test_feedback_line_lists_rated_parts_and_comment():
    row = {"overall": 1, "hook": None, "expanded": None, "practise": -1, "say_it": None, "comment": "good"}
    assert feedback_line(row) == "Overall 👍 · Practise 👎 · 💬 good"


def test_feedback_line_empty_when_nothing_filled():
    row = {"overall": None, "hook": None, "expanded": None, "practise": None, "say_it": None, "comment": None}
    assert feedback_line(row) == ""


def test_feedback_line_comment_only():
    row = {"overall": None, "hook": None, "expanded": None, "practise": None, "say_it": None, "comment": "text"}
    assert feedback_line(row) == "💬 text"
