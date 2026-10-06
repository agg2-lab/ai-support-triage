import pandas as pd


def summary_metrics(df: pd.DataFrame):
    if df.empty:
        return {
            "total": 0,
            "open": 0,
            "human_rate": 0.0,
            "top_category": "N/A",
        }

    total = len(df)
    open_count = int((df["status"] == "Open").sum())
    human_rate = float(df["needs_human"].mean() * 100)
    top_category = df["category"].mode().iloc[0]

    return {
        "total": total,
        "open": open_count,
        "human_rate": human_rate,
        "top_category": top_category,
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

    return (
        df.groupby("priority")
        .size()
        .reset_index(name="tickets")
        .sort_values("tickets", ascending=False)
    )
