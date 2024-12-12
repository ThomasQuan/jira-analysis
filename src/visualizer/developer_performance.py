import pandas as pd
import plotly.express as px
import streamlit as st


def developer_performance(data):
    st.title("Year End Dev Performance Report")
    col1, col2, col3 = st.columns([2, 2, 1])

    with col1:
        assignee_dist = data["Assignee"].value_counts()
        fig_assignee = px.bar(
            x=assignee_dist.index,
            y=assignee_dist.values,
            labels={"x": "Assignee", "y": "Number of Tickets"},
            title="Total Tickets per Assignee",
        )
        st.plotly_chart(fig_assignee)

    with col2:
        priority_by_assignee = pd.crosstab(data["Assignee"], data["Priority"])
        fig_priority = px.bar(
            priority_by_assignee,
            title="Tickets by Priority per Assignee",
            labels={"value": "Number of Tickets", "Assignee": "Assignee"},
            barmode="stack",
        )
        fig_priority.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_priority)

    with col3:
        st.subheader("MVP Leaderboard")
        completed_tickets = data[
            data["Status"].isin(["In Prod", "Duplicate", "Cancelled"])
        ]
        mvp_by_tickets = completed_tickets["Assignee"].value_counts()
        if not mvp_by_tickets.empty:
            for rank, (name, count) in enumerate(mvp_by_tickets.head(5).items(), 1):
                st.metric(f"#{rank} - {name}", f"{count} tickets completed")

    col1, col2 = st.columns(2)
    with col1:
        if "Story Points" in data.columns and data["Story Points"].notna().any():
            story_points = (
                data.groupby("Assignee")["Story Points"]
                .sum()
                .sort_values(ascending=False)
            )
            fig_points = px.bar(
                x=story_points.index,
                y=story_points.values,
                labels={"x": "Assignee", "y": "Total Story Points"},
                title="Story Points per Assignee",
            )
            fig_points.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_points)

    with col2:
        issue_types_by_assignee = pd.crosstab(data["Assignee"], data["Issue Type"])
        fig_types = px.bar(
            issue_types_by_assignee,
            title="Issue Types Distribution per Assignee",
            labels={"value": "Number of Tickets", "Assignee": "Assignee"},
            barmode="stack",
        )
        fig_types.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_types)
