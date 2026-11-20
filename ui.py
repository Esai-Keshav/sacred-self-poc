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
    with st.container(border=True):
        st.markdown(f"**{card['hook']}**")
        with st.expander(config.EXPANDED_LABEL):
            st.write(card["expanded"])
            st.markdown(f"**{config.PRACTISE_LABEL}**")
            st.write(card["practise"])
            st.markdown(f"**{config.SAY_IT_LABEL}**")
            st.markdown(f"> {card['say_it']}")


def render_feedback(card_id: int, feedback_rows: list[dict]) -> None:
    """Thumbs per part of the card, an optional comment, and a Send button.
    Earlier comments for this card show above the form."""
    for row in feedback_rows:
        if row.get("comment"):
            st.caption(f"💬 {row['comment']}")
    with st.expander(config.FEEDBACK_HEADING):
        votes = []
        for name, label in FEEDBACK_ITEMS:
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
