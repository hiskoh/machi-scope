# -*- coding: utf-8 -*-
from __future__ import annotations

import io
import itertools
import json
from collections import Counter
from html import escape
from typing import Any

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from ui_common import page_hero


AWS_REGION = "us-west-2"
S3_KEY = "trending-words/mayor-and-council.jsonl.zst"


def secret_get(*keys: str) -> Any | None:
    current: Any = st.secrets
    try:
        for key in keys:
            current = current[key]
        return current
    except Exception:
        return None


def missing_required_secrets() -> list[str]:
    required = {
        "AWS-KEY.AWS_ACCESS_KEY": secret_get("AWS-KEY", "AWS_ACCESS_KEY"),
        "AWS-KEY.AWS_SECRET_KEY": secret_get("AWS-KEY", "AWS_SECRET_KEY"),
        "AWS-KEY.DATA_BUCKET_NAME": secret_get("AWS-KEY", "DATA_BUCKET_NAME"),
    }
    return [name for name, value in required.items() if not value]


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
def load_records() -> list[dict[str, Any]]:
    import zstandard as zstd

    s3 = get_s3_client()
    bucket = secret_get("AWS-KEY", "DATA_BUCKET_NAME")
    obj = s3.get_object(Bucket=bucket, Key=S3_KEY)
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


def expand_all(selected: list[Any], universe: list[Any]) -> set[Any]:
    if not selected or "すべて" in selected:
        return set(universe)
    return set(selected)


def aggregate_terms(records: list[dict[str, Any]]) -> tuple[Counter[str], int]:
    counter: Counter[str] = Counter()
    utterances = 0
    for record in records:
        utterances += int(record.get("utterances", 0) or 0)
        for term, count in record.get("top_terms", []) or []:
            counter[str(term)] += int(count)
    return counter, utterances


def year_counter(records: list[dict[str, Any]], year: Any) -> Counter[str]:
    counter: Counter[str] = Counter()
    for record in records:
        if record.get("year") != year:
            continue
        for term, count in record.get("top_terms", []) or []:
            counter[str(term)] += int(count)
    return counter


def compare_year_terms(records: list[dict[str, Any]], target_year: Any, base_year: Any) -> pd.DataFrame:
    target = year_counter(records, target_year)
    base = year_counter(records, base_year)
    terms = set(target) | set(base)
    rows = []
    for term in terms:
        current = int(target.get(term, 0))
        previous = int(base.get(term, 0))
        diff = current - previous
        if current == 0 and previous == 0:
            continue
        change_rate = None if previous == 0 else (current - previous) / previous * 100
        rows.append(
            {
                "ことば": term,
                str(target_year): current,
                str(base_year): previous,
                "前年差": diff,
                "増減率": "NEW" if previous == 0 and current > 0 else (f"{change_rate:+.0f}%" if change_rate is not None else "-"),
            }
        )
    return pd.DataFrame(rows)


def find_year_value(years: list[Any], preferred: int | str) -> Any | None:
    preferred_text = str(preferred)
    for year in years:
        year_text = str(year).replace("年", "")
        if year_text == preferred_text:
            return year
    return None


def default_target_year(years: list[Any]) -> Any:
    return find_year_value(years, 2025) or (years[-1] if years else None)


def default_base_year(years: list[Any], target_year: Any) -> Any:
    candidate = find_year_value(years, 2024)
    if candidate is not None and candidate != target_year:
        return candidate

    previous_candidates = [year for year in years if str(year) < str(target_year)]
    if previous_candidates:
        return previous_candidates[-1]
    for year in years:
        if year != target_year:
            return year
    return target_year


def year_label(year: Any) -> str:
    text = str(year)
    return text if text.endswith("年") else f"{text}年"


def display_rate(value: Any) -> str:
    text = str(value)
    if text == "NEW":
        return "NEW"
    if text.startswith("+"):
        return f"+ {text[1:]}"
    if text.startswith("-"):
        return f"- {text[1:]}"
    return text


def count_term_in_record(record: dict[str, Any], term: str) -> int:
    for record_term, count in record.get("top_terms", []) or []:
        if str(record_term) == term:
            return int(count or 0)
    return 0


