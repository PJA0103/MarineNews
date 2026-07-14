import streamlit as st

from database import (
    get_all_countries,
    get_all_technologies,
    get_all_topics,
    search_news
)

st.set_page_config(
    page_title="Marine Energy Intelligence",
    page_icon="🌊",
    layout="wide"
)

st.title(" 不停滿溢的新聞大平台 ")

# =========================
# Sidebar
# =========================

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
    end_date=end_date
)

st.write(f"### 共有 {len(rows)} 條新聞")

for row in rows:
    with st.expander(f"💾 {row[1]} | {row[0]}"):

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
        st.link_button(
            "🔗 Original Article",
            row[14]
        )
