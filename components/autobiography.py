"""Render the student's full autobiography."""

from pathlib import Path

import streamlit as st

from utils.content import load_markdown


def render_autobiography(content_dir: Path) -> None:
    """Display and offer the unmodified autobiography Markdown."""
    st.header("Autobiography")
    autobiography = load_markdown(content_dir / "my-autobiography.md")
    if autobiography is None:
        st.warning("Autobiography content could not be loaded.")
        return

    st.markdown(autobiography)
    st.download_button(
        "Download my autobiography",
        data=autobiography,
        file_name="arth-endrina-autobiography.md",
        mime="text/markdown",
    )
