from __future__ import annotations

import streamlit as st

from ui_common import apply_base_styles, page_hero, pill_row


def action_card(
    title: str,
    body: str,
    tags: tuple[str, ...],
    button_label: str,
    page: str,
    primary: bool = False,
) -> None:
    button_type = "primary" if primary else "secondary"
    st.markdown(
        f"""
        <section class="scope-action-card">
            <div>{pill_row(tags)}</div>
            <h2>{title}</h2>
            <p>{body}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if st.button(button_label, type=button_type, use_container_width=True):
        st.switch_page(page)


apply_base_styles()

page_hero(
    "このまちレンズ",
    "まちのこと、聞いてみる。見てみる。",
    "気になることを聞く。まちで語られる言葉を見る。",
)

left, right = st.columns(2, gap="large")

with left:
    action_card(
        "聞く",
        "知りたいことを入れると、市長発言と議会でのやりとりを並べて探します。",
        ("質問する", "方針", "議会"),
        "聞いてみる",
        "pages/01_議会を検索.py",
        primary=True,
    )

with right:
    action_card(
        "見る",
        "増えている言葉や、近くで語られるテーマを眺めます。",
        ("ことば", "昨年比", "つながり"),
        "見てみる",
        "pages/02_見る.py",
        primary=True,
    )

st.caption("AI要約のため、重要な判断や引用では必ず公式情報を確認してください。")
