import pandas as pd


def summary_metrics(df: pd.DataFrame, feedback_df: pd.DataFrame | None = None):
    if df.empty:
        return {
            "total": 0,
            "open": 0,
            "human_rate": 0.0,
            "top_category": "N/A",
            "helpful_rate": None,
            "feedback_count": 0,
        }

    total = len(df)
    open_count = int((df["status"] == "Open").sum())
    human_rate = float(df["needs_human"].mean() * 100)
    top_category = df["category"].mode().iloc[0]

    feedback_count = 0
    helpful_rate = None
    if feedback_df is not None and not feedback_df.empty:
        feedback_count = len(feedback_df)
        helpful_rate = float(feedback_df["helpful"].mean() * 100)

    return {
        "total": total,
        "open": open_count,
        "human_rate": human_rate,
        "top_category": top_category,
        "helpful_rate": helpful_rate,
        "feedback_count": feedback_count,
    }


def category_counts(df: pd.DataFrame):
    if df.empty:
        return pd.DataFrame(columns=["category", "tickets"])

    return (
        df.groupby("category")
        .size()
        .reset_index(name="tickets")
        .sort_values("tickets", ascending=False)
    )


def priority_counts(df: pd.DataFrame):
    if df.empty:
        return pd.DataFrame(columns=["priority", "tickets"])

    order = {"High": 0, "Medium": 1, "Low": 2}
    result = (
        df.groupby("priority")
        .size()
        .reset_index(name="tickets")
    )
    result["sort_order"] = result["priority"].map(order).fillna(99)
    return result.sort_values("sort_order").drop(columns=["sort_order"])
