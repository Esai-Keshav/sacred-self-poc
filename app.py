import logging

import streamlit as st

import config
from agent import UserError, get_perspectives
from prompts import PERSPECTIVES

logger = logging.getLogger(__name__)

# Keeps the last answer across Streamlit reruns, so interacting with the page
# does not wipe it.
RESULT_KEY = "result"

st.set_page_config(page_title=config.APP_TITLE, layout="wide")
st.title(config.APP_TITLE)
st.caption(config.APP_SUBTITLE)

with st.form("situation_form", enter_to_submit=True):
    situation = st.text_area(
        config.INPUT_LABEL,
        placeholder=config.INPUT_PLACEHOLDER,
        height=config.INPUT_HEIGHT,
        max_chars=config.settings.max_input_chars,
    )
    submitted = st.form_submit_button(config.SUBMIT_LABEL, type="primary")

if submitted:
    # Drop the previous answer so the page never shows stale output next to a
    # failed attempt.
    st.session_state.pop(RESULT_KEY, None)
    try:
        with st.spinner(config.SPINNER_TEXT):
            st.session_state[RESULT_KEY] = get_perspectives(situation)
    except UserError as e:
        st.warning(str(e))
    except Exception:
        logger.exception("Perspective generation failed")
        st.error(config.ERROR_GENERIC)

result = st.session_state.get(RESULT_KEY)
if result is not None:
    for col, perspective in zip(st.columns(len(PERSPECTIVES)), PERSPECTIVES):
        with col:
            st.subheader(perspective.title)
            st.caption(perspective.tagline)
            st.write(getattr(result, perspective.key).response)

st.caption(config.DISCLAIMER)
