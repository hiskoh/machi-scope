# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import streamlit as st


st.set_page_config(
    page_title="議会を検索 | まちすこーぷ",
    page_icon="🔎",
    layout="wide",
)

AWS_REGION = "us-west-2"
OUTPUT_PREFIX = "council_chunk_jsonl_ui/"
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
        "AWS-KEY.VECTOR_INDEX_ARN_COUNCIL": secret_get("AWS-KEY", "VECTOR_INDEX_ARN_COUNCIL"),
    }
    return [name for name, value in required.items() if not value]


def load_prompt(filename: str, default_text: str) -> str:
    path = Path("prompts") / filename
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return default_text


def base_from_chunk_id(chunk_id: str) -> str:
    return re.sub(r"_[0-9]{1,3}$", "", chunk_id or "")


def similarity(distance: float) -> float:
    return max(0.0, min(1.0, 1.0 - float(distance)))


@st.cache_resource(show_spinner=False)
def get_clients():
    import boto3
    from openai import OpenAI

    aws_access_key = secret_get("AWS-KEY", "AWS_ACCESS_KEY")
    aws_secret_key = secret_get("AWS-KEY", "AWS_SECRET_KEY")
    openai_key = secret_get("OPENAI_API_KEY")

    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=AWS_REGION,
    )
    s3vectors = boto3.client(
        "s3vectors",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key,
        region_name=AWS_REGION,
    )
    openai = OpenAI(api_key=openai_key)
    return s3, s3vectors, openai


def query_vectors(query: str) -> list[dict[str, Any]]:
    _, s3vectors, openai = get_clients()
    index_arn = secret_get("AWS-KEY", "VECTOR_INDEX_ARN_COUNCIL")

    embedding = openai.embeddings.create(model=EMBED_MODEL, input=query)
    qvec = [float(value) for value in embedding.data[0].embedding]

    response = s3vectors.query_vectors(
        indexArn=index_arn,
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
        pair_id = metadata.get("pair_id")
        hits.append(
            {
                "score": score,
                "key": match.get("key") or match.get("id"),
                "source_file": metadata.get("source_file")
                or metadata.get("source_id")
                or metadata.get("source")
                or "",
                "chunk_id": metadata.get("chunk_id")
                or metadata.get("chank_id")
                or match.get("key")
                or match.get("id")
                or "",
                "pair_id": int(float(pair_id)) if pair_id is not None else None,
            }
        )

    return sorted(hits, key=lambda item: item["score"], reverse=True)[:TOP_N_RETURN]


def load_pair_rows(base_name: str, pair_ids: list[int]) -> list[dict[str, Any]]:
    from botocore.exceptions import ClientError

    s3, _, _ = get_clients()
    bucket = secret_get("AWS-KEY", "DATA_BUCKET_NAME")
    key = f"{OUTPUT_PREFIX}{base_name}.jsonl"
    ids = sorted({int(pair_id) for pair_id in pair_ids if pair_id is not None})
    if not ids:
        return []

    try:
        id_list = ",".join(str(pair_id) for pair_id in ids)
        response = s3.select_object_content(
            Bucket=bucket,
            Key=key,
            ExpressionType="SQL",
            Expression=(
                "SELECT s.pair_id, s.qa_role, s.chunk_id, s.text, "
                "s.speaker, s.speaker_role, s.source_file "
                f"FROM S3Object s WHERE cast(s.pair_id as int) IN ({id_list})"
            ),
            InputSerialization={"JSON": {"Type": "LINES"}},
            OutputSerialization={"JSON": {}},
        )
        rows: list[dict[str, Any]] = []
        for event in response["Payload"]:
            if "Records" not in event:
                continue
            payload = event["Records"]["Payload"].decode("utf-8")
            for line in payload.splitlines():
                if line.strip():
                    rows.append(json.loads(line))
        return rows
    except ClientError:
        pass

    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
    except Exception:
        return []

    ids_set = set(ids)
    rows = []
    for line in body.splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if int(row.get("pair_id", -1)) in ids_set:
            rows.append(row)
    return rows


def build_pairs(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    wanted: dict[str, list[int]] = defaultdict(list)
    for hit in hits:
        if hit["pair_id"] is None:
            continue
        base = base_from_chunk_id(hit["chunk_id"])
        if hit["pair_id"] not in wanted[base]:
            wanted[base].append(hit["pair_id"])

    pairs: list[dict[str, Any]] = []
    for base, pair_ids in wanted.items():
        rows = load_pair_rows(base, pair_ids)
        for pair_id in pair_ids:
            records = [row for row in rows if int(row.get("pair_id", -1)) == int(pair_id)]
            questions = [row for row in records if row.get("qa_role") == "Q"]
            answers = [row for row in records if row.get("qa_role") == "A"]
            if not questions and not answers:
                continue

            first_chunk = (
                (questions and questions[0].get("chunk_id"))
                or (answers and answers[0].get("chunk_id"))
                or ""
            )
            meeting_name = first_chunk.split("_")[0] if first_chunk else "会議名不明"
            pairs.append(
                {
                    "pair_id": pair_id,
                    "source_file": f"{base}.txt",
                    "meeting_name": meeting_name,
                    "Q": questions,
                    "A": answers,
                }
            )
    return pairs


def summarize_pair(query: str, pair: dict[str, Any]) -> str:
    _, _, openai = get_clients()
    prompt = load_prompt(
        "gikai_pair_summary.txt",
        "議会質疑を市民向けに短く要約してください。本文にないことは補わないでください。",
    )
    guard = f"\n\n質問: {query}\n質問に直接関係する内容だけを要約してください。"
    blocks = []
    for question in pair.get("Q", []):
        blocks.append(
            f"質問: {question.get('speaker_role', '')} {question.get('speaker', '')}\n{question.get('text', '')}"
        )
    for answer in pair.get("A", []):
        blocks.append(
            f"答弁: {answer.get('speaker_role', '')} {answer.get('speaker', '')}\n{answer.get('text', '')}"
        )

    response = openai.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": prompt + guard},
            {"role": "user", "content": "\n\n".join(blocks)},
        ],
        temperature=GPT_TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


def summarize_overall(query: str, summaries: list[str]) -> str:
    _, _, openai = get_clients()
    prompt = load_prompt(
        "gikai_summary_overall.txt",
        "複数の議会質疑の要約を、市民向けにわかりやすく統合してください。",
    )
    guard = f"\n\n質問: {query}\n本文にない推測は避け、関係する論点だけをまとめてください。"
    context = "\n\n".join(f"{index + 1}. {summary}" for index, summary in enumerate(summaries))

    response = openai.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": prompt + guard},
            {"role": "user", "content": context},
        ],
        temperature=GPT_TEMPERATURE,
    )
    return response.choices[0].message.content.strip()


