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
    "まちのことを、もっと知ろう。",
    "気になるテーマを聞いたり、まちでよく語られている言葉を眺めたりできます。",
)

st.markdown(
    """
    <section class="scope-band">
        <div class="scope-mini">
        難しい資料を最初から読む前に、まずは入口を選んでみてください。
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2, gap="large")

with left:
    action_card(
        "チャットで聞く",
        "気になることを入力すると、市長発言と議会でのやりとりを並べて探します。",
        ("質問する", "方針", "議会"),
        "気になることを聞いてみる",
        "pages/01_議会を検索.py",
        primary=True,
    )

with right:
    action_card(
        "特徴を知る",
        "どんなキーワードが増えているか、どの言葉が近くで語られているかを眺めます。",
        ("ことば", "昨年比", "つながり"),
        "まちのことばを見る",
        "pages/02_ことばトレンド.py",
    )

st.markdown(
    """
    <section class="scope-focus">
        <div class="scope-focus-main">
            <div class="scope-kicker">まずはここから</div>
            <h2>気になる話題を、少し近くで見てみる。</h2>
            <p>
            子育て、防災、交通、まちづくり。気になる言葉から、まちで話されていることを見つけられます。
            </p>
        </div>
        <div class="scope-focus-side">
            <strong>おすすめ</strong>
            <span>聞いてみる → 気になる結果を見る → 出典で確かめる</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.caption("AI要約は原典の代わりではありません。重要な判断や引用では、必ず公式情報を確認してください。")
