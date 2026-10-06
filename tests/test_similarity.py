import pandas as pd

from similarity import find_similar_tickets, ticket_similarity


def test_export_ticket_is_more_similar_to_export_issue():
    export_score = ticket_similarity(
        "Export stuck at 99%",
        "My video render never finishes.",
        "Render failed",
        "The video export failed while processing.",
    )
    billing_score = ticket_similarity(
        "Export stuck at 99%",
        "My video render never finishes.",
        "Charged twice",
        "I have two subscription charges.",
    )

    assert export_score > billing_score


def test_find_similar_tickets_returns_best_match_first():
    tickets = pd.DataFrame(
        [
            {
                "id": 1,
                "subject": "Billing issue",
                "description": "I was charged twice.",
                "category": "Billing",
                "priority": "High",
                "status": "Open",
                "suggested_article": "Billing help",
                "draft_response": "",
            },
            {
                "id": 2,
                "subject": "Export failed",
                "description": "My video render failed during export.",
                "category": "Export & Rendering",
                "priority": "Medium",
                "status": "Open",
                "suggested_article": "Export help",
                "draft_response": "",
            },
        ]
    )

    matches = find_similar_tickets(
        "Video export failed",
        "My render fails during export.",
        tickets,
        limit=2,
        min_score=0.0,
    )

    assert matches[0]["id"] == 2
