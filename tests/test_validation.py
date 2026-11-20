import pytest
from pydantic_ai import ModelRetry

import config
from agent import WillingnessCard, check_hook_length, check_punctuation, word_count


def card(**overrides) -> WillingnessCard:
    fields = {
        "expanded": "A calm body of text.",
        "hook": " ".join(["word"] * config.HOOK_MIN_WORDS),
        "practise": "In 3 days, pick one calm moment.",
        "say_it": "I can ask for what I need.",
    }
    fields.update(overrides)
    return WillingnessCard(**fields)


def test_word_count_splits_on_whitespace():
    assert word_count("  one two\nthree  ") == 3


@pytest.mark.parametrize("n", [config.HOOK_MIN_WORDS, 27, config.HOOK_MAX_WORDS])
def test_hook_length_in_range_is_accepted(n):
    check_hook_length(" ".join(["word"] * n))


@pytest.mark.parametrize("n", [config.HOOK_MIN_WORDS - 1, config.HOOK_MAX_WORDS + 1])
def test_hook_length_out_of_range_retries(n):
    with pytest.raises(ModelRetry, match=f"{n} words"):
        check_hook_length(" ".join(["word"] * n))


def test_plain_card_passes_punctuation_check():
    check_punctuation(card())


@pytest.mark.parametrize("field", ["hook", "practise", "say_it", "expanded"])
def test_exclamation_mark_anywhere_retries(field):
    with pytest.raises(ModelRetry, match="exclamation"):
        check_punctuation(card(**{field: "Wow!"}))


@pytest.mark.parametrize("field", ["hook", "practise", "say_it"])
def test_question_mark_outside_expanded_retries(field):
    with pytest.raises(ModelRetry, match="question mark"):
        check_punctuation(card(**{field: "Really?"}))


def test_one_question_in_expanded_is_allowed():
    check_punctuation(card(expanded="What would help most? Start there."))


def test_two_questions_in_expanded_retry():
    with pytest.raises(ModelRetry, match="more than one question"):
        check_punctuation(card(expanded="What is this? What else?"))
