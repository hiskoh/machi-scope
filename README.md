# このまちレンズ

自分のまちの議会や市長発言で話されていることを、暮らしの関心から見つけるためのStreamlitアプリです。

## コンセプト

議会や市長発言をただの議事録・広報として読むのではなく、子育て、防災、交通、地域経済など、自分の関心に沿って「自分ごと」として眺められる入口をつくります。

## 機能

- `議会を検索`: 旧「きいてギカイ」相当。議会質疑を質問から検索して要約します。
- `ことばトレンド`: 旧「ことばトレンド」相当。頻出語とことばネットワークで議論の傾向を俯瞰します。
- `市長発言を検索`: 旧「きいてミライ」相当。市長発言や記者会見を質問から検索して要約します。
- `出典`: 公式情報と処理済みデータの所在を確認します。

## ローカル起動

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## デプロイ

Streamlit Community Cloudで以下を指定します。

- Repository: `hiskoh/KonoMachi-Lens`
- Branch: `main`
- Main file path: `app.py`

トップページは外部APIやsecretsに依存しないため、そのまま起動できます。

## 旧機能の復活

旧サイトの思想と主要機能を、このまちレンズの構成に合わせて再配置しています。

このページを動かすには、Streamlit Community CloudのSecretsに以下が必要です。

```toml
OPENAI_API_KEY = "sk-..."

[AWS-KEY]
AWS_ACCESS_KEY = "..."
AWS_SECRET_KEY = "..."
DATA_BUCKET_NAME = "..."
VECTOR_INDEX_ARN_COUNCIL = "..."
VECTOR_INDEX_ARN_MAYOR = "..."
```

Secretsが未設定でもトップページは動きます。検索・分析・出典データ一覧の各ページは、必要な設定案内を表示して停止します。
