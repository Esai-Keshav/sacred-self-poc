import pytest

import agent as agent_module
import config
import db
from agent import Card, UserError, get_cards
from prompts import build_system_prompt

CARD = Card(expanded="a body", hook="a hook", practise="a step")


class FakeUsage:
    input_tokens = 1
    output_tokens = 2


class FakeResult:
    usage = FakeUsage()

    def __init__(self, output):
        self.output = output


@pytest.fixture
def saved(monkeypatch):
    """Record the perspective of every saved card, in save order."""
    order = []

    def save(*args):
        order.append(args[-1])
        return len(order)

    monkeypatch.setattr(db, "save_card", save)
    return order


def fake_run(failing=(), output=CARD):
    def run(situation, perspective):
        if perspective in failing:
            raise UserError(f"{perspective} failed")
        return situation, FakeResult(output), None

    return run


def test_love_joy_prompt_has_common_rules_and_not_willingness_voice():
    prompt = build_system_prompt("love_joy")
    assert "# Common language" in prompt
    assert "I can see this with more compassion." in prompt
    assert "the reader must reach Love & Joy" in prompt
    assert "experience joy" in prompt
    assert "must reach Willingness" not in prompt
    assert "# Willingness bot" not in prompt
    assert "High-Energy Willingness Voice" not in prompt
    assert "## Examples" not in prompt
    assert "{HOOK_MIN}" not in prompt


def test_default_prompt_is_willingness():
    assert build_system_prompt() == build_system_prompt("willingness")


def test_get_cards_returns_both_in_display_order(monkeypatch, saved):
    monkeypatch.setattr(agent_module, "_run", fake_run())
    results = get_cards("My friend ignored me.")
    assert [r[0] for r in results] == list(config.PERSPECTIVES) == ["willingness", "love_joy"]
    # Saved in reverse, so History (newest id first) lists Willingness first.
    assert saved == ["love_joy", "willingness"]
    assert [r[2] for r in results] == [2, 1]


def test_one_failing_perspective_keeps_the_other(monkeypatch, saved):
    monkeypatch.setattr(agent_module, "_run", fake_run(failing={"willingness"}))
    results = get_cards("My friend ignored me.")
    assert results[0] == ("willingness", None, None, True)
    assert results[1] == ("love_joy", CARD, 1, False)


def test_all_failing_raises_the_first_error(monkeypatch, saved):
    monkeypatch.setattr(agent_module, "_run", fake_run(failing=set(config.PERSPECTIVES)))
    with pytest.raises(UserError, match="willingness failed"):
        get_cards("My friend ignored me.")


def test_fallback_is_not_saved(monkeypatch, saved):
    monkeypatch.setattr(agent_module, "_run", fake_run(output=agent_module.Fallback(message="FALLBACK")))
    results = get_cards("What is the capital of France?")
    assert [r[1] for r in results] == [None, None]
    assert saved == []


def test_show_love_off_runs_only_willingness(monkeypatch, saved):
    monkeypatch.setattr(config, "SHOW_LOVE", False)
    monkeypatch.setattr(agent_module, "_run", fake_run())
    assert [r[0] for r in get_cards("My friend ignored me.")] == ["willingness"]
    assert saved == ["willingness"]
