import streamlit as st
import plotly.express as px


def fix_versions_kpi(data):
    st.subheader("Fix Version KPIs")

    fix_version_data = data[data["Fix Version"].notna()]

    fix_version_counts = fix_version_data["Fix Version"].value_counts()

    fig_fix_version = px.bar(
        x=fix_version_counts.index,
        y=fix_version_counts.values,
        title="Highest Fix Version",
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

    col1, col2, col3, col4 = st.columns(4)
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
    with col4:
        # fix version with the most tickets
        st.metric(
            "Fix Version with the most tickets",
            f"{fix_version_counts.idxmax()} ({fix_version_counts.max()} tickets)",
            help=f"This is the fix version with the most tickets: {fix_version_counts.max()}",
        )
