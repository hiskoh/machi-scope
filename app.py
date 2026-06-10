from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class Topic:
    title: str
    area: str
    tags: tuple[str, ...]
    summary: str
    why_it_matters: str
    questions: tuple[str, ...]
    source: str


TOPICS = [
    Topic(
        title="通学路の安全対策",
        area="山口市",
        tags=("子育て", "交通", "安全"),
        summary="通学路の危険箇所、見守り体制、道路整備の優先順位について議論されています。",
        why_it_matters="毎日の通学や送迎に関わる話題です。地域でどこが危ないと見られているかを知る入口になります。",
        questions=("どの地域が対象になっている？", "いつまでに改善される？", "市民から危険箇所を伝える方法は？"),
        source="議会質疑サンプル",
    ),
    Topic(
        title="大雨・災害時の避難情報",
        area="山口市",
        tags=("防災", "高齢者", "情報発信"),
        summary="避難所の開設、避難情報の伝え方、支援が必要な人への連絡体制が取り上げられています。",
        why_it_matters="災害時に自分や家族がどう動くかに直結します。近所の支援体制を考えるきっかけになります。",
        questions=("避難所はどこに開く？", "スマホを使わない人への連絡は？", "地域の自主防災組織とどう連携する？"),
        source="議会質疑サンプル",
    ),
    Topic(
        title="公共交通と移動手段",
        area="山口市",
        tags=("交通", "高齢者", "地域"),
        summary="バス路線、デマンド交通、免許返納後の移動支援について議論されています。",
        why_it_matters="買い物、通院、通学に関わるテーマです。車に頼りにくい人の暮らしをどう支えるかが見えてきます。",
        questions=("どの地域で移動手段が不足している？", "利用しやすい料金になっている？", "実証実験の結果は？"),
        source="議会質疑サンプル",
    ),
    Topic(
        title="中心市街地と商店街",
        area="山口市",
        tags=("地域経済", "観光", "まちづくり"),
        summary="中心市街地のにぎわい、空き店舗、観光客と地元住民の回遊について話されています。",
        why_it_matters="休日の過ごし方、買い物、働く場所、まちの雰囲気に関係します。",
        questions=("どんな支援策がある？", "若い世代の出店は増えている？", "観光と暮らしのバランスは？"),
        source="議会質疑サンプル",
    ),
    Topic(
        title="子育て支援と保育",
        area="山口市",
        tags=("子育て", "教育", "福祉"),
        summary="保育の受け皿、放課後児童クラブ、子育て家庭への情報提供が論点になっています。",
        why_it_matters="子どもの預け先や親の働き方に関わります。制度の隙間にある困りごとも見つけやすくなります。",
        questions=("待機や定員の状況は？", "支援情報は届いている？", "現場の人手は足りている？"),
        source="議会質疑サンプル",
    ),
]


def topic_score(topic: Topic, interests: set[str], query: str) -> int:
    score = len(interests.intersection(topic.tags)) * 3
    haystack = " ".join((topic.title, topic.summary, topic.why_it_matters, *topic.tags))
    if query and query in haystack:
        score += 4
    return score


def render_styles() -> None:
    st.markdown(
        """
        <style>
        .main .block-container { max-width: 1120px; padding-top: 2rem; }
        .hero {
            padding: 1.25rem 1.35rem;
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
            font-size: 2rem;
            line-height: 1.25;
            margin: 0 0 .35rem;
            color: #1f2f2b;
            letter-spacing: 0;
        }
        .hero p {
            color: #52615f;
            margin: 0;
            line-height: 1.7;
        }
        .topic-card {
            border: 1px solid rgba(36, 48, 47, .13);
            background: #ffffff;
            border-radius: 8px;
            padding: 1rem 1.05rem;
            margin: .75rem 0;
        }
        .topic-card h3 {
            font-size: 1.2rem;
            margin: 0 0 .35rem;
            color: #24302f;
            letter-spacing: 0;
        }
        .meta {
            color: #63706e;
            font-size: .92rem;
            margin-bottom: .55rem;
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
        .small-note { color: #687572; font-size: .9rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_topic(topic: Topic) -> None:
    tags_html = "".join(f'<span class="pill">{tag}</span>' for tag in topic.tags)
    questions_html = "".join(f"<li>{question}</li>" for question in topic.questions)
    st.markdown(
        f"""
        <section class="topic-card">
            <h3>{topic.title}</h3>
            <div class="meta">{topic.area} / {topic.source}</div>
            <div>{tags_html}</div>
            <p>{topic.summary}</p>
            <div class="why"><strong>自分ごとポイント</strong><br>{topic.why_it_matters}</div>
            <details>
                <summary>この論点で見ておきたい問い</summary>
                <ul>{questions_html}</ul>
            </details>
        </section>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title="まちすこーぷ",
    page_icon="🔎",
    layout="wide",
)

render_styles()

st.markdown(
    """
    <section class="hero">
        <div class="hero-label">まちすこーぷ</div>
        <h1>自分のまちの議論が、関心から見えてくる。</h1>
        <p>
        議会を議事録として読むだけではなく、暮らしのテーマから眺めるための入口です。
        まずは軽量版として、関心タグに沿って論点を見つける体験を試せます。
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.divider()

left, right = st.columns([1, 2], gap="large")

with left:
    st.subheader("関心を選ぶ")
    area = st.selectbox("まち", ["山口市"])
    all_tags = sorted({tag for topic in TOPICS for tag in topic.tags})
    interests = set(
        st.multiselect(
            "気になるテーマ",
            all_tags,
            default=["子育て", "防災"],
        )
    )
    query = st.text_input("キーワード", placeholder="例: 通学路、避難所、バス")
    st.caption("この初期版はサンプルデータで動きます。外部APIやsecretsは不要です。")

with right:
    st.subheader("あなたに近い論点")
    filtered = [topic for topic in TOPICS if topic.area == area]
    ranked = sorted(
        filtered,
        key=lambda topic: topic_score(topic, interests, query.strip()),
        reverse=True,
    )
    visible = [topic for topic in ranked if topic_score(topic, interests, query.strip()) > 0]
    if not visible:
        visible = ranked

    for topic in visible:
        render_topic(topic)

st.divider()
st.markdown(
    """
    <p class="small-note">
    次の段階では、実際の議会データ、発言者、会議日、出典URLをつなぎ込み、
    「なぜ自分に関係があるのか」までたどれる形に拡張します。
    </p>
    """,
    unsafe_allow_html=True,
)
