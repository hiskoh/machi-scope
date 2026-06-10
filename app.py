from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class Entry:
    title: str
    page: str
    tags: tuple[str, ...]
    summary: str
    why_it_matters: str
    next_action: str


ENTRIES = [
    Entry(
        title="議会を検索",
        page="01_議会を検索.py",
        tags=("質疑", "議員", "行政の答弁"),
        summary="気になるテーマを質問すると、関連する議会質疑を探して要約します。",
        why_it_matters="議事録全文を読む前に、自分の関心に近い論点と質疑応答を見つけられます。",
        next_action="具体的な質問から探す",
    ),
    Entry(
        title="ことばトレンド",
        page="02_ことばトレンド.py",
        tags=("傾向", "ネットワーク", "頻出語"),
        summary="市長発言や議会質疑に出てくる言葉を集計し、頻出語と共起ネットワークで眺めます。",
        why_it_matters="まちで何が繰り返し語られているか、どのテーマ同士が近いかを俯瞰できます。",
        next_action="まちの論点を俯瞰する",
    ),
    Entry(
        title="市長発言を検索",
        page="03_市長発言.py",
        tags=("市長", "方針", "未来"),
        summary="市長の発言や記者会見などから、質問に近い内容を探して要約します。",
        why_it_matters="市の方向性や重点施策を、暮らしのテーマから確認できます。",
        next_action="市の方針を見る",
    ),
    Entry(
        title="出典を見る",
        page="04_出典.py",
        tags=("出典", "透明性", "原典"),
        summary="このサイトが参照しているデータや公開情報への入口をまとめます。",
        why_it_matters="AIの要約だけで終わらず、必要なときに原典へ戻れます。",
        next_action="根拠を確認する",
    ),
]


def score_entry(entry: Entry, interests: set[str], query: str) -> int:
    score = len(interests.intersection(entry.tags)) * 3
    haystack = " ".join((entry.title, entry.summary, entry.why_it_matters, *entry.tags))
    if query and query in haystack:
        score += 4
    return score


def render_styles() -> None:
    st.markdown(
        """
        <style>
        .main .block-container { max-width: 1160px; padding-top: 2rem; }
        .hero {
            padding: 1.35rem 1.45rem;
            border: 1px solid rgba(31, 122, 104, .18);
            background: #ffffff;
            border-radius: 8px;
        }
        .hero-label {
            color: #1f7a68;
            font-size: .9rem;
            font-weight: 700;
            margin-bottom: .25rem;
        }
        .hero h1 {
            font-size: 2.1rem;
            line-height: 1.25;
            margin: 0 0 .35rem;
            color: #1f2f2b;
            letter-spacing: 0;
        }
        .hero p {
            color: #52615f;
            margin: 0;
            line-height: 1.75;
        }
        .entry-card {
            border: 1px solid rgba(36, 48, 47, .13);
            background: #ffffff;
            border-radius: 8px;
            padding: 1rem 1.05rem;
            margin: .75rem 0;
        }
        .entry-card h3 {
            font-size: 1.18rem;
            margin: 0 0 .35rem;
            color: #24302f;
            letter-spacing: 0;
        }
        .pill {
            display: inline-block;
            padding: .16rem .48rem;
            border-radius: 999px;
            border: 1px solid #cddbd5;
            background: #f3f8f5;
            color: #315f53;
            font-size: .82rem;
            margin: 0 .25rem .25rem 0;
        }
        .why {
            border-left: 4px solid #1f7a68;
            padding-left: .75rem;
            color: #35413f;
            margin: .7rem 0;
        }
        .small-note { color: #687572; font-size: .9rem; line-height: 1.6; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_entry(entry: Entry) -> None:
    tags_html = "".join(f'<span class="pill">{tag}</span>' for tag in entry.tags)
    st.markdown(
        f"""
        <section class="entry-card">
            <h3>{entry.title}</h3>
            <div>{tags_html}</div>
            <p>{entry.summary}</p>
            <div class="why"><strong>自分ごとポイント</strong><br>{entry.why_it_matters}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    if st.button(entry.next_action, key=f"go-{entry.page}"):
        st.switch_page(f"pages/{entry.page}")


st.set_page_config(
    page_title="まちすこーぷ",
    page_icon="🔭",
    layout="wide",
)

render_styles()

st.markdown(
    """
    <section class="hero">
        <div class="hero-label">まちすこーぷ</div>
        <h1>自分のまちの議論が、関心から見えてくる。</h1>
        <p>
        議会や市長発言を、ただの議事録や広報として読むのではなく、
        子育て、防災、交通、地域経済などの関心からたどるための入口です。
        検索、傾向分析、出典確認をひとつの流れで扱えます。
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.divider()

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("関心から入る")
    all_tags = sorted({tag for entry in ENTRIES for tag in entry.tags})
    interests = set(
        st.multiselect(
            "気になる切り口",
            all_tags,
            default=["質疑", "傾向", "出典"],
        )
    )
    query = st.text_input("キーワード", placeholder="例: 子育て、防災、交通")
    st.markdown(
        """
        <p class="small-note">
        旧サイトの「きいてギカイ」「きいてミライ」「ことばトレンド」「出典」を、
        まちすこーぷの思想に合わせて再配置しています。
        </p>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.subheader("おすすめの入口")
    ranked = sorted(
        ENTRIES,
        key=lambda entry: score_entry(entry, interests, query.strip()),
        reverse=True,
    )
    visible = [entry for entry in ranked if score_entry(entry, interests, query.strip()) > 0]
    if not visible:
        visible = ranked

    for entry in visible:
        render_entry(entry)

st.divider()
st.markdown(
    """
    <p class="small-note">
    AI要約は原典の代わりではありません。気になる論点を見つけたら、必ず出典ページや各ページの原文情報に戻って確認してください。
    </p>
    """,
    unsafe_allow_html=True,
)
