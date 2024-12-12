import streamlit as st
import pandas as pd
import os
from src.visualizer.ticket_distribution import ticket_distribution
from src.visualizer.developer_performance import developer_performance
from src.visualizer.ticket_linkage import ticket_linkage
from src.visualizer.fix_versions_kpi import fix_versions_kpi
from src.visualizer.comment_stats import comment_stats

st.set_page_config(layout="wide")

st.title("Company Year End Report")

csv_files = sorted(
    [f for f in os.listdir("csv_data") if f.endswith(".csv")], reverse=True
)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    selected_file = st.selectbox("Select data file:", csv_files, index=0)

with open(f"csv_data/{selected_file}", "r") as file:
    data = pd.read_csv(file)


data["Created"] = pd.to_datetime(data["Created"], utc=True)

ticket_distribution(data)

developer_performance(data)

ticket_linkage(data)

fix_versions_kpi(data)

comment_stats(data)