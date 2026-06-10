from __future__ import annotations

import streamlit as st


st.set_page_config(
    page_title="このまちレンズ",
    page_icon="🔭",
    layout="wide",
)

pages = [
    st.Page("Home.py", title="このまちレンズ", icon="🔭"),
    st.Page("pages/02_ことばトレンド.py", title="ことばトレンド", icon="📊"),
    st.Page("pages/01_議会を検索.py", title="議会を検索", icon="🔎"),
    st.Page("pages/03_市長発言.py", title="市長発言", icon="🗣️"),
    st.Page("pages/04_出典.py", title="出典", icon="📚"),
]

st.navigation(pages).run()