def search_and_answer(query: str) -> dict[str, Any]:
    hits = query_vectors(query)
    pairs = build_pairs(hits)
    if not pairs:
        return {
            "summary": "関連する質疑応答を見つけられませんでした。",
            "pairs": [],
        }

    pair_summaries = []
    for pair in pairs:
        try:
            pair["summary"] = summarize_pair(query, pair)
        except Exception:
            pair["summary"] = "この質疑の要約生成に失敗しました。"
        pair_summaries.append(pair["summary"])

    try:
        summary = summarize_overall(query, pair_summaries)
    except Exception:
        summary = "\n\n".join(pair_summaries)

    return {"summary": summary, "pairs": pairs}


def render_pair(pair: dict[str, Any], index: int) -> None:
    st.markdown(f"#### {index}. {pair.get('summary', '関連質疑')}")
    st.caption(f"{pair.get('meeting_name', '会議名不明')} / {pair.get('source_file', '')}")

    for question in pair.get("Q", []):
        label = f"質問: {question.get('speaker_role', '')} {question.get('speaker', '')}"
        with st.expander(label.strip(), expanded=False):
            st.write(question.get("text", ""))

    for answer in pair.get("A", []):
        label = f"答弁: {answer.get('speaker_role', '')} {answer.get('speaker', '')}"
        with st.expander(label.strip(), expanded=False):
            st.write(answer.get("text", ""))


st.title("議会を検索")
st.caption("旧「きいてギカイ」の中核機能を、まちすこーぷの1機能として戻したページです。")

missing = missing_required_secrets()
if missing:
    st.warning("この機能を使うには、Streamlit CloudのSecrets設定が必要です。")
    st.code("\n".join(missing), language="text")
    st.info("トップページはsecretsなしで動きます。このページだけ、旧機能用のOpenAI/AWS設定が必要です。")
    st.stop()

query = st.text_input(
    "知りたいこと",
    placeholder="例: 学校給食費の無償化について、どんな議論がありましたか",
)

sample_queries = [
    "公共交通の維持について、どんな議論がありましたか",
    "災害時の避難支援について知りたい",
    "子育て支援について議会で何が話されていますか",
]
cols = st.columns(3)
for index, sample in enumerate(sample_queries):
    if cols[index].button(sample):
        query = sample

if st.button("検索する", type="primary", disabled=not query.strip()):
    with st.spinner("議会質疑を探して要約しています..."):
        try:
            st.session_state["gikai_result"] = search_and_answer(query.strip())
            st.session_state["gikai_query"] = query.strip()
        except Exception as exc:
            st.error("検索中にエラーが発生しました。secrets、AWS権限、S3Vectorsの設定を確認してください。")
            st.exception(exc)

result = st.session_state.get("gikai_result")
if result:
    st.divider()
    st.subheader("まとめ")
    st.success(result["summary"])

    st.subheader("関連する質疑")
    pairs_by_meeting: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for pair in result.get("pairs", []):
        pairs_by_meeting[pair.get("meeting_name", "会議名不明")].append(pair)

    for meeting_name, pairs in pairs_by_meeting.items():
        with st.expander(f"{meeting_name} ({len(pairs)}件)", expanded=True):
            for index, pair in enumerate(pairs, start=1):
                render_pair(pair, index)
                st.divider()

st.divider()
st.caption("AIの要約は正確性を保証するものではありません。重要な判断は必ず原典を確認してください。")
