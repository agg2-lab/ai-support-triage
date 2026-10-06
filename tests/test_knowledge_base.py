from knowledge_base import find_article


def test_find_export_article():
    article = find_article(
        "Export & Rendering",
        "My export is stuck at 99 percent.",
    )

    assert article is not None
    assert article["category"] == "Export & Rendering"
