# -*- coding: utf-8 -*-
from __future__ import annotations

import io
import itertools
import json
from collections import Counter
from typing import Any

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="ことばトレンド | まちすこーぷ",
    page_icon="📊",
    layout="wide",
)

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


def render_network(graph, min_edge_weight: int, height: int = 650) -> None:
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
    net.barnes_hut(gravity=-42000, central_gravity=0.15, spring_length=130, spring_strength=0.04)

    for node, attrs in filtered.nodes(data=True):
        size = int(attrs.get("size", 1))
        net.add_node(
            node,
            label=node,
            value=size,
            title=f"{node}: {size}",
            group=community_by_node.get(node, 0),
        )
    for left, right, attrs in filtered.edges(data=True):
        weight = int(attrs.get("weight", 1))
        net.add_edge(left, right, value=weight, title=f"共起: {weight}")

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
            f"""
            <span style="
                display:inline-block;
                margin:.18rem .32rem;
                padding:.14rem .2rem;
                color:#1f4f45;
                font-size:{font_size:.2f}rem;
                font-weight:{weight};
                line-height:1.2;
            " title="{count}回">{term}</span>
            """
        )

    st.markdown(
        f"""
        <div style="
            border:1px solid rgba(36,48,47,.12);
            border-radius:8px;
            background:#fff;
            padding:1rem;
            margin:.5rem 0 1rem;
        ">
            {''.join(chips)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def normalize_role(role: str) -> str:
    aliases = {
        "議員": "議員",
        "市長": "市長",
        "行政関係者": "行政関係者",
    }
    return aliases.get(role, role or "不明")


st.title("ことばトレンド")
st.caption("市長発言や議会質疑に出てくる言葉を、頻度とつながりから眺めます。")

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
    st.header("条件")
    selected_roles = st.multiselect("発言者の立場", ["すべて"] + roles, default=["すべて"])
    selected_years = st.multiselect("年", ["すべて"] + years, default=["すべて"])
    selected_meetings = st.multiselect("会議", ["すべて"] + meetings, default=["すべて"])
    selected_speakers = st.multiselect("発言者", ["すべて"] + speakers, default=["すべて"])

role_set = expand_all(selected_roles, roles)
year_set = expand_all(selected_years, years)
meeting_set = expand_all(selected_meetings, meetings)
speaker_set = expand_all(selected_speakers, speakers)

filtered_records = [
    record
    for record in records
    if normalize_role(record.get("speaker_role", "")) in role_set
    and record.get("year") in year_set
    and record.get("meeting_name") in meeting_set
    and record.get("speaker") in speaker_set
]

freq, utterances = aggregate_terms(filtered_records)

metric_cols = st.columns(3)
metric_cols[0].metric("対象レコード", f"{len(filtered_records):,}")
metric_cols[1].metric("発言数", f"{utterances:,}")
metric_cols[2].metric("語彙数", f"{len(freq):,}")

if not filtered_records or not freq:
    st.info("条件に一致するデータがありません。")
    st.stop()

tab_terms, tab_network, tab_context = st.tabs(["頻出語", "ことばネットワーク", "見方"])

with tab_terms:
    top_n = st.slider("表示する語数", 10, 60, 25, 5)
    top_terms = freq.most_common(top_n)
    df_terms = pd.DataFrame(top_terms, columns=["ことば", "出現数"])
    render_word_cloud(freq, top_n)
    st.bar_chart(df_terms.set_index("ことば"))
    st.dataframe(df_terms, use_container_width=True, hide_index=True)

with tab_network:
    c1, c2, c3 = st.columns(3)
    with c1:
        top_k_per_record = st.slider("各発言で使う上位語", 10, 80, 30, 5)
    with c2:
        max_nodes = st.slider("最大ノード数", 30, 160, 80, 10)
    with c3:
        min_edge_weight = st.slider("つながりの最小強度", 1, 30, 3, 1)

    graph = build_network(
        filtered_records,
        freq,
        top_k_per_record=top_k_per_record,
        max_nodes=max_nodes,
    )
    render_network(graph, min_edge_weight=min_edge_weight)

with tab_context:
    st.markdown(
        """
        このページは、議会や市長発言を一文ずつ読む前に、まちで繰り返し語られているテーマをつかむための入口です。

        - 頻出語は、対象条件のなかでよく現れる言葉です。
        - ネットワークは、同じ発言や同じまとまりに出てくる言葉同士を近づけています。
        - 大きいノードほど出現が多く、太いつながりほど一緒に出やすい言葉です。

        ここで気になった言葉は、議会検索や市長発言検索で詳しくたどれます。
        """
    )
