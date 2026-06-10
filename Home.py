from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from ui_common import apply_base_styles, feature_card, page_hero, pill_row


@dataclass(frozen=True)
class Feature:
    title: str
    page: str
    tags: tuple[str, ...]
    body: str
    note: str
    action: str


FEATURES = [
    Feature(
        title="議会を検索",
        page="01_議会を検索.py",
        tags=("問い", "答弁", "暮らし"),
        body="気になるテーマを自然文で入力すると、関連する議会質疑を探して要約します。",
        note="議事録を全部読む前に、自分の関心に近い質疑応答へたどり着けます。",
        action="議会にきいてみる",
    ),
    Feature(
        title="ことばトレンド",
        page="02_ことばトレンド.py",
        tags=("ことば", "地図", "発見"),
        body="市長発言や議会質疑で繰り返し出てくる言葉を、ことば雲とネットワークで眺めます。",
        note="まずは見て、気になる言葉を見つける。そこから検索で深掘りできます。",
        action="まちのことばを見る",
    ),
    Feature(
        title="市長発言を検索",
        page="03_市長発言.py",
        tags=("方針", "未来", "市長"),
        body="市長発言や記者会見から、暮らしのテーマに近い発言を探して要約します。",
        note="議会での問いと、市が語る方向性を行き来して確認できます。",
        action="市の方針を見る",
    ),
    Feature(
        title="出典",
        page="04_出典.py",
        tags=("原典", "公式情報", "確認"),
        body="公式の会議録、市長関連情報、処理済みデータの所在を確認できます。",
        note="AI要約を入口にしつつ、最後は原典へ戻るためのページです。",
        action="出典を確認する",
    ),
]

LIFE_THEMES = [
    ("子育て", "給食、保育、放課後、教育環境"),
    ("防災", "避難、災害情報、地域の支援体制"),
    ("交通", "バス、移動支援、通学路、免許返納"),
    ("地域経済", "商店街、観光、雇用、中心市街地"),
    ("福祉", "高齢者、障がい、相談、孤立防止"),
    ("まちづくり", "公共施設、都市計画、地域活動"),
]


def render_feature(feature: Feature) -> None:
    feature_card(feature.title, feature.body, feature.tags, feature.note)
    if st.button(feature.action, key=f"go-{feature.page}", use_container_width=True):
        st.switch_page(f"pages/{feature.page}")


apply_base_styles()
page_hero(
    "このまちレンズ",
    "まちの未来を、自分ごとに。",
    "まちの未来を見て、対話しよう。議会や市長発言を、難しい記録としてではなく、"
    "自分の暮らしにつながる問いとして眺めるための入口です。",
)

st.markdown(
    """
    <section class="scope-focus">
        <div class="scope-focus-main">
            <div class="scope-kicker">まずは、気になるところから</div>
            <h2>見つける、たどる、話してみる。</h2>
            <p>
            ことばの広がりを眺めて、気になる論点を見つける。議会の問いや市長の発言をたどる。
            そして、自分のまちの未来について話し始める。そのための小さなレンズです。
            </p>
        </div>
        <div class="scope-focus-side">
            <strong>おすすめの流れ</strong>
            <span>ことばを見る → 気になる言葉を検索 → 原典で確かめる</span>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([0.9, 1.6], gap="large")

with left:
    st.subheader("暮らしのテーマ")
    selected_life = st.radio(
        "入口を選ぶ",
        [theme for theme, _ in LIFE_THEMES],
        captions=[caption for _, caption in LIFE_THEMES],
        label_visibility="collapsed",
    )
    st.markdown(
        f"""
        <section class="scope-card">
            <div class="scope-kicker">このテーマで見る</div>
            <h3>{selected_life}</h3>
            <p>{dict(LIFE_THEMES)[selected_life]}に関係する言葉や議論を、まずは眺めてみましょう。</p>
            <div>{pill_row(("見る", "探す", "確かめる"))}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.subheader("入口")
    for feature in FEATURES:
        render_feature(feature)

st.divider()

st.subheader("このまちレンズが大事にすること")
cols = st.columns(3)
with cols[0]:
    feature_card(
        "自分ごとにする",
        "行政や議会の言葉を、暮らしのテーマに引き寄せて読み始められるようにします。",
        ("暮らし", "関心", "入口"),
    )
with cols[1]:
    feature_card(
        "まず見せる",
        "分析から入るのではなく、ことばの広がりやつながりを先に見せます。",
        ("可視化", "発見", "対話"),
    )
with cols[2]:
    feature_card(
        "原典へ戻る",
        "AIの要約は入口です。気になる論点は、公式情報や会議録で確認できるようにします。",
        ("出典", "透明性", "確認"),
    )

st.caption("AI要約は原典の代わりではありません。重要な判断や引用では、必ず公式情報を確認してください。")
