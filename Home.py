from __future__ import annotations

import io
import json
from collections import Counter
from dataclasses import dataclass
from typing import Any

import streamlit as st

from ui_common import apply_base_styles, feature_card, page_hero, pill_row


AWS_REGION = "us-west-2"
TREND_KEY = "trending-words/mayor-and-council.jsonl.zst"


@dataclass(frozen=True)
class Feature:
    title: str
    page: str
    tags: tuple[str, ...]
    body: str
    note: str
    action: str


@dataclass(frozen=True)
class Theme:
    name: str
    description: str
    keywords: tuple[str, ...]


FEATURES = [
    Feature(
        title="ことばトレンド",
        page="02_ことばトレンド.py",
        tags=("ことば", "トレンド", "発見"),
        body="年ごとに目立ってきた言葉や、言葉同士の近さを眺めます。",
        note="まずは見て、気になる言葉を見つける入口です。",
        action="まちのことばを見る",
    ),
    Feature(
        title="議会を検索",
        page="01_議会を検索.py",
        tags=("問い", "答弁", "暮らし"),
        body="気になるテーマを自然文で入力すると、関連する議会質疑を探して要約します。",
        note="議員が何を問い、行政がどう答えたのかをたどれます。",
        action="議会にきいてみる",
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

THEMES = [
    Theme("子育て", "給食、保育、放課後、教育環境", ("子育て", "保育", "給食", "学校", "教育", "児童", "放課後")),
    Theme("防災", "避難、災害情報、地域の支援体制", ("防災", "災害", "避難", "水害", "消防", "復旧", "ハザード")),
    Theme("交通", "バス、移動支援、通学路、免許返納", ("交通", "バス", "通学路", "移動", "道路", "免許", "公共交通")),
    Theme("地域経済", "商店街、観光、雇用、中心市街地", ("観光", "商店街", "雇用", "経済", "中心市街地", "産業", "創業")),
    Theme("福祉", "高齢者、障がい、相談、孤立防止", ("福祉", "高齢者", "介護", "障害", "相談", "孤独", "支援")),
    Theme("まちづくり", "公共施設、都市計画、地域活動", ("公共施設", "都市計画", "地域", "まちづくり", "公園", "空き家", "自治会")),
]


def secret_get(*keys: str) -> Any | None:
    current: Any = st.secrets
    try:
        for key in keys:
            current = current[key]
        return current
    except Exception:
        return None


def has_trend_secrets() -> bool:
    return all(
        [
            secret_get("AWS-KEY", "AWS_ACCESS_KEY"),
            secret_get("AWS-KEY", "AWS_SECRET_KEY"),
            secret_get("AWS-KEY", "DATA_BUCKET_NAME"),
        ]
    )


@st.cache_resource(show_spinner=False)
def get_s3_client():
    import boto3

    return boto3.client(
        "s3",
        aws_access_key_id=secret_get("AWS-KEY", "AWS_ACCESS_KEY"),
        aws_secret_access_key=secret_get("AWS-KEY", "AWS_SECRET_KEY"),
        region_name=AWS_REGION,
    )


@st.cache_data(ttl=1800, show_spinner=False)
def load_trend_records() -> list[dict[str, Any]]:
    import zstandard as zstd

    s3 = get_s3_client()
    bucket = secret_get("AWS-KEY", "DATA_BUCKET_NAME")
    obj = s3.get_object(Bucket=bucket, Key=TREND_KEY)
    records: list[dict[str, Any]] = []

    dctx = zstd.ZstdDecompressor()
    with dctx.stream_reader(obj["Body"]) as reader:
        text_stream = io.TextIOWrapper(reader, encoding="utf-8", errors="strict", newline="")
        for line in text_stream:
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return records


def pick_default_year(years: list[Any]) -> Any | None:
    if not years:
        return None
    return years[-2] if len(years) >= 2 else years[-1]


def record_matches_theme(record: dict[str, Any], theme: Theme) -> bool:
    terms = [str(term) for term, _ in record.get("top_terms", []) or []]
    haystack = " ".join(terms + [str(record.get("meeting_name", "")), str(record.get("speaker", ""))])
    return any(keyword in haystack for keyword in theme.keywords)


def summarize_theme(records: list[dict[str, Any]], theme: Theme) -> dict[str, Any] | None:
    years = sorted({record.get("year") for record in records if record.get("year")})
    target_year = pick_default_year(years)
    if target_year is None:
        return None

    previous_years = [year for year in years if str(year) < str(target_year)]
    base_year = previous_years[-1] if previous_years else None

    target_records = [
        record
        for record in records
        if record.get("year") == target_year and record_matches_theme(record, theme)
    ]
    base_records = [
        record
        for record in records
        if base_year is not None and record.get("year") == base_year and record_matches_theme(record, theme)
    ]

    utterances = sum(int(record.get("utterances", 0) or 0) for record in target_records)
    base_utterances = sum(int(record.get("utterances", 0) or 0) for record in base_records)
    if base_year is not None and base_utterances:
        yoy = (utterances - base_utterances) / base_utterances * 100
    else:
        yoy = None

    counter: Counter[str] = Counter()
    for record in target_records:
        for term, count in record.get("top_terms", []) or []:
            term = str(term)
            if term not in theme.keywords:
                counter[term] += int(count)

    return {
        "year": target_year,
        "base_year": base_year,
        "records": len(target_records),
        "utterances": utterances,
        "yoy": yoy,
        "words": [term for term, _ in counter.most_common(3)],
    }


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
            ことばの変化を眺めて、気になる論点を見つける。議会の問いや市長の発言をたどる。
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

left, right = st.columns([0.95, 1.55], gap="large")

with left:
    st.subheader("暮らしのテーマ")
    selected_theme_name = st.radio(
        "入口を選ぶ",
        [theme.name for theme in THEMES],
        captions=[theme.description for theme in THEMES],
        label_visibility="collapsed",
    )
    selected_theme = next(theme for theme in THEMES if theme.name == selected_theme_name)

    if has_trend_secrets():
        try:
            summary = summarize_theme(load_trend_records(), selected_theme)
        except Exception:
            summary = None
    else:
        summary = None

    if summary:
        yoy_text = "比較なし" if summary["yoy"] is None else f"{summary['yoy']:+.1f}%"
        words = "、".join(summary["words"]) if summary["words"] else "関連語なし"
        st.markdown(
            f"""
            <section class="scope-card">
                <div class="scope-kicker">{summary['year']}の{selected_theme.name}</div>
                <h3>発言数 {summary['utterances']:,}件</h3>
                <p>前年比 {yoy_text}。関連してよく出る言葉は、{words} です。</p>
                <div>{pill_row((selected_theme.name, "トレンド", "くわしく見る"))}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        if st.button("くわしくはことばトレンドへ", use_container_width=True):
            st.switch_page("pages/02_ことばトレンド.py")
    else:
        st.markdown(
            f"""
            <section class="scope-card">
                <div class="scope-kicker">このテーマで見る</div>
                <h3>{selected_theme.name}</h3>
                <p>{selected_theme.description}に関係する言葉や議論を、ことばトレンドで眺められます。</p>
                <div>{pill_row(("見る", "探す", "確かめる"))}</div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        if st.button("ことばトレンドへ", use_container_width=True):
            st.switch_page("pages/02_ことばトレンド.py")

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
        "分析から入るのではなく、ことばの変化やつながりを先に見せます。",
        ("可視化", "発見", "対話"),
    )
with cols[2]:
    feature_card(
        "原典へ戻る",
        "AIの要約は入口です。気になる論点は、公式情報や会議録で確認できるようにします。",
        ("出典", "透明性", "確認"),
    )

st.caption("AI要約は原典の代わりではありません。重要な判断や引用では、必ず公式情報を確認してください。")
