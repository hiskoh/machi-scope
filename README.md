# まちすこーぷ

自分のまちの議会で話されていることを、暮らしの関心から見つけるための軽量Streamlitアプリです。

## コンセプト

議会をただの議事録として読むのではなく、子育て、防災、交通、地域経済など、自分の関心に沿って「自分ごと」として眺められる入口をつくります。

## ローカル起動

```powershell
pip install -r requirements.txt
streamlit run app.py
```

## デプロイ

Streamlit Community Cloudで以下を指定します。

- Repository: `hiskoh/machi-scope`
- Branch: `main`
- Main file path: `app.py`

トップページは外部APIやsecretsに依存しないため、そのまま起動できます。

## 旧機能の復活

`pages/01_議会を検索.py` に、旧「きいてギカイ」の中核だった議会質疑検索機能を戻しています。

このページを動かすには、Streamlit Community CloudのSecretsに以下が必要です。

```toml
OPENAI_API_KEY = "sk-..."

[AWS-KEY]
AWS_ACCESS_KEY = "..."
AWS_SECRET_KEY = "..."
DATA_BUCKET_NAME = "..."
VECTOR_INDEX_ARN_COUNCIL = "..."
```

Secretsが未設定でもトップページは動きます。議会検索ページだけ、設定案内を表示して停止します。
