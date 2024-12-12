import pandas as pd
import plotly.express as px
import streamlit as st
from src.visualizer.priority_icons import priority_icons


def ticket_distribution(data: pd.DataFrame):
    st.title("Ticket distribution of the year")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Daily Ticket Creation")
        daily_tickets = (
            data.groupby(data["Created"].dt.date)["Issue Key"].count().sort_index()
        )
        fig_daily = px.line(
            x=daily_tickets.index,
            y=daily_tickets.values,
            labels={"x": "Date", "y": "Number of Tickets"},
        )
        st.plotly_chart(fig_daily, use_container_width=True)

    with col2:
        st.subheader("Issue Type Distribution")
        issue_type_dist = data["Issue Type"].value_counts()
        fig_issue = px.pie(
            values=issue_type_dist.values,
            names=issue_type_dist.index,
            title="Distribution of Issue Types",
        )
        st.plotly_chart(fig_issue, use_container_width=True)

    with col3:
        st.subheader("Status Distribution")
        status_dist = data["Status"].value_counts()
        fig_status = px.pie(
            values=status_dist.values,
            names=status_dist.index,
            title="Distribution of Issue Status",
        )
        st.plotly_chart(fig_status, use_container_width=True)

    st.subheader("Summary Metrics")
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    with col1:
        st.metric("Total Tickets", len(data))
    with col2:
        st.metric("Issue Types", len(data["Issue Type"].unique()))
    with col3:
        st.metric("Status Types", len(data["Status"].unique()))
    with col4:
        st.metric("Assignees", len(data["Assignee"].unique()))
    with col5:
        st.metric("Story Points", data["Story Points"].sum())
    with col6:
        priority_with_icon = f"{priority_icons.get(data['Priority'].mode()[0], '•')} {data['Priority'].mode()[0]}"
        st.metric("Most Common Priority", priority_with_icon)
    with col7:
        highest_priority = len(data[data["Priority"] == "Highest"])
        highest_priority_pct = f"{(highest_priority/len(data)*100):.1f}%"

        def burn_out_calc(highest_priority_pct):
            if float(highest_priority_pct.strip("%")) > 50:
                return "You are at risk of burnout. Please take a break."
            else:
                return "You are not at risk of burnout. Keep up the good work!"

        st.metric(
            "Highest Priority %",
            highest_priority_pct,
            help=burn_out_calc(highest_priority_pct),
        )
