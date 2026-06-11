from __future__ import annotations


def build_query_suggestions(query: str) -> list[str]:
    query = query.strip()
    compact_query = query.replace("について", "").replace("知りたい", "").strip(" 。、")

    topic_suggestions = {
        "教育": ["教育スポーツ行政の方針", "教育委員会の方針", "学校施設の整備", "通学路の安全"],
        "学校": ["学校施設の老朽化", "通学路の安全", "不登校支援", "教育委員会の対応"],
        "子育て": ["保育所の待機児童", "放課後児童クラブ", "子育て支援策", "給食費の負担軽減"],
        "防災": ["避難所の運営", "災害時の情報伝達", "自主防災組織", "浸水対策"],
        "交通": ["公共交通の維持", "バス路線の見直し", "高齢者の移動支援", "免許返納後の移動手段"],
        "福祉": ["高齢者支援", "介護人材の確保", "障がい者支援", "地域包括ケア"],
        "観光": ["観光振興", "インバウンド対応", "地域経済への効果", "観光施設の整備"],
    }

    suggestions: list[str] = []
    for keyword, examples in topic_suggestions.items():
        if keyword in query:
            suggestions.extend(examples)

    if not suggestions and compact_query:
        suggestions = [
            f"{compact_query}の現状",
            f"{compact_query}への支援",
            f"{compact_query}の課題",
            f"{compact_query}に関する予算",
        ]

    return suggestions[:4]


def no_relevant_message(query: str) -> str:
    suggestions = build_query_suggestions(query)
    if suggestions:
        suggestion_text = "、".join(f"「{item}」" for item in suggestions)
        return (
            "AI判定により、類似性が高いと思われる会話は見つけられませんでした。"
            f"「{query.strip()}」だと広すぎる可能性があります。検索語を少し変えてみませんか。"
            f"例えば {suggestion_text} のように少し具体化して聞くと、拾いやすくなるかもしれません。"
            "気になったら、直接議事録や公式情報を見て一次情報を集めることもおすすめします。"
        )

    return (
        "AI判定により、類似性が高いと思われる会話は見つけられませんでした。"
        "キーワードを少し具体化して聞き直すと、関連する発言を拾いやすくなるかもしれません。"
        "気になったら、直接議事録や公式情報を見て一次情報を集めることもおすすめします。"
    )
