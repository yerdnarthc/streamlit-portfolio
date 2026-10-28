"""Shared presentation helpers for the Streamlit portfolio."""

from pathlib import Path

import streamlit as st


def apply_visual_system(stylesheet: Path) -> None:
    """Inject the trusted local stylesheet for the portfolio."""
    try:
        css = stylesheet.read_text(encoding="utf-8")
    except OSError:
        st.warning("The portfolio stylesheet could not be loaded.")
        return

    st.html(f"<style>{css}</style>")
