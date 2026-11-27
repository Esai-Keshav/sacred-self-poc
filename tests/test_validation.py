import pytest
from pydantic_ai import Agent, ModelRetry
from pydantic_ai.exceptions import UnexpectedModelBehavior
from pydantic_ai.messages import ModelResponse, ToolCallPart
from pydantic_ai.models.function import FunctionModel

import agent as agent_module
import config
from agent import (
    Card,
    check_expanded,
    check_hook_length,
    check_no_gender,
    check_practise,
    check_punctuation,
    check_stock_word,
    word_count,
)


def card(**overrides) -> Card:
    fields = {
        "expanded": "A calm body of text.",
        "hook": " ".join(["word"] * config.HOOK_MIN_WORDS),
        "practise": " ".join(["word"] * config.PRACTISE_MIN_WORDS),
    }
    fields.update(overrides)
    return Card(**fields)


def test_word_count_splits_on_whitespace():
    assert word_count("  one two\nthree  ") == 3


@pytest.mark.parametrize("n", [config.HOOK_MIN_WORDS, 27, config.HOOK_MAX_WORDS])
def test_hook_length_in_range_is_accepted(n):
    check_hook_length(" ".join(["word"] * n))


@pytest.mark.parametrize("n", [config.HOOK_MIN_WORDS - 1, config.HOOK_MAX_WORDS + 1])
def test_hook_length_out_of_range_retries(n):
    with pytest.raises(ModelRetry, match=f"{n} words"):
        check_hook_length(" ".join(["word"] * n))


def test_expanded_at_max_is_accepted():
    check_expanded(" ".join(["word"] * config.EXPANDED_MAX_WORDS))


def test_expanded_over_max_retries():
    n = config.EXPANDED_MAX_WORDS + 1
    with pytest.raises(ModelRetry, match=f"{n} words"):
        check_expanded(" ".join(["word"] * n))


@pytest.mark.parametrize("n", [config.PRACTISE_MIN_WORDS, config.PRACTISE_MAX_WORDS])
def test_practise_length_in_range_is_accepted(n):
    check_practise(" ".join(["word"] * n))


@pytest.mark.parametrize("n", [config.PRACTISE_MIN_WORDS - 1, config.PRACTISE_MAX_WORDS + 1])
def test_practise_length_out_of_range_retries(n):
    with pytest.raises(ModelRetry, match=f"{n} words"):
        check_practise(" ".join(["word"] * n))


def test_expanded_semicolon_retries():
    with pytest.raises(ModelRetry, match="semicolon"):
        check_expanded("This hurts; you know it.")


@pytest.mark.parametrize("text", ["It can sting.", "It Stings, doesn't it?", "A stinging word."])
def test_stock_word_retries(text):
    with pytest.raises(ModelRetry, match="sting"):
        check_stock_word(text)


@pytest.mark.parametrize("text", ["You keep resisting.", "An interesting day.", "A lasting bond."])
def test_stock_word_ignores_longer_words(text):
    check_stock_word(text)


@pytest.mark.parametrize(
    "text", ["She left you out.", "Tell him today.", "It was her dinner.", "His words hurt."]
)
def test_gendered_pronoun_retries(text):
    with pytest.raises(ModelRetry, match="gender"):
        check_no_gender(text)


@pytest.mark.parametrize(
    "text", ["Your friend left you out.", "They may not know.", "The other day, here at home."]
)
def test_neutral_text_passes_gender_check(text):
    check_no_gender(text)


def test_plain_card_passes_punctuation_check():
    check_punctuation(card())


def test_hook_may_end_with_one_exclamation_mark():
    check_punctuation(card(hook="Go again!"))


@pytest.mark.parametrize("hook", ["Wow! Go again.", "Go again!!"])
def test_hook_exclamation_mark_not_at_end_retries(hook):
    with pytest.raises(ModelRetry, match="exclamation"):
        check_punctuation(card(hook=hook))


def test_exclamation_mark_in_expanded_retries():
    with pytest.raises(ModelRetry, match="exclamation"):
        check_punctuation(card(expanded="Wow!"))


def test_practise_may_end_with_one_exclamation_mark():
    check_punctuation(card(practise="Do it. Let it speak before you do!"))


@pytest.mark.parametrize("practise", ["Wow! Do it.", "Do it!!"])
def test_practise_exclamation_mark_not_at_end_retries(practise):
    with pytest.raises(ModelRetry, match="exclamation"):
        check_punctuation(card(practise=practise))


@pytest.mark.parametrize("field", ["hook", "practise"])
def test_question_mark_outside_expanded_retries(field):
    with pytest.raises(ModelRetry, match="question mark"):
        check_punctuation(card(**{field: "Really?"}))


def test_one_question_in_expanded_is_allowed():
    check_punctuation(card(expanded="What would help most? Start there."))


def test_two_questions_in_expanded_retry():
    with pytest.raises(ModelRetry, match="more than one question"):
        check_punctuation(card(expanded="What is this? What else?"))


@pytest.mark.parametrize(
    ("args", "reason"),
    [
        ({"expanded": "a", "hook": "b", "practise": "c"}, "The hook is too long."),
        ({"expanded": "a", "practise": "c"}, "hook: Field required"),
    ],
)
def test_run_prints_retry_reason_when_retries_run_out(monkeypatch, capsys, args, reason):
    def reply(messages, info):
        return ModelResponse(parts=[ToolCallPart(info.output_tools[0].name, args)])

    test_agent = Agent(FunctionModel(reply), output_type=Card, retries=1)

    @test_agent.output_validator
    def _always_retry(output):
        raise ModelRetry("The hook is too long.")

    monkeypatch.setattr(agent_module, "get_agent", lambda perspective: test_agent)
    with pytest.raises(UnexpectedModelBehavior):
        agent_module._run("My friend ignored me.", "love_joy")
    assert f"[love_joy] [retry 1] {reason}" in capsys.readouterr().out
