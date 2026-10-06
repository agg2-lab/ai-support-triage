from pathlib import Path

import streamlit as st

from analytics import category_counts, priority_counts, summary_metrics
from classifier import classify_ticket
from database import add_ticket, init_db, load_tickets, seed_from_csv, ticket_count
from knowledge_base import find_article

ROOT = Path(__file__).parent

st.set_page_config(
    page_title="Support Triage & Insights",
    page_icon="🎫",
    layout="wide",
)

init_db()

if ticket_count() == 0:
    seed_from_csv(ROOT / "data" / "tickets.csv")

st.title("AI-Assisted Support Triage & Insights")
st.caption(
    "Portfolio project for ticket triage, human escalation, "
    "knowledge-base matching, and support analytics."
)

tab1, tab2, tab3 = st.tabs(
    ["Analyze Ticket", "Support Dashboard", "Ticket Queue"]
)

with tab1:
    st.subheader("Analyze a new support ticket")

    col1, col2 = st.columns([2, 1])

    with col1:
        subject = st.text_input(
            "Subject",
            placeholder="Export is stuck at 99%",
        )
        description = st.text_area(
            "Description",
            height=160,
            placeholder="Describe the user's issue...",
        )

    with col2:
        plan = st.selectbox(
            "Customer plan",
            ["Free", "Standard", "Pro", "Unlimited"],
        )
        st.info(
            "The app works without an API key using local rules. "
            "Configure OPENAI_API_KEY and OPENAI_MODEL to enable "
            "model-assisted classification."
        )

    if st.button("Analyze ticket", type="primary"):
        if not subject.strip() or not description.strip():
            st.warning("Add both a subject and description.")
        else:
            triage = classify_ticket(subject, description)

            combined_text = f"{subject}\n{description}"
            article = find_article(
                triage["category"],
                combined_text,
            )

            suggested_article = (
                article["title"]
                if article
                else "No close match found"
            )

            if article:
                draft_response = (
                    "Thanks for reaching out. "
                    f"This looks related to {article['title'].lower()}. "
                    f"{article['resolution']} "
                    "If the issue continues, we can escalate it for further review."
                )
            else:
                draft_response = (
                    "Thanks for reaching out. I wasn't able to match this issue "
                    "to an existing support article, so it may need additional review."
                )

            ticket = {
                "subject": subject,
                "description": description,
                "plan": plan,
                "category": triage["category"],
                "priority": triage["priority"],
                "needs_human": triage["needs_human"],
                "suggested_article": suggested_article,
                "draft_response": draft_response,
            }

            ticket_id = add_ticket(ticket)

            st.success(f"Ticket #{ticket_id} analyzed and saved.")

            metric1, metric2, metric3 = st.columns(3)

            metric1.metric(
                "Category",
                triage["category"],
            )
            metric2.metric(
                "Priority",
                triage["priority"],
            )
            metric3.metric(
                "Human escalation",
                "Yes" if triage["needs_human"] else "No",
            )

            st.write("**Classification reason**")
            st.write(triage["reason"])

            st.write("**Suggested knowledge-base article**")
            st.write(suggested_article)

            st.write("**Draft response**")
            st.code(
                draft_response,
                language=None,
            )

with tab2:
    st.subheader("Support operations dashboard")

    tickets = load_tickets()
    metrics = summary_metrics(tickets)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total tickets", metrics["total"])
    c2.metric("Open tickets", metrics["open"])
    c3.metric("Human escalation rate", f"{metrics['human_rate']:.0f}%")
    c4.metric("Top issue", metrics["top_category"])

    left, right = st.columns(2)

    with left:
        st.write("**Tickets by category**")
        category_df = category_counts(tickets)
        if not category_df.empty:
            st.bar_chart(
                category_df.set_index("category")["tickets"]
            )

    with right:
        st.write("**Tickets by priority**")
        priority_df = priority_counts(tickets)
        if not priority_df.empty:
            st.bar_chart(
                priority_df.set_index("priority")["tickets"]
            )

    if not tickets.empty:
        top_category = metrics["top_category"]
        top_count = int((tickets["category"] == top_category).sum())

        st.write("**Recurring issue signal**")
        st.info(
            f"{top_category} is currently the most common category "
            f"with {top_count} ticket(s). Review whether this pattern "
            "suggests a documentation update, product bug, or workflow improvement."
        )

with tab3:
    st.subheader("Ticket queue")

    tickets = load_tickets()

    display_columns = [
        "id",
        "subject",
        "plan",
        "category",
        "priority",
        "status",
        "needs_human",
        "created_at",
    ]

    st.dataframe(
        tickets[display_columns],
        use_container_width=True,
        hide_index=True,
    )
