import streamlit as st

from database import (
    get_all_countries,
    get_all_technologies,
    get_all_topics,
    search_news,
    mark_as_read,
    export_excel
)

from openpyxl import Workbook
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="Marine Energy Intelligence",
    page_icon="🌊",
    layout="wide"
)

st.title(" 不停溢流的大平台 ")

# =========================
# Sidebar
# =========================

# show_unread_only = st.sidebar.checkbox(
#     "Unread only",
#     value=True
# )

with st.sidebar:
    st.header("Filters")
    countries = st.multiselect(
        "Country",
        get_all_countries()
    )
    technologies = st.multiselect(
        "Technology",
        get_all_technologies()
    )
    topics = st.multiselect(
        "Topic",
        get_all_topics()
    )
    st.divider()
    start_date = st.date_input(
        "Start Date",
        value=None
    )
    end_date = st.date_input(
        "End Date",
        value=None
    )
    st.divider()

    company = st.text_input("Company")
    organization = st.text_input("Organization")
    project = st.text_input("Project")
    site = st.text_input("Site")
    sea_area = st.text_input("Sea Area")
    custom = st.text_input("Custom")

# =========================
# Main Page  
# =========================

# col1, col2 = st.columns([1, 1])
col1, col2, col3 = st.columns([6, 2, 2])

with col1:
    show_unread_only = st.toggle(
        "Unread Only",
        value=True
    )

rows = search_news(
    country=countries,
    technology=technologies,
    topic=topics,
    company=company,
    organization=organization,
    project=project,
    site=site,
    sea_area=sea_area,
    custom=custom,
    start_date=start_date,
    end_date=end_date,
    unread_only=show_unread_only
)

with col2:
    st.metric(
        "News",
        len(rows)
    )

for idx, row in enumerate(rows):
    news_url = row[14]
    is_read_status = row[15]
    with st.expander(f"🧾 {row[1]} | {row[0]}"):

        st.write(f"**Country:** {row[5]}")
        st.write(f"**Technology:** {row[6]}")
        st.write(f"**Topic:** {row[7]}")
        st.divider()

        st.subheader("Highlight")
        st.write(row[2])

        st.subheader("重點摘要")
        st.write(row[3])

        st.subheader("💡Note")
        st.write(row[4])
        st.divider()

        if is_read_status != 1 and is_read_status != "1":
            btn_col1, btn_col2 = st.columns([1,1])
            with btn_col1:
                st.link_button(
                    "🔗 Original Article",
                    row[14]
                )
            with btn_col2:
                if st.button("已讀", key=f"read_btn_{idx}"):
                    mark_as_read(news_url)
                    st.toast("標記為已讀")
                    st.rerun()
        else:
            st.link_button(
                "🔗 Original Article",
                row[14]
                )

with col3:
    now = datetime.now().strftime("%Y%m%d_%H%M")
    st.download_button(
        label="匯出excel",
        data=export_excel(rows),
        file_name=f"MarineNews_{now}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
