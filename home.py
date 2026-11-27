import logging

import streamlit as st

import config
import db
from agent import UserError, get_cards
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
                results = get_cards(thought)
            cards = [
                {**card.model_dump(), "perspective": perspective, "id": card_id}
                for perspective, card, card_id, _ in results
                if card is not None
            ]
            if any(failed for *_, failed in results):
                st.warning(config.ERROR_PARTIAL)
            elif not cards:
                st.info(config.FALLBACK_MESSAGE)
            if any(c["id"] is None for c in cards):
                st.warning(config.ERROR_SAVE)
            if cards:
                st.session_state["last"] = {"thought": thought, "cards": cards}
        except UserError as e:
            st.warning(str(e))
        except Exception:
            logger.exception("Card generation failed")
            st.error(config.ERROR_GENERIC)

    # Kept in session_state so the cards survive reruns caused by feedback clicks.
    last = st.session_state.get("last")
    if last:
        st.markdown("> " + last["thought"].replace("\n", "\n> "))
        for card in last["cards"]:
            render_card(card)
            if card["id"] is not None:
                render_feedback(card["id"], [], key_prefix="home_")

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
