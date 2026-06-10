from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from ui_common import apply_base_styles, feature_card, page_hero, pill_row, step_row


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
        tags=("質問から探す", "議員の問い", "行政の答弁"),
        body="気になるテーマを自然文で入力すると、関連する議会質疑を探して要約します。",
        note="議事録を全部読む前に、自分の関心に近い質疑応答へたどり着けます。",
        action="質問から議会を見る",
    ),
    Feature(
        title="ことばトレンド",
        page="02_ことばトレンド.py",
        tags=("頻出語", "共起ネットワーク", "まちの傾向"),
        body="市長発言や議会質疑で繰り返し出てくる言葉を、ことば雲とネットワークで俯瞰します。",
        note="検索する前に、いま何が語られているのかを広く眺められます。",
        action="まちの論点を俯瞰する",
    ),
    Feature(
        title="市長発言を検索",
        page="03_市長発言.py",
        tags=("市の方針", "重点施策", "未来"),
        body="市長発言や記者会見から、暮らしのテーマに近い発言を探して要約します。",
        note="議会での問いと、市の方向性を行き来して確認できます。",
        action="市の方針を見る",
    ),
    Feature(
        title="出典",
        page="04_出典.py",
        tags=("原典確認", "公式情報", "透明性"),
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


def score_feature(feature: Feature, interests: set[str], query: str) -> int:
    haystack = " ".join((feature.title, feature.body, feature.note, *feature.tags))
    score = len(interests.intersection(feature.tags)) * 3
    if query and query in haystack:
        score += 5
    return score


def render_feature(feature: Feature) -> None:
    feature_card(feature.title, feature.body, feature.tags, feature.note)
    if st.button(feature.action, key=f"go-{feature.page}", use_container_width=True):
        st.switch_page(f"pages/{feature.page}")


st.set_page_config(
    page_title="このまちレンズ",
    page_icon="🔭",
    layout="wide",
)

apply_base_styles()
page_hero(
    "このまちレンズ",
    "議会と市政を、自分の暮らしから見つける。",
    "議事録や会見録をただ検索するのではなく、子育て、防災、交通、地域経済などの関心から、"
    "まちで話されている論点へ近づくためのサイトです。",
)

st.markdown(
    """
    <div class="scope-band">
        <div class="scope-mini">
        このまちレンズは、検索窓にたどり着く前の「何から見ればいいかわからない」を減らすためのサイトです。
        まず暮らしのテーマから入り、全体像と具体的な発言を行き来します。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

step_row(
    (
        ("1. 暮らしから入る", "子育て、防災、交通など、身近なテーマを選びます。"),
        ("2. 全体と具体を見る", "言葉の傾向を眺め、気になる論点を検索します。"),
        ("3. 原典に戻る", "AI要約で終わらず、公式情報や会議録を確認します。"),
    )
)

st.divider()

left, right = st.columns([0.95, 1.55], gap="large")

with left:
    st.subheader("暮らしのテーマ")
    selected_life = st.radio(
        "入口を選ぶ",
        [theme for theme, _ in LIFE_THEMES],
        captions=[caption for _, caption in LIFE_THEMES],
        label_visibility="collapsed",
    )
    query = st.text_input("キーワード", placeholder="例: 通学路、避難所、バス、給食")
    st.markdown(
        f"""
        <section class="scope-card">
            <div class="scope-kicker">いま見るなら</div>
            <h3>{selected_life}から議論をたどる</h3>
            <p>{dict(LIFE_THEMES)[selected_life]}に関係する言葉で、議会検索や市長発言検索を試してみてください。</p>
            <div>{pill_row(("まず俯瞰", "気になったら検索", "最後に原典"))}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.subheader("何をしたいですか")
    interest_options = sorted({tag for feature in FEATURES for tag in feature.tags})
    interests = set(
        st.multiselect(
            "目的",
            interest_options,
            default=["質問から探す", "頻出語", "原典確認"],
        )
    )
    ranked = sorted(
        FEATURES,
        key=lambda feature: score_feature(feature, interests, query.strip()),
        reverse=True,
    )
    for feature in ranked:
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
        "全体を見る",
        "検索だけでなく、言葉の傾向やつながりから、まちの論点を俯瞰します。",
        ("傾向", "比較", "俯瞰"),
    )
with cols[2]:
    feature_card(
        "原典へ戻る",
        "AIの要約は入口です。気になる論点は、公式情報や会議録で確認できるようにします。",
        ("出典", "透明性", "確認"),
    )

st.caption("AI要約は原典の代わりではありません。重要な判断や引用では、必ず公式情報を確認してください。")
