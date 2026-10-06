from classifier import rule_based_classify


def test_billing_ticket_escalates():
    result = rule_based_classify(
        "Charged twice",
        "I was charged twice for my subscription.",
    )

    assert result["category"] == "Billing"
    assert result["priority"] == "High"
    assert result["needs_human"] is True


def test_export_ticket_classification():
    result = rule_based_classify(
        "Export stuck",
        "My video export is stuck at 99 percent.",
    )

    assert result["category"] == "Export & Rendering"
    assert result["priority"] == "Medium"


def test_duo_lost_phone_escalates():
    result = rule_based_classify(
        "Locked out after losing phone",
        "I lost the phone that had Duo Mobile and now I cannot access my account.",
    )

    assert result["category"] == "MFA / Duo Mobile"
    assert result["priority"] == "High"
    assert result["needs_human"] is True


def test_duo_push_issue_escalates():
    result = rule_based_classify(
        "Duo push never arrives",
        "Duo Mobile is not sending the push notification to my phone.",
    )

    assert result["category"] == "MFA / Duo Mobile"
    assert result["needs_human"] is True
