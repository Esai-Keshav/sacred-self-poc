import logging

import streamlit as st

import config
from agent import UserError, get_perspectives
from prompts import PERSPECTIVES

logger = logging.getLogger(__name__)

st.set_page_config(page_title=config.APP_TITLE, layout="wide")
st.title(config.APP_TITLE)
st.caption(config.APP_SUBTITLE)

situation = st.text_area(
    config.INPUT_LABEL,
    placeholder=config.INPUT_PLACEHOLDER,
    height=config.INPUT_HEIGHT,
)

if st.button(config.SUBMIT_LABEL, type="primary"):
    try:
        with st.spinner(config.SPINNER_TEXT):
            result = get_perspectives(situation)
    except UserError as e:
        st.warning(str(e))
    except Exception:
        logger.exception("Perspective generation failed")
        st.error(config.ERROR_GENERIC)
    else:
        for col, perspective in zip(st.columns(len(PERSPECTIVES)), PERSPECTIVES):
            with col:
                st.subheader(perspective.title)
                st.caption(perspective.tagline)
                st.write(getattr(result, perspective.key).response)

st.caption(config.DISCLAIMER)
