"""Streamlit entry point for Arth Andrey C. Endrina's portfolio."""

from pathlib import Path

import streamlit as st

from components.about import render_about
from components.autobiography import render_autobiography
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
apply_visual_system(ROOT / "assets" / "styles" / "app.css")

st.title("Arth Andrey C. Endrina")
st.caption("Bachelor of Science in Computer Science · 3rd Year")

with st.sidebar:
    st.header("Explore")
    page = st.radio(
        "Portfolio sections",
        ["About", "Autobiography", "Skills", "Portfolio", "Feedback"],
        label_visibility="collapsed",
    )

if page == "About":
    render_about(CONTENT_DIR, ASSET_DIR)
elif page == "Autobiography":
    render_autobiography(CONTENT_DIR)
elif page == "Skills":
    render_skills(CONTENT_DIR)
else:
    st.info(f"The {page} section will be added in the next implementation tasks.")
