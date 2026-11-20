import streamlit as st

import config

st.set_page_config(page_title=config.APP_TITLE, layout="wide")

# Importing home would run it only once per process, so Streamlit runs it as
# the only page instead. The menu is hidden because there is one page.
st.navigation([st.Page("home.py", default=True)], position="hidden").run()
