import streamlit as st

import config
from prompts import PERSPECTIVES


def render_answers(answers: dict[str, str]) -> None:
    """The four answers side by side."""
    for col, perspective in zip(st.columns(len(PERSPECTIVES)), PERSPECTIVES):
        with col:
            # Same height for all four boxes; longer text scrolls inside.
            with st.container(border=True, height=config.ANSWER_BOX_HEIGHT):
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
