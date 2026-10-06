import json
from pathlib import Path

KB_PATH = Path(__file__).parent / "data" / "knowledge_base.json"


def load_articles():
    return json.loads(KB_PATH.read_text())


def find_article(category, text):
    articles = load_articles()
    text_lower = text.lower()

    candidates = [
        article
        for article in articles
        if article["category"].lower() == category.lower()
    ]

    if not candidates:
        return None

    scored = []
    for article in candidates:
        score = sum(
            keyword.lower() in text_lower
            for keyword in article.get("keywords", [])
        )
        scored.append((score, article))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[0][1]
