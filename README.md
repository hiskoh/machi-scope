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

この初期版は外部APIやsecretsに依存しないため、そのまま起動できます。
