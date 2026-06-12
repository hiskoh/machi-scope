# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import re
from collections import defaultdict
from typing import Any


OUTPUT_PREFIX = "council_chunk_jsonl_ui/"


def base_from_chunk_id(chunk_id: str) -> str:
    return re.sub(r"_[0-9]{1,3}$", "", chunk_id or "")


def base_from_record(record: dict[str, Any]) -> str:
    chunk_id = str(record.get("chunk_id") or "")
    if chunk_id:
        return base_from_chunk_id(chunk_id)
    source_file = str(record.get("source_file") or "").replace(".txt", "")
    return source_file


def load_pair_rows(s3, bucket: str, base_name: str, pair_ids: list[int]) -> list[dict[str, Any]]:
    from botocore.exceptions import ClientError

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


def load_source_rows(s3, bucket: str, base_name: str) -> list[dict[str, Any]]:
    key = f"{OUTPUT_PREFIX}{base_name}.jsonl"
    try:
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read().decode("utf-8")
    except Exception:
        return []

    rows = []
    for line in body.splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def pair_id_for_chunk(s3, bucket: str, base_name: str, chunk_id: str) -> int | None:
    if not chunk_id:
        return None
    for row in load_source_rows(s3, bucket, base_name):
        if str(row.get("chunk_id") or "") != str(chunk_id):
            continue
        pair_id = row.get("pair_id")
        if pair_id in (None, ""):
            return None
        try:
            return int(float(pair_id))
        except (TypeError, ValueError):
            return None
    return None


def build_pairs(hits: list[dict[str, Any]], s3, bucket: str) -> list[dict[str, Any]]:
    wanted: dict[str, list[int]] = defaultdict(list)
    for hit in hits:
        pair_id = hit.get("pair_id")
        if pair_id is None:
            continue
        base = base_from_record(hit)
        if not base:
            continue
        if int(pair_id) not in wanted[base]:
            wanted[base].append(int(pair_id))

    pairs: list[dict[str, Any]] = []
    for base, pair_ids in wanted.items():
        rows = load_pair_rows(s3, bucket, base, pair_ids)
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
