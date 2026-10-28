"""Streamlit entry point for Arth Andrey C. Endrina's portfolio."""

from pathlib import Path

import streamlit as st

from components.about import render_about
from components.autobiography import render_autobiography
from components.feedback import render_feedback
from components.portfolio import render_portfolio
from components.skills import render_skills
from components.ui import apply_visual_system


ROOT = Path(__file__).parent
CONTENT_DIR = ROOT / "contents"
ASSET_DIR = ROOT / "assets"

st.set_page_config(
    page_title="Arth Andrey C. Endrina | Portfolio",
    page_icon="👋",
    layout="wide",
)

# # Custom CSS to change the sidebar width
# st.markdown(
#     """
#     <style>
#     [data-testid="stSidebar"] {
#         min-width: 350px;
#         max-width: 500px;
#     }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

apply_visual_system(ROOT / "assets" / "styles" / "app.css")

with st.sidebar:
    st.title("Arth Andrey C. Endrina")
    st.caption("Computer Science · 3rd Year · CIT-U")
    st.divider()
    page = st.radio(
        "Navigation",
        ["About", "Autobiography", "Skills", "Portfolio", "Feedback"],
        label_visibility="collapsed",
    )

if page == "About":
    render_about(CONTENT_DIR, ASSET_DIR)
elif page == "Autobiography":
    render_autobiography(CONTENT_DIR)
elif page == "Skills":
    render_skills(CONTENT_DIR)
elif page == "Portfolio":
    render_portfolio(CONTENT_DIR, ASSET_DIR)
elif page == "Feedback":
    render_feedback()
else:
    st.info(f"The {page} section will be added in the next implementation tasks.")
