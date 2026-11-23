import logging

import streamlit as st

import config
import db
from agent import UserError, get_card
from ui import format_when, render_card, render_feedback

logger = logging.getLogger(__name__)

st.title(config.APP_TITLE)

tab_new, tab_history = st.tabs([config.TAB_NEW_LABEL, config.TAB_HISTORY_LABEL])

with tab_new:
    thought = st.chat_input(
        config.INPUT_PLACEHOLDER,
        max_chars=config.settings.max_input_chars,
        submit_mode="disable",  # greyed out while a card is being generated
    )

    if thought:
        st.session_state.pop("last", None)
        try:
            with st.spinner(config.SPINNER_TEXT):
                card, card_id = get_card(thought)
            if card is None:
                st.info(config.FALLBACK_MESSAGE)
            else:
                if card_id is None:
                    st.warning(config.ERROR_SAVE)
                st.session_state["last"] = {"thought": thought, "card": card.model_dump(), "id": card_id}
        except UserError as e:
            st.warning(str(e))
        except Exception:
            logger.exception("Card generation failed")
            st.error(config.ERROR_GENERIC)

    # Kept in session_state so the card survives reruns caused by feedback clicks.
    last = st.session_state.get("last")
    if last:
        st.markdown("> " + last["thought"].replace("\n", "\n> "))
        render_card(last["card"])
        if last["id"] is not None:
            render_feedback(last["id"], [], key_prefix="home_")

with tab_history:
    try:
        cards = db.list_cards()
        feedback = db.list_feedback([c["id"] for c in cards])
    except Exception:
        logger.exception("Could not load history")
        cards, feedback = [], []
        st.warning(config.ERROR_HISTORY)

    if not cards:
        st.caption(config.HISTORY_EMPTY)
    for c in cards:
        st.markdown(f"**{format_when(c['created_at'])}**")
        st.markdown("> " + c["thought"].replace("\n", "\n> "))
        render_card(c)
        render_feedback(c["id"], [f for f in feedback if f["card_id"] == c["id"]])
        st.divider()
