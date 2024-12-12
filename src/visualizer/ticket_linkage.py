import pandas as pd
import plotly.express as px
import streamlit as st


def ticket_linkage(data):
    st.title("Ticket Linkage")

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

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Total Parent Tickets",
            len(parent_tickets["Epic Link"].unique()),
            help="This does not count the tickets that are not categorized as a parent ticket",
        )
    with col2:
        st.metric(
            "Total Sub-tickets",
            len(parent_tickets),
            help="This counts all the tickets that are categorized as a sub-ticket, meaning they have tickets that are linked to them",
        )
    with col3:
        st.metric(
            "Ticket with the most sub-tickets",
            parent_assignee_dist.idxmax().values[0],
            help="This is the ticket with the most sub-tickets",
        )
