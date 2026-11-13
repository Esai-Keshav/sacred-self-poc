import streamlit as st

import config
import db
from ui import render_answers, render_copy_box

st.page_link("home.py", label=config.BACK_LABEL)

request = db.get_request(st.session_state.get("selected_id", -1))
if request is None:
    st.warning(config.DETAIL_NOT_FOUND)
else:
    when = request["created_at"][:16].replace("T", " ") + " UTC"
    st.caption(f"{when} · {request['model']}")
    st.subheader(config.COPY_QUESTION_LABEL)
    st.write(request["situation"])
    if request["willingness"] is None:  # a fallback request: no answers were given
        st.info(config.FALLBACK_MESSAGE)
    else:
        render_answers(request)
        render_copy_box(request["situation"], request)
