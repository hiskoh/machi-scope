from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st


AWS_REGION = "us-west-2"
OUTPUT_PREFIX = "mayor_chunk_jsonl/"
GPT_MODEL = "gpt-4.1-mini"
GPT_TEMPERATURE = 0.1
EMBED_MODEL = "text-embedding-3-small"
TOPK_CANDIDATES = 30
TOP_N_RETURN = 10
SIM_THRESHOLD = 0.7
NO_RELEVANT_MESSAGE = (
    "AI判定により、類似性が高いと思われる会話は見つけられませんでした。"
    "気になったら、直接議事録や公式情報を見て一次情報を集めることをおすすめします。"
)


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


def similarity(distance: float) -> float:
    return max(0.0, min(1.0, 1.0 - float(distance)))


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
        return {"summary": NO_RELEVANT_MESSAGE, "hits": []}
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
