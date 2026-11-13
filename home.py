import logging

import streamlit as st

import config
import db
from agent import UserError, answers_dict, get_perspectives
from ui import render_answers

logger = logging.getLogger(__name__)

# Keeps the last answer across Streamlit reruns, so interacting with the page
# does not wipe it.
RESULT_KEY = "result"
FALLBACK_KEY = "fallback"
QUESTION_KEY = "question"

st.title(config.APP_TITLE)
st.caption(config.APP_SUBTITLE)

st.markdown(f"**{config.INPUT_LABEL}**")
# Inside a container the chat input stays here instead of pinning to the page
# bottom. Enter sends, Shift+Enter adds a new line.
with st.container():
    situation = st.chat_input(
        config.INPUT_PLACEHOLDER,
        max_chars=config.settings.max_input_chars,
        submit_mode="disable",  # greyed out while an answer is being generated
    )

if situation:
    # Drop the previous answer so the page never shows stale output next to a
    # failed attempt.
    st.session_state.pop(RESULT_KEY, None)
    st.session_state.pop(FALLBACK_KEY, None)
    st.session_state[QUESTION_KEY] = situation.strip()
    try:
        with st.spinner(config.SPINNER_TEXT):
            output = get_perspectives(situation)
        if output is None:  # the model returned FALLBACK: not a personal issue
            st.session_state[FALLBACK_KEY] = True
        else:
            st.session_state[RESULT_KEY] = answers_dict(output)
    except UserError as e:
        st.warning(str(e))
    except Exception:
        logger.exception("Perspective generation failed")
        st.error(config.ERROR_GENERIC)

answers = st.session_state.get(RESULT_KEY)
if answers is not None or st.session_state.get(FALLBACK_KEY):
    # The input box clears after sending, so show what was asked.
    st.markdown("> " + st.session_state[QUESTION_KEY].replace("\n", "\n> "))
if st.session_state.get(FALLBACK_KEY):
    st.info(config.FALLBACK_MESSAGE)
elif answers is not None:
    render_answers(answers)

st.caption(config.DISCLAIMER)
st.caption(config.SAVE_NOTICE)

# --- History: every saved request, newest first. Click one to open it. ---
st.divider()
st.subheader(config.HISTORY_HEADING)
history = db.list_requests()
if not history:
    st.caption(config.HISTORY_EMPTY)
else:
    with st.container(height=config.HISTORY_BOX_HEIGHT, border=True):
        for row in history:
            question = " ".join(row["situation"].split())
            if len(question) > config.HISTORY_SNIPPET_CHARS:
                question = question[: config.HISTORY_SNIPPET_CHARS].rstrip() + "…"
            when = row["created_at"][:16].replace("T", " ") + " UTC"
            if st.button(
                question,
                key=f"open_{row['id']}",
                help=when,
                type="tertiary",
                width="stretch",
            ):
                st.session_state["selected_id"] = row["id"]
                st.switch_page("detail.py")
            st.caption(
                f"{when} · {config.HISTORY_FALLBACK_LABEL}" if row["is_fallback"] else when
            )
