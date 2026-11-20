import streamlit as st

import config
import db
from ui import render_answers, render_copy_box

st.page_link("home.py", label=config.BACK_LABEL)

request = db.get_request(st.session_state.get("selected_id", -1))
if request is None:
    st.warning(config.DETAIL_NOT_FOUND)
else:
    when = db.format_when(request["created_at"])
    st.caption(f"{when} · {request['model']}")
    st.subheader(config.COPY_QUESTION_LABEL)
    st.write(request["situation"])
    answers_v2 = db.v2_answers(request)
    if request["willingness"] is None and not answers_v2:  # fallback: no answers given
        st.info(config.FALLBACK_MESSAGE)
    else:
        if request["willingness"] is not None:
            render_answers(request)
        if answers_v2:
            if request["willingness"] is not None:
                st.divider()
            st.subheader(config.V2_HEADING)
            render_answers(answers_v2)
        render_copy_box(
            request["situation"],
            request if request["willingness"] is not None else answers_v2,
        )
