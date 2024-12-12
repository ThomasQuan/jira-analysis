import streamlit as st
from src.visualizer.priority_icons import priority_icons

def comment_stats(data):
    st.subheader("Most Commented Tickets")

    most_commented = data[
        ["Issue Key", "Issue Summary", "Comment count", "Status", "Priority"]
    ]
    most_commented = most_commented.sort_values("Comment count", ascending=False).head(
        10
    )

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

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_comments = data["Comment count"].mean()
        st.metric("Average Comments per Ticket", f"{avg_comments:.1f}")
    with col2:
        total_comments = data["Comment count"].sum()
        st.metric("Total Comments", total_comments)
    with col3:
        total_tickets_without_comments = len(data[data["Comment count"] == 0])
        st.metric("Total Tickets without Comments", total_tickets_without_comments)
    with col4:
        total_tickets_with_comments = len(data[data["Comment count"] > 0])
        st.metric("Total Tickets with Comments", total_tickets_with_comments)
