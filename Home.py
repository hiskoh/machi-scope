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
    "まちの未来を、自分ごとに。",
    "議会で交わされたやりとりや、市が示す方針を、暮らしの関心からのぞくための入口です。",
)

st.markdown(
    """
    <section class="scope-band">
        <div class="scope-mini">
        知りたいことがあるなら、まず聞いてみる。まだ言葉になっていないなら、まちで飛び交っているキーワードから眺める。
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2, gap="large")

with left:
    action_card(
        "チャットで聞く",
        "議員の質問、行政の答弁、市長の発言から、自分の興味あるテーマがどう語られているかをのぞきます。",
        ("問いから入る", "議論を見る", "方針を見る"),
        "気になることを聞いてみる",
        "pages/01_議会を検索.py",
        primary=True,
    )

with right:
    action_card(
        "特徴を知る",
        "どんなキーワードが増えているか、どの言葉が近くで語られているかを眺めて、まちの論点を見つけます。",
        ("ことば", "昨年比", "つながり"),
        "まちのことばを見る",
        "pages/02_ことばトレンド.py",
    )

st.markdown(
    """
    <section class="scope-focus">
        <div class="scope-focus-main">
            <div class="scope-kicker">見る範囲は、あとで切り替えられます</div>
            <h2>市長か議員かではなく、知りたいことから始める。</h2>
            <p>
            検索では、市長発言などから市の方向性を見る「方針を見る」、議員の質問と行政答弁から論点を見る「議論を見る」、
            その両方をあわせて見る入口を用意します。市民にとって先に大事なのは、役職の違いよりも
            「自分の関心がどこで、どう語られているか」です。
            </p>
        </div>
        <div class="scope-focus-side">
            <strong>基本の流れ</strong>
            <span>聞く → 関連する発言を読む → 気になる言葉を広げる → 出典で確かめる</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.caption("AI要約は原典の代わりではありません。重要な判断や引用では、必ず公式情報を確認してください。")
