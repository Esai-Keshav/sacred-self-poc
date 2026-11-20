import re
from datetime import datetime

import pytest

import config
from prompts import (
    EXAMPLES,
    PRECEDENCE,
    PROMPT_DIR,
    build_system_prompt,
    language_guide,
    today_line,
)


def word_count(text: str) -> int:
    return len(text.split())


def test_hooks_within_word_range():
    for example in EXAMPLES:
        assert config.HOOK_MIN_WORDS <= word_count(example["hook"]) <= config.HOOK_MAX_WORDS


def test_expanded_within_word_range():
    for example in EXAMPLES:
        assert (
            config.EXPANDED_MIN_WORDS
            <= word_count(example["expanded"])
            <= config.EXPANDED_MAX_WORDS
        )


def test_practise_is_one_short_sentence_with_deadline():
    deadline_words = ["today", "tonight", "tomorrow", "day", "days", "week", "hour", "hours", "by", "within"]
    for example in EXAMPLES:
        text = example["practise"].lower()
        assert word_count(example["practise"]) <= 25, example["practise"]
        assert any(word in text for word in deadline_words), example["practise"]


def test_say_it_is_first_person():
    for example in EXAMPLES:
        assert example["say_it"].startswith("I "), example["say_it"]


def test_examples_obey_punctuation_rules():
    for example in EXAMPLES:
        for name in ("hook", "practise", "say_it", "expanded"):
            assert "!" not in example[name], (name, example[name])
        for name in ("hook", "practise", "say_it"):
            assert "?" not in example[name], (name, example[name])
        assert example["expanded"].count("?") <= 1


def test_prompt_files_exist():
    assert (PROMPT_DIR / "language_v1.md").is_file()
    assert (PROMPT_DIR / "language_v2.md").is_file()
    assert (PROMPT_DIR / "willingness.md").is_file()


def test_default_guide_is_v2(monkeypatch):
    monkeypatch.setattr(config, "PROMPT_VERSION", "v2")
    assert "Core Language & Voice" in language_guide()


def test_v1_guide_is_master_prompt_filled_for_willingness(monkeypatch):
    monkeypatch.setattr(config, "PROMPT_VERSION", "v1")
    guide = language_guide()
    assert "Master System Prompt" in guide
    assert "willingness" in guide
    assert "{{" not in guide


def test_unknown_prompt_version_is_rejected(monkeypatch):
    monkeypatch.setattr(config, "PROMPT_VERSION", "v9")
    with pytest.raises(ValueError, match="v1, v2"):
        language_guide()


def test_prompt_contains_language_guide_after_precedence():
    prompt = build_system_prompt()
    guide = language_guide()
    assert guide in prompt
    assert prompt.index(PRECEDENCE) < prompt.index(guide)
    assert "Example responses inside the guide show voice only" in prompt


def test_prompt_speaks_as_sacred_self_not_lakshana():
    prompt = build_system_prompt()
    assert "Sacred Self" in prompt
    for old_line in ("Living in a joint family taught me", "You are Lakshana"):
        assert old_line not in prompt


def test_prompt_is_secular():
    prompt = build_system_prompt().lower()
    for spiritual_word in ("divine", "sanskrit", "gita", "sankalpa", "seva", "swadharma"):
        assert spiritual_word not in prompt, spiritual_word


def test_prompt_contains_example_thoughts_and_limits():
    prompt = build_system_prompt()
    for example in EXAMPLES:
        assert example["thought"] in prompt
    assert str(config.HOOK_MIN_WORDS) in prompt
    assert str(config.HOOK_MAX_WORDS) in prompt


def test_prompt_has_no_unfilled_placeholders():
    prompt = build_system_prompt()
    assert "{HOOK_" not in prompt
    assert "{EXP_" not in prompt
    assert "{{" not in prompt


def test_prompt_contains_all_teachings():
    prompt = build_system_prompt()
    for teaching in (
        "Challenges refine us",
        "Triggers are doorways",
        "Effort is ours, results are not",
        "One clear intention",
        "The key is within",
        "A willing heart is a teachable heart",
        "Service",
        "Effort invites support",
        "Our own way of shining",
    ):
        assert teaching in prompt


def test_prompt_says_no_helpline_numbers():
    assert "Do not write helpline numbers" in build_system_prompt()


def test_system_prompt_has_no_xml_tags():
    assert re.search(r"</?[a-z_]+>", build_system_prompt()) is None


def test_today_line_formats_date():
    assert today_line(datetime(2026, 11, 20)) == "Today is Friday, 20 November 2026."
    assert today_line(datetime(2026, 11, 5)) == "Today is Thursday, 5 November 2026."
