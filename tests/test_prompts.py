import re
from datetime import datetime

import pytest

import config
from prompts import (
    EXAMPLES,
    EXAMPLES_V4,
    PRECEDENCE,
    PROMPT_DIR,
    build_system_prompt,
    language_guide,
    today_line,
)


def word_count(text: str) -> int:
    return len(text.split())


def test_hooks_within_word_range():
    for example in EXAMPLES + EXAMPLES_V4:
        assert config.HOOK_MIN_WORDS <= word_count(example["hook"]) <= config.HOOK_MAX_WORDS


def test_expanded_within_word_range():
    for example in EXAMPLES + EXAMPLES_V4:
        assert (
            config.EXPANDED_MIN_WORDS
            <= word_count(example["expanded"])
            <= config.EXPANDED_MAX_WORDS
        )


def test_expanded_has_two_or_three_paragraphs():
    for example in EXAMPLES:
        paragraphs = example["expanded"].split("\n\n")
        assert 2 <= len(paragraphs) <= 3, example["expanded"]


def test_v4_expanded_has_exactly_two_paragraphs():
    for example in EXAMPLES_V4:
        assert len(example["expanded"].split("\n\n")) == 2, example["expanded"]


def test_common_prompt_asks_for_two_paragraphs_without_closing_line():
    common = (PROMPT_DIR / "language_common.md").read_text(encoding="utf-8")
    willingness = (PROMPT_DIR / "willingness.md").read_text(encoding="utf-8")
    assert "exactly 2 short paragraphs" in common
    assert "closing line" not in common
    assert "4 to 10 words" not in willingness


def test_practise_is_one_short_sentence_with_deadline():
    deadline_words = ["today", "tonight", "tomorrow", "day", "days", "week", "hour", "hours", "by", "within"]
    for example in EXAMPLES + EXAMPLES_V4:
        text = example["practise"].lower()
        assert word_count(example["practise"]) <= 25, example["practise"]
        assert any(word in text for word in deadline_words), example["practise"]


def test_examples_have_no_say_it():
    for example in EXAMPLES + EXAMPLES_V4:
        assert "say_it" not in example
    assert "say_it" not in build_system_prompt()


def test_v4_examples_name_the_task_only_in_practise():
    for example in EXAMPLES_V4:
        words = re.findall(r"[a-z']+", example["practise"].lower())
        runs = {" ".join(words[i : i + 3]) for i in range(len(words) - 2)}
        body = " ".join(re.findall(r"[a-z']+", f"{example['hook']} {example['expanded']}".lower()))
        assert not [run for run in runs if run in body], example["practise"]


def test_v4_practise_holds_one_task():
    second_task = r"\band (tell|write|ask|offer|send|list|choose|practise|set)\b"
    for example in EXAMPLES_V4:
        assert re.search(second_task, example["practise"].lower()) is None, example["practise"]


def test_common_prompt_keeps_task_rule_and_crisis_exception():
    common = (PROMPT_DIR / "language_common.md").read_text(encoding="utf-8")
    assert "Only practise names the task" in common
    assert "does not apply to a crisis card" in common


def test_crisis_rule_forbids_promising_presence():
    common = (PROMPT_DIR / "language_common.md").read_text(encoding="utf-8")
    assert """never say "I'm here with you\"""" in common
    assert "never claim to stay with the person" in common


def test_v4_examples_avoid_stock_closers():
    for example in EXAMPLES_V4:
        text = f"{example['hook']} {example['expanded']}".lower()
        for phrase in ("is still yours", "still matters", "was real", "meet this moment"):
            assert phrase not in text, phrase


def test_v4_has_no_repeated_self_talk():
    assert "tell yourself" not in v4_text()


def test_examples_obey_punctuation_rules():
    for example in EXAMPLES + EXAMPLES_V4:
        for name in ("hook", "practise", "expanded"):
            assert "!" not in example[name], (name, example[name])
        for name in ("hook", "practise"):
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


def test_prompt_speaks_as_lakshana_in_first_person():
    prompt = build_system_prompt()
    assert "You are Lakshana Shravan" in prompt
    assert "in the first person" in prompt
    for story_name in ("Joint family", "Ice House", "Homeschooling"):
        assert story_name in prompt
    assert "Sacred Self" in prompt


