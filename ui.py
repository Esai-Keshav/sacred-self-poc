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
    """The whole card at once: hook, body and practise."""
    with st.container(border=True):
        # Rows saved before perspectives existed have no key.
        st.caption(config.PERSPECTIVES[card.get("perspective", "willingness")])
        st.markdown(f"**{card['hook']}**")
        st.write(card["expanded"])
        st.markdown(f"**{config.PRACTISE_LABEL}**")
        st.write(card["practise"])


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


def render_feedback(card_id: int, feedback_rows: list[dict], key_prefix: str = "") -> None:
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
            label_col, vote_col = st.columns([1, 2])
            label_col.markdown(f"**{label}**")
            votes.append(to_vote(vote_col.feedback("thumbs", key=f"{key_prefix}{name}_{card_id}")))
        comment = st.text_area(config.FEEDBACK_COMMENT_LABEL, key=f"{key_prefix}comment_{card_id}")
        if st.button(config.FEEDBACK_SUBMIT_LABEL, key=f"{key_prefix}send_{card_id}"):
            try:
                db.save_feedback(db.build_feedback_row(card_id, *votes, comment))
                st.success(config.FEEDBACK_THANKS)
            except Exception:
                st.error(config.ERROR_FEEDBACK)
