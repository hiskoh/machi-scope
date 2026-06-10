# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from ui_common import page_hero


st.set_page_config(
    page_title="出典 | このまちレンズ",
    page_icon="📚",
    layout="wide",
)

AWS_REGION = "us-west-2"
DATA_PREFIXES = [
    "council_chunk_jsonl_ui/",
    "mayor_chunk_jsonl/",
    "trending-words/",
]


def secret_get(*keys: str) -> Any | None:
    current: Any = st.secrets
    try:
        for key in keys:
            current = current[key]
        return current
    except Exception:
        return None


def can_list_sources() -> bool:
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
def list_s3_sources() -> list[dict[str, Any]]:
    s3 = get_s3_client()
    bucket = secret_get("AWS-KEY", "DATA_BUCKET_NAME")
    rows: list[dict[str, Any]] = []

    for prefix in DATA_PREFIXES:
        paginator = s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for item in page.get("Contents", []) or []:
                key = item.get("Key", "")
                if key.endswith("/"):
                    continue
                rows.append(
                    {
                        "区分": prefix.rstrip("/"),
                        "ファイル": key.split("/")[-1],
                        "S3キー": key,
                        "更新日": item.get("LastModified"),
                        "サイズ": item.get("Size"),
                    }
                )
    return rows


page_hero(
    "出典",
    "要約から、いつでも原典へ戻る。",
    "AIの回答や可視化は入口です。気になる論点を見つけたら、公式の会議録や市の公開情報に戻って確認できます。",
)

st.markdown(
    """
    <div class="scope-band">
        <div class="scope-mini">
        このサイトは、AIで読み始めやすくするための入口です。
        引用したい内容や重要な判断に使う内容は、必ずこのページから公式情報へ戻って確認してください。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.subheader("公式情報")
official_sources = [
    {
        "名称": "山口市議会 会議録検索",
        "説明": "議会質疑の原典を確認できます。",
        "URL": "https://www.city.yamaguchi.yamaguchi.dbsr.jp/index.php/",
    },
    {
        "名称": "山口市 市長の部屋",
        "説明": "市長発言、記者会見、関連情報の入口です。",
        "URL": "https://www.city.yamaguchi.lg.jp/site/shicho/",
    },
    {
        "名称": "山口市公式サイト",
        "説明": "市政情報、施策、統計、広報などの入口です。",
        "URL": "https://www.city.yamaguchi.lg.jp/",
    },
]

for source in official_sources:
    st.markdown(f"**[{source['名称']}]({source['URL']})**")
    st.caption(source["説明"])

st.divider()
st.subheader("このサイトで使うデータ")

if not can_list_sources():
    st.info("AWS secretsが設定されている場合、ここに処理済みデータの一覧を表示します。")
    st.code(
        "\n".join(
            [
                "AWS-KEY.AWS_ACCESS_KEY",
                "AWS-KEY.AWS_SECRET_KEY",
                "AWS-KEY.DATA_BUCKET_NAME",
            ]
        ),
        language="text",
    )
else:
    try:
        rows = list_s3_sources()
    except Exception as exc:
        st.error("S3の出典データ一覧を読み込めませんでした。")
        st.caption(str(exc))
        st.stop()

    if not rows:
        st.warning("表示できるデータファイルが見つかりませんでした。")
    else:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

st.divider()
st.subheader("使うときの注意")
st.markdown(
    """
    - AIの回答や要約は、原典確認の前段として使ってください。
    - 重要な判断や引用では、公式の会議録・市公式情報を確認してください。
    - このサイトの検索結果は、データ化済みの範囲に依存します。
    """
)
