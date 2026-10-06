import math
import re
from collections import Counter

import pandas as pd

STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from",
    "has", "have", "i", "in", "is", "it", "my", "of", "on", "or", "that",
    "the", "this", "to", "was", "with", "you", "your",
}


def _tokens(text: str):
    words = re.findall(r"[a-z0-9]+", (text or "").lower())
    return [word for word in words if len(word) > 1 and word not in STOP_WORDS]


def _cosine_similarity(left: Counter, right: Counter):
    if not left or not right:
        return 0.0

    shared = set(left) & set(right)
    numerator = sum(left[token] * right[token] for token in shared)
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return numerator / (left_norm * right_norm)


def ticket_similarity(subject: str, description: str, candidate_subject: str, candidate_description: str):
    query = Counter(_tokens(f"{subject} {subject} {description}"))
    candidate = Counter(_tokens(f"{candidate_subject} {candidate_subject} {candidate_description}"))
    return _cosine_similarity(query, candidate)


def find_similar_tickets(
    subject: str,
    description: str,
    tickets: pd.DataFrame,
    limit: int = 3,
    min_score: float = 0.12,
):
    if tickets is None or tickets.empty:
        return []

    results = []

    for _, row in tickets.iterrows():
        score = ticket_similarity(
            subject,
            description,
            str(row.get("subject", "")),
            str(row.get("description", "")),
        )

        if score < min_score:
            continue

        results.append(
            {
                "id": int(row["id"]),
                "subject": str(row.get("subject", "")),
                "category": str(row.get("category", "Other")),
                "priority": str(row.get("priority", "Low")),
                "status": str(row.get("status", "Open")),
                "score": score,
                "suggested_article": str(row.get("suggested_article") or ""),
                "draft_response": str(row.get("draft_response") or ""),
            }
        )

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:limit]
