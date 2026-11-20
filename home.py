import logging

import streamlit as st

import config
import db
from agent import UserError, answers_dict, get_perspectives, get_perspectives_v2
from ui import render_answers

logger = logging.getLogger(__name__)

# Keeps the last answer across Streamlit reruns, so interacting with the page
# does not wipe it.
RESULT_KEY = "result"
FALLBACK_KEY = "fallback"
RESULT_V2_KEY = "result_v2"
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
    st.session_state.pop(RESULT_V2_KEY, None)
    st.session_state[QUESTION_KEY] = situation.strip()
    try:
        if not (config.ENABLE_V1 or config.ENABLE_V2):
            st.warning(config.ERROR_NO_VERSION)
        elif config.ENABLE_V1:
            with st.spinner(config.SPINNER_TEXT):
                output, request_id = get_perspectives(situation)
            if output is None:  # the model returned FALLBACK: not a personal issue
                st.session_state[FALLBACK_KEY] = True
            else:
                st.session_state[RESULT_KEY] = answers_dict(output)
                if config.ENABLE_V2:
                    # A v2 failure must not hide the v1 answers.
                    try:
                        with st.spinner(config.SPINNER_TEXT):
                            st.session_state[RESULT_V2_KEY], _ = get_perspectives_v2(
                                situation, request_id
                            )
                    except Exception:
                        logger.exception("v2 generation failed")
                        st.warning(config.ERROR_V2)
        else:  # v1 off: v2 alone, saved as its own row
            with st.spinner(config.SPINNER_TEXT):
                answers_v2, _ = get_perspectives_v2(situation, None)
            if answers_v2 is None:
                st.session_state[FALLBACK_KEY] = True
            else:
                st.session_state[RESULT_V2_KEY] = answers_v2
    except UserError as e:
        st.warning(str(e))
    except Exception:
        logger.exception("Perspective generation failed")
        st.error(config.ERROR_GENERIC)

answers = st.session_state.get(RESULT_KEY)
answers_v2 = st.session_state.get(RESULT_V2_KEY)
if answers is not None or answers_v2 is not None or st.session_state.get(FALLBACK_KEY):
    # The input box clears after sending, so show what was asked.
    st.markdown("> " + st.session_state[QUESTION_KEY].replace("\n", "\n> "))
if st.session_state.get(FALLBACK_KEY):
    st.info(config.FALLBACK_MESSAGE)
else:
    if answers is not None:
        render_answers(answers)
    if answers_v2 is not None:
        if answers is not None:
            st.divider()
        st.subheader(config.V2_HEADING)
        render_answers(answers_v2)

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
            when = db.format_when(row["created_at"])
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
