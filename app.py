from __future__ import annotations

import streamlit as st


st.set_page_config(
    page_title="このまちレンズ",
    page_icon="🔭",
    layout="wide",
)

pages = [
    st.Page("Home.py", title="このまちレンズ", icon="🔭"),
    st.Page("pages/01_議会を検索.py", title="聞く", icon="💬"),
    st.Page("pages/02_ことばトレンド.py", title="見る", icon="📊"),
    st.Page("pages/04_出典.py", title="出典", icon="📚"),
]

st.navigation(pages).run()
