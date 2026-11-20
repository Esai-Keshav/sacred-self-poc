from datetime import datetime

import streamlit as st

import config
import db

# (key, label) for each thumbs rating, in the order they are saved.
FEEDBACK_ITEMS = [
    ("overall", "Overall"),
    ("hook", "Hook"),
    ("expanded", "Expanded"),
    ("practise", "Practise"),
    ("say_it", "Say it"),
]


def to_vote(value: int | None) -> int | None:
    """st.feedback("thumbs") gives 1 for up and 0 for down. Store down as -1."""
    if value is None:
        return None
    return 1 if value == 1 else -1


def format_when(created_at: str) -> str:
    dt = datetime.fromisoformat(created_at).astimezone(config.DISPLAY_TZ)
    return f"{dt:%Y-%m-%d %H:%M} {config.DISPLAY_TZ_LABEL}"


def render_card(card: dict) -> None:
    """The whole card at once: hook, body, practise and say-it."""
    with st.container(border=True):
        st.markdown(f"**{card['hook']}**")
        st.write(card["expanded"])
        st.markdown(f"**{config.PRACTISE_LABEL}**")
        st.write(card["practise"])
        if config.INCLUDE_SAY_IT:
            st.markdown(f"**{config.SAY_IT_LABEL}**")
            st.markdown(f"> {card['say_it']}")


def feedback_line(row: dict) -> str:
    """One submission as a line: rated parts as 'Label 👍/👎', then the comment."""
    parts = []
    for name, label in FEEDBACK_ITEMS:
        vote = row.get(name)
        if vote is not None:
            parts.append(f"{label} {'👍' if vote == 1 else '👎'}")
    if row.get("comment"):
        parts.append(f"💬 {row['comment']}")
    return " · ".join(parts)


def render_feedback(card_id: int, feedback_rows: list[dict]) -> None:
    """Filled feedback for this card, then the thumbs form, an optional comment and Send."""
    st.markdown(f"**{config.FEEDBACK_SO_FAR}**")
    lines = [line for line in (feedback_line(row) for row in feedback_rows) if line]
    if not lines:
        st.caption(config.FEEDBACK_NONE)
    for line in lines:
        st.markdown(f"- {line}")
    with st.expander(config.FEEDBACK_HEADING):
        votes = []
        for name, label in FEEDBACK_ITEMS:
            if name == "say_it" and not config.INCLUDE_SAY_IT:
                votes.append(None)
                continue
            label_col, vote_col = st.columns([1, 2])
            label_col.markdown(f"**{label}**")
            votes.append(to_vote(vote_col.feedback("thumbs", key=f"{name}_{card_id}")))
        comment = st.text_area(config.FEEDBACK_COMMENT_LABEL, key=f"comment_{card_id}")
        if st.button(config.FEEDBACK_SUBMIT_LABEL, key=f"send_{card_id}"):
            try:
                db.save_feedback(db.build_feedback_row(card_id, *votes, comment))
                st.success(config.FEEDBACK_THANKS)
            except Exception:
                st.error(config.ERROR_FEEDBACK)