def test_prompt_is_secular():
    prompt = build_system_prompt().lower()
    for spiritual_word in ("divine", "sanskrit", "gita", "sankalpa", "seva", "swadharma"):
        assert spiritual_word not in prompt, spiritual_word


def test_prompt_contains_example_thoughts_and_limits():
    prompt = build_system_prompt()
    for example in EXAMPLES + EXAMPLES_V4:
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


def test_v2_guide_sections_in_order():
    guide = (PROMPT_DIR / "language_v2.md").read_text(encoding="utf-8")
    headings = [
        "## 1. Voice",
        "## 2. Vocabulary",
        "## 3. Sentences",
        "## 4. Questions",
        "## 5. Conversation flow",
        "## 6. Imagery and explanation",
        "## 7. Examples",
    ]
    positions = [guide.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_v2_guide_has_only_willingness_example():
    guide = (PROMPT_DIR / "language_v2.md").read_text(encoding="utf-8")
    for other_perspective in ("Reasoning Mind", "Loving Heart", "Still Witness"):
        assert other_perspective not in guide


def v4_text() -> str:
    guide = (PROMPT_DIR / "language_v4.md").read_text(encoding="utf-8")
    cards = " ".join(
        example[name]
        for example in EXAMPLES_V4
        for name in ("expanded", "hook", "practise")
    )
    return f"{guide} {cards}".lower()


def test_v4_guide_loads(monkeypatch):
    monkeypatch.setattr(config, "PROMPT_VERSION", "v4")
    assert "Spoken Language & Voice" in language_guide()


def test_v4_guide_sections_in_order():
    guide = (PROMPT_DIR / "language_v4.md").read_text(encoding="utf-8")
    headings = [
        "## 1. Voice",
        "## 2. Vocabulary",
        "## 3. Sentences",
        "## 4. Questions",
        "## 5. Conversation flow",
        "## 6. Imagery and explanation",
        "## 7. Examples",
    ]
    positions = [guide.index(heading) for heading in headings]
    assert positions == sorted(positions)


def test_v4_has_no_religious_words():
    pattern = r"\b(god|gods|divine|sacred|soul|souls|blessed|bless|blessing|krishna|gita|saint|saints)\b"
    # The app name is the one allowed use of "Sacred".
    assert re.search(pattern, v4_text().replace("sacred self", "")) is None


def test_v4_has_no_em_dashes_outside_title():
    body = v4_text().split("\n", 1)[1]
    assert "—" not in body


def test_v4_has_no_bedtime_sign_offs():
    text = v4_text()
    for phrase in ("good night", "tonight", "rest now", "inhale", "exhale"):
        assert phrase not in text, phrase


def test_v4_prompt_renders_v4_examples(monkeypatch):
    monkeypatch.setattr(config, "PROMPT_VERSION", "v4")
    prompt = build_system_prompt()
    assert EXAMPLES_V4[0]["hook"] in prompt
    assert EXAMPLES[0]["hook"] not in prompt


def test_v2_prompt_keeps_old_examples(monkeypatch):
    monkeypatch.setattr(config, "PROMPT_VERSION", "v2")
    prompt = build_system_prompt()
    assert EXAMPLES[0]["hook"] in prompt
    assert EXAMPLES_V4[0]["hook"] not in prompt


def test_common_comes_before_perspective_with_safety_first():
    prompt = build_system_prompt()
    assert prompt.startswith("# Common language\n\n## Safety")
    assert prompt.index("## Card fields") < prompt.index("# Willingness bot")


@pytest.mark.parametrize("version", ["v1", "v2", "v4"])
def test_every_version_includes_common_rules(monkeypatch, version):
    monkeypatch.setattr(config, "PROMPT_VERSION", version)
    prompt = build_system_prompt()
    for heading in ("## Safety", "## Scope", "## Grounding", "## Practise", "## Card fields"):
        assert prompt.count(heading) == 1, heading


def test_perspective_file_holds_no_common_sections():
    text = (PROMPT_DIR / "willingness.md").read_text(encoding="utf-8")
    for heading in ("## Safety", "## Scope", "## Grounding", "## Practise", "## Card fields", "## Who you are"):
        assert heading not in text, heading


def test_today_line_formats_date():
    assert today_line(datetime(2026, 11, 20)) == "Today is Friday, 20 November 2026."
    assert today_line(datetime(2026, 11, 5)) == "Today is Thursday, 5 November 2026."
