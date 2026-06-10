# -*- coding: utf-8 -*-
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st

from ui_common import page_hero


st.set_page_config(
    page_title="市長発言 | このまちレンズ",
    page_icon="🗣️",
    layout="wide",
)

AWS_REGION = "us-west-2"
OUTPUT_PREFIX = "mayor_chunk_jsonl/"
GPT_MODEL = "gpt-4.1-mini"
GPT_TEMPERATURE = 0.1
EMBED_MODEL = "text-embedding-3-small"
TOPK_CANDIDATES = 30
TOP_N_RETURN = 10
SIM_THRESHOLD = 0.1


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
        "OPENAI_API_KEY": secret_get("OPENAI_API_KEY"),
        "AWS-KEY.AWS_ACCESS_KEY": secret_get("AWS-KEY", "AWS_ACCESS_KEY"),
        "AWS-KEY.AWS_SECRET_KEY": secret_get("AWS-KEY", "AWS_SECRET_KEY"),
        "AWS-KEY.DATA_BUCKET_NAME": secret_get("AWS-KEY", "DATA_BUCKET_NAME"),
        "AWS-KEY.VECTOR_INDEX_ARN_MAYOR": secret_get("AWS-KEY", "VECTOR_INDEX_ARN_MAYOR"),
    }
    return [name for name, value in required.items() if not value]


def load_prompt(filename: str, default_text: str) -> str:
    try:
        return (Path("prompts") / filename).read_text(encoding="utf-8")
    except OSError:
        return default_text


def is_openai_quota_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "insufficient_quota" in text or "exceeded your current quota" in text


@st.cache_resource(show_spinner=False)
def get_clients():
    import boto3
    from openai import OpenAI

    s3 = boto3.client(
        "s3",
        aws_access_key_id=secret_get("AWS-KEY", "AWS_ACCESS_KEY"),
        aws_secret_access_key=secret_get("AWS-KEY", "AWS_SECRET_KEY"),
        region_name=AWS_REGION,
    )
    s3vectors = boto3.client(
        "s3vectors",
        aws_access_key_id=secret_get("AWS-KEY", "AWS_ACCESS_KEY"),
        aws_secret_access_key=secret_get("AWS-KEY", "AWS_SECRET_KEY"),
        region_name=AWS_REGION,
    )
    openai = OpenAI(api_key=secret_get("OPENAI_API_KEY"))
    return s3, s3vectors, openai


def similarity(distance: float) -> float:
    return max(0.0, min(1.0, 1.0 - float(distance)))


def fetch_original_chunk(source_file: str, chunk_id: str) -> dict[str, Any] | None:
    s3, _, _ = get_clients()
    bucket = secret_get("AWS-KEY", "DATA_BUCKET_NAME")
    key = f"{OUTPUT_PREFIX}{source_file}.jsonl"

    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
    except Exception:
        return None

    for line in body.splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("chunk_id") == chunk_id:
            return row
    return None


def query_vectors(query: str) -> list[dict[str, Any]]:
    _, s3vectors, openai = get_clients()
    embedding = openai.embeddings.create(model=EMBED_MODEL, input=query)
    qvec = [float(value) for value in embedding.data[0].embedding]

    response = s3vectors.query_vectors(
        indexArn=secret_get("AWS-KEY", "VECTOR_INDEX_ARN_MAYOR"),
        queryVector={"float32": qvec},
        topK=TOPK_CANDIDATES,
        returnMetadata=True,
        returnDistance=True,
    )

    hits: list[dict[str, Any]] = []
    for match in response.get("vectors", []) or []:
        score = similarity(float(match.get("distance", 0.0)))
        if score < SIM_THRESHOLD:
            continue
        metadata = match.get("metadata") or {}
        source_file = metadata.get("source_file") or ""
        chunk_id = metadata.get("chunk_id") or match.get("key") or match.get("id") or ""
        original = fetch_original_chunk(source_file, chunk_id) if source_file else None
        hits.append(
            {
                "score": score,
                "source_file": source_file,
                "chunk_id": chunk_id,
                "original": original or {},
            }
        )

    return sorted(hits, key=lambda item: item["score"], reverse=True)[:TOP_N_RETURN]