def records_for_term(records: list[dict[str, Any]], term: str, limit: int = 5) -> list[dict[str, Any]]:
    hits = []
    for record in records:
        count = count_term_in_record(record, term)
        if count <= 0:
            continue
        enriched = dict(record)
        enriched["_term_count"] = count
        hits.append(enriched)
    return sorted(hits, key=lambda item: int(item.get("_term_count", 0)), reverse=True)[:limit]


def record_label(record: dict[str, Any]) -> str:
    meeting = record.get("meeting_name") or record.get("meeting") or "会議"
    speaker = record.get("speaker") or "発言者不明"
    role = normalize_role(str(record.get("speaker_role", "")))
    return f"{meeting} / {role} {speaker}"


def record_excerpt(record: dict[str, Any], term: str) -> str:
    for key in ("summary", "要旨", "text", "content", "chunk_text", "body"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            text = value.strip().replace("\n", " ")
            return text[:280] + ("..." if len(text) > 280 else "")

    related = [str(item[0]) for item in (record.get("top_terms", []) or [])[:6]]
    related_text = "、".join(related) if related else term
    return f"この発言群では「{term}」が目立ちます。近いことば: {related_text}"


def render_term_details(term: str, records: list[dict[str, Any]], target_year: Any) -> None:
    hits = records_for_term(records, term, limit=5)
    st.markdown(
        f'<div class="scope-panel-title"><h3>「{escape(term)}」の発言要旨</h3>'
        f"<span>{year_label(target_year)}の発言から</span></div>",
        unsafe_allow_html=True,
    )
    if not hits:
        st.info("この条件では発言要旨を表示できませんでした。スコープを広げると見つかるかもしれません。")
        return

    for index, record in enumerate(hits, start=1):
        label = record_label(record)
        count = int(record.get("_term_count", 0))
        st.markdown(
            f"""
            <section class="scope-detail-card">
                <span>{index}. {escape(label)}</span>
                <strong>{escape(term)} {count:,}回</strong>
                <p>{escape(record_excerpt(record, term))}</p>
            </section>
            """,
            unsafe_allow_html=True,
        )


def select_term_button(term: str, key: str) -> None:
    if st.button(f"「{term}」を見る", key=key, use_container_width=True):
        st.session_state["selected_rising_term"] = str(term)


def render_top_term_cards(counter: Counter[str], target_year: Any) -> None:
    terms = counter.most_common(5)
    if not terms:
        st.info("表示できることばがありません。")
        return

    max_count = max(count for _, count in terms) or 1
    for index, (term, count) in enumerate(terms, start=1):
        width = max(12, min(100, round(count / max_count * 100)))
        st.markdown(
            f"""
            <section class="scope-word-rank-card">
                <div class="scope-word-rank-head">
                    <span>{index}</span>
                    <strong>{escape(str(term))}</strong>
                    <em>{count:,}</em>
                </div>
                <div class="scope-word-rank-track">
                    <div style="width:{width}%"></div>
                </div>
            </section>
            """,
            unsafe_allow_html=True,
        )
        select_term_button(str(term), f"top-word-{target_year}-{index}-{term}")


def render_rising_cards(rows: pd.DataFrame, target_year: Any, base_year: Any) -> None:
    if rows.empty:
        st.info("前年差で目立つことばは見つかりませんでした。")
        return

    for index, row in enumerate(rows.head(5).to_dict("records"), start=1):
        term = row["ことば"]
        current = row[str(target_year)]
        previous = row[str(base_year)]
        diff = row["前年差"]
        change_rate = row["増減率"]
        badge = display_rate(change_rate)
        count_text = "新しく登場" if previous == 0 else f"{int(previous):,} → {int(current):,}"
        card_html = (
            '<section class="scope-rise-card">'
            f'<div class="scope-rise-badge">{escape(badge)}</div>'
            f'<strong class="scope-rise-word">{escape(str(term))}</strong>'
            f'<span class="scope-rise-meta">{escape(str(base_year))} → {escape(str(target_year))} / {count_text}</span>'
            f'<span class="scope-rise-hint">+{int(diff):,}回</span>'
            "</section>"
        )
        st.markdown(card_html, unsafe_allow_html=True)
        select_term_button(str(term), f"rising-word-{target_year}-{base_year}-{index}-{term}")


def render_term_bar_chart(df_terms: pd.DataFrame) -> None:
    if df_terms.empty:
        return

    try:
        import altair as alt

        chart = (
            alt.Chart(df_terms)
            .mark_bar(color="#1f7a68")
            .encode(
                x=alt.X("ことば:N", sort="-y", title=None),
                y=alt.Y("出現数:Q", title="出現数"),
                tooltip=["ことば", "出現数"],
            )
            .properties(height=300)
        )
        st.altair_chart(chart, use_container_width=True)
    except Exception:
        st.bar_chart(df_terms.set_index("ことば"))


def render_signal_cards(
    utterance_delta_text: str,
    year_label: str,
    current_utterances: int,
    base_utterances: int,
    edge_count: int,
    node_count: int,
) -> None:
    delta = current_utterances - base_utterances
    delta_class = " is-down" if delta < 0 else " is-up"
    delta_sign = "+" if delta > 0 else ""
    st.markdown(
        f"""
        <div class="scope-signal-grid">
            <section class="scope-signal-card{delta_class}">
                <span>{escape(year_label)}</span>
                <strong>{delta_sign}{delta:,}</strong>
                <em>発言量</em>
            </section>
            <section class="scope-signal-card">
                <strong>{edge_count:,}</strong>
                <em>つながり / {node_count:,}語</em>
            </section>
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_network(records: list[dict[str, Any]], global_freq: Counter[str], top_k_per_record: int, max_nodes: int):
    import networkx as nx

    allowed_terms = {term for term, _ in global_freq.most_common(max_nodes)}
    edge_weight: Counter[tuple[str, str]] = Counter()
    node_weight: Counter[str] = Counter()

    for record in records:
        terms = [
            (str(term), int(count))
            for term, count in (record.get("top_terms", []) or [])[:top_k_per_record]
            if str(term) in allowed_terms
        ]
        for term, count in terms:
            node_weight[term] += count
        for (term_a, count_a), (term_b, count_b) in itertools.combinations(terms, 2):
            left, right = sorted((term_a, term_b))
            edge_weight[(left, right)] += min(count_a, count_b)

    graph = nx.Graph()
    for term, weight in node_weight.items():
        graph.add_node(term, size=weight)
    for (left, right), weight in edge_weight.items():
        graph.add_edge(left, right, weight=weight)
    return graph


def render_network(
    graph,
    min_edge_weight: int,
    height: int = 560,
    *,
    physics: bool = False,
    edge_opacity: float = 0.24,
) -> None:
    import networkx as nx
    from networkx.algorithms.community import greedy_modularity_communities
    from pyvis.network import Network

    filtered = nx.Graph()
    for node, attrs in graph.nodes(data=True):
        filtered.add_node(node, **attrs)
    for left, right, attrs in graph.edges(data=True):
        if int(attrs.get("weight", 1)) >= min_edge_weight:
            filtered.add_edge(left, right, **attrs)

    filtered.remove_nodes_from(list(nx.isolates(filtered)))
    if filtered.number_of_nodes() == 0:
        st.info("ネットワークに表示できる語がありません。条件を広げるか、しきい値を下げてください。")
        return

    communities = list(greedy_modularity_communities(filtered, weight="weight"))
    community_by_node = {
        node: index
        for index, nodes in enumerate(communities)
        for node in nodes
    }

    net = Network(
        height=f"{height}px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#24302f",
        notebook=False,
        directed=False,
    )
    if physics:
        net.barnes_hut(gravity=-42000, central_gravity=0.15, spring_length=130, spring_strength=0.04)

    for node, attrs in filtered.nodes(data=True):
        size = int(attrs.get("size", 1))
        net.add_node(
            node,
            label=node,
            value=size,
            title=f"{node}: {size}",
            group=community_by_node.get(node, 0),
            font={"size": 18},
            physics=physics,
        )
    for left, right, attrs in filtered.edges(data=True):
        weight = int(attrs.get("weight", 1))
        width = min(6, 1 + weight / max(min_edge_weight, 1))
        net.add_edge(
            left,
            right,
            value=weight,
            title=f"共起: {weight}",
            width=width,
            color=f"rgba(31, 122, 104, {edge_opacity})",
        )

    net.set_options(
        json.dumps(
            {
                "physics": {"enabled": physics},
                "edges": {"smooth": False},
                "interaction": {"hover": True, "tooltipDelay": 80},
                "nodes": {
                    "borderWidth": 1,
                    "scaling": {"min": 12, "max": 34},
                    "font": {"face": "sans-serif", "size": 18},
                },
            }
        )
    )

    html = net.generate_html(notebook=False)
    components.html(html, height=height, scrolling=True)


def render_word_cloud(counter: Counter[str], top_n: int) -> None:
    terms = counter.most_common(top_n)
    if not terms:
        return

    max_count = max(count for _, count in terms)
    chips = []
    for term, count in terms:
        scale = count / max_count if max_count else 0
        font_size = 0.9 + scale * 1.65
        weight = 500 + int(scale * 300)
        chips.append(
            f'<span class="scope-word-chip" style="font-size:{font_size:.2f}rem;'
            f'font-weight:{weight};" title="{count}回">{escape(str(term))}</span>'
        )

    st.markdown(
        f'<div class="scope-word-cloud">{"".join(chips)}</div>',
        unsafe_allow_html=True,
    )


def normalize_role(role: str) -> str:
    aliases = {
        "議員": "議員",
        "市長": "市長",
        "行政関係者": "行政関係者",
    }
    return aliases.get(role, role or "不明")


page_hero(
    "見る",
    "まちのこと、見てみよう。",
    "増えたことば、つながる話題。",
)

missing = missing_required_secrets()
if missing:
    st.warning("この機能を使うには、Streamlit CloudのSecrets設定が必要です。")
    st.code("\n".join(missing), language="text")
    st.stop()

with st.spinner("言葉データを読み込んでいます..."):
    try:
        records = load_records()
    except Exception as exc:
        st.error("言葉データを読み込めませんでした。S3の権限またはデータ配置を確認してください。")
        st.caption(str(exc))
        st.stop()

if not records:
    st.warning("言葉データが空でした。")
    st.stop()

years = sorted({record.get("year") for record in records if record.get("year")})
meetings = sorted({record.get("meeting_name") for record in records if record.get("meeting_name")})
roles = sorted({normalize_role(record.get("speaker_role", "")) for record in records})
speakers = sorted({record.get("speaker") for record in records if record.get("speaker")})

with st.sidebar:
    st.header("スコープ")
    selected_roles = st.multiselect("立場", ["すべて"] + roles, default=["すべて"])
    role_set_for_speakers = expand_all(selected_roles, roles)
    speaker_options = sorted(
        {
            record.get("speaker")
            for record in records
            if record.get("speaker") and normalize_role(record.get("speaker_role", "")) in role_set_for_speakers
        }
    )
    selected_years = st.multiselect("年", ["すべて"] + years, default=["すべて"])
    selected_meetings = st.multiselect("会議", ["すべて"] + meetings, default=["すべて"])
    selected_speakers = st.multiselect("発言者", ["すべて"] + speaker_options, default=["すべて"])

role_set = expand_all(selected_roles, roles)
year_set = expand_all(selected_years, years)
meeting_set = expand_all(selected_meetings, meetings)
speaker_set = expand_all(selected_speakers, speaker_options)

filtered_records = [
    record
    for record in records
    if normalize_role(record.get("speaker_role", "")) in role_set
    and record.get("year") in year_set
    and record.get("meeting_name") in meeting_set
    and record.get("speaker") in speaker_set
]

freq, utterances = aggregate_terms(filtered_records)

filtered_years = sorted({record.get("year") for record in filtered_records if record.get("year")})

if not filtered_records or not freq:
    st.info("条件に一致するデータがありません。")
    st.stop()

preferred_target_year = default_target_year(filtered_years)
default_year_index = filtered_years.index(preferred_target_year) if preferred_target_year in filtered_years else 0

target_year = preferred_target_year

preferred_base_year = default_base_year(filtered_years, target_year)
base_year = None
if len(filtered_years) >= 2:
    base_year_options = [year for year in filtered_years if year != target_year]
    base_year = preferred_base_year if preferred_base_year in base_year_options else base_year_options[0]

with st.expander("比べる年を変える", expanded=False):
    control_cols = st.columns(2)
    target_year = control_cols[0].selectbox("見る年", filtered_years, index=default_year_index)
    base_year_options = [year for year in filtered_years if year != target_year]
    if base_year_options:
        preferred_base_year = default_base_year(filtered_years, target_year)
        base_index = base_year_options.index(preferred_base_year) if preferred_base_year in base_year_options else 0
        base_year = control_cols[1].selectbox("比べる年", base_year_options, index=base_index)

year_records = [record for record in filtered_records if record.get("year") == target_year]
year_freq, year_utterances = aggregate_terms(year_records)
comparison = compare_year_terms(filtered_records, target_year, base_year) if base_year is not None else pd.DataFrame()

if not year_records or not year_freq:
    st.info("この年に表示できるデータがありません。")
    st.stop()

base_records = [record for record in filtered_records if base_year is not None and record.get("year") == base_year]
_, base_utterances = aggregate_terms(base_records)
utterance_delta = year_utterances - base_utterances if base_year is not None else None
utterance_delta_text = "比較なし" if utterance_delta is None else f"{utterance_delta:+,}"

graph = build_network(
    year_records,
    year_freq,
    top_k_per_record=18,
    max_nodes=55,
)

visual_left, visual_right = st.columns([.95, 1.05], gap="large")

with visual_left:
    st.markdown(f"### 発言数 上位5件")
    render_top_term_cards(year_freq, target_year)

with visual_right:
    st.markdown(f"### 変化率 上位5件")
    if not comparison.empty:
        rising = comparison[comparison["前年差"] > 0].copy()
        rising["_rate_sort"] = rising.apply(
            lambda row: 999999.0
            if int(row[str(base_year)] or 0) == 0
            else (int(row[str(target_year)] or 0) - int(row[str(base_year)] or 0)) / int(row[str(base_year)] or 1) * 100,
            axis=1,
        )
        rising = rising.sort_values(["_rate_sort", "前年差"], ascending=False)
        render_rising_cards(rising, target_year, base_year)
    else:
        st.info("比較できる年がありません。")

selected_rising_term = st.session_state.get("selected_rising_term")
if selected_rising_term:
    render_term_details(str(selected_rising_term), year_records, target_year)

network_note = "言葉の分布を眺める"
st.markdown(
    f'<div class="scope-panel-title"><h3>{target_year}のことばの近さ</h3><span>{network_note}</span></div>',
    unsafe_allow_html=True,
)
render_network(graph, min_edge_weight=5, height=560, physics=False, edge_opacity=0.24)

if base_year is not None:
    with st.expander(f"{base_year}のことばの近さも見る", expanded=False):
        base_network_records = [record for record in filtered_records if record.get("year") == base_year]
        base_network_freq, _ = aggregate_terms(base_network_records)
        base_graph = build_network(
            base_network_records,
            base_network_freq,
            top_k_per_record=18,
            max_nodes=55,
        )
        render_network(base_graph, min_edge_weight=5, height=460, physics=False, edge_opacity=0.2)

with st.expander("数字でも見る", expanded=False):
    c1, c2, c3 = st.columns(3)
    c1.metric("対象レコード", f"{len(year_records):,}")
    c2.metric("発言数", f"{year_utterances:,}")
    c3.metric("語彙数", f"{len(year_freq):,}")
    c4, c5 = st.columns(2)
    c4.metric("発言量の変化", utterance_delta_text)
    c5.metric("ことばのつながり", f"{graph.number_of_edges():,}")
    df_year_terms = pd.DataFrame(year_freq.most_common(20), columns=["ことば", "出現数"])
    render_term_bar_chart(df_year_terms)
    st.dataframe(df_year_terms, use_container_width=True, hide_index=True)
    if not comparison.empty:
        up = comparison[comparison["前年差"] > 0].sort_values("前年差", ascending=False).head(15)
        down = comparison[comparison["前年差"] < 0].sort_values("前年差", ascending=True).head(15)
        c_up, c_down = st.columns(2)
        with c_up:
            st.markdown(f"##### {base_year}から増えたことば")
            st.dataframe(up, use_container_width=True, hide_index=True)
        with c_down:
            st.markdown(f"##### {base_year}から減ったことば")
            st.dataframe(down, use_container_width=True, hide_index=True)

with st.expander("ネットワークを調整する", expanded=False):
    c1, c2, c3 = st.columns(3)
    with c1:
        top_k_per_record = st.slider("各発言の語数", 8, 80, 18, 2)
    with c2:
        max_nodes = st.slider("語の数", 20, 160, 50, 10)
    with c3:
        min_edge_weight = st.slider("つながり", 1, 40, 6, 1)

    scoped_graph = build_network(
        year_records,
        year_freq,
        top_k_per_record=top_k_per_record,
        max_nodes=max_nodes,
    )
    render_network(scoped_graph, min_edge_weight=min_edge_weight, physics=True, edge_opacity=0.22)
