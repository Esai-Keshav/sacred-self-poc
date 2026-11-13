import streamlit as st

import config
from prompts import PERSPECTIVES


def render_answers(answers: dict[str, str]) -> None:
    """The four answers as cards in a grid. Cards grow to fit their text, so nothing scrolls."""
    per_row = config.ANSWER_CARDS_PER_ROW
    for start in range(0, len(PERSPECTIVES), per_row):
        row = PERSPECTIVES[start : start + per_row]
        for col, perspective in zip(st.columns(per_row), row):
            with col:
                # "stretch" makes the cards in one row the same height.
                with st.container(border=True, height="stretch"):
                    st.subheader(perspective.title)
                    st.caption(perspective.tagline)
                    st.write(answers[perspective.key])


def copy_text(question: str, answers: dict[str, str]) -> str:
    """Question and the four answers as plain text, for pasting elsewhere."""
    parts = [f"{config.COPY_QUESTION_LABEL}: {question}"]
    for p in PERSPECTIVES:
        parts.append(f"{p.title}\n{answers[p.key]}")
    return "\n\n".join(parts)


def render_copy_box(question: str, answers: dict[str, str]) -> None:
    st.subheader(config.COPY_HEADING)
    st.code(copy_text(question, answers), language=None, wrap_lines=True)
