from pathlib import Path

import streamlit as st

from analytics import category_counts, priority_counts, summary_metrics
from classifier import classify_ticket
from database import (
    add_feedback,
    add_ticket,
    init_db,
    load_feedback,
    load_tickets,
    seed_from_csv,
    ticket_count,
)
from knowledge_base import find_article
from similarity import find_similar_tickets

ROOT = Path(__file__).parent

st.set_page_config(
    page_title="Support Triage & Insights",
    page_icon="🎫",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px;}
    div[data-testid="stMetric"] {border: 1px solid rgba(128,128,128,.25); padding: 14px; border-radius: 12px;}
    </style>
    """,
    unsafe_allow_html=True,
)

init_db()

if ticket_count() == 0:
    seed_from_csv(ROOT / "data" / "tickets.csv")

st.title("Support Triage & Insights")
st.caption(
    "AI-assisted ticket triage with human escalation, similar-ticket retrieval, "
    "knowledge-base matching, agent feedback, and support analytics."
)

with st.sidebar:
    st.header("Demo workflow")
    st.write(
        "1. Analyze a ticket\n\n"
        "2. Review similar historical tickets\n\n"
        "3. Check the escalation recommendation\n\n"
        "4. Rate whether the recommendation was useful"
    )
    st.divider()
    st.caption(
        "The app works without an API key using deterministic fallback rules. "
        "OpenAI-assisted classification is optional."
    )

tab1, tab2, tab3, tab4 = st.tabs(
    ["Analyze Ticket", "Dashboard", "Ticket Queue", "Agent Feedback"]
)

with tab1:
    st.subheader("Analyze a new support ticket")

    input_col, context_col = st.columns([2, 1], gap="large")

    with input_col:
        subject = st.text_input(
            "Subject",
            placeholder="Export is stuck at 99%",
        )
        description = st.text_area(
            "Description",
            height=170,
            placeholder="Describe the user's issue...",
        )

    with context_col:
        plan = st.selectbox(
            "Customer plan",
            ["Free", "Standard", "Pro", "Unlimited"],
        )
        st.info(
            "Tickets are compared against previous cases before the new ticket is saved, "
            "so the similarity results only show historical examples."
        )

    if st.button("Analyze ticket", type="primary", use_container_width=False):
        if not subject.strip() or not description.strip():
            st.warning("Add both a subject and description.")
        else:
            existing_tickets = load_tickets()
            similar = find_similar_tickets(
                subject,
                description,
                existing_tickets,
                limit=3,
            )

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

            st.session_state["last_analysis"] = {
                "ticket_id": ticket_id,
                "triage": triage,
                "similar": similar,
                "suggested_article": suggested_article,
                "draft_response": draft_response,
            }

    analysis = st.session_state.get("last_analysis")

    if analysis:
        st.divider()
        st.success(f"Ticket #{analysis['ticket_id']} analyzed and saved.")

        triage = analysis["triage"]
        metric1, metric2, metric3, metric4 = st.columns(4)
        metric1.metric("Category", triage["category"])
        metric2.metric("Priority", triage["priority"])
        metric3.metric(
            "Human escalation",
            "Yes" if triage["needs_human"] else "No",
        )
        metric4.metric("Classifier", triage.get("source", "rules").title())

        result_left, result_right = st.columns([1, 1], gap="large")

        with result_left:
            st.markdown("#### Recommendation")
            st.write("**Classification reason**")
            st.write(triage["reason"])

            st.write("**Suggested help article**")
            st.write(analysis["suggested_article"])

            st.write("**Draft response**")
            st.code(analysis["draft_response"], language=None)

        with result_right:
            st.markdown("#### Similar historical tickets")
            similar = analysis["similar"]

            if not similar:
                st.caption("No historical tickets cleared the similarity threshold.")
            else:
                for match in similar:
                    with st.container(border=True):
                        st.write(f"**#{match['id']} — {match['subject']}**")
                        st.caption(
                            f"{match['category']} · {match['priority']} · "
                            f"{match['score'] * 100:.0f}% text similarity"
                        )
                        if match["suggested_article"]:
                            st.write(f"Help article: {match['suggested_article']}")

        st.markdown("#### Agent feedback")
        st.caption(
            "This feedback is stored separately from the ticket so recommendation quality "
            "can be measured over time."
        )

        with st.form(f"feedback_{analysis['ticket_id']}"):
            helpful_label = st.radio(
                "Was this recommendation useful?",
                ["Helpful", "Not helpful"],
                horizontal=True,
            )
            notes = st.text_input(
                "Optional note",
                placeholder="Example: Correct category, but escalation was unnecessary.",
            )
            submitted = st.form_submit_button("Save feedback")

            if submitted:
                add_feedback(
                    analysis["ticket_id"],
                    helpful_label == "Helpful",
                    notes,
                )
                st.success("Feedback saved.")

with tab2:
    st.subheader("Support operations dashboard")

    tickets = load_tickets()
    feedback = load_feedback()

    filter1, filter2, filter3 = st.columns(3)

    with filter1:
        category_options = ["All"] + sorted(tickets["category"].dropna().unique().tolist())
        category_filter = st.selectbox("Category", category_options, key="dashboard_category")

    with filter2:
        priority_options = ["All", "High", "Medium", "Low"]
        priority_filter = st.selectbox("Priority", priority_options, key="dashboard_priority")

    with filter3:
        plan_options = ["All"] + sorted(tickets["plan"].dropna().unique().tolist())
        plan_filter = st.selectbox("Plan", plan_options, key="dashboard_plan")

    filtered = tickets.copy()
    if category_filter != "All":
        filtered = filtered[filtered["category"] == category_filter]
    if priority_filter != "All":
        filtered = filtered[filtered["priority"] == priority_filter]
    if plan_filter != "All":
        filtered = filtered[filtered["plan"] == plan_filter]

    metrics = summary_metrics(filtered, feedback)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Tickets", metrics["total"])
    c2.metric("Open", metrics["open"])
    c3.metric("Escalation rate", f"{metrics['human_rate']:.0f}%")
    c4.metric("Top issue", metrics["top_category"])
    c5.metric(
        "Helpful feedback",
        "N/A" if metrics["helpful_rate"] is None else f"{metrics['helpful_rate']:.0f}%",
        help=f"Based on {metrics['feedback_count']} feedback response(s).",
    )

    chart_left, chart_right = st.columns(2, gap="large")

    with chart_left:
        st.markdown("#### Tickets by category")
        category_df = category_counts(filtered)
        if category_df.empty:
            st.caption("No tickets match the current filters.")
        else:
            st.bar_chart(category_df.set_index("category")["tickets"])

    with chart_right:
        st.markdown("#### Tickets by priority")
        priority_df = priority_counts(filtered)
        if priority_df.empty:
            st.caption("No tickets match the current filters.")
        else:
            st.bar_chart(priority_df.set_index("priority")["tickets"])

    if not filtered.empty:
        top_category = metrics["top_category"]
        top_count = int((filtered["category"] == top_category).sum())

        with st.container(border=True):
            st.markdown("#### Recurring issue signal")
            st.write(
                f"**{top_category}** is the most common issue in the current view "
                f"with **{top_count} ticket(s)**. This is a candidate for a help-center "
                "update, product investigation, or support workflow improvement."
            )

        st.markdown("#### Recent tickets")
        recent_columns = [
            "id", "subject", "plan", "category", "priority", "status", "needs_human"
        ]
        st.dataframe(
            filtered[recent_columns].head(8),
            use_container_width=True,
            hide_index=True,
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

with tab4:
    st.subheader("Agent feedback")
    feedback = load_feedback()

    if feedback.empty:
        st.info("No recommendation feedback has been submitted yet.")
    else:
        helpful_rate = feedback["helpful"].mean() * 100
        f1, f2, f3 = st.columns(3)
        f1.metric("Responses", len(feedback))
        f2.metric("Helpful", f"{helpful_rate:.0f}%")
        f3.metric("Needs improvement", f"{100 - helpful_rate:.0f}%")

        feedback_display = feedback.copy()
        feedback_display["helpful"] = feedback_display["helpful"].map(
            {1: "Helpful", 0: "Not helpful"}
        )
        st.dataframe(
            feedback_display[
                ["ticket_id", "subject", "category", "helpful", "notes", "created_at"]
            ],
            use_container_width=True,
            hide_index=True,
        )
