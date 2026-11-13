import streamlit as st

import config

st.set_page_config(page_title=config.APP_TITLE, layout="wide")

# Pages live in home.py and detail.py. The menu is hidden: users move between
# them with the History list and the Back link.
st.navigation(
    [st.Page("home.py", default=True), st.Page("detail.py")],
    position="hidden",
).run()
