import streamlit as st
import pandas as pd
import plotly.express as px
import os


priority_icons = {
    "Highest": "⚡",
    "High": "↑",
    "Medium": "→",
    "Low": "↓",
    "Lowest": "⬇",
}

st.set_page_config(layout="wide")

st.title("Appello Year End Report")

csv_files = sorted(
    [f for f in os.listdir("csv_data") if f.endswith(".csv")], reverse=True
)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    selected_file = st.selectbox("Select data file:", csv_files, index=0)

with open(f"csv_data/{selected_file}", "r") as file:
    data = pd.read_csv(file)

data["Created"] = pd.to_datetime(data["Created"], utc=True)

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
    priority_dist = data["Priority"].value_counts()
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


st.subheader("Assignee Workload Analysis")

col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    assignee_dist = data["Assignee"].value_counts()
    print(assignee_dist.values)
    fig_assignee = px.bar(
        x=assignee_dist.index,
        y=assignee_dist.values,
        labels={"x": "Assignee", "y": "Number of Tickets"},
        title="Total Tickets per Assignee",
    )
    st.plotly_chart(fig_assignee)

with col2:
    st.subheader("Leaderboard")
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
    completed_tickets = data[data["Status"].isin(["In Prod", "Duplicate", "Cancelled"])]
    mvp_by_tickets = completed_tickets["Assignee"].value_counts()
    if not mvp_by_tickets.empty:
        for rank, (name, count) in enumerate(mvp_by_tickets.items(), 1):
            st.metric(f"#{rank} - {name}", f"{count} tickets completed")


col1, col2 = st.columns(2)
with col1:
    if "Story Points" in data.columns and data["Story Points"].notna().any():
        story_points = (
            data.groupby("Assignee")["Story Points"].sum().sort_values(ascending=False)
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

st.subheader("Parent Ticket Distribution by Assignee")

parent_tickets = data[data["Parent Ticket"].notna()]
parent_assignee_dist = pd.crosstab(
    parent_tickets["Parent Ticket"], parent_tickets["Assignee"]
)

fig_parent = px.bar(
    parent_assignee_dist,
    title="Parent Tickets Distribution by Assignee",
    labels={
        "value": "Number of Sub-tickets",
        "Parent Ticket": "Parent Ticket",
        "Assignee": "Assignee",
    },
    barmode="stack",
)

fig_parent.update_layout(
    xaxis_tickangle=-45,
    height=600,
    showlegend=True,
    legend_title="Assignees",
    xaxis={
        "tickmode": "array",
        "ticktext": [
            f"{text[:30]}..." if len(text) > 30 else text
            for text in parent_assignee_dist.index
        ],
        "tickvals": list(range(len(parent_assignee_dist.index))),
        "tickfont": {"size": 10},
        "tickangle": -45,
        "automargin": True,
    },
)

st.plotly_chart(fig_parent, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Parent Tickets", len(parent_tickets["Epic Link"].unique()))
with col2:
    st.metric("Total Sub-tickets", len(parent_tickets))


st.subheader("Fix Version")

fix_version_data = data[data["Fix Version"].notna()]

fix_version_counts = fix_version_data["Fix Version"].value_counts()

fig_fix_version = px.bar(
    x=fix_version_counts.index,
    y=fix_version_counts.values,
    title="Total Tickets per Fix Version",
    labels={"x": "Fix Version", "y": "Number of Tickets"},
)

fig_fix_version.update_layout(
    xaxis_tickangle=-45,
    height=500,
    xaxis={
        "tickfont": {"size": 10},
        "automargin": True,
    },
)

st.plotly_chart(fig_fix_version, use_container_width=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Fix Versions", len(fix_version_counts))
with col2:
    st.metric(
        "Total Tickets with Fix Versions",
        f"{(fix_version_counts.sum() / len(data) * 100):.1f}%",
    )
with col3:
    st.metric(
        "Total Tickets without Fix Versions",
        f"{((len(data) - fix_version_counts.sum()) / len(data) * 100):.1f}%",
    )

st.subheader("Most Commented Tickets")

most_commented = data[
    ["Issue Key", "Issue Summary", "Comment count", "Status", "Priority"]
]
most_commented = most_commented.sort_values("Comment count", ascending=False).head(10)

for idx, row in most_commented.iterrows():
    with st.container():
        cols = st.columns([1, 6, 1, 2, 2, 1])
        with cols[0]:
            st.write(f"#{row['Issue Key']}")
        with cols[1]:
            st.write(row["Issue Summary"])
        with cols[2]:
            st.write(f"💬 {row['Comment count']}")
        with cols[3]:
            st.write(row["Status"])
        with cols[4]:
            priority_icon = priority_icons.get(row["Priority"], "•")
            st.write(f"{priority_icon} {row['Priority']}")
        with cols[5]:
            st.write(row["Comment count"])
        st.divider()

col1, col2 = st.columns(2)
with col1:
    avg_comments = data["Comment count"].mean()
    st.metric("Average Comments per Ticket", f"{avg_comments:.1f}")
with col2:
    total_comments = data["Comment count"].sum()
    st.metric("Total Comments", total_comments)
