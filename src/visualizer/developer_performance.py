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
        completed_tickets = data[
            data["Status"].isin(["In Prod", "Duplicate", "Cancelled"])
        ].copy()
        completed_tickets["Created"] = pd.to_datetime(
            completed_tickets["Created"], utc=True
        )

        def get_completion_date(history):
            try:
                changes = eval(history)
                if changes[0]["to"] in ["In Prod", "Duplicate", "Cancelled"]:
                    return pd.to_datetime(changes[0]["date"], utc=True)
            except:
                return pd.NaT

        completed_tickets["Completion Date"] = pd.to_datetime(
            completed_tickets["Status Change History"].apply(get_completion_date),
            utc=True,
        )
        completed_tickets = completed_tickets.dropna(subset=["Completion Date"])

        completed_tickets["Resolution Time (Days)"] = (
            completed_tickets["Completion Date"] - completed_tickets["Created"]
        ).dt.total_seconds() / 86400 

        fig_resolution = px.scatter(
            completed_tickets,
            x="Severity",
            y="Resolution Time (Days)",
            color="Assignee",
            title="Resolution Time by Severity",
            labels={
                "Resolution Time (Days)": "Days to Resolve",
                "Severity": "Severity Level",
            },
            hover_data=["Issue Key", "Issue Summary"],
        )

        # Update layout to show grid
        fig_resolution.update_layout(
            xaxis_title="Severity Level",
            yaxis_title="Days to Resolve",
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True),
        )

        st.plotly_chart(fig_resolution)
    with col2:
        completed_tickets = data[
            data["Status"].isin(["In Prod", "Duplicate", "Cancelled"])
        ].copy()
        completed_tickets["Created"] = pd.to_datetime(
            completed_tickets["Created"], utc=True
        )

        def get_completion_date(history):
            try:
                changes = eval(history)
                if changes[0]["to"] in ["In Prod", "Duplicate", "Cancelled"]:
                    return pd.to_datetime(changes[0]["date"], utc=True)
            except:
                return pd.NaT

        completed_tickets["Completion Date"] = pd.to_datetime(
            completed_tickets["Status Change History"].apply(get_completion_date),
            utc=True,
        )

        daily_tickets = (
            completed_tickets.groupby(completed_tickets["Created"].dt.date)
            .size()
            .reset_index()
        )
        daily_tickets.columns = ["Date", "Number of Tickets"]

        daily_tickets["Date"] = pd.to_datetime(daily_tickets["Date"])

        time_granularity = st.selectbox("Select Time Granularity", ["Weekly", "Daily"])

        if time_granularity == "Weekly":
            x_value = daily_tickets["Date"].dt.strftime("%U")
            x_label = "Week of Year"
        else:
            x_value = daily_tickets["Date"].dt.strftime("%d")
            x_label = "Day of Month"

        fig_resolution = px.density_heatmap(
            daily_tickets,
            x=x_value,
            y=daily_tickets["Date"].dt.strftime("%A"),
            z="Number of Tickets",
            title=f"Ticket Creation Calendar Heatmap ({time_granularity} View)",
            labels={"x": x_label, "y": "Day of Week", "z": "Number of Tickets"},
        )

        fig_resolution.update_layout(
            xaxis_title="Day of Month",
            yaxis_title="Day of Week",
            coloraxis_colorbar_title="Number of Tickets",
        )

        st.plotly_chart(fig_resolution)

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
