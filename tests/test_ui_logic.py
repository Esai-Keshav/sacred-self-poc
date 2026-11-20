import pytest

from ui import format_when, to_vote


@pytest.mark.parametrize(("widget", "stored"), [(1, 1), (0, -1), (None, None)])
def test_to_vote_maps_widget_value_to_stored_vote(widget, stored):
    assert to_vote(widget) == stored


def test_format_when_shows_local_time_with_label():
    assert format_when("2026-11-20T00:00:00+00:00") == "2026-11-20 05:30 IST"
