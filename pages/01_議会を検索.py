# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import streamlit as st

import mayor_search
from search_feedback import no_relevant_message
from ui_common import page_hero


AWS_REGION = "us-west-2"
OUTPUT_PREFIX = "council_chunk_jsonl_ui/"
GPT_MODEL = "gpt-4.1-mini"
GPT_TEMPERATURE = 0.1
EMBED_MODEL = "text-embedding-3-small"
TOPK_CANDIDATES = 30
TOP_N_RETURN = 10
SIM_THRESHOLD = 0.4


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
            "summary": no_relevant_message(query),
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


def is_openai_quota_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return "insufficient_quota" in text or "exceeded your current quota" in text


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


page_hero(
    "チャットで聞く",
    "まちのこと、聞いてみよう。",
    "気になることを、暮らしの言葉で入力してください。",
)

missing: list[str] = missing_required_secrets() + mayor_search.missing_required_secrets()
missing = sorted(set(missing))
if missing:
    st.warning("この機能を使うには、Streamlit CloudのSecrets設定が必要です。")
    st.code("\n".join(missing), language="text")
    st.info("トップページと特徴ページはsecretsなしでも動きます。チャット検索にはOpenAI/AWS設定が必要です。")
    st.stop()

with st.form("chat-search-form", clear_on_submit=False):
    query = st.text_input(
        "知りたいこと",
        placeholder="例: 給食費、通学路の安全、災害時の避難支援",
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("聞いてみる", type="primary")

if submitted and not query.strip():
    st.warning("知りたいことを入力してください。")

if submitted and query.strip():
    search_query = query.strip()
    chat_result: dict[str, Any] = {"query": search_query, "council": None, "mayor": None}
    status_message = st.empty()

    status_message.info(f"「{search_query}」で検索しています。市長発言と議会でのやりとりを確認します。")
    with st.spinner("検索しています..."):
        try:
            chat_result["mayor"] = mayor_search.search_and_answer(search_query)
        except Exception as exc:
            chat_result["mayor_error"] = exc

        try:
            chat_result["council"] = search_and_answer(search_query)
        except Exception as exc:
            chat_result["council_error"] = exc

    status_message.empty()
    st.session_state["chat_result"] = chat_result

result = st.session_state.get("chat_result")
if result:
    st.divider()
    result_query = result.get("query", "")
    st.subheader(f"「{result_query}」の検索結果" if result_query else "検索結果")

    council_error = result.get("council_error")
    if council_error:
        if is_openai_quota_error(council_error):
            st.error("OpenAI APIの利用枠が不足しているため、議論を見る検索ができませんでした。")
        else:
            st.error("議論を見る検索中にエラーが発生しました。")
            st.caption(str(council_error))

    mayor_error = result.get("mayor_error")
    if mayor_error:
        if mayor_search.is_openai_quota_error(mayor_error):
            st.error("OpenAI APIの利用枠が不足しているため、方針を見る検索ができませんでした。")
        else:
            st.error("方針を見る検索中にエラーが発生しました。")
            st.caption(str(mayor_error))

    mayor_col, council_col = st.columns(2, gap="large")

    with mayor_col:
        st.markdown("### 市長・方針")
        st.caption("市長発言などから、市がどんな方向を示しているかを見ます。")
        mayor_result = result.get("mayor")
        if mayor_result:
            if mayor_result.get("hits"):
                st.success(mayor_result["summary"])
                st.markdown("#### 関連する発言")
                for index, hit in enumerate(mayor_result.get("hits", []), start=1):
                    mayor_search.render_hit(hit, index)
            else:
                st.info(mayor_result["summary"])

    with council_col:
        st.markdown("### 議会・やりとり")
        st.caption("議員の質問と行政の答弁から、具体的な論点を見ます。")
        council_result = result.get("council")
        if council_result:
            if council_result.get("pairs"):
                st.success(council_result["summary"])
                st.markdown("#### 関連する議会でのやりとり")
                pairs_by_meeting: dict[str, list[dict[str, Any]]] = defaultdict(list)
                for pair in council_result.get("pairs", []):
                    pairs_by_meeting[pair.get("meeting_name", "会議名不明")].append(pair)

                for meeting_name, pairs in pairs_by_meeting.items():
                    with st.expander(f"{meeting_name} ({len(pairs)}件)", expanded=True):
                        for index, pair in enumerate(pairs, start=1):
                            render_pair(pair, index)
                            st.divider()
            else:
                st.info(council_result["summary"])

st.divider()
st.caption("AIの要約は正確性を保証するものではありません。重要な判断は必ず原典を確認してください。")