def summarize(query: str, hits: list[dict[str, Any]]) -> str:
    _, _, openai = get_clients()
    prompt = load_prompt(
        "mirai_summary.txt",
        "市長発言を、市民向けにわかりやすく要約してください。本文にないことは補わないでください。",
    )
    guard = f"\n\n質問: {query}\n質問に直接関係する内容だけを対象にしてください。"
    texts = []
    for hit in hits:
        original = hit.get("original") or {}
        text = original.get("text") or ""
        if text:
            texts.append(text)

    response = openai.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": prompt + guard},
            {"role": "user", "content": "\n\n".join(texts) or "(関連本文なし)"},
        ],
        temperature=GPT_TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


def search_and_answer(query: str) -> dict[str, Any]:
    hits = query_vectors(query)
    if not hits:
        return {"summary": "関連する市長発言を見つけられませんでした。", "hits": []}
    return {"summary": summarize(query, hits), "hits": hits}


def render_hit(hit: dict[str, Any], index: int) -> None:
    original = hit.get("original") or {}
    topic = original.get("topic") or original.get("title") or f"関連発言 {index}"
    source_file = (hit.get("source_file") or "").replace(".txt", "")
    date = original.get("date") or ""
    score = hit.get("score", 0)

    with st.expander(f"{topic} / 類似度 {score:.2f}", expanded=False):
        if date:
            st.caption(str(date))
        st.write(original.get("text") or "本文を取得できませんでした。")
        if source_file:
            st.caption(source_file)


page_hero(
    "市長発言を検索",
    "市の方針を、暮らしのテーマから探す。",
    "市長発言や記者会見などから、質問に近い内容を探して要約します。"
    "議会での問いと、市が語る方向性を行き来して確認できます。",
)

st.markdown(
    """
    <div class="scope-band">
        <div class="scope-mini">
        議会検索が「どんな問いが出たか」を見る場所だとすれば、こちらは「市がどんな方向を語っているか」を見る場所です。
        同じテーマを議会検索と市長発言検索で行き来すると、論点の立体感が出ます。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

missing = missing_required_secrets()
if missing:
    st.warning("この機能を使うには、Streamlit CloudのSecrets設定が必要です。")
    st.code("\n".join(missing), language="text")
    st.stop()

query = st.text_input(
    "知りたいこと",
    placeholder="例: 防災に関する市長の発言はありますか",
)

sample_queries = [
    "観光やインバウンドについて市長は何を話していますか",
    "子育て支援についての方針を知りたい",
    "防災に関する市長発言はありますか",
]
cols = st.columns(3)
for index, sample in enumerate(sample_queries):
    if cols[index].button(sample):
        query = sample

if st.button("検索する", type="primary", disabled=not query.strip()):
    with st.spinner("市長発言を探して要約しています..."):
        try:
            st.session_state["mayor_result"] = search_and_answer(query.strip())
            st.session_state["mayor_query"] = query.strip()
        except Exception as exc:
            if is_openai_quota_error(exc):
                st.error("OpenAI APIの利用枠が不足しているため、検索できませんでした。")
                st.info("Streamlit Secretsに設定している `OPENAI_API_KEY` の課金設定、残高、利用上限を確認してください。")
            else:
                st.error("検索中にエラーが発生しました。secrets、AWS権限、S3Vectorsの設定を確認してください。")
                st.caption(str(exc))

result = st.session_state.get("mayor_result")
if result:
    st.divider()
    st.subheader("まとめ")
    st.success(result["summary"])

    st.subheader("関連する発言")
    for index, hit in enumerate(result.get("hits", []), start=1):
        render_hit(hit, index)

st.divider()
st.caption("AIの要約は正確性を保証するものではありません。重要な判断は必ず原典を確認してください。")
