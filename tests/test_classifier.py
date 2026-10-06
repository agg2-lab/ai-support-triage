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
