import json
import os

from dotenv import load_dotenv

load_dotenv()

CATEGORIES = [
    "Account & Login",
    "MFA / Duo Mobile",
    "Billing",
    "Export & Rendering",
    "Performance",
    "Bug Report",
    "Feature Question",
    "Account Security",
    "Other",
]


def rule_based_classify(subject, description):
    text = f"{subject} {description}".lower()

    rules = [
        (
            "MFA / Duo Mobile",
            [
                "duo mobile",
                "duo push",
                "duo",
                "mfa",
                "multi-factor",
                "multifactor",
                "two-factor",
                "2fa",
                "verification code",
                "authenticator",
            ],
        ),
        ("Account Security", ["hacked", "unauthorized", "security", "stolen account"]),
        ("Billing", ["charge", "charged", "refund", "invoice", "billing", "subscription"]),
        ("Account & Login", ["login", "log in", "password", "sign in", "account access"]),
        ("Export & Rendering", ["export", "render", "stuck at", "download video"]),
        ("Performance", ["slow", "lag", "freezing", "timeout", "performance"]),
        ("Bug Report", ["bug", "broken", "error", "crash", "not working"]),
        ("Feature Question", ["how do i", "can i", "feature", "where is", "does it support"]),
    ]

    category = "Other"
    for name, keywords in rules:
        if any(keyword in text for keyword in keywords):
            category = name
            break

    high_terms = [
        "hacked",
        "unauthorized",
        "data loss",
        "charged twice",
        "cannot access",
        "locked out",
        "lost phone",
        "new phone",
        "push never arrives",
        "cannot authenticate",
        "can't authenticate",
    ]
    medium_terms = [
        "error",
        "crash",
        "stuck",
        "billing",
        "refund",
        "charged",
        "verification code",
        "duo push",
    ]

    if any(term in text for term in high_terms):
        priority = "High"
    elif any(term in text for term in medium_terms):
        priority = "Medium"
    else:
        priority = "Low"

    needs_human = (
        priority == "High"
        or category in {"Billing", "Account Security", "MFA / Duo Mobile"}
    )

    return {
        "category": category,
        "priority": priority,
        "needs_human": needs_human,
        "reason": "Classified using local fallback rules.",
        "source": "rules",
    }


def classify_ticket(subject, description):
    """
    Uses the OpenAI Responses API when both OPENAI_API_KEY and OPENAI_MODEL
    are configured. Otherwise, the app falls back to deterministic local rules.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key or not model:
        return rule_based_classify(subject, description)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        prompt = f"""
You are triaging a customer support ticket for a creative software product.

Allowed categories:
{", ".join(CATEGORIES)}

Return ONLY valid JSON with these fields:
category: one allowed category
priority: Low, Medium, or High
needs_human: true or false
reason: one short sentence

Escalate billing disputes, account-security concerns, possible data loss,
MFA/Duo Mobile issues that require device enrollment or account-specific
authentication changes, or other issues requiring account-specific investigation.

Subject: {subject}
Description: {description}
"""

        response = client.responses.create(
            model=model,
            input=prompt,
        )

        text = response.output_text.strip()

        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()

        result = json.loads(text)

        if result.get("category") not in CATEGORIES:
            result["category"] = "Other"

        if result.get("priority") not in {"Low", "Medium", "High"}:
            result["priority"] = "Low"

        result["needs_human"] = bool(result.get("needs_human", False))
        result["reason"] = str(result.get("reason", "Model-assisted classification."))
        result["source"] = "openai"

        return result

    except Exception:
        return rule_based_classify(subject, description)
